import tkinter as tk
from functools import partial
from tkinter import ttk
import numpy as np
import threading
import datetime
import os
from PIL import Image, ImageTk
import time
import cv2 as cv

import capture
import utils
from setup import Setup
import face_detector
from face_detector import Person # Debug - remov

class Filters:
    
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

    def blur(frame, kernel_size=(5,5)):
        return cv.GaussianBlur(frame, kernel_size, 0)
    

class CalibrationFrame(tk.Frame):
     
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        top = self.winfo_toplevel()
        
        box_properties = dict(height=1, width=4, padx=10, pady=10) 
        self.panel1_coords = (-1, -1) 
        self.panel1_textbox = tk.Text(self, **box_properties)
        self.panel1_label = tk.Label(self, text="Panel 1 (unselected):")
        self.panel1_label.grid(row=0, column=0)
        self.panel1_textbox.grid(row=0, column=1)
        
        self.panel2_coords = (-1, -1) 
        self.panel2_textbox = tk.Text(self, **box_properties)
        self.panel2_label = tk.Label(self, text="Panel 2 (unselected:")
        self.panel2_label.grid(row=1, column=0)
        self.panel2_textbox.grid(row=1, column=1)
        
        self.explain_panel = tk.Label(self, text="To define a panel point, put the cursor on it and press L (for panel 1) or H (for panel 2), then enter their temperature")
        self.explain_panel.grid(row=2, column=0)
   
    @property 
    def panel1_temperature(self):
        return float(self.panel1_textbox.get('1.0', tk.END)) 

    @property
    def panel2_temperature(self):
        return float(self.panel2_textbox.get('1.0', tk.END)) 

    def select_panel1(self, x, y):
        self.panel1_label['text'] = "Panel 1 ({}, {}):".format(x,y)
        self.panel1_coords = (x,y)

    def select_panel2(self, x, y):
        self.panel2_label['text'] = "Panel 2 ({}, {}):".format(x,y)
        self.panel2_coords = (x,y)
    
    def calibrate_temperature(self, frame):
        panel1_val  = float(frame[self.panel1_coords[1]][self.panel1_coords[0]])
        panel2_val  = float(frame[self.panel2_coords[1]][self.panel2_coords[0]])

        m = (self.panel1_temperature - self.panel2_temperature) / (panel2_val - panel1_val) 

        p = self.panel1_temperature - m * panel1_val 
        temp_function = lambda dl: m*dl + p

        return temp_function

    def get_temperature(self, frame, point):
        point_val = float(frame[point[1]][point[0]])
        scale = self.calibrate_temperature(frame)
        
        temperature = scale(point_val)

        return temperature
        
    
class VideoFrame(tk.Frame):

    def __init__(self, master=None, stream=None):
        tk.Frame.__init__(self, master)
        top = self.winfo_toplevel()

        self.selected_color = tk.StringVar()

        self.current_temp = tk.StringVar()
        self.current_temp.set("Temperature: 0")
        self.init_temp_label()
        self.init_color_select()

        self.stream         = stream
        
        self.init_panel()

        self.video_thread   = threading.Thread(target=self.video_loop)
        self.stop_video     = threading.Event()
        self.video_thread.start()
        
        
        self.init_calibration_frame()

        
    def init_color_select(self):
        colors =  list(Filters.cv_colors.keys()).copy()

        self.selected_color.set('None')
        self.color_select = tk.OptionMenu(self, self.selected_color, *colors) 
        
        self.color_select.grid(row=0, column=0)
        
    def init_temp_label(self):
        self.temp_label = tk.Label(self, textvariable=self.current_temp)
        self.temp_label.grid(row=1, column=0)
    
    def init_panel(self):
        self.panel = tk.Label(self, anchor=tk.NW)
        self.panel.grid(row=2, column=0)

        # Bind click to --> change temperature
        self.panel.bind('<Button-1>', self.pick_temperature)
        self.panel.bind('<Key>', self.key_press_handler)
        self.panel.bind('<Enter>', self.focus_panel)

    def init_calibration_frame(self):
        self.calibration_frame = CalibrationFrame(self)        
        self.calibration_frame.grid(row=3, column=0)
    
    def focus_panel(self, event):
        self.panel.focus_set()

    def key_press_handler(self, event):
        char = event.char.lower()
        fmap = {
            'l':partial(self.select_temp_panel1, x=event.x, y=event.y),
            'h':partial(self.select_temp_panel2, x=event.x, y=event.y),
        }
        if char in fmap.keys():
            f=fmap[char]
            f()
 
    def select_temp_panel1(self, x, y):
        self.calibration_frame.select_panel1(x, y)

    def select_temp_panel2(self, x, y):
        self.calibration_frame.select_panel2(x, y)

    def update_temperature(self, temperature):
        self.current_temp.set("Temperature: {:2.1f}".format(temperature))
    
    def get_temperature(self, frame, point):
        return self.calibration_frame.get_temperature(frame, point)

    def pick_temperature(self, event):
        temp = self.get_temperature(self.stream.current_frame, (event.x, event.y))
        self.update_temperature(temp)
        return temp
        
    def update_panel(self, frametk):
        self.panel.imgtk = frametk
        self.panel.configure(image=self.panel.imgtk)
    
    def resize_frame(self, frame):
        return frame

    def filter_frame(self, frame):
        if self.selected_color.get() != 'None':
            frame = Filters.color_filter(frame, self.selected_color.get())
        
        frame = Filters.face_detection(frame)
        frame = Filters.blur(frame)

        if self.calibration_frame.panel1_coords[0] != -1:
            frame = Filters.draw_x(frame, self.calibration_frame.panel1_coords)

        if self.calibration_frame.panel2_coords[0] != -1:
            frame = Filters.draw_x(frame, self.calibration_frame.panel2_coords)


        return frame
    
    def video_loop(self):

        while True:

            if self.stop_video.is_set():
                return 1                
                
            frame       = self.stream.read()
            original    = frame.copy()

            # Change frame to uint8 because uint16 isn't supported by PIL
            cv.normalize(frame, frame, 0, 255, cv.NORM_MINMAX)
            frame       = frame.astype(np.uint8) 
            frame       = self.filter_frame(frame)
            frame       = self.resize_frame(frame)

            # Convert to tkinter frame
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            
            # Display it
            self.update_panel(frame)
            
            time.sleep(1/Setup.VIDEO_FPS)

        return 1

    def on_close(self):
        self.stream.stop()
        self.stop_video.set()

    

class ReportFrame(tk.Frame):
    
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        top = self.winfo_toplevel()
        self.current_persons = []
        self.urgent_persons  = []
        
        self.init_current_list()
        self.init_urgent_list()
    
    def init_current_list(self):
        self.current_label = tk.Label(self, text="In-Frame report:")
        self.current_label.grid(row=0, column=0)
        self.current_list = tk.Text(self, height=10, width=15)
        self.current_list.grid(row=1, column=0)

    def init_urgent_list(self):
        self.urgent_label = tk.Label(self, text="Urgent report:")
        self.urgent_label.grid(row=2, column=0)
        self.urgent_list = tk.Text(self, height=10, width=15)
        self.urgent_list.grid(row=3, column=0)

    def add_person(self, person, target='current'):
        target = target.lower()
        assert target in ['current', 'urgent']

        if person.temperature >= Setup.TEMP_THRESHOLD:
            target = 'urgent'

        message = "{} ({:2.1f} C)".format(person.name, person.temperature)
        message += "\n"
        if target == 'current':
            self.current_persons.append(person)
            widget = self.current_list
        else:
            self.urgent_persons.append(person)
            widget = self.urgent_list

        ix_before = widget.index(tk.END)
        widget.insert(tk.END, message)
        ix_after  = widget.index(tk.END)
        widget.tag_add(person.name, ix_before, ix_after)
            
    def remove_person(self, person, target='current'):
        assert target.lower() in ['current', 'urgent']

        if target == 'current':
            widget = self.current_list
        else:
            widget = self.urgent_list   
        
        widget.tag_delete(person.name)
        


main = tk.Tk()
main.geometry("1200x800")
main.wm_title('Temperature check')

# All those classes should have a on_close method
modules_to_close = []

# Add video frame
video_stream = capture.PipeStream(Setup.VIDEO_PIPE)
video_frame = VideoFrame(main, stream=video_stream)
video_frame.grid(row=0, column=0, padx=10, pady=10)
modules_to_close.append(video_frame)

# Add report frame
report_frame = ReportFrame(main)
report_frame.grid(row=0, column=1, padx=10, pady=10)
for person in [Person(37), Person(38), Person(39), Person(36)]:
    report_frame.add_person(person)


def on_close():

    for module in modules_to_close:
        module.on_close()

    main.destroy()

main.protocol("WM_DELETE_WINDOW", on_close)
        

main.mainloop()
