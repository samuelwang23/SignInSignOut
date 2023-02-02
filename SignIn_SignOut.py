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
import pygame



from utils import *


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

# pygame.mixer.init()

# TODO make update Records happen more effectively 
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
        # TODO Add to GSpread Queue
        wait.iconify()
        wait.wait_window(keybd.keyboard)
        print(keybd.entry)
        wait.destroy()
        


    

    
# TODO Later: Make this accept a custom list of locations
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
        wait = Tk()
        keybd = Keyboard(wait, title, text)
        # TODO Add to GSpread Queue
        wait.iconify()
        wait.wait_window(keybd.keyboard)
        print(keybd.entry)
        wait.destroy()
        
        
        

# TODO: Later Reconcile differences between Functions "LogSignOut" and "FacultyLogSignOut" 
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


# TODO Later Make this and Error Pop classes that inherit from each other, super().init
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
#TODO Later add a setting in Keyboard for "Password mode"
def Admin(root):
    keybd = Keyboard(root, "Please Enter the Password", "Password")

    #TODO Later Remove this password from the code itself somehow
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
        self.screen= Tk()
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

    def get_key(self, event):
        if event.char in '0123456789':
            self.code += event.char
        elif event.keysym == 'Return':
            scan_id = int(self.code[-6:])
            print(scan_id)


def main():
    root = MainScreen()
    title_image = renderImage("GA.png", 1600, 600)
    imageFrame(root.screen, title_image, 0.5, 0.05, 0.8, 0.5)
    root.screen.mainloop()

if __name__ == "__main__":
    main()