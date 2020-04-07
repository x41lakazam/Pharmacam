import numpy as np
import cv2 as cv
import os 
import time
import face_recognition
import sys

import frames_io_handler as io
from setup import Setup



class Person:
    count = 0

    def __init__(self, temperature, face=None):
        self.temperature = float(temperature)
        self.face        = face
        self.mark        = None

        self.name             = "Person.{}".format(self.__class__.count)
        self.__class__.count += 1

def generate_data(n, out_dir, sleep=.2, background=False, gen_info=False):
    print('Starting in 3 seconds')
    time.sleep(1)
    print('2..')
    time.sleep(1)
    print('1..')
    time.sleep(1)
    saved = []
    for i in range(n):
        print("SHOT {}/{}".format(i, n))
        name = 'img{}'.format(i)
        if background:
            name = 'bkg{}'.format(i)
        path = os.path.join(out_dir, name)
        io.save_frame(Setup.VIDEO_PIPE, path, secure=False, totype=np.uint8)
        saved.append(path)
        time.sleep(sleep)

    if gen_info:
        gen_file = os.path.join(out_dir, 'info.dat')
        with open(gen_info, 'w') as f:
            for imgname in saved:
                f.write(imgname + '\n')
    
 
def detect_faces(frame):
    # With haar cascade
    cascade = cv.CascadeClassifier(Setup.FD_HAAR_MODEL,)
    landmarks = cascade.detectMultiScale(frame, 1.05, 3)
    return landmarks

    # With face_recognition module
    """
    landmarks_multi = face_recognition.face_landmarks(frame)
    fheads = []
    for landmarks in landmarks_multi:
        reye     = landmarks['right_eye'][0]
        reyebrow = landmarks['right_eyebrow'][0]
        leyebrow = landmarks['left_eyebrow'][0]
        
        mid_eyes = [(reyebrow[0] - leyebrow[0])//2 ,  (reyebrow[1] + leyebrow[1]) // 2]
        eye_eyebrow_vec = [
                        reyebrow[0] - reye[0], 
                        reyebrow[1] - reye[1] 
                    ] 
        mid_fhead = [mid_eyes[0] + eye_eyebrow_vec[0], mid_eyes[1] + eye_eyebrow_vec[1]]
        fheads.append(mid_fhead)
    """ 
    return fheads
        
    return face_boundaries

def classify_faces(frame, known_faces):
    pass

def get_forehead(frame, face_boundaries):
    forehead_boundaries = np.array()
    return forehead_boundaries

if __name__ == "__main__":
    generate_data(30, 'resources/classifiers/train_data/thermdata/background', sleep=5, gen_info=True)
