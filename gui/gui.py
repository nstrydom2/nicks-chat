
from tkinter import *

from tkinter import scrolledtext, Entry, Button

window = Tk()

window.title("Welcome to LikeGeeks app")

window.geometry('500x400')

txt = scrolledtext.ScrolledText(window, width=69, height=20)
txt.pack()

input_txt = scrolledtext.ScrolledText(window, width=52, height=4)
input_txt.pack(side=LEFT)

button = Button(window, text='Send', width=10, height=4)
button.pack(side=RIGHT)

window.mainloop()