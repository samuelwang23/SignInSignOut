
# Setup Google Sheets Record Spreadsheet

# First Time setup
## Creating a GSPREAD Token
Create a project on google cloud.  In the box labeled “Search for APIs and Services”, search for “Google Sheets API” and enable it. Then follow these [instructions](https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account) for creating a service account. Transfer this json file over to the Raspberry Pi, naming it myCredentials.json, and put it in the same directory as the project files.

## Creating the Google Sheets
There are two google spreadsheets needed for the current configuration of this program: 

**ID List: Static data that impacts program logic**
- Students: All student info (Columns: Full Name, Person ID, Preferred Name, Last Name, Current Grade, House, Advisor)
- Faculty: All faculty info (Columns: Person ID, Full Name)
- Policy: Policies for student off campus privileges (Columns: Grade, Earliest Sign Out Time, Latest Sign Out Time, Day of the Week, Earliest Leave for Day Time)

Follow the procedure in ID list update to get data for the Student and Faculty sheets. In the student sheet, in the Full name Column, paste in the following formula to create a column of full names: `=Concatenate(C2, " ", D2).` For the policy sheet, set the policies for each grade by creating a row and filling out the information. 

**Records: Record keeping, including archives**
- Lateness: Lateness records (Columns: Date, Time, First Name, Last Name, Grade, ID, House, Advisor, Reason for Lateness)
- Off Campus: Off campus records for students (Columns: Date, Time Out, First Name, Last Name, Grade, ID, House, Advisor, Location, Transportation, Time Back, Attendance Status, Estimated Return Time)
- Faculty Off Campus: Off campus records for faculty (Columns: Date, Time Out, Full Name, ID, Time Back, Attendance Status, Estimated Return Time) 
- Driving Note: Driving note permissions (Columns: Student Name, Start Time, Student ID)
- Imported Students Sheet: Import of student names and IDs for Driver's Note Autofill (Columns: Student Name, ID)

Firstly, for the sheets Lateness, Off Campus, and Faculty Off Campus, there must always be a filler row in the sheet, or else the pandas DataFrame is read incorrectly by gspread. To create the imported students sheet, paste the following formula in the cell:
`=Sort(ImportRange(URL OF ID LIST SHEET,"Student!A2:B700"), 1, true)`.

To set up the autofill, hover over "Data" in the tooltip and click Data Validation. Add a new rule. Select "Dropdown (from a range)" as the criteria, then select all of the first column in the Imported Students sheet as members of the criteria. Click Advanced Options and select "Reject the input" for when there is invalid data and "Plain Text" for the display. In the column Student ID, paste in the following formula:
`ARRAYFORMULA(IF(ISBLANK(A3:A100), " ", VLOOKUP(A3:A100, 'Imported Students Sheet'!A1:B700, 2, false)))`.

## Setup Google Sheet Script
**Overview**: This documentation will show how to set up the Apps Script that was used to automatically archive the sign in sign out spreadsheet after each day.

### Step 1
Begin by opening up your records spreadsheet. Then, click the menu item Extension and the sub item App Script.
### Step 2
Copy the code below. Replace all of the "my function" boilerplate with the code below. Test the function using the run button, authorizing the program with your credentials, and making sure archiveAndClearSheets is the selected function. Make sure that the time zone used to set the name of the archive folder is correct.
```
function  archiveAndClearSheets() {

	const  ss = SpreadsheetApp.getActive();

	logs = ['Lateness', 'Off Campus', 'Faculty Off Campus'];

	for (i  in  logs){

		sheetOfLogs = logs[i];

		const  sheetToLogTo = sheetOfLogs + ' Archive ' + Utilities.formatDate(new  Date(), "GMT-5", "yyyy/MM");

		let  archiveSheet = ss.getSheetByName(sheetToLogTo);

		let  logSheet = ss.getSheetByName(sheetOfLogs);

		let  valuesToLog = logSheet.getDataRange().getValues();

		// Ignore the header and the Filler Entry

		valuesToLog.splice(0, 2);

		if(valuesToLog.length <= 0){

			Logger.log("No new data to log");

			continue;

		}

		if (!archiveSheet) {

			const  headerRow = logSheet.getDataRange().getValues()[0];

			archiveSheet = ss.insertSheet(sheetToLogTo, 4);

			archiveSheet.appendRow(headerRow);

			headerRow.forEach((column, index) =>{

				if(column.includes("Time")){

					const  columnChar = (index+10).toString(36).toUpperCase();

					archiveSheet.getRange(columnChar+"2:"+columnChar).setNumberFormat("hh:mm AM/PM");

				}

			})

		}

		const  lastRow = archiveSheet.getLastRow();

		archiveSheet.getRange(lastRow + 1,1,valuesToLog.length, valuesToLog[0].length).setValues(valuesToLog);

		  

		// Delete the archived data

		logSheet.deleteRows(3, valuesToLog.length+1);

	}

	  

	clearSheet = ss.getSheetByName("Driving Note");

	data = clearSheet.getDataRange().getValues();

	clearSheet.getRange('A3:B'+String(data.length+1)).clearContent();

	clearSheet.getRange('C3').setValue('=ARRAYFORMULA(IF(ISBLANK(A3:A100), " " ,VLOOKUP(A3:A100, IMPORTRANGE("1xgwMCl0X7d-AuKxmPgsLiRuQJ7eDUxKQyKmpTC7YvKk", "Student!$A$2:$F$569"), 2, false)))');

}
```

### Step 3
Go to the timer icon on the left menu (triggers).  On the bottom right, click Add Trigger. Select archiveAndClearSheets as the function, change event source to Time-driven, then set the timer trigger and interval based on user needs. Make sure to save the trigger by clicking the save button at the end of the form, if you click out of the modal it doesn't save.

# ID list update 
Every year, the user roster changes and a few sheets need to be updated. Firstly, the sheets "Student" and "Faculty" in IDList should be updated. For the "Student" sheet, the leftmost column is used to create a full name, so the new data needs to be pasted in starting at the second column. The needed columns are "Person ID", "Preferred Name", "Last Name", "Current Grade", "House", and "Advisor". Previously, the most efficient way to get the reports through Veracross was to generate a report for each grade. If this is how the data is fed in, collate all of the reports into one sheet, making sure not to include any repeated headers.

Additionally, the policy sheet in IDList should be reviewed every year. This allows for the off campus policy to be changed without any code modifications. The sign out times should be in 24 hour format. For day of the week, it takes in a list with the numerical days of the week that students can sign out on. For example, [3, 4] would allow members of that grade to sign out on Thursdays and Fridays. Typing in "All" is equivalent to [0, 1, 2, 3, 4, 5, 6]. 