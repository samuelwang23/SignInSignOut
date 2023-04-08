from tkinter import *
from PIL import ImageTk, Image
from datetime import datetime
import pygame
import inspect

def get_date_and_clock():
    date = datetime.now().strftime('%Y-%m-%d')
    clock = datetime.now().strftime('%H:%M:%S')
    return date, clock


def clean_name(comma_name):
    name_split = comma_name.split(", ")
    return name_split[1] + " " + name_split[0]

def close(top, other):
    top.deiconify()
    other.destroy()

def imageFrame(window, image, relx, rely, relwidth, relheight):
    frame = Frame(window, bg='#80c1ff', bd=5)
    frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight, anchor='n')
    label = Label(frame, image = image)
    label.place(relwidth = 1, relheight= 1) 

def renderImage(path, width, height):
    my_pic = Image.open(path)
    render = my_pic.resize((width, height), Image.ANTIALIAS)
    new_pic = ImageTk.PhotoImage(render)
    return new_pic

def textFrame(window, text, color, font_size, relx, rely, relwidth, relheight):
    frame = Frame(window, bd=5)
    frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight, anchor='s')
    label = Label(frame, text=text)
    label.config(font=(f'Helvetica {font_size} bold'), fg=color)
    label.place(relwidth = 1, relheight= 1)

def buttonFrame(window, text, command, font_size, relx, rely, relheight, relwidth):
    frame = Frame(window, bg='#80c1ff', bd=3)
    frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight, anchor='s')
    btn1 = Button(frame, text = text, font = f'Helvetica {font_size} bold', command=command)
    btn1.place(relwidth = 1, relheight= 1)

def create_confirm_box(text, type):
    message = Toplevel()
    message.geometry("500x400+700+300")
    global image
    image = ImageTk.PhotoImage(file = f'{type}.png')
    label = Label(message, text=text, font=('Helvetica 20 bold'))
    label.pack()
    label.bind('<Configure>', lambda e: label.config(wraplength=label.winfo_width() + 10))
    image_label = Label(message, image=image)
    image_label.pack()
    return message

def success_confirm(confirm_text):
    confirmation = create_confirm_box(confirm_text, "complete")
    operation_name = inspect.stack()[1][3]
    print(operation_name)
    # Button(confirmation, text = "Cancel", font ='Helvetica 17 bold', command=lambda:fac_off_campus.delete_rows(row_id)).pack()
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

def get_top_level_windows(root):
    tops = [] 
    for widget in root.winfo_children(): # Looping through widgets in main window
        if '!toplevel' in str(widget): 
            tops.append(widget)      
    return len(tops)

def get_day_of_week():
    return datetime.now().weekday()

def get_time_from_string(string):
    return datetime.strptime(string,'%H:%M')

def get_current_time():
    return datetime.now()

def is_root_window_in_front(root):
    return root.tk.eval('wm stackorder '+str(root)).split(" ")[-1] == str(root)

def close_children_windows(root):
    for widget in root.winfo_children(): # Looping through widgets in main window
        if '!toplevel' in str(widget): # If toplevel exists in the item
            widget.destroy()

# Threaded Timer (Credit: https://stackoverflow.com/a/38317060)
from threading import Timer
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False