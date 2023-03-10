import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from utils import *
import time
from pytz import timezone
import inspect

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
        pd.concat([self.lateness_entry, student_data])

    def log_student_sign_out(self, location, user, transport, gone_for_day, window):
        print(location)
        date, clock = get_date_and_clock()
        student_data = pd.Series([date, clock, user['Preferred Name'], user['Last Name'], user['Current Grade'], int(user['Person ID']), user['House'], user['Advisor'], location, transport, gone_for_day, "Absent"])
        # print(student_data)
        pd.concat([self.off_campus_entry, student_data])

        confirm_msg = f"{user['Preferred Name']} is going to {location}"
        if gone_for_day:
            confirm_msg += " for the rest of the day"
        success_confirm(confirm_msg)
        window.destroy()

    def log_faculty_sign_out(self, user, gone_for_day, window) :
        date, clock = get_date_and_clock()
        
        confirm_msg = f"{user['Preferred Name']} is signing out"

        if gone_for_day:
            time_back = "Gone For Day"
            confirm_msg += " for the rest of the day"
        else:
            time_back = ""

        faculty_data = pd.Series([date, clock, user['Full Name'], int(user['Person ID']), time_back, "Absent"])
        pd.concat([self.fac_off_campus_entry, faculty_data])
        
        
        success_confirm(confirm_msg)
        window.destroy()
        

    def retrieve_google_sheets(self):
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


        # Save local copy of records and way to update
        records = gc.open_by_url("https://docs.google.com/spreadsheets/d/1tWKMoprqwx6J9sQpf4Cd-NvbMtUd5p3_sYhiPz17pZQ")
        self.lateness = records.worksheet("Lateness")
        self.lateness_entry = pd.DataFrame(self.lateness.get_all_records())
        self.off_campus = records.worksheet("Off Campus")
        self.off_campus_entry = pd.DataFrame(self.off_campus.get_all_records())
        self.fac_off_campus = records.worksheet("Faculty Off Campus")
        self.fac_off_campus_entry = pd.DataFrame(self.fac_off_campus.get_all_records())