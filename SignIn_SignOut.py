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
from time import sleep
import pygame
pygame.mixer.init()

data_handler = data_handler()
rt = RepeatedTimer(30, data_handler.sync_sheets)

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
                    ('Being Driven / Driving Off Campus', 'Driving'))

        # buttons
        button_grid = [None] * len(locations)
        for i, place in enumerate(locations):
            if place[1] != "Walking" and place[1] != "Driving":
                photo = PhotoImage(file = f"logos/{place[1]}.png")
                button_grid[i] = Button(window, text = place[0], image = photo, width=200, height=200, command=lambda place=place:LogSignOut(place[0] , self.user, "Walk", window))
                button_grid[i].image = photo
                button_grid[i].grid(row=i//3+1, column=(i%3)*2, pady = 10, columnspan=2)
            elif place[1] == "Walking":
                photo = PhotoImage(file = f"logos/{place[1]}.png")
                button_grid[i] = Button(window, text = place[0], image = photo, width=200, height=200, command=lambda place=place:CustomLocation(self.user, window, place[1]))
                button_grid[i].image = photo
                button_grid[i].grid(row=i//3+1, column=(i%3)*2, pady = 10, columnspan=2)
            else:
                r = Button(window, text=place[0], font=('Arial 24'), command=lambda place=place:CustomLocation(self.user, window, place[1]))
                r.grid(row=4, column = 0, columnspan= 6, padx = 10)

class CustomLocation(Tk):
    def __init__(self, user, window, transport):
        if transport == "Driving" and not data_handler.does_user_have_driving_note(user):
            return
        title = 'Enter your destination'
        text = 'Please enter where you are going:'
        keybd = Keyboard(window, title, text)
        window.wait_window(keybd.keyboard)
        window.destroy()
        location = keybd.entry
        if location != "":
            LogSignOut(location, user, transport, window)
        else:
            print("Operation Canceled")
        
        

def LogSignOut(location, user, transport, window):
    # Student users who are walking are not allowed to leave for the day
    if transport == "Walk" and user["Type"] == "Student":
        data_handler.log_student_sign_out(location, user, transport, False, window)
        window.destroy()
    else:
        # Check if the user is leaving for the day or not
        gone_for_day_check = Toplevel()
        gone_for_day_check.geometry("800x180+450+450")
        buttonframe = Frame(gone_for_day_check)
        buttonframe.grid(row=2, column=0, columnspan=2)      
        Label(gone_for_day_check, text=f"Are you leaving for the rest of the day, {user['Preferred Name']}?", font=('Helvetica 25 bold'), wraplength=800, justify=CENTER).grid(row=0, column=0, padx=20, pady = 20)
    
    
        if user["Type"] == "Student":
            Button(buttonframe, text ="Yes", font ='Helvetica 30 bold', command=lambda:data_handler.log_student_sign_out(location, user, transport, True, gone_for_day_check)).grid(row= 1, column=0, padx= 10)
            # Button(buttonframe, text = "No", font ='Helvetica 30 bold', command=lambda:data_handler.log_student_sign_out(location, user, transport, False, gone_for_day_check)).grid(row= 1, column=2, padx= 10)
            Button(buttonframe, text = "No", font ='Helvetica 30 bold', command=lambda:get_eta(user, transport, gone_for_day_check, location)).grid(row= 1, column=2, padx= 10)
            # Close Window
            window.destroy()

        else:
            Button(buttonframe, text ="Yes", font ='Helvetica 30 bold', command=lambda:data_handler.log_faculty_sign_out(user, True, gone_for_day_check)).grid(row= 1, column=0, padx= 10)
            Button(buttonframe, text = "No", font ='Helvetica 30 bold', command=lambda:get_eta(user, False, gone_for_day_check)).grid(row= 1, column=2, padx= 10)

def get_eta(user, transport, window, location=None):
    
    test = ReturnSelector()
    window.wait_window(test.screen)
    if test.time != "":
        if user["Type"] == "Student":
            data_handler.log_student_sign_out(location, user, transport, False, window, test.time)        
        else:
            data_handler.log_faculty_sign_out(user, False, window, test.time)
        window.destroy()
    else:
        print("Canceled")
        

#Admin functions exit program
def Admin(root):
    keybd = Keyboard(root, "Please Enter the Password", "Password", obscured=True)

    root.wait_window(keybd.keyboard)
    if keybd.entry == "patriot":
        rt.stop()
        root.destroy()
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
        textFrame(self.screen, text="Please scan your key card.", font_size=60, color = "black", relx=0.45, rely=0.80, relwidth= 0.75, relheight=0.10)
        textFrame(self.screen, text="An Advanced Topics in CS Project created by Sam Wang under the guidance of Mr. Oswald, Ms. Kennedy, and Mr. DiFranco", font_size=18, color = "blue", relx=0.5, rely=0.95, relwidth=0.88, relheight=0.04)

        # # Create buttons
        buttonFrame(self.screen, text="Admin", command=lambda:Admin(self.screen), font_size=36, relx=0.85, rely=0.80, relwidth=0.15, relheight=0.09)    
        buttonFrame(self.screen, text="Sync", command=lambda:data_handler.sync_sheets(), font_size=36, relx=0.85, rely=0.90, relwidth=0.15, relheight=0.09)    
        # Set up barcode reading
        self.code = ''
        self.screen.bind('<Key>', self.get_key)

    def get_key(self, event):
        if event.char in '0123456789':
            self.code += event.char
        elif event.keysym == 'Return':
            scan_id = int(self.code[-6:])
            print(scan_id)
            if is_root_window_in_front(self.screen):
                close_children_windows(self.screen)
            if get_top_level_windows(self.screen) == 0:
                process_barcode(scan_id) 

class OperationSelector(Tk):
    def __init__(self, user):
        self.screen = Toplevel()
        self.screen.geometry('800x200+500+400')
        
        self.screen.title('Select an Operation')
        self.screen.resizable(False, False)
        self.screen.protocol("WM_DELETE_WINDOW", disable_event)
        self.user = user
        textFrame(self.screen, text="Select an Operation", font_size=22, color = "black", relx=0.5, rely=0.2, relwidth=0.88, relheight=0.2)
        buttonFrame(self.screen, text="Lateness", command=lambda:self.dispatch_operation("Lateness"), font_size=36, relx=0.25, rely=0.80, relwidth=0.30, relheight=0.50)    
        buttonFrame(self.screen, text="Off Campus", command=lambda:self.dispatch_operation("Off Campus"), font_size=36, relx=0.75, rely=0.80, relwidth=0.37, relheight=0.50)    

    def dispatch_operation(self, operation):
        if operation == "Lateness":
            Lateness(self.user, self.screen)
        elif operation == "Off Campus":
            self.screen.destroy()
            # Check to make sure that the operation is allowed
            if data_handler.operation_allowed(self.user):
                LocationChoiceWindow(self.user)

class ReturnSelector(Tk):
    def __init__(self):
        self.screen = Toplevel()
        self.screen.title('Select an estimated return time')
        self.screen.resizable(False, False)
        self.screen.protocol("WM_DELETE_WINDOW", disable_event)
        colon = Label(self.screen, text="What will your estimated time of return be?")
        colon.config(font=(f'Helvetica {30} bold'), fg="black", wraplength=500)
        colon.pack()

        self.hour_options = [hour for hour in range(8, 15)]
        self.minute_options = [x * 5 for x in range(0, 12)]
        self.hour_selector = create_selector(self.screen, self.hour_options, 50, LEFT)
        self.minute_selector = create_selector(self.screen, self.minute_options, 30, RIGHT)

        colon = Label(self.screen, text=":")
        colon.config(font=(f'Helvetica {200} bold'), fg="black")
        colon.pack()
        btn1 = Button(self.screen, text = "Set time", font = f'Helvetica {14} bold', command=self.get_selected_times)
        btn1.pack()
        self.error = Label(self.screen, text="Please select both an hour and minute value for your time.", wraplength=350)
        self.error.config(font=(f'Helvetica {20} bold'), fg="red")
        colon.focus_set()
        self.time = None

    def get_selected_times(self):
        hour_select = self.hour_selector.curselection()
        minute_select = self.minute_selector.curselection()
        if len(hour_select) != 1 or len(minute_select) != 1:
            self.error.pack()
            self.time = None
        else:
            self.error.pack_forget()
            self.time = f"{self.hour_options[hour_select[0]]}:{self.minute_options[minute_select[0]]}"
            self.screen.destroy()
            


def Lateness(user, window):
    keybd = Keyboard(window, "Reason for Lateness", "Please enter your reason for lateness")
    window.wait_window(keybd.keyboard)
    if keybd.entry != "":
        print(f"{user['Preferred Name']} is late because {keybd.entry}")
        data_handler.log_student_lateness(user, keybd.entry)
        window.destroy()
    else:
        print("Operation Canceled")
    

def return_to_campus(user):
    return_to_campus_check = Toplevel()
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
            # error_pop("This program is currently in a Faculty-only Beta, but will be available for student use soon.")
            selector = OperationSelector(user)
        elif user_type == "Faculty":
            LogSignOut(None, user, "Driving", None)

def main():
    root = MainScreen()
    title_image = renderImage("GA.png", 1600, 600)
    imageFrame(root.screen, title_image, 0.5, 0.05, 0.8, 0.5)
    root.screen.mainloop()
    

if __name__ == "__main__":
    main()
    
