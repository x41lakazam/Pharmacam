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
        'Rainbow': lambda f: cv.cvtColor(f, cv.COLORMAP_RAINBOW), 'Ocean': lambda f: cv.cvtColor(f, cv.COLORMAP_OCEAN),
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
            x = int(coords[1] + n)
            for yshift in range(-thickness // 2, (thickness // 2)+1):
                y = int(coords[0] + yshift)
                frame[x][y] = color

        # Vertical
        for n in range(-half_size, half_size+1):
            y = int(coords[0] + n)
            for xshift in range(-thickness // 2, (thickness // 2)+1):
                x = int(coords[1] + xshift)
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

    @staticmethod
    def zoom_glass(frame, coords=(0,0), window_size=100, zoom=4, offset=10, bbox_size=3,
                   padding_value=0):
        """
        Display a zoom glass on the frame
        coords: coordinates (as (X,Y)) of the point to zoom
        window_size: size of the square
        zoom: zoom factor (img will be displayed times <zoom>)
        offset: offset between cursor and zoomglass
        bbox_size: size of the bounding box
        padding_value: value of the padding
        """
        coords = (coords[1], coords[0])

        # --> Get zoomed frame
        cropped_size = window_size // zoom
        half_cropped = cropped_size // 2
        cropped_topleft = [
            coords[0] - half_cropped,
            coords[1] - half_cropped
        ]
        # Prevent errors
        for ix in range(len(cropped_topleft)):
            if cropped_topleft[ix] <= 0:
                cropped_topleft[ix] = 0
            if cropped_topleft[ix] >= frame.shape[ix]:
                cropped_topleft[ix] = frame.shape[ix] - window_size
                
        cropped_botright = [
            cropped_topleft[0] + cropped_size,
            cropped_topleft[1] + cropped_size
        ]

        # Prevent errors
        for ix in range(len(cropped_botright)):
            if cropped_botright[ix] <= 0:
                cropped_botright[ix] = 0
            if cropped_botright[ix] >= frame.shape[ix]:
                cropped_botright[ix] = frame.shape[ix]

        cropped_frame = frame[
            cropped_topleft[0]:cropped_botright[0],
            cropped_topleft[1]:cropped_botright[1]
        ]

        zoomed_frame = cv.resize(cropped_frame, (window_size, window_size))

        # --> Display it above coords
        # Window coords
        half_win    = window_size // 2
        win_botleft = [
            offset+coords[0]-half_win, 
            offset+coords[1]-half_win
        ]

        win_topleft = [
            win_botleft[0] - window_size,
            win_botleft[1]
        ]

        # Prevent errors
        for ix in range(len(win_topleft)):
            if win_topleft[ix] <= 0:
                win_topleft[ix] = bbox_size
            if win_topleft[ix] >= frame.shape[ix]:
                win_topleft[ix] = frame.shape[ix] - bbox_size


        # Draw it in the window
        frame[
            win_topleft[0]:win_topleft[0]+window_size,
            win_topleft[1]:win_topleft[1]+window_size,
        ] = zoomed_frame

        # Draw bounding box (coords are reverted bc its X,Y)
        # TODO -- not working
        #bbox_topleft = (
        #    win_topleft[1] - bbox_size,
        #    win_topleft[0] - bbox_size,
        #)
        #bbox_botright = (
        #    bbox_topleft[1] + window_size + bbox_size*2,
        #    bbox_topleft[0] + window_size + bbox_size*2,
        #)

        #frame = cv.rectangle(frame, bbox_topleft, bbox_botright, color=0, thickness=bbox_size)

        return frame



