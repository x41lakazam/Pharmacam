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

    p = self.panel1_temperature - m * px2_val
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
    transform_mat = cv.getAffineTransform(cam1_3points, cam2_3points)
    return cv.transform(point_to_convert, transform_mat)

if __name__ == "__main__":
    # Test matching pts
    img1 = cv.imread('rgbframe.png')
    img2 = cv.imread('thermframe.png')

    img1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
    img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
    matches = find_matching_pts(img1, img2, draw=True)
    
