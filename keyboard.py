#Import the tkinter library
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
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

class MyKeyboard(Tk):

    def __init__(self, title, text, fn, args):
        self.keyboard = Tk()
        self.keyboard.title(title)
        self.text = text
        self.keyboard.config(bg='whitesmoke')
        self.keyboard.resizable(0, 0)
        self.entry =""
        self.fn = fn
        self.args = args

        self.buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o','p', 
                    'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'Backspace', 
                    'Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', 'Cancel','Enter', 'Space']
        self.ShiftButtons = ['~', '!', '@', '#', '&', '*', '(', ')', '_', '+', 
                            'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 
                            'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', "Backspace", 
                            'lowercase', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'Cancel', 'Enter', 'Space']

    def select(self, textarea, value):
        varRow = 2
        varColumn = 0
        for button in self.buttons:
            command = lambda x=button: self.select(textarea, x)
            if button != 'Space':
                Button(self.keyboard, text=button, command=command, font=('arial', 20, 'bold'), height=4, width=9,relief= RAISED).grid(row=varRow, column=varColumn)

                varColumn += 1
                if varColumn > 9:
                    varColumn = 0
                    varRow += 1

        if value == 'Space':
            textarea.insert(INSERT, ' ')

        elif value == 'Enter':
            i = textarea.get(1.0, END)
            self.entry = i[:-1]
            self.keyboard.destroy()
            self.fn(self.entry, self.args)
            return

        elif value == 'Cancel':
            textarea = ""
            self.entry = ""
            self.keyboard.destroy()
            return

        elif value == 'Backspace':
            i = textarea.get(1.0, END)
            newtext = i[:-2]
            textarea.delete(1.0, END)
            textarea.insert(INSERT, newtext)

        elif value == 'Shift':
            varRow = 2
            varColumn = 0
            for button in self.ShiftButtons:
                command = lambda x=button: self.select(textarea, x)
                if button != 'Space':
                    Button(self.keyboard, text=button, command=command, font=('arial', 20, 'bold'), height=4, width= 9,relief= RAISED ).grid(row=varRow, column=varColumn)

                    varColumn += 1
                    if varColumn > 9:
                        varColumn = 0
                        varRow += 1
        elif value == 'lowercase':            
            varRow = 2
            varColumn = 0
            for button in self.buttons:
                command = lambda x=button: self.select(textarea, x)
                if button != 'Space':
                    Button(self.keyboard, text=button, command=command, font=('arial', 20, 'bold'), height=4, width=9,relief= RAISED).grid(row=varRow, column=varColumn)

                    varColumn += 1
                    if varColumn > 9:
                        varColumn = 0
                        varRow += 1
        else:
            textarea.insert(INSERT, value)
        textarea.focus_set()

    def ky(self): 
        titleLabel = Label(self.keyboard, text= self.text, font=('arial', 24, 'bold'), bg='whitesmoke', fg='gray30')
        titleLabel.grid(row=0, columnspan=15)
        textarea =" "
        textarea = Text(self.keyboard, font=('arial', 28, 'bold'), height= 1, width= 60, wrap='word',bd=8, relief=SUNKEN)
        textarea.grid(row=1, columnspan=15)
        textarea.focus_set()

        
        varRow = 2
        varColumn = 0
        for button in self.buttons:
            
            
            command = lambda x=button: self.select(textarea, x)
            
            if button != 'Space':
                Button(self.keyboard, text=button, command=command,font=('arial', 20, 'bold'), height=4, width=9,relief= RAISED).grid(row=varRow, column=varColumn)
            if button == 'Space':
                Button(self.keyboard, text=button, command=command,font=('arial', 20, 'bold'), height=2, width=30,relief= RAISED).grid(row=6, column=0, columnspan=14)
            varColumn += 1
            if varColumn > 9:
                varColumn = 0
                varRow += 1
        