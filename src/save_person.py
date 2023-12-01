import pickle

import cv2

from camera import Camera

class Saver:
    def __init__(self, data_inclusions=None):
        if data_inclusions is not None:
            with open('../data/people/people.pkl', 'wb') as out_file:
                pickle.dump((data_inclusions, [None]), out_file, pickle.HIGHEST_PROTOCOL)

    def add(self, preface=None):
        with open('../data/people/people.pkl', 'rb') as in_file:
            # print(len(pickle.load(in_file)))
            data_inclusions, existing = pickle.load(in_file)
        if len(existing) == 1 and existing[0] is None:
            existing.pop(0)

        patient_info = []
        
        name = input('What is patient\'s name?  ')
        if name in [patient['name'] for patient in existing]:
            print(f'{name} is already in the system.')
            return
        patient_info.append(('name', name))

        for inclusion in data_inclusions[1:]:
            patient_info.append((str(inclusion), input(f'What is patient\'s {str(inclusion)}?  ')))
        
        frame = None
        if preface is None:
            cam = Camera(1)
            frame = None
            while frame is None:
                frame = cam.get_frame()
            cam.kill()
        else:
            frame = preface

        with open('../data/people/people.pkl', 'wb') as out_file:
            existing.append({'frame':frame, **dict(patient_info)})
            pickle.dump((data_inclusions, existing), out_file, pickle.HIGHEST_PROTOCOL)

    def remove(self, remove_name):
        with open('../data/people/people.pkl', 'rb') as in_file:
            data_inclusions, existing = pickle.load(in_file)
        
        for idx, name in enumerate([patient['name'] for patient in existing]):
            if name == remove_name:
                existing.pop(idx)
        
        with open('../data/people/people.pkl', 'wb') as out_file:
            pickle.dump((data_inclusions, existing), out_file, pickle.HIGHEST_PROTOCOL)

    def access(self, patient_name):
        with open('../data/people/people.pkl', 'rb') as in_file:
            data_inclusions, existing = pickle.load(in_file)
        
        for idx, patient in enumerate(existing):
            if patient['name'] == patient_name:
                return dict([item for item in patient.items() if item[0] != 'frame'])
        
        return None
            

    def show(self):
        with open('../data/people/people.pkl', 'rb') as in_file:
            data_inclusions, existing = pickle.load(in_file)
        
        print(f'there are {len(existing)} people stored')

        per = int(input('which person to show? '))
        print(existing[per][1:])

        while True:
            cv2.imshow('person', existing[per][0])
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    def get_data(self):
        with open('../data/people/people.pkl', 'rb') as in_file:
            data_inclusions, existing = pickle.load(in_file)
        return data_inclusions, existing