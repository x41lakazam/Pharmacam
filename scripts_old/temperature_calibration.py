'''
Script for extracting manually the objectPoints (in the world) and the imagePoints (pixel coordinates).
The script save the extracted points from each image in a dict where the key is the name of the image
and contain two np array:
 - imagePoints of shape: (1, n, 3) with n the number of corners for this specific image
 - imgpoints of shape: (n, 1, 2)
 Select the points with the mouse in this order
 3  6
 2  5
 1  4
'''
import cv2
import numpy as np
import glob
import pickle

import frames_io_handler as io
from setup import Setup

############ VARIABLES ################

output_pck  = 'temperature_scale.pck'
frame       = "/home/debian/opgal/dump/frame_10.bin"
image_name  = 'frame.png'

# --> Change them in function def 
#####################################################

global ix, iy
ix, iy = -1, -1

# mouse callback function
def get_pixel(event, x, y, flags, param):
    global ix, iy
    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y

def main(frame='/opt/eyerop/bin/camera_out'):
    
    image_name = 'tmp_frame.png'

    output_pck = Setup.SCALE_FILE

    frame_vals = io.open_frame(frame)
    image = io.save_frame(frame, image_name, secure=False)

    # defining global variables for saving the coordinates on click event



    # creating the window and setting the Callback on mouse event
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 1025, 768)
    cv2.setMouseCallback('image', get_pixel)
    cv2.moveWindow('image', 220, 5)

    img_original = cv2.imread(image)
    img = img_original.copy()
    cv2.imshow('image', img)
    cv2.waitKey(100)
    # Check temperature of point 1
    p1_temp = input('[?] Please input temperature of point 1: ')
    p1_temp = float(p1_temp)

    print("[?] Now please click on a point and press enter (while being on the picture window)")
    cv2.waitKey()
    p1_ix, p1_iy = ix, iy
    print('[v] Got point 1:', (p1_ix, p1_iy))

    # Check temperature of point 2
    p2_temp = input('[?] Please input temperature of point 2: ')
    p2_temp = float(p2_temp)

    print("[?] Now please click on a point and press enter (while being on the picture window)")
    cv2.waitKey()
    p2_ix, p2_iy = ix, iy
    print('[v] Got point 2:', (p2_ix, p2_iy))

    print("[*] Processing points:", (p1_ix, p1_iy), (p2_ix, p2_iy))
    p1_val = float(frame_vals[p1_iy][p1_ix])
    p2_val = float(frame_vals[p2_iy][p2_ix])

    scale_diff = abs(p2_val - p1_val)
    temp_diff  = abs(p2_temp - p1_temp)

    temp_per_scale = temp_diff / scale_diff
    print("[v] Temperature resolution:", temp_per_scale)

    # updating the dict with the result of the current image
    # saving the result
    pickle.dump(temp_per_scale, open(output_pck, 'wb'))

    print("[v] Result dumped to ", output_pck)

    return temp_per_scale

if __name__ == "__main__":
    main()


