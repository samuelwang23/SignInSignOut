# Setup Google Sheet Script

**Overview**: This documentation will show how to set up the Apps Script that was used to automatically archive the sign in sign out spreadsheet after each day.

## Step 1
Begin by opening up your records spreadsheet. Then, click the menu item Extension and the sub item App Script.
## Step 2
Copy the code below. Replace all of the "my function" boilerplate with the code below. Test the function using the run button, authorizing the program with your credentials, and making sure archiveAndClearSheets is the selected function. 
```
function  archiveAndClearSheets() {

	const  ss = SpreadsheetApp.getActive();

	logs = ['Lateness', 'Off Campus', 'Faculty Off Campus'];

	for (i  in  logs){
		sheetOfLogs = logs[i];
		const  sheetToLogTo = sheetOfLogs + ' Archive ' + Utilities.formatDate(new  Date(), "GMT+1", "yyyy/MM");

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
					const columnChar = (index+10).toString(36).toUpperCase();
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

	clearSheet.deleteRows(3, data.length+1);

}
```

## Step 3
Go to the timer icon on the left menu (triggers).  On the bottom right, click Add Trigger. Select archiveAndClearSheets as the function, change event source to Time-driven, then set the timer trigger and interval based on user needs. Make sure to save the trigger by clicking the save button at the end of the form, if you click out of the modal it doesn't save.
