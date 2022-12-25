# TODO Clean up Imports

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
from datetime import datetime
from pytz import timezone
from keyboard import MyKeyboard
import pygame



from utils import *


tz = timezone('EST')

# # TODO Make this into a model class that handles the Google SpreadSheet side of things
# gc = gspread.service_account(filename='myCredentials.json')


# IDList = gc.open_by_url("https://docs.google.com/spreadsheets/d/1xgwMCl0X7d-AuKxmPgsLiRuQJ7eDUxKQyKmpTC7YvKk/")
# students = IDList.worksheet("Student")
# student_users = pd.DataFrame(students.get_all_records()) 
# student_users["Type"] = "Student"
# student_ids = student_users["Person ID"].values

# faculty = IDList.worksheet("Faculty")
# faculty_users = pd.DataFrame(faculty.get_all_records()) 
# faculty_users["Type"] = "Faculty"
# faculty_ids = faculty_users["Person ID"].values

# records = gc.open_by_url("https://docs.google.com/spreadsheets/d/1tWKMoprqwx6J9sQpf4Cd-NvbMtUd5p3_sYhiPz17pZQ")
# lateness = records.worksheet("Lateness")
# lateness_entry = pd.DataFrame(lateness.get_all_records())
# off_campus = records.worksheet("Off Campus")
# off_campus_entry = pd.DataFrame(off_campus.get_all_records())
# fac_off_campus = records.worksheet("Faculty Off Campus")
# fac_off_campus_entry = pd.DataFrame(fac_off_campus.get_all_records())

# pygame.mixer.init()



def LogSignIn(reason, args):
    user = args["user"]
    date, clock = get_date_and_clock()
    student_data = [date, clock, user['Preferred Name'], user['Last Name'], user['Current Grade'], int(user['Person ID']), user['House'], user['Advisor'], reason]
    lateness.append_row(student_data)


class Reason(Tk):
    def __init__(self, user):

        title = 'Enter your reason for lateness'
        text = 'Please enter your reason for lateness'
        args = {"user": user}
        keybd = MyKeyboard(title, text, LogSignIn, args)
        keybd.ky()
        

#TODO Refactor this class completely
class BarcodeWindow(Tk):

    def __init__(self, purpose):
        Tk.__init__(self)
        title = purpose
        self.title(title)
        self.purpose = purpose
       #print("Purpose is: ", self.purpose)
        # self.geometry('1200x130')
        self.geometry(f'+300+500')

        self.code = ''

        self.label = Label(self, text="Please use the barcode scanner to scan your badge.", font=('Helvetica 28 bold'))
        self.label.pack(pady= 10, padx =3)

        self.bind('<Key>', self.get_key)
        bttn = Button(self, text ="Cancel",font=('Helvetica 20'), command=self.destroy)
        bttn.pack(pady= 10, padx =3)



    def get_key(self, event):

        if event.char in '0123456789':
            self.code += event.char
            #print('>', self.code)
            #self.label['text'] = self.code

        elif event.keysym == 'Return':
            
            try:
                scan_id = int(self.code[-6:])
                # Desktop Test - not using barcode

                # scan_id = 213660
                # scan_id = 196097
                # scan_id = 69
                print("Scanned in:", scan_id)
                self.withdraw()

                # Update Records
                records = gc.open_by_url("https://docs.google.com/spreadsheets/d/1tWKMoprqwx6J9sQpf4Cd-NvbMtUd5p3_sYhiPz17pZQ")
                lateness = records.worksheet("Lateness")
                lateness_entry = pd.DataFrame(lateness.get_all_records())
                off_campus = records.worksheet("Off Campus")
                off_campus_entry = pd.DataFrame(off_campus.get_all_records())
                fac_off_campus = records.worksheet("Faculty Off Campus")
                fac_off_campus_entry = pd.DataFrame(fac_off_campus.get_all_records())
                print(fac_off_campus_entry)
                if scan_id in student_ids:
                    error_pop("This beta is currently faculty-only, but is coming soon for students!", False)
                    user = student_users[student_users['Person ID'] == int(scan_id)].iloc[0]
                    print("Student User")
                elif scan_id in faculty_ids:
                    user = faculty_users[faculty_users['Person ID'] == int(scan_id)].iloc[0]
                    print(user)
                    print("Faculty User")
                else:
                    raise Exception("User Not Found Error")
                    
#                 if askyesno('Name', "Are you "  + name + "?", font = ('Helvetica 14 bold')):
                
                
                if self.purpose == "Sign In":
                    pass
                    # reas = Reason(user)
                # elif self.purpose == "Sign Out" and user["Type"] == "Student":   
                #     loc = LocationChoiceWindow(user)
                    
                elif user["Type"] == "Faculty":
                    # Check if there is an outstanding record
                    date, clock = get_date_and_clock()
                    print(fac_off_campus_entry.columns)
                    all_outstanding_records = fac_off_campus_entry[(fac_off_campus_entry["Time Back"] == "") & (fac_off_campus_entry["Date"] == date)]
                    IDs = pd.DataFrame([])
                    if len(all_outstanding_records) > 0:
                        IDs = all_outstanding_records["ID"]
                    outstanding_records = IDs[IDs.isin([scan_id])]
                    if len(outstanding_records) > 0:
                        row_index = outstanding_records.index[-1] + 2
                        update_row = fac_off_campus.row_values(row_index)

                        sign_in_check = Toplevel()
                        sign_in_check.geometry("700x200+450+450")
                        buttonframe = Frame(sign_in_check)
                        buttonframe.grid(row=2, column=0, columnspan=2)        
                        label = Label(sign_in_check, text=f"{clean_name(update_row[2])}, are you signing in from your trip to {update_row[4]}?", font=('Helvetica 20 bold'))
                        
                        label.bind('<Configure>', lambda e: label.config(wraplength=650))

                        label.grid(row=0, column=0, padx=50, pady = 20)
                        
                        Button(buttonframe, text ="Yes", font ='Helvetica 30 bold', command=lambda:OffCampusReturn(row_index, clock, sign_in_check)).grid(row= 1, column=0, padx= 10)
                        Button(buttonframe, text = "No", font ='Helvetica 30 bold', command=lambda:sign_in_check.destroy()).grid(row= 1, column=2, padx= 10)


                    else:
                        # args = {"user": user, "transport": "Walk"}
                        # LogSignOut("home", args) 
                        CustomLocation(user, "", "Drive")
                        
                    # if scan_id in fac_off_campus[fac_off_campus["Time Back"] == ""]["ID"].values:
                    #     if 
                   
                #else:
                    #self.code = ""
                    #self.deiconify()

            except Exception as e:
                print(e)
                error_pop("Invalid ID: Please try rescanning your ID")
                print("Invalid ID")

    
# TODO Make this part of a Model class
def OffCampusReturn(row_index, clock, window):
    fac_off_campus.update_cell(row_index, 6, clock)
    fac_off_campus.update_cell(row_index, 7, "Present")
    window.destroy()
    
# TODO later: Make this accept a custom list of locations
class LocationChoiceWindow(Tk):
    def __init__(self, user):
        window = Tk()
        self.user = user
        window.geometry('800x560+300+300')
        window.resizable(False, False)
        window.title('Location')
        name = user['Preferred Name'] + " " + user['Last Name']
        label = Label(window, text=f"Please select a location, {name}", font=('Helvetica 24 bold'))
        label.pack(pady= 10, padx =3)


        self.selected_place = StringVar(window, value='Others')
        locations = (('Rich\'s Deli', 'Rich\'s'),
                    ('Cantina Feliz', 'Cantina'),
                    ('Little Italy', 'Little Italy'),
                    ('Wawa', 'Wawa'),
                    ('Zakes Cafe', 'Zakes Cafe'),
                    ('Walking Off Campus', 'Walking'),
                    ('Driving Off Campus', 'Driving'))


        # buttons
        for place in locations:
            r = Radiobutton(
                window, font=('Arial 24'),
                text=place[0],
                value=place[1],
                variable=self.selected_place,
                tristatevalue=0
            )
            r.pack(anchor = W, padx=5, pady=5)
            #r.deselect()

        # button
        button = Button(
            window,
            text="Get Selected Place",font=('Arial 24'),
            command=lambda:self.show_selected_place(window))

        button.pack(pady= 10)#fill='x', padx=5, pady=5)
    def show_selected_place(self, window):
        place = self.selected_place.get()
        if place == "Driving":
            print("Check to see if there is permission to drive")
            loc = CustomLocation(self.user, window, "Drive")
        elif place == "Walking":
            print("Custom Walking")
            loc = CustomLocation(self.user, window, "Walk")
            
        else:
            args = {"user": self.user, "window": window, "transport": "Walk"}
            LogSignOut(place, args)

class CustomLocation(Tk):
    def __init__(self, user, window, transport):
        title = 'Enter your destination'
        text = 'Please enter where you are going:'
        args = {"user": user, "transport": transport, "window": window}
        keybd = MyKeyboard(title, text, LogSignOut, args)
        keybd.ky()

# TODO: Understand differences between Functions "LogSignOut" and "FacultyLogSignOut" 
def LogSignOut(location, args):
    user = args["user"]
    date, clock = get_date_and_clock()
    if user["Type"] == "Student":
        transport = args["transport"]
        student_data = [date, clock, user['Preferred Name'], user['Last Name'], user['Current Grade'], int(user['Person ID']), user['House'], user['Advisor'], location, transport, "Absent"]
        off_campus.append_row(student_data)
        #Close Window
        window = args["window"]
        window.destroy()
    else:
        gone_for_day_check = Tk()
        gone_for_day_check.geometry("700x180+450+450")
        buttonframe = Frame(gone_for_day_check)
        buttonframe.grid(row=2, column=0, columnspan=2)        
        Label(gone_for_day_check, text="Are you leaving for the rest of the day?", font=('Helvetica 25 bold')).grid(row=0, column=0, padx=20, pady = 20)
        Button(buttonframe, text ="Yes", font ='Helvetica 30 bold', command=lambda:FacultySignOut(location, args, True, gone_for_day_check)).grid(row= 1, column=0, padx= 10)
        Button(buttonframe, text = "No", font ='Helvetica 30 bold', command=lambda:FacultySignOut(location, args, False, gone_for_day_check)).grid(row= 1, column=2, padx= 10)
        

def FacultySignOut(location, args, gone_for_day, window) :
    user = args["user"]
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


# TODO Make this and Error Pop classes that inherit from each other, super().init
def success_confirm(confirm_text, row_id):
    confirmation = Toplevel()
    confirmation.geometry("500x400+700+300")
    label = Label(confirmation, text=confirm_text, font=('Helvetica 20 bold'))
    label.pack()
    label.bind('<Configure>', lambda e: label.config(wraplength=label.winfo_width() + 10))

    canvas = Canvas(confirmation, width = 300, height = 200)
    canvas.pack(expand = YES, fill = BOTH)
    complete = ImageTk.PhotoImage(file = 'complete.png')
    canvas.create_image(250, 170, image = complete, anchor = CENTER)
    canvas.complete = complete
    Button(confirmation, text = "Cancel", font ='Helvetica 17 bold', command=lambda:fac_off_campus.delete_rows(row_id)).pack()
    confirmation.overrideredirect(True)
    confirmation.after(2000,lambda:confirmation.destroy())

def error_pop(error_text, audio=True, length=3000):

    message = Toplevel()
    message.geometry("500x350+700+500")
    label = Label(message, text=error_text, font=('Helvetica 20 bold'))
    label.pack()
    label.bind('<Configure>', lambda e: label.config(wraplength=label.winfo_width() + 5))

    canvas = Canvas(message, width = 300, height = 200)
    canvas.pack(expand = YES, fill = BOTH)
    error = ImageTk.PhotoImage(file = 'error.png')
    canvas.create_image(250, 170, image = error, anchor = CENTER)
    canvas.error = error
    message.overrideredirect(True)
    message.after(length,lambda:message.destroy())   
    if audio:
        speaker_volume = 0.5
        pygame.mixer.music.set_volume(speaker_volume)
        pygame.mixer.music.load('output1.mp3')
        pygame.mixer.music.play()
    


#Define SignIn funcation
def SignIn():
    error_pop("Lateness Sign In is only for students", False, 1000)
#    op = BarcodeWindow("Sign In") 

#Define SignOut funcation
def SignOut():
    op = BarcodeWindow("Sign Out")

#Admin functions exit program
#TODO add a setting in MyKeyboard for "Password mode"
def Admin(root):
    keybd = MyKeyboard("Please Enter the Password", "Password", CloseMain, root)
    keybd.ky()

#TODO Remove this password from the code itself somehow
def CloseMain(password, root):
    if password == "patriot":
        root.quit()
    else:
        error_pop("Incorrect Password")
        






#Disable X on the window
def disable_event():
    pass

def main():

    root= Tk()
    # Window Setup
    root.title('Sign-In and Sign-Out')
    # Define the geometry of the function
    root.geometry("1400x900")
    # Create a fullscreen window
    root.attributes('-fullscreen', True)
    #Disable the Close Window Control Icon
    root.protocol("WM_DELETE_WINDOW", disable_event)
    
    #Create Title Splash
    title_image = renderImage("GA.png", 1600, 600)
    imageFrame(root, title_image, 0.5, 0.05, 0.8, 0.5)
    textFrame(root, text="Germantown Academy Sign In Sign Out System", font_size=40, color = "black", relx=0.5, rely=0.68, relwidth= 1, relheight=0.1)
    textFrame(root, text="Please click on a button to sign-in or sign-out", font_size=25, color = "black", relx=0.4, rely=0.75, relwidth= 0.75, relheight=0.05)
    textFrame(root, text="An Advanced Topics in CS Project created by Sam Wang under the guidance of Mr. Oswald, Ms. Kennedy, and Mr. DiFranco", font_size=18, color = "blue", relx=0.5, rely=0.95, relwidth=0.88, relheight=0.04)


    # Create buttons
    buttonFrame(root, text="Lateness", command=SignIn, font_size=36, relx=0.2, rely=0.86, relwidth=0.25, relheight=0.09)
    buttonFrame(root, text="Off Campus", command=SignOut, font_size=36, relx=0.52, rely=0.86, relwidth=0.25, relheight=0.09)
    buttonFrame(root, text="Admin", command=Admin(root), font_size=36, relx=0.85, rely=0.86, relwidth=0.15, relheight=0.09)    

    root.mainloop()

if __name__ == "__main__":
    main()