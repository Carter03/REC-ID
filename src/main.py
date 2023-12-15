import os
import numpy as np
import cv2

from image_tools import Process, FastProcess
from save_person import Saver
from camera import Camera
from gui import UI
from TestGUI import *

class Main:
    def __init__(self, cam_coords):
        self.cam_size = cam_coords
        self.loading_screen = cv2.imread(r'../data/screenshots/loading_screen.jpg', 0)
        self.camera = Camera(0)

        if 'people.pkl' not in os.listdir(r'../data/people'): 
            categories = []
            i=1
            for _ in range(2):
                response = input(f'Create data category {i}:  ')
                while response == '' or len(response) > 30:
                    response = input(f'Create valid data category {i}:  ')
                categories.append(response)
                print(categories)
                i += 1
            while response != '':
                response = input(f'Create data category {i}:  ')
                if len(response) > 30: continue
                if response != '': categories.append(response)
                i += 1
            try: categories.remove('name')
            except: pass
            categories.insert(0, 'name')
            print(categories)
            self.saver = Saver(categories)
        else:
            self.saver = Saver()

        self.known_encodings, self.known_names = Process.get_data(self.saver)

    def create_image(self, data_inclusions, patient_data):
        patient_data.insert(0, dict([(inclusion, inclusion.title()) for inclusion in data_inclusions]))

        image_height = max(40 * len(patient_data) + 40, self.cam_size[1])
        image = np.ones((image_height, self.cam_size[0], 3), dtype=np.uint8) * 26

        font = cv2.FONT_HERSHEY_TRIPLEX
        font_scale = 1
        font_thickness = 2

        for i, patient in enumerate(patient_data):
            if i == 0:
                font_color = (141*1.65, 83*1.65, 31*1.65)
            else:
                font_color = (255, 255, 255)
            
            name_text = f"{patient['name']}"
            y_offset = i * 40 + 50 + (20 if not i==0  else 0)
            cv2.putText(image, name_text, (20, y_offset), font, font_scale, font_color, font_thickness)
            
            room_num_text = f"{patient[str(data_inclusions[1])]}"
            x_off = max(self.cam_size[0] // 2, 25*len(name_text)) + 20

            if 25*len(room_num_text) < self.cam_size[0] - x_off:
                cv2.putText(image, room_num_text, (x_off, y_offset), font, font_scale, font_color, font_thickness)
            else:
                cv2.putText(image, room_num_text, (x_off, y_offset), font, (self.cam_size[0] - x_off)/(25*len(room_num_text)), font_color, 1)

        return image

    def create_identity(self, face, patient_data):
        face = cv2.resize(face, (300, 300))
        image_height = max(40 * len(patient_data) + face.shape[0], self.cam_size[1])
        image = np.ones((image_height, self.cam_size[0], 3), dtype=np.uint8) * 26

        font = cv2.FONT_HERSHEY_TRIPLEX
        font_scale = 1
        font_thickness = 2
        font_color = (255, 255, 255)
        outline_width = 8

        image[30+outline_width:30+outline_width+face.shape[0], self.cam_size[0]//2-face.shape[1]//2:self.cam_size[0]//2+face.shape[1]//2 + (1 if face.shape[1]%2 == 1 else 0)] = face
        cv2.rectangle(image, (self.cam_size[0]//2-outline_width//2-face.shape[1]//2, 30+outline_width//2), (self.cam_size[0]//2+outline_width//2+face.shape[1]//2 + (1 if face.shape[1]%2 == 1 else 0), 30+outline_width+outline_width//2+face.shape[0]), (141*1.65, 83*1.65, 31*1.65), outline_width)

        for i, datapoint in enumerate(patient_data.items()):
            label_text = str(datapoint[0]).title()
            y_offset = i * 40 + face.shape[0] + 100 + outline_width
            cv2.putText(image, label_text, (20, y_offset), font, font_scale, font_color, font_thickness)
            
            data_text = str(datapoint[1])
            x_off = max(self.cam_size[0] // 2, 25*len(label_text))

            if 25*len(data_text) < self.cam_size[0] - x_off:
                cv2.putText(image, data_text, (x_off, y_offset), font, font_scale, font_color, font_thickness)
            else:
                cv2.putText(image, data_text, (x_off, y_offset), font, (self.cam_size[0] - x_off)/(25*len(data_text)), font_color, 1)

        return image

    def Identify(self):
        camera = Camera(0)
        while True:
            frame = camera.get_frame()
            if frame is None: continue

            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, self.cam_size)

            drawn_frame, selected = FastProcess(frame).draw_faces(15, 15)
            
            if cv2.waitKey(1) & 0xFF == ord(' ') and selected is not None and selected.any():
                processed = Process(selected)
                processed.load_data(self.known_encodings, self.known_names)
                
                if locs:=processed.get_faces():
                    name = processed.get_name(locs[0])
                    if name == 'Unlisted':
                        continue
                    identity_image = self.create_identity(selected, self.saver.access(name))
                    cv2.imshow('Residents', identity_image)
                    cv2.waitKey(1)
                    continue

            cv2.imshow('cv2', drawn_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        camera.kill()
    
    def get_boxed_frame(self):
        frame = self.camera.get_frame()
        if frame is None: return None

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, self.cam_size)

        drawn_frame, self.selected = FastProcess(frame).draw_faces(15, 15)
        return cv2.cvtColor(drawn_frame, cv2.COLOR_BGR2RGB)
    
    def get_identity(self):
        processed = Process(self.selected)
        processed.load_data(self.known_encodings, self.known_names)
        
        if locs:=processed.get_faces():
            name = processed.get_name(locs[0])
            if name == 'Unlisted':
                return None
            identity_image = self.create_identity(self.selected, self.saver.access(name))
            cv2.imshow('Identity', identity_image)
            cv2.waitKey(1)
            return identity_image
        return None
    
    def add_and_update(self):
        if self.selected is not None:
            self.saver.add(self.selected)
            self.known_encodings, self.known_names = Process.get_data(self.saver)

    def Add(self):
        camera = Camera(0)
        while True:
            frame = camera.get_frame()
            if frame is None: continue

            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, self.cam_size)

            drawn_frame, selected = FastProcess(frame).draw_faces(15, 15)

            if cv2.waitKey(1) & 0xFF == ord(' ') and selected is not None:
                cv2.imshow('cv2', self.loading_screen)
                cv2.waitKey(1)
                self.saver.add(selected)
                self.known_encodings, self.known_names = Process.get_data(self.saver)
                continue

            cv2.imshow('cv2', drawn_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        camera.kill()

    def Remove(self):
        data_inclusions, database = self.saver.get_data()
        cv2.imshow('Residents', self.create_image(data_inclusions, database))

        remove_name = input('Which patient would you like to remove (enter to exit)? ')
        while remove_name not in [patient['name'] for patient in database] and remove_name != '':
            remove_name = input('Please enter a valid name: ')

        if remove_name == '':
            cv2.destroyAllWindows()
            return
        
        self.saver.remove(remove_name)
        self.known_encodings, self.known_names = Process.get_data(self.saver)

        cv2.destroyAllWindows()

    def remove_and_update_info(self, remove_name):
        self.saver.remove(remove_name)
        self.known_encodings, self.known_names = Process.get_data(self.saver)

    def get_remove_frame(self):
        data_inclusions, database = self.saver.get_data()
        return database, cv2.cvtColor(self.create_image(data_inclusions, database), cv2.COLOR_BGR2RGB)

if __name__ == '__main__':
    main = Main((700, 1100))
    ui = RECID(main.get_boxed_frame, main.get_remove_frame, main.remove_and_update_info, main.get_identity, main.add_and_update)
    ui.mainloop()