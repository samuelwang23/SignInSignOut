# Later TODO Clean up Imports

from tkinter import ttk

import os
import time
import pandas as pd
from tkinter.messagebox import askyesno
import random
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from pytz import timezone

from keyboard import Keyboard
from utils import *

import pygame
pygame.mixer.init()


tz = timezone('EST')

# Later TODO Make this into a model class that handles the Google SpreadSheet side of things
gc = gspread.service_account(filename='myCredentials.json')


IDList = gc.open_by_url("https://docs.google.com/spreadsheets/d/1xgwMCl0X7d-AuKxmPgsLiRuQJ7eDUxKQyKmpTC7YvKk/")
students = IDList.worksheet("Student")
student_users = pd.DataFrame(students.get_all_records()) 
student_users["Type"] = "Student"
student_ids = student_users["Person ID"].values

faculty = IDList.worksheet("Faculty")
faculty_users = pd.DataFrame(faculty.get_all_records()) 
faculty_users["Type"] = "Faculty"
faculty_ids = faculty_users["Person ID"].values

records = gc.open_by_url("https://docs.google.com/spreadsheets/d/1tWKMoprqwx6J9sQpf4Cd-NvbMtUd5p3_sYhiPz17pZQ")
lateness = records.worksheet("Lateness")
lateness_entry = pd.DataFrame(lateness.get_all_records())
off_campus = records.worksheet("Off Campus")
off_campus_entry = pd.DataFrame(off_campus.get_all_records())
fac_off_campus = records.worksheet("Faculty Off Campus")
fac_off_campus_entry = pd.DataFrame(fac_off_campus.get_all_records())


# TODO DATA: make update Records happen more effectively 
# records = gc.open_by_url("https://docs.google.com/spreadsheets/d/1tWKMoprqwx6J9sQpf4Cd-NvbMtUd5p3_sYhiPz17pZQ")
# lateness = records.worksheet("Lateness")
# lateness_entry = pd.DataFrame(lateness.get_all_records())
# off_campus = records.worksheet("Off Campus")
# off_campus_entry = pd.DataFrame(off_campus.get_all_records())
# fac_off_campus = records.worksheet("Faculty Off Campus")
# fac_off_campus_entry = pd.DataFrame(fac_off_campus.get_all_records())
# # print(fac_off_campus_entry)


def LogSignIn(reason, args):
    user = args["user"]
    date, clock = get_date_and_clock()
    student_data = [date, clock, user['Preferred Name'], user['Last Name'], user['Current Grade'], int(user['Person ID']), user['House'], user['Advisor'], reason]
    lateness.append_row(student_data)


class Reason(Tk):
    def __init__(self, user):

        title = 'Enter your reason for lateness'
        text = 'Please enter your reason for lateness'
        wait = Tk()
        keybd = Keyboard(wait, title, text)
        # TODO DATA: Add to GSpread Queue
        wait.iconify()
        wait.wait_window(keybd.keyboard)
        print(keybd.entry)
        wait.destroy()
        
# TODO NEW GUI: Make this accept a custom list of locations
class LocationChoiceWindow(Tk):
    def __init__(self, user):
        window = Toplevel()
        self.user = user
        window.geometry('755x630+300+300')
        window.resizable(False, False)
        window.title('Location')
        name = user['Preferred Name'] + " " + user['Last Name']
        label = Label(window, text=f"Please select a location, {name}", font=('Helvetica 24 bold'),  justify=CENTER)
        label.grid(row = 0, column = 0, columnspan = 6, pady= 10, padx =3)


        self.selected_place = StringVar(window, value='Others')
        locations = (('Wawa', 'Wawa'),
                    ('Rich\'s Deli', 'Rich\'s'),
                    ('Cantina Feliz', 'Cantina'),
                    ('Little Italy', 'Little Italy'),
                    ('Zakes Cafe', 'Zakes Cafe'),
                    ('Walking Somewhere else', 'Walking'),
                    ('Driving Off Campus', 'Driving'))

        # buttons
        for i, place in enumerate(locations):
            if place[1] != "Walking" and place[1] != "Driving":
                photo = PhotoImage(file = f"logos/{place[1]}.png")
                r = Button(window, text = place[0], image = photo, width=200, height=200, command=lambda:LogSignOut(place[1], self.user, "Walk", window))
                r.image = photo
                r.grid(row=i//3+1, column=(i%3)*2, pady = 10, columnspan=2)
            else:
                r = Button(window, text=place[0], font=('Arial 24'), command=lambda:CustomLocation(self.user, window, place[1]))
                r.grid(row=4, column = i%2*3, columnspan=3, padx = 10)

class CustomLocation(Tk):
    def __init__(self, user, window, transport):
        title = 'Enter your destination'
        text = 'Please enter where you are going:'
        wait = Tk()
        keybd = Keyboard(wait, title, text)
        # TODO DATA: Add to GSpread Queue
        wait.iconify()
        wait.wait_window(keybd.keyboard)
        print(keybd.entry)
        wait.destroy()

# TODO:Reconcile differences between Functions "LogSignOut" and "FacultyLogSignOut" 
def LogSignOut(location, user, transport, window):
    date, clock = get_date_and_clock()
    if user["Type"] == "Student":
        student_data = [date, clock, user['Preferred Name'], user['Last Name'], user['Current Grade'], int(user['Person ID']), user['House'], user['Advisor'], location, transport, "Absent"]
        # off_campus.append_row(student_data)
        off_campus_entry.append(student_data)
        # Close Window
        window.destroy()
    else:
        gone_for_day_check = Tk()
        gone_for_day_check.geometry("700x180+450+450")
        buttonframe = Frame(gone_for_day_check)
        buttonframe.grid(row=2, column=0, columnspan=2)        
        Label(gone_for_day_check, text="Are you leaving for the rest of the day?", font=('Helvetica 25 bold')).grid(row=0, column=0, padx=20, pady = 20)
        Button(buttonframe, text ="Yes", font ='Helvetica 30 bold', command=lambda:FacultySignOut(location, user, True, gone_for_day_check)).grid(row= 1, column=0, padx= 10)
        Button(buttonframe, text = "No", font ='Helvetica 30 bold', command=lambda:FacultySignOut(location, user, False, gone_for_day_check)).grid(row= 1, column=2, padx= 10)
        

def FacultySignOut(location, user, gone_for_day, window) :
    date, clock = get_date_and_clock()
    time_back = ""
    if gone_for_day:
        time_back = "Gone For Day"
    
    faculty_data = [date, clock, user['Full Name'], int(user['Person ID']), location, time_back, "Absent"]
    fac_off_campus.append_row(faculty_data)
    window.destroy()

    #Confirmation Window
    confirm_msg = f"{ clean_name(user['Full Name']) } is going to {location}"
    if gone_for_day:
        confirm_msg += " and is leaving for the day"
    success_confirm(confirm_msg, len(fac_off_campus.get_all_values()))

def create_confirm_box(text, type):
    message = Toplevel()
    message.geometry("500x400+700+300")
    label = Label(message, text=text, font=('Helvetica 20 bold'))
    label.pack()
    label.bind('<Configure>', lambda e: label.config(wraplength=label.winfo_width() + 10))
    image = ImageTk.PhotoImage(file = f'{type}.png')
    canvas = Canvas(message, width = 300, height = 200)
    canvas.pack(expand = YES, fill = BOTH)
    canvas.create_image(250, 170, image = image, anchor = CENTER)
    canvas.image = image
    return message

def success_confirm(confirm_text, row_id):
    confirmation = create_confirm_box(confirm_text, "complete")
    Button(confirmation, text = "Cancel", font ='Helvetica 17 bold', command=lambda:fac_off_campus.delete_rows(row_id)).pack()
    confirmation.overrideredirect(True)
    confirmation.after(2000,lambda:confirmation.destroy())

def error_pop(error_text, audio=True, length=3000):
    error_msg = create_confirm_box(error_text, "error")
    error_msg.overrideredirect(True)
    error_msg.after(length,lambda:error_msg.destroy())   
    if audio:
        speaker_volume = 0.5
        pygame.mixer.music.set_volume(speaker_volume)
        pygame.mixer.music.load('output1.mp3')
        pygame.mixer.music.play()
    

#Admin functions exit program
#TODO Later add a setting in Keyboard for "Password mode"
def Admin(root):
    keybd = Keyboard(root, "Please Enter the Password", "Password")

    #TODO DATA:Later Remove this password from the code itself somehow
    root.wait_window(keybd.keyboard)
    if keybd.entry == "patriot":
        root.quit()
    else:
        error_pop("Incorrect Password")    
        
#Disable X on the window
def disable_event():
    pass

class MainScreen(Tk):
    def __init__(self):
        self.screen = Tk()
        # Window Setup
        self.screen.title('Sign-In and Sign-Out')
        # Define the geometry of the function
        self.screen.geometry("1400x900")
        # Create a fullscreen window
        self.screen.attributes('-fullscreen', True)
        # Disable the Close Window Control Icon
        self.screen.protocol("WM_DELETE_WINDOW", disable_event)
        
        #Create Title Splash
        textFrame(self.screen, text="Germantown Academy Sign In Sign Out System", font_size=40, color = "black", relx=0.5, rely=0.68, relwidth= 1, relheight=0.1)
        textFrame(self.screen, text="Please scan your key card.", font_size=70, color = "black", relx=0.45, rely=0.80, relwidth= 0.75, relheight=0.10)
        textFrame(self.screen, text="An Advanced Topics in CS Project created by Sam Wang under the guidance of Mr. Oswald, Ms. Kennedy, and Mr. DiFranco", font_size=18, color = "blue", relx=0.5, rely=0.95, relwidth=0.88, relheight=0.04)

        # # Create buttons
        buttonFrame(self.screen, text="Admin", command=lambda:Admin(self.screen), font_size=36, relx=0.85, rely=0.80, relwidth=0.15, relheight=0.09)    

        # Set up barcode reading
        self.code = ''
        self.screen.bind('<Key>', self.get_key)
        self.state = "active"

    def get_key(self, event):
        if event.char in '0123456789' and self.state =="active":
            self.code += event.char
        elif event.keysym == 'Return' and self.state =="active":
            scan_id = int(self.code[-6:])
            print(scan_id)
            process_barcode(scan_id)


class OperationSelector(Tk):
    def __init__(self, user):
        self.screen = Tk()
        self.screen.geometry('800x200+500+400')
        self.screen.resizable(False, False)
        self.screen.title('Select an Operation')
        self.user = user
        textFrame(self.screen, text="Select an Operation", font_size=22, color = "black", relx=0.5, rely=0.2, relwidth=0.88, relheight=0.2)
        buttonFrame(self.screen, text="Lateness", command=lambda:self.dispatch_operation("Lateness"), font_size=36, relx=0.25, rely=0.80, relwidth=0.30, relheight=0.50)    
        buttonFrame(self.screen, text="Off Campus", command=lambda:self.dispatch_operation("Off Campus"), font_size=36, relx=0.75, rely=0.80, relwidth=0.37, relheight=0.50)    

    def dispatch_operation(self, operation):
        self.screen.destroy()
        if operation == "Lateness":
            Lateness(self.user)
        elif operation == "Off Campus":
            LocationChoiceWindow(self.user)

def Lateness(user):
    root = Tk()
    keybd = Keyboard(root, "Reason for Lateness", "Please enter your reason for lateness")
    root.iconify()
    root.wait_window(keybd.keyboard)
    if keybd.entry != "":
        print(f"{user['First Name']} is late because {keybd.entry}")
    else:
        print("Operation Canceled")



def process_barcode(scan_id):
    if scan_id in student_ids:
        # error_pop("This beta is currently faculty-only, but is coming soon for students!", False)
        user = student_users[student_users['Person ID'] == int(scan_id)].iloc[0]
        print("Student User")
        type = "Student"
    elif scan_id in faculty_ids:
        user = faculty_users[faculty_users['Person ID'] == int(scan_id)].iloc[0]
        print("Faculty User")
        type = "Faculty"
    else:
        raise Exception("User Not Found Error")
    user["type"] = type
    selector = OperationSelector(user)
    selector.screen.grab_set()

def main():
    root = MainScreen()
    title_image = renderImage("GA.png", 1600, 600)
    imageFrame(root.screen, title_image, 0.5, 0.05, 0.8, 0.5)
    root.screen.mainloop()

if __name__ == "__main__":
    main()