import math

import cv2
import face_recognition as fr
import numpy as np
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

class Process:
    def __init__(self, frame):
        self.frame = frame
        self.known_face_encodings = []
        self.known_face_names = []

    def load_data(self, encodings=None, names=None):
        self.known_face_encodings, self.known_face_names = encodings, names
    
    @staticmethod
    def get_data(saver):
        known_face_encodings = []
        known_face_names = []
        
        if not saver.get_data()[1] or saver.get_data()[1][0] is None:
            return known_face_encodings, known_face_names

        for person in saver.get_data()[1]:
            img = person['frame']
            try:
                imgEncoding = fr.face_encodings(img)[0]
                known_face_encodings.append(imgEncoding)
                known_face_names.append(person['name'])
            except:
                pass

        return known_face_encodings, known_face_names

    def get_faces(self):
        if self.frame is None or not self.frame.any():
            return None
        self.frame_rgb_small = cv2.resize(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB), (0, 0), fx=0.25, fy=0.25)
        face_locations = fr.face_locations(self.frame_rgb_small)
        return face_locations
    
    def get_name(self, face_location):
        if not self.known_face_encodings:
            return 'Unlisted'

        try: face_encoding = fr.face_encodings(self.frame_rgb_small, [face_location])[0]
        except: return 'Unlisted'

        # if not self.known_face_encodings:
        #     self.load_data()

        matches = fr.compare_faces(self.known_face_encodings, face_encoding)
        name = 'Unlisted'

        face_distances = fr.face_distance(self.known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = self.known_face_names[best_match_index]
        
        return name
    
class FastProcess:
    def __init__(self, frame):
        self.frame = frame
    
    def draw_faces(self, padx=0, pady=0):
        def _normalized_to_pixel_coordinates(normalized_x, normalized_y, image_width, image_height):
            x_px = min(math.floor(normalized_x * image_width), image_width - 1)
            y_px = min(math.floor(normalized_y * image_height), image_height - 1)
            return x_px, y_px
        
        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
            image = self.frame.copy()
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detection.process(image)
            image_rows, image_cols, _ = image.shape

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            selected = None

            if results.detections:
                box_start_ends = []
                closest = (10000, -1)
                for idx, box in enumerate([i.location_data.relative_bounding_box for i in results.detections]):
                    rect_start_point = _normalized_to_pixel_coordinates(box.xmin, box.ymin, image_cols, image_rows)
                    rect_end_point = _normalized_to_pixel_coordinates(box.xmin + box.width, box.ymin + box.height, image_cols, image_rows)
                    if (dist:=math.sqrt((image_cols/2 - (rect_start_point[0] + (rect_end_point[0] - rect_start_point[0])/2))**2 + (image_rows/2 - (rect_start_point[1] + (rect_end_point[1] - rect_start_point[1])/2))**2)) < closest[0]:
                        closest = (dist, idx)
                    box_start_ends.append((rect_start_point, rect_end_point))
                
                for idx, (start, end) in enumerate(box_start_ends):
                    if idx == closest[1]:
                        selected = image.copy()[start[1]-3*pady:end[1]+3*pady, start[0]-3*padx:end[0]+3*padx, :]
                        cv2.rectangle(image, (start[0]-padx, start[1]-pady), (end[0]+padx, end[1]+pady), (127, 255, 0), 5)
                        cv2.putText(image, 'DETECTED FACE', (start[0] + int(padx/2), start[1] - 15 - pady), cv2.FONT_HERSHEY_TRIPLEX, abs(end[0] - start[0]) / 300, (127, 255, 0), 2)
                    else:
                        cv2.rectangle(image, start, end, (255, 255, 255), 3)
            
            return image, selected