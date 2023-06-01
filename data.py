import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from utils import *
import time
from pytz import timezone
import inspect
import json

tz = timezone('EST')

gc = gspread.service_account(filename='myCredentials.json')

class data_handler:
    def __init__(self):
        self.retrieve_google_sheets()

    def user_type_from_barcode(self, barcode):
        if barcode in self.student_ids:
            return "Student"
        elif barcode in self.faculty_ids:
            return "Faculty"
        else:
            return None
    
    def get_user_from_barcode(self, barcode, user_type):
        if user_type == "Student":
            return self.student_users[self.student_users['Person ID'] == int(barcode)].iloc[0]
        elif user_type == "Faculty":
            return self.faculty_users[self.faculty_users['Person ID'] == int(barcode)].iloc[0]
        else:
            #Unknown outcome
            pass
    def log_student_lateness(self, user, reason):
        date, clock = get_date_and_clock()
        student_data = [date, clock, user['Preferred Name'], user['Last Name'], user['Current Grade'], int(user['Person ID']), user['House'], user['Advisor'], reason]
        self.lateness_entry = pd.concat([self.lateness_entry, pd.DataFrame([student_data], columns=self.lateness_entry.columns)], axis = 0,  ignore_index = True)
        self.lateness.append_row(student_data)

    def log_student_sign_out(self, location, user, transport, gone_for_day, window, etr="N/A"):
        date, clock = get_date_and_clock()
        confirm_msg = f"{user['Preferred Name']} is signing out to {location}"

        if gone_for_day:
            time_back = "Gone For Day"
            confirm_msg += " for the rest of the day"
        else:
            time_back = ""

        student_data = [date, clock, user['Preferred Name'], user['Last Name'], user['Current Grade'], int(user['Person ID']), user['House'], user['Advisor'], location, transport, time_back, "Absent", etr]
        self.off_campus_entry = pd.concat([self.off_campus_entry, pd.DataFrame([student_data], columns=self.off_campus_entry.columns)], axis = 0, ignore_index = True)
        self.off_campus.append_row(student_data)
        success_confirm(confirm_msg)
        window.destroy()

    def log_faculty_sign_out(self, user, gone_for_day, window, etr="N/A") :
        date, clock = get_date_and_clock()
        
        confirm_msg = f"{user['Preferred Name']} is signing out"

        if gone_for_day:
            time_back = "Gone For Day"
            confirm_msg += " for the rest of the day"
        else:
            time_back = ""

        faculty_data = [date, clock, user['Full Name'], int(user['Person ID']), time_back, "Absent", etr]
        self.fac_off_campus_entry = pd.concat([self.fac_off_campus_entry, pd.DataFrame([faculty_data], columns=self.fac_off_campus_entry.columns)], axis=0, ignore_index=True)
        self.fac_off_campus.append_row(faculty_data)           
        success_confirm(confirm_msg)
        window.destroy()
        
    def sync_sheets(self):
        print("Sync Sheets")
        confirmation = create_confirm_box("Syncing data with server, please wait.", "sync")
        confirmation.after(200,lambda:confirmation.destroy())
        self.IDList = gc.open_by_url("https://docs.google.com/spreadsheets/d/1xgwMCl0X7d-AuKxmPgsLiRuQJ7eDUxKQyKmpTC7YvKk/")
        self.policy = self.IDList.worksheet("Policy")
        self.policy_df = pd.DataFrame(self.policy.get_all_records()) 
        records = gc.open_by_url("https://docs.google.com/spreadsheets/d/1tWKMoprqwx6J9sQpf4Cd-NvbMtUd5p3_sYhiPz17pZQ")
        self.lateness = records.worksheet("Lateness")
        self.lateness_entry = pd.DataFrame(self.lateness.get_all_records())
        self.off_campus = records.worksheet("Off Campus")
        self.off_campus_entry = pd.DataFrame(self.off_campus.get_all_records())
        self.fac_off_campus = records.worksheet("Faculty Off Campus")
        self.fac_off_campus_entry = pd.DataFrame(self.fac_off_campus.get_all_records())

        self.driving_notes = records.worksheet("Driving Note")
        self.driving_notes_df = pd.DataFrame(self.driving_notes.get_all_records())

    def retrieve_google_sheets(self):
        print("Retrieving Google Sheets")
        self.IDList = gc.open_by_url("https://docs.google.com/spreadsheets/d/1xgwMCl0X7d-AuKxmPgsLiRuQJ7eDUxKQyKmpTC7YvKk/")
        self.students = self.IDList.worksheet("Student")
        self.student_users = pd.DataFrame(self.students.get_all_records()) 
        self.student_users["Type"] = "Student"
        self.student_ids = self.student_users["Person ID"].values

        self.faculty = self.IDList.worksheet("Faculty")
        self.faculty_users = pd.DataFrame(self.faculty.get_all_records()) 
        self.faculty_users["Type"] = "Faculty"
        self.faculty_ids = self.faculty_users["Person ID"].values
        self.faculty_users["Last Name"] = self.faculty_users["Full Name"].apply(lambda name: name.split(", ")[0])
        self.faculty_users["Preferred Name"] = self.faculty_users["Full Name"].apply(lambda name: name.split(", ")[1])

        self.policy = self.IDList.worksheet("Policy")
        self.policy_df = pd.DataFrame(self.policy.get_all_records()) 

        # Save local copy of records and way to update
        records = gc.open_by_url("https://docs.google.com/spreadsheets/d/1tWKMoprqwx6J9sQpf4Cd-NvbMtUd5p3_sYhiPz17pZQ")
        self.lateness = records.worksheet("Lateness")
        self.lateness_entry = pd.DataFrame(self.lateness.get_all_records())
        self.off_campus = records.worksheet("Off Campus")
        self.off_campus_entry = pd.DataFrame(self.off_campus.get_all_records())
        self.fac_off_campus = records.worksheet("Faculty Off Campus")
        self.fac_off_campus_entry = pd.DataFrame(self.fac_off_campus.get_all_records())

        self.driving_notes = records.worksheet("Driving Note")
        self.driving_notes_df = pd.DataFrame(self.driving_notes.get_all_records())

    def is_user_currently_signed_out(self, user_id, user_type):
        if user_type == "Student":
            logs = self.off_campus_entry
        elif user_type == "Faculty":
            logs = self.fac_off_campus_entry
        else:
            print("Improper User Type given")
            error_pop("Invalid User ID, please see Ms. Kennedy")
        currently_signed_out_ids = logs[logs["Attendance Status"] == "Absent"]["ID"]
        if user_id in currently_signed_out_ids.values:
            print("User is off campus")
            return True
        else:
            print("User is on campus")
            return False
    
    def return_to_campus(self, user, window):
        print(f"{user['Preferred Name']} is returning to campus")
        if user["Type"] == "Student":
            logs = self.off_campus_entry
            gspread = self.off_campus
        elif user["Type"] == "Faculty":
            logs = self.fac_off_campus_entry
            gspread = self.fac_off_campus
        else:
            print("Improper User Type given")
        
        date, clock = get_date_and_clock()
        index = logs.loc[(logs["Attendance Status"] == "Absent") & (logs["ID"] == user["Person ID"]), ["Time Back", "Attendance Status"]].index[0]
        print(index)
        #Time Back and Attendance Status are the second to last and last columns respectively
        num_columns = logs.shape[1]
        gspread.update_cell(index+2, num_columns-1, "Present")
        gspread.update_cell(index+2, num_columns-2, clock)
        logs.loc[(logs["Attendance Status"] == "Absent") & (logs["ID"] == user["Person ID"]), ["Time Back", "Attendance Status"]] = clock, "Present"
        window.destroy()
    
    def get_user_policies(self, user):
        user_grade = int(user["Current Grade"].split(" ")[-1])
        policies = self.policy_df[self.policy_df["Grade"] == user_grade]
        return policies.iloc[0]
    
    def operation_allowed(self, user):
        clock = get_current_time()
        day_of_week = get_day_of_week()
        
        policies = self.get_user_policies(user)
        if policies["Day of the Week"] != "All":
            allowed_days = json.loads(policies["Day of the Week"])
        else:
            allowed_days = [x for x in range(0, 7)]
        
        # Only uncomment for testing 
        clock = get_time_from_string("12:15")

        earliest = get_time_from_string(policies["Earliest Sign Out Time"])
        latest = get_time_from_string(policies["Latest Sign Out Time"])
        # Check for the following policies: Earliest sign out time, Day of week, and Latest Sign Out Time
        if not day_of_week in allowed_days:
            error_pop(f"Unfortunately, you cannot sign out on this day of the week.")
            return False
        elif earliest > clock:
            error_pop(f"Please wait until {policies['Earliest Sign Out Time']} to sign out")
            return False
        elif latest < clock:
            error_pop(f"Unfortunately, because it is past {policies['Latest Sign Out Time']}, you can no longer sign out.")
            return False
        else:
            return True
    
    def does_user_have_driving_note(self, user):
        clock = get_current_time()
        drivers_notes = self.driving_notes_df[(self.driving_notes_df["Student ID"] == user["Person ID"])]
        if drivers_notes.shape[0] > 0:
            print(get_time_from_string(drivers_notes.iloc[0]["Start Time"]))
            if get_time_from_string(drivers_notes.iloc[0]["Start Time"]).time() < clock.time():
                return True
            else:
                error_pop(f"Your driver's note does not start until {drivers_notes.iloc[0]['Start Time']}")
                return False
        error_pop("The system's records does not currently have a driving permission note for you today.")
        print("no note at all")
        return False
        
