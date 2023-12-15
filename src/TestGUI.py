import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import time


# Create arrays of known face encodings and their names

class RECID(ctk.CTk):
    def __init__(self, get_identify_frame, get_remove_frame, remove_and_update, get_identity, add_and_update, *args, **kwargs):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        ctk.CTk.__init__(self, *args, **kwargs)
        self.get_identify_frame = get_identify_frame
        self.get_remove_frame = get_remove_frame
        self.remove_and_update = remove_and_update
        self.get_identity = get_identity
        self.add_and_update = add_and_update
        # self.get_add_frame = get_add_frame 

        # Create custom fonts
        self.title_font = ctk.CTkFont(family='helvetica', weight='bold', size=60)
        self.button_font = ctk.CTkFont(family='Calibri', size=25)
        self.home_button_font = ctk.CTkFont(family='Calibri', size=35, weight='bold')
        self.remove_button_font = ctk.CTkFont(family='Calibri', size=17)
        
        container = ctk.CTkFrame(self, width=500, height=750)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_propagate(False)

        self.frames = {}
        for F in (ControlsPage, IdentifyPage, AddPage, RemovePage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
        
            frame.grid(row=0, column=0, sticky="nsew")
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_propagate(False)
            
            frame.title_font = self.title_font
            frame.button_font = self.button_font
            
        self.title("Face Recognition GUI")
        self.resizable(False, False)
        self.show_frame("ControlsPage")
       

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        # print('hide frames')
        for frame in self.frames.values():
            try: frame.stop()
            except: pass
        frame = self.frames[page_name]
        frame.set_running = True
        frame.tkraise()
        try: frame.update()
        except: pass

class ControlsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        label = ctk.CTkLabel(self, text="Controls", font=controller.title_font)

        button1 = ctk.CTkButton(self, text="Identify", width=270, height=75, font=controller.button_font, command=lambda: controller.show_frame("IdentifyPage"))
        button2 = ctk.CTkButton(self, text="Add", width=270, height=75, font=controller.button_font, command=lambda: controller.show_frame("AddPage"))
        button3 = ctk.CTkButton(self, text="Remove", width=270, height=75, font=controller.button_font, command=lambda: controller.show_frame("RemovePage"))

        label.grid(row=0, column=0, pady=(70, 20), sticky='ns')
        button1.grid(row=1, column=0, pady=25, sticky='ns')
        button2.grid(row=2, column=0, pady=25, sticky='ns')
        button3.grid(row=3, column=0, pady=(25, 100), sticky='ns')


class IdentifyPage(ctk.CTkFrame):  # New IdentifyPage class
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        self.canvas = ctk.CTkCanvas(self, width=700, height=1100)  # Create a canvas for video display
        self.canvas.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        button = ctk.CTkButton(self, text="Home", width=170, height=60, font=controller.home_button_font, command=lambda: controller.show_frame("ControlsPage"))
        identify_button = ctk.CTkButton(self, text="Identify", width=170, height=60, font=controller.home_button_font, command=lambda: self.show_identity())
        button.grid(row=1, column=0, padx=27, pady=25)
        identify_button.grid(row=1, column=1, padx=40, pady=25)

        self.frame_image = ImageTk.PhotoImage(Image.new("RGB", (480, 550)))
        self.canvas_image = self.canvas.create_image(0, 0, anchor="nw", image=self.frame_image)

        self.set_running = True

    def update(self):
        if (frame:=self.controller.get_identify_frame()) is not None:
            frame_image = ImageTk.PhotoImage(image=Image.fromarray(cv2.resize(frame, (700, 1100))))

            self.canvas.itemconfig(self.canvas_image, image=frame_image)
            self.frame_image = frame_image

        if self.set_running:
            self.controller.after(10, self.update)

    def show_identity(self):
        identity = self.controller.get_identity()
            
    
    def stop(self):
        self.set_running = False

    def __del__(self):
        self.stop()


class AddPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        self.canvas = ctk.CTkCanvas(self, width=700, height=1100)  # Create a canvas for video display
        self.canvas.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        button = ctk.CTkButton(self, text="Home", width=170, height=60, font=controller.home_button_font, command=lambda: controller.show_frame("ControlsPage"))
        identify_button = ctk.CTkButton(self, text="Add", width=170, height=60, font=controller.home_button_font, command=lambda: self.add())
        button.grid(row=1, column=0, padx=27, pady=25)
        identify_button.grid(row=1, column=1, padx=40, pady=25)

        self.frame_image = ImageTk.PhotoImage(Image.new("RGB", (480, 550)))
        self.canvas_image = self.canvas.create_image(0, 0, anchor="nw", image=self.frame_image)

        self.set_running = True

        # self.update()

    def update(self):
        if (frame:=self.controller.get_identify_frame()) is not None:
            frame_image = ImageTk.PhotoImage(image=Image.fromarray(cv2.resize(frame, (700, 1100))))

            self.canvas.itemconfig(self.canvas_image, image=frame_image)
            self.frame_image = frame_image

        if self.set_running: self.controller.after(10, self.update)

    def add(self):
        self.stop()
        self.controller.add_and_update()
        self.set_running = True
        self.update()

    def stop(self):
        self.set_running = False

    def __del__(self):
        self.stop()
    

class RemovePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        self.canvas = ctk.CTkCanvas(self, width=700, height=1100)  # Create a canvas for video display
        self.canvas.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        home_button = ctk.CTkButton(self, text="Home", width=170, height=60, font=controller.home_button_font, command=lambda: controller.show_frame("ControlsPage"))
        self.remove_entry = ctk.CTkEntry(self, width=170, height=20)
        remove_button = ctk.CTkButton(self, text="Remove", font=controller.remove_button_font, width=170, height=35, command=self.remove)
        
        home_button.grid(row=1, column=0, padx=27, pady=25, sticky='ns')
        self.remove_entry.grid(row=1, column=1, padx=40, pady=20, sticky='n')
        remove_button.grid(row=1, column=1, padx=40, pady=20, sticky='s')

        self.frame_image = ImageTk.PhotoImage(Image.new("RGB", (480, 550)))
        self.canvas_image = self.canvas.create_image(0, 0, anchor="nw", image=self.frame_image)

        self.set_running = True

        # self.update()

    def update(self):
        self.database, frame = self.controller.get_remove_frame()
        if frame is not None:
            frame_image = ImageTk.PhotoImage(image=Image.fromarray(cv2.resize(frame, (700, 1100))))

            self.canvas.itemconfig(self.canvas_image, image=frame_image)
            self.frame_image = frame_image

        if self.set_running: self.controller.after(10, self.update)

    def remove(self):
        remove_name = self.remove_entry.get()
        self.remove_entry.delete(0, len(remove_name))
        if remove_name not in [patient['name'] for patient in self.database]:
            self.remove_entry.insert(0, '[Please enter valid name]')
        self.controller.remove_and_update(remove_name)

    def stop(self):
        self.set_running = False

    def __del__(self):
        self.stop()

if __name__ == "__main__":
    from main import Main

    main = Main((800, 1100))
    app = RECID(main.frame)
    app.mainloop()
