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
from keyboard import Keyboard
from utils import *
from data import data_handler
import pygame
pygame.mixer.init()

data_handler = data_handler()
        
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
        button_grid = [None] * len(locations)
        for i, place in enumerate(locations):
            if place[1] != "Walking" and place[1] != "Driving":
                photo = PhotoImage(file = f"logos/{place[1]}.png")
                button_grid[i] = Button(window, text = place[0], image = photo, width=200, height=200, command=lambda place=place:LogSignOut(place[0] , self.user, "Walk", window))
                button_grid[i].image = photo
                button_grid[i].grid(row=i//3+1, column=(i%3)*2, pady = 10, columnspan=2)
            else:
                r = Button(window, text=place[0], font=('Arial 24'), command=lambda:CustomLocation(self.user, window, place[1]))
                r.grid(row=4, column = i%2*3, columnspan=3, padx = 10)

class CustomLocation(Tk):
    def __init__(self, user, window, transport):
        title = 'Enter your destination'
        text = 'Please enter where you are going:'
        wait = Toplevel()
        keybd = Keyboard(wait, title, text)
        wait.iconify()
        wait.wait_window(keybd.keyboard)
        location = keybd.entry
        LogSignOut(location, user, transport, window)
        wait.destroy()

def LogSignOut(location, user, transport, window):
    # Student users who are walking are not allowed to leave for the day
    if transport == "Walk" and user["Type"] == "Student":
        data_handler.log_student_sign_out(location, user, transport, False, window)
        window.destroy()
    else:
        # Check if the user is leaving for the day or not
        gone_for_day_check = Toplevel()
        gone_for_day_check.grab_set()
        gone_for_day_check.geometry("800x180+450+450")
        buttonframe = Frame(gone_for_day_check)
        buttonframe.grid(row=2, column=0, columnspan=2)      
        Label(gone_for_day_check, text=f"Are you leaving for the rest of the day, {user['Preferred Name']}?", font=('Helvetica 25 bold'), wraplength=800, justify=CENTER).grid(row=0, column=0, padx=20, pady = 20)
    
    
        if user["Type"] == "Student":
            Button(buttonframe, text ="Yes", font ='Helvetica 30 bold', command=lambda:data_handler.log_student_sign_out(location, user, transport, True, gone_for_day_check)).grid(row= 1, column=0, padx= 10)
            Button(buttonframe, text = "No", font ='Helvetica 30 bold', command=lambda:data_handler.log_student_sign_out(location, user, transport, False, gone_for_day_check)).grid(row= 1, column=2, padx= 10)
            data_handler.log_student_sign_out(location, user, transport, gone_for_day_check)
            # Close Window
            window.destroy()

        else:
            Button(buttonframe, text ="Yes", font ='Helvetica 30 bold', command=lambda:data_handler.log_faculty_sign_out(user, True, gone_for_day_check)).grid(row= 1, column=0, padx= 10)
            Button(buttonframe, text = "No", font ='Helvetica 30 bold', command=lambda:data_handler.log_faculty_sign_out(user, False, gone_for_day_check)).grid(row= 1, column=2, padx= 10)



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
            if get_top_level_windows(self.screen) == 0:
                process_barcode(scan_id) 

class OperationSelector(Tk):
    def __init__(self, user):
        self.screen = Toplevel()
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
            # Check to make sure that the operation is allowed
            if data_handler.operation_allowed(self.user):
                LocationChoiceWindow(self.user)


def Lateness(user):
    root = Toplevel()
    keybd = Keyboard(root, "Reason for Lateness", "Please enter your reason for lateness")
    root.iconify()
    root.wait_window(keybd.keyboard)
    if keybd.entry != "":
        print(f"{user['First Name']} is late because {keybd.entry}")
    else:
        print("Operation Canceled")
    root.destroy()

def return_to_campus(user):
    return_to_campus_check = Toplevel()
    return_to_campus_check.grab_set()
    return_to_campus_check.geometry("600x200+450+450")
    buttonframe = Frame(return_to_campus_check)
    buttonframe.grid(row=2, column=0, columnspan=2)      
    Label(return_to_campus_check, text=f"Are you signing back in, {user['Preferred Name']}?", font=('Helvetica 25 bold'), wraplength=600, justify=CENTER).grid(row=0, column=0, padx=20, pady = 20)
    Button(buttonframe, text ="Yes", font ='Helvetica 30 bold', command=lambda:data_handler.return_to_campus(user, return_to_campus_check)).grid(row= 1, column=0, padx= 10)
    Button(buttonframe, text = "No", font ='Helvetica 30 bold', command=lambda:return_to_campus_check.destroy()).grid(row= 1, column=2, padx= 10)



def process_barcode(scan_id):
    
    user_type = data_handler.user_type_from_barcode(scan_id)
    if user_type:
        user = data_handler.get_user_from_barcode(scan_id, user_type)
        user["type"] = user_type
    if data_handler.is_user_currently_signed_out(scan_id, user_type):
        return_to_campus(user)
    else:        
        if user_type == "Student":
            selector = OperationSelector(user)
            selector.screen.grab_set()
        elif user_type == "Faculty":
            LogSignOut(None, user, "Driving", None)

def main():
    root = MainScreen()
    title_image = renderImage("GA.png", 1600, 600)
    imageFrame(root.screen, title_image, 0.5, 0.05, 0.8, 0.5)
    root.screen.mainloop()

if __name__ == "__main__":
    main()