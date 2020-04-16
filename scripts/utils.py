from setup import Setup
import matplotlib.pyplot as plt
import numpy as np 
import cv2 as cv

def calibrate_temperature(temp1, temp2, px1_val, px2_val):
    """
    Returns a mapping function 
    temp1 & temp2 are the two real temperatures of the picked points
    px1_val & px2_val are the two pixels values
    """
    m = (temp1 - temp2) / (px1_val - px2_val) 

    p = temp1 - m * px2_val
    temp_function = lambda dl: m*dl + p

    return temp_function

def find_matching_pts(img1, img2, draw=False, n_matching=3):

##    # Create sift detector
#    orb = cv.ORB_create()
    # Surf detector
    surf = cv.SURF_CREATE(400)

    kp1, des1 = surf.detectAndCompute(img1, None)
    kp2, des2 = surf.detectAndCompute(img2, None)

    # Create BFMatcher 
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)

    # Match descriptors
    matches = sorted(bf.match(des1, des2), key=lambda m: m.distance)
    
    if draw:
        outimg = np.array([])
        outimg = cv.drawMatches(img1, kp1, img2, kp2, matches1to2=matches[:n_matching], outImg=outimg, flags=2)
        plt.imshow(outimg);plt.show()

    # Return first 3 matches
    return matches[:n_matching]

def camera_project_point(cam1_3points, cam2_3points, point_to_convert):
    cam1_3points = np.float32(cam1_3points)
    cam2_3points = np.float32(cam2_3points)
    transform_mat = cv.getAffineTransform(cam1_3points, cam2_3points)
    converted = np.dot(transform_mat, np.array([point_to_convert[0], point_to_convert[1], 1])) # From the equation of the opencv doc cv.GetAffineTranform
    #points = np.float32([point_to_convert])
    #converted = np.zeros_like(points)
    #cv.transform(points, converted, transform_mat)
    #converted = converted[0]

    converted = np.uint(converted)

    #333
    #print("Cam 1 points:", cam1_3points)
    #print("Cam 2 points:", cam2_3points)
    #print("Transform mat:", transform_mat)
    #print("Point to convert:", point_to_convert)
    #print("Converted:", converted)

    return converted

if __name__ == "__main__":
    # Test matching pts
    img1 = cv.imread('rgbframe.png')
    img2 = cv.imread('thermframe.png')

    img1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
    img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
    matches = find_matching_pts(img1, img2, draw=True)
    
