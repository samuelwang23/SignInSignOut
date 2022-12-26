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
        self.entry = ""
        self.fn = fn
        self.args = args
        self.buttons = []
        self.upper = False
        self.keys = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                    'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o','p', 
                    'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'Backspace', 
                    'Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', 'Cancel','Enter', 'Space'],
                    ['~', '!', '@', '#', '&', '*', '(', ')', '_', '+', 
                    'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 
                    'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', "Backspace", 
                    'Lowercase', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'Cancel', 'Enter', 'Space']]
        
        self.createKeyboardGUI()

    def createKeyboardGUI(self):
        self.keyboard.config(bg='whitesmoke')
        self.keyboard.resizable(0, 0)
        titleLabel = Label(self.keyboard, text=self.text, font=('arial', 24, 'bold'), bg='whitesmoke', fg='gray30')
        titleLabel.grid(row=0, columnspan=15)
        self.textarea = " "
        self.textarea = Text(self.keyboard, font=('arial', 28, 'bold'), height= 1, width= 60, wrap='word',bd=8, relief=SUNKEN)
        self.textarea.grid(row=1, columnspan=15)
        self.textarea.focus_set() 
        self.createKeyboardButtons()

    def createKeyboardButtons(self):
        for i, button in enumerate(self.keys[0]):
            command = lambda x = button: self.key_pressed(x)
            varColumn = i % 10
            varRow = int(i / 10) + 2
            if button != 'Space':
                key = Button(self.keyboard, text=button, command=command,font=('arial', 20, 'bold'), height=4, width=9,relief= RAISED)
                key.grid(row=varRow, column=varColumn)
                self.buttons.append(key)
                
            else:
                key = Button(self.keyboard, text=button, command=command,font=('arial', 20, 'bold'), height=2, width=30,relief= RAISED)
                key.grid(row=6, column=0, columnspan=14)
                self.buttons.append(key)
    
    def shiftKeys(self):
        self.upper = not self.upper
        keys_index = self.upper if 1 else 0
        for i, button in enumerate(self.buttons):
            button["text"] = self.keys[keys_index][i]
            command = lambda x = button["text"]: self.key_pressed(x)
            button.configure(command=command)
            button.value = self.keys[keys_index][i]

    def key_pressed(self, value):       
        if value == 'Space':
            self.textarea.insert(INSERT, ' ')

        # TODO Don't have keyboard handle any function calling
        elif value == 'Enter':
            i = self.textarea.get(1.0, END)
            self.entry = i[:-1]
            self.keyboard.destroy()
            self.fn(self.entry, self.args)
            return

        elif value == 'Cancel':
            self.textarea = ""
            self.entry = ""
            self.keyboard.destroy()
            return

        elif value == 'Backspace':
            i = self.textarea.get(1.0, END)
            new_text = i[:-2]
            self.textarea.delete(1.0, END)
            self.textarea.insert(INSERT, new_text)

        elif value == 'Shift' or value == 'Lowercase':
            self.shiftKeys()
        else:
            self.textarea.insert(INSERT, value)
            # Return keys to lowercase if they are currently uppercase
            if self.upper:
                self.shiftKeys()

        self.textarea.focus_set()

keyboard = MyKeyboard("test of title", "test", None, None)
keyboard.keyboard.mainloop()