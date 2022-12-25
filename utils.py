from tkinter import *
from PIL import ImageTk, Image



def get_date_and_clock():
    date = datetime.now(tz).strftime('%Y-%m-%d')
    clock = datetime.now(tz).strftime('%H:%M:%S')
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