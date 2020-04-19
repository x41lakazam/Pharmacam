import numpy as np
import cv2 as cv
import os 
import time
import sys

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
        #io.save_frame(Setup.VIDEO_PIPE, path, secure=False, totype=np.uint8)
        saved.append(path)
        time.sleep(sleep)

    if gen_info:
        gen_file = os.path.join(out_dir, 'info.dat')
        with open(gen_info, 'w') as f:
            for imgname in saved:
                f.write(imgname + '\n')
    
 
def detect_faces(frame):
    # With haar cascade
    #cascade = cv.CascadeClassifier(Setup.FD_HAAR_MODEL,)
    #landmarks = cascade.detectMultiScale(frame, 1.05, 3)
    #return landmarks

    # With face_recognition module
    return {}


def classify_faces(frame, known_faces):
    pass

def get_forehead(frame, face_boundaries):
    forehead_boundaries = np.array()
    return forehead_boundaries

if __name__ == "__main__":
    generate_data(30, 'resources/classifiers/train_data/thermdata/background', sleep=5, gen_info=True)
