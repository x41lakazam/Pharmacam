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

from video_filters import Filters
import capture
import utils
from setup import Setup
import face_detector
from face_detector import Person # Debug - remov

# Blocks

class Module(tk.Frame):

    def close(self):
        return

class App(Module):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master 
        self.master.protocol("WM_DELETE_WINDOW", self.close) 

        self.modules = []

        # Add video frame RGB 
        rgb_camera          = capture.WebcamCamera()
        rgb_stream          = capture.WebcamStream(rgb_camera)
        self.rgb_frame      = VideoFrame(self, stream=rgb_stream)
        self.rgb_frame.grid(row=0, column=0, padx=10, pady=10)
        self.modules.append(self.rgb_frame)

        therm_camera         = capture.OpgalCamera()
        therm_stream         = capture.PipeStream(therm_camera, Setup.VIDEO_PIPE)
        therm_stream.add_filter(Filters.flip_horizontal)
        self.therm_frame     = VideoFrame(self, stream=therm_stream)
        self.therm_frame.grid(row=0, column=1, padx=10, pady=10)
        self.modules.append(self.therm_frame)

        # Add report frame
        self.report_frame = ReportFrame(self)
        self.report_frame.grid(row=1, column=0, padx=10, pady=10)
        for person in [Person(37), Person(38), Person(39), Person(36)]:
            self.report_frame.add_person(person)


    def bindings(self):

        # Bind click to --> change temperature
        self.therm_frame.panel.bind('<Button-1>', self.pick_temperature)



    def close(self):

        for module in self.modules:
            module.close()

        self.master.destroy()

class CalibrationFrame(Module):
     
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
        
        temp_function = utils.calibrate_temperature(self.panel1_temperature,
                                                    self.panel2_temperature,
                                                    panel1_val,
                                                    panel2_val
                                            )
        return temp_function

    def get_temperature(self, frame, point):
        point_val = float(frame[point[1]][point[0]])
        scale     = self.calibrate_temperature(frame)
        
        temperature = scale(point_val)

        return temperature

class VideoFrame(Module):

    def __init__(self, master=None, stream=None):

        tk.Frame.__init__(self, master)
        top = self.winfo_toplevel()

        self.stream         = stream

        self.selected_color = tk.StringVar()

        self.current_temp = tk.StringVar()
        self.current_temp.set("Temperature: 0")

        self.init_temp_label()
        self.init_color_select()
        
        self.init_panel()

        self.video_thread   = threading.Thread(target=self.video_loop)
        self.stop_video     = threading.Event()
        
        self.video_thread.start()

        
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

        # Bind Enter to  --> Focus panel
        self.panel.bind('<Enter>', self.focus_panel)

        # Bind Key to  --> key_press_handler
        self.panel.bind('<Key>', self.key_press_handler)

    
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

    def pick_temperature(self, event):
        temp = self.get_temperature(self.stream.current_frame, (event.x, event.y))
        self.update_temperature(temp)
        return temp
 
    def select_temp_panel1(self, x, y):
        self.master.calibration_frame.select_panel1(x, y)

    def select_temp_panel2(self, x, y):
        self.master.calibration_frame.select_panel2(x, y)

    def update_temperature(self, temperature):
        self.current_temp.set("Temperature: {:2.1f}".format(temperature))
    
    def get_temperature(self, frame, point):
        return self.master.calibration_frame.get_temperature(frame, point)
    
    def update_panel(self, frametk):
        self.panel.imgtk = frametk
        self.panel.configure(image=self.panel.imgtk)
    
    def resize_frame(self, frame):
        return frame

    def filter_frame(self, frame):
        
        # Convert frame to uint8 because uint16 isn't supported by PIL

        frame = Filters.convert_to_uint8(frame)

        # Apply face detection
        #frame = Filters.face_detection(frame)

        # Blur frame
        #frame = Filters.blur(frame)
        
        # Apply colormap filter
        if self.selected_color.get() != 'None':
            frame = Filters.color_filter(frame, self.selected_color.get())
        
        # Draw X on selected points
        if self.master.calibration_frame.panel1_coords[0] != -1:
            frame = Filters.draw_x(frame, self.master.calibration_frame.panel1_coords)
        if self.master.calibration_frame.panel2_coords[0] != -1:
            frame = Filters.draw_x(frame, self.master.calibration_frame.panel2_coords)

        return frame
    
    def video_loop(self):

        while True:

            if self.stop_video.is_set():
                return 1                
                
            frame       = self.stream.read()    # Get frame
            original    = frame.copy()          # Copy it

            frame       = self.filter_frame(frame)
            frame       = self.resize_frame(frame)

            # Convert to tkinter frame
            tkframe = ImageTk.PhotoImage(Image.fromarray(frame))
            
            # Display it
            self.update_panel(tkframe)
           
            # Sleep a bit
            time.sleep(1/Setup.VIDEO_FPS)

        return 1

    def close(self):
        self.stream.close()
        self.stop_video.set()


class ReportFrame(Module):
    
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
        


root = tk.Tk()
root.geometry("1200x800")
root.wm_title('Temperature check')

main = App(root)
main.grid(row=0, column=0, padx=20, pady=20)

main.mainloop()
