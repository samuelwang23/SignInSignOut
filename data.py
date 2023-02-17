import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from utils import *
import time
from pytz import timezone

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
    
    def log_student_sign_out(self, location, user, transport, window):
        date, clock = get_date_and_clock()
        student_data = pd.Series([date, clock, user['Preferred Name'], user['Last Name'], user['Current Grade'], int(user['Person ID']), user['House'], user['Advisor'], location, transport, "Absent"])
        pd.concat([self.off_campus_entry, student_data])

    def log_faculty_sign_out(self, location, user, gone_for_day, window) :
        date, clock = get_date_and_clock()
        if gone_for_day:
            time_back = "Gone For Day"
        else:
            time_back = ""

        faculty_data = [date, clock, user['Full Name'], int(user['Person ID']), location, time_back, "Absent"]
        self.fac_off_campus_entry.concat(faculty_data)
        window.destroy()

        #Confirmation Window
        confirm_msg = f"{ clean_name(user['Full Name']) } is going to {location}"
        if gone_for_day:
            confirm_msg += " and is leaving for the day"
        # This will be fixed as part of the confirm data leak fix
        # success_confirm(confirm_msg, len(fac_off_campus.get_all_values()))

    def retrieve_google_sheets(self):
        # TODO: May only need to save the final variable of student_ids/faculty_ids
        self.IDList = gc.open_by_url("https://docs.google.com/spreadsheets/d/1xgwMCl0X7d-AuKxmPgsLiRuQJ7eDUxKQyKmpTC7YvKk/")
        self.students = self.IDList.worksheet("Student")
        self.student_users = pd.DataFrame(self.students.get_all_records()) 
        self.student_users["Type"] = "Student"
        self.student_ids = self.student_users["Person ID"].values

        self.faculty = self.IDList.worksheet("Faculty")
        self.faculty_users = pd.DataFrame(self.faculty.get_all_records()) 
        self.faculty_users["Type"] = "Faculty"
        self.faculty_ids = self.faculty_users["Person ID"].values


        # Save local copy of records and way to update
        records = gc.open_by_url("https://docs.google.com/spreadsheets/d/1tWKMoprqwx6J9sQpf4Cd-NvbMtUd5p3_sYhiPz17pZQ")
        self.lateness = records.worksheet("Lateness")
        self.lateness_entry = pd.DataFrame(self.lateness.get_all_records())
        self.off_campus = records.worksheet("Off Campus")
        self.off_campus_entry = pd.DataFrame(self.off_campus.get_all_records())
        self.fac_off_campus = records.worksheet("Faculty Off Campus")
        self.fac_off_campus_entry = pd.DataFrame(self.fac_off_campus.get_all_records())