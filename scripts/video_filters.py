import cv2 as cv
import numpy as np

class Filters:
    """ 
    Filters are functions that receive frames, and return frames
    """
    
    cv_colors = {
        'Grayscale': None,
        'Reverted': lambda f: 255 - f,
        'Bone': lambda f: cv.cvtColor(f, cv.COLORMAP_BONE),
        'Jet': lambda f: cv.cvtColor(f, cv.COLORMAP_JET),
        'Winter': lambda f: cv.cvtColor(f, cv.COLORMAP_WINTER),
        'Rainbow': lambda f: cv.cvtColor(f, cv.COLORMAP_RAINBOW),
        'Ocean': lambda f: cv.cvtColor(f, cv.COLORMAP_OCEAN),
        'Summer': lambda f: cv.cvtColor(f, cv.COLORMAP_SUMMER),
        'Spring': lambda f: cv.cvtColor(f, cv.COLORMAP_SPRING),
        'Cool': lambda f: cv.cvtColor(f, cv.COLORMAP_COOL),
        'Hsv': lambda f: cv.cvtColor(f, cv.COLORMAP_HSV),
        'Pink': lambda f: cv.cvtColor(f, cv.COLORMAP_PINK),
        'Hot': lambda f: cv.cvtColor(f, cv.COLORMAP_HOT),
    }

    @staticmethod
    def flip_vertical(frame):
        cv.flip(frame, frame, 0)
        return frame

    @staticmethod
    def flip_horizontal(frame):
        frame = cv.flip(frame, 1)
        return frame

    @staticmethod  
    def face_detection(frame):
        frame = frame.astype(np.uint8)
        faces = face_detector.detect_faces(frame)
        for (x,y,w,h) in faces:
            frame = cv.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
#        for (x,y) in faces:
#            print("FACE AT:", (x,y))
#            frame = Filters.draw_x(frame, (x,y), color=255, size=30, thickness=3)
#            frame = cv.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
        
        return frame
   
    @staticmethod 
    def color_filter(frame, color_code):
        if frame.shape[-1] != 3:
            frame = cv.cvtColor(frame, cv.COLOR_GRAY2RGB)

        colormap_func = Filters.cv_colors[color_code]
        try:
            colored = colormap_func(frame)
            return colored
        except:
            return frame
    
    @staticmethod
    def draw_x(frame, coords, color=0, size=10, thickness=3):
        if frame.shape[-1] == 3:
            color = np.array([color, color, color])
        half_size = size // 2
        # Horizontal
        for n in range(-half_size, half_size+1):
            x = coords[1] + n
            for yshift in range(-thickness // 2, (thickness // 2)+1):
                y = coords[0] + yshift
                frame[x][y] = color

        # Vertical
        for n in range(-half_size, half_size+1):
            y = coords[0] + n
            for xshift in range(-thickness // 2, (thickness // 2)+1):
                x = coords[1] + xshift
                frame[x][y] = color
        frame[coords[1]][coords[0]] = color
        return frame
    
    @staticmethod
    def blur(frame, kernel_size=(5,5)):
        return cv.GaussianBlur(frame, kernel_size, 0)

    @staticmethod
    def convert_to_uint8(frame):
        cv.normalize(frame, frame, 0, 255, cv.NORM_MINMAX)
        frame       = frame.astype(np.uint8) 
        return frame
    
