import cv2

class Camera:
    def __init__(self, cam_num, rot=False, flip=True):
        self.cam = cv2.VideoCapture(cam_num)
        self.rot = rot
        self.flip = flip

    def get_frame(self):
        ret, frame = self.cam.read()
        if not ret: return None

        if self.rot:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        if self.flip:
            frame = cv2.flip(frame, 1)
        
        return frame
    
    def kill(self):
        self.cam.release()
        cv2.destroyAllWindows()