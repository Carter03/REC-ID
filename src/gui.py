import customtkinter
from tkinter import *

class UI:
    def __init__(self, main):
        self.main = main

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        self.root = customtkinter.CTk()

        self.root.title("Face Recognition GUI")

        self.root.geometry("500x650")
        self.root.resizable(True, True)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        title_font = customtkinter.CTkFont(family='helvetica', weight='bold', size=60)
        button_font = customtkinter.CTkFont(family='Calibri', size=25)

        Label1 = customtkinter.CTkLabel(master=self.root, text = 'Controls', font=title_font)
        Label1.grid(row=0, column=0, pady=(70, 20), sticky='ns')

        Button1 = customtkinter.CTkButton(master=self.root, command=self.Identify, text = 'Identify', width=270, height=75, font=button_font)
        Button1.grid(row=1, column=0, pady=25, sticky='ns')

        Button2 = customtkinter.CTkButton(master=self.root, command=self.Add, text = 'Add', width=270, height=75, font=button_font)
        Button2.grid(row=2, column=0, pady=25, sticky='ns')

        Button3 = customtkinter.CTkButton(master=self.root, command=self.Remove, text = 'Remove', width=270, height=75, font=button_font)
        Button3.grid(row=3, column=0, pady=(25, 100), sticky='ns')

        self.root.protocol("WM_DELETE_WINDOW", exit)
    
    def Identify(self):
        self.hide_window()
        self.main.Identify()
        self.show_window()

    def Add(self):
        self.hide_window()
        self.main.Add()
        self.show_window()

    def Remove(self):
        self.hide_window()
        self.main.Remove()
        self.show_window()

    def init(self):
        self.root.mainloop()

    def show_window(self):
        self.root.deiconify()

    def hide_window(self):
        self.root.withdraw()