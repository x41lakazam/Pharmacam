import tkinter as tk
from functools import partial
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

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

    def close(self):
        return

class App(Module):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master 
        self.master.protocol("WM_DELETE_WINDOW", self.close) 

        self.modules = []


        self.video_dashboard = VideoDashboardFrame(self)
        self.modules.append(self.video_dashboard)

        self.video_dashboard.grid(row=0, column=1)

        # Add report frame
        #self.report_frame = ReportFrame(self)
        #self.report_frame.grid(row=1, column=0, padx=10, pady=10)
        #for person in [Person(37), Person(38), Person(39), Person(36)]:
        #    self.report_frame.add_person(person)

    def bindings(self):

        # Bind click to --> change temperature
        self.rgb_frame.panel.bind('<Button-1>', self.pick_temperature)

    def close(self):

        for module in self.modules:
            module.close()

        self.master.destroy()

class CalibrationFrame(Module):
     
    def __init__(self, master=None):
        super().__init__(master)
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
        val = self.panel1_textbox.get('1.0', tk.END)
        try:
            return float(val)
        except:
            return False

    @property
    def panel2_temperature(self):
        val = self.panel2_textbox.get('1.0', tk.END)
        try:
            return float(val)
        except:
            return False

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

    def __init__(self, master=None, stream=None, filter_feed=None, perma_filter_feed=None):
        
        self.filter_feed = filter_feed
        self.perma_filter_feed = perma_filter_feed

        super().__init__(master)
        top = self.winfo_toplevel()

        self.stream         = stream

        self.selected_color = tk.StringVar()

        self.init_color_select()
        
        self.init_panel()

        self.video_thread   = threading.Thread(target=self.video_loop)
        self.stop_video     = threading.Event()
        
        self.video_thread.start()

    def init_color_select(self):
        colors =  list(Filters.cv_colors.keys()).copy()

        self.selected_color.set('Jet')
        self.color_select = tk.OptionMenu(self, self.selected_color, *colors) 
        
        self.color_select.grid(row=0, column=0)
        
    def init_panel(self):
        self.panel = tk.Label(self, anchor=tk.NW, cursor='tcross')
        self.panel.grid(row=2, column=0)

        self.panel.bind('<Enter>', self.enter_handler)
        self.panel.bind('<Key>', self.key_press_handler)
        self.panel.bind('<Leave>', self.leave_handler)
        self.panel.bind('<Motion>', self.motion_handler)

    def init_ready_label(self):
        self.ready_text = tk.StringVar()
        self.ready_set.set("Not ready to measure temperature.")
        self.ready_label = tk.Label(self, textvariable=self.ready_text)
        self.ready_label.grid(row=3, column=0)

    def focus_panel(self):
        self.panel.focus_set()

    def enter_handler(self, event):
        self.focus_panel()

    def leave_handler(self, event):
        self.perma_filter_feed.remove_filter('zoom_glass')

    def motion_handler(self, event):
        self.master.widget_press_callback(event, self)
        zoomglass_filter = lambda f: Filters.zoom_glass(f, coords=(event.x, event.y))
        self.perma_filter_feed.add_filter(zoomglass_filter, name="zoom_glass", overwrite=True)

    def key_press_handler(self, event):
        self.master.widget_press_callback(event, self)

    def update_panel(self, frametk):
        self.panel.imgtk = frametk
        self.panel.configure(image=self.panel.imgtk)
    
    def resize_frame(self, frame):
        return frame

    def filter_frame(self, frame):
        
        # Convert frame to uint8 because uint16 isn't supported by PIL

        frame = Filters.convert_to_uint8(frame)

        # Apply face detection
        frame = Filters.face_detection(frame)

        # Blur frame
        #frame = Filters.blur(frame)
        
        # Apply colormap filter
        if self.selected_color.get() != 'None':
            frame = Filters.color_filter(frame, self.selected_color.get())

        # Take all the filters from the dashboard
        for feed in (self.filter_feed, self.perma_filter_feed):
            if feed:
                for f in feed.get_filters():
                    try:
                        frame = f(frame)
                    except Exception as e:
                        print("Failed to apply filter", f)
                        print(str(e))
                    #333 Above is better, but for debugging, lets remove the try


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

class FilterFeed():
    def __init__(self):
        self.filters = []
        self.filters_names = {}
    
    def add_filter(self, f, index=-1, name=None, overwrite=False):
        """
        TODO: DOESNT WORK
        """

        if name:
            if name in self.filters_names.keys():
                print("NAME:", name)
                print("Name is here:", self.filters_names)
                if overwrite: self.remove_filter(name)
                else: return False


        if index != -1:
            for filter_name, filter_ix in self.filters_names.items():
                if filter_ix >= index:
                    self.filters_names[filter_name] += 1


        self.filters.insert(index, f)
        if index <= 0:
            index = len(self.filters) - index
        self.filters_names[name] = index

    def create_filter(self, func, *args, **kwargs):
        """
        Create filter from func args and kwargs and append it to filters
        index: use index to insert filter at a special index
        """
        filt = lambda frame: func(frame, *args, **kwargs)
        return filt

    def remove_filter(self, name):
        """
        Can only be performed if filter has a name.
        TODO: DOESNT WORK
        """
        # Rearange
        for fname, fix in self.filters_names.items():
            print("Try, ix is", fix)
            print(self.filters_names)
            if fix >= fix and self.filters_names[fname] > 0:
                print("found !")
                self.filters_names[fname] -= 1
        if name not in self.filters_names:
            return False

        ix = self.filters_names[name]
        self.filters.pop(ix)
        del self.filters_names[name]
        # Rearrange

    def get_filters(self):
        return self.filters

    def clean(self):
        self.filters = []

    def update_filters(self, filters):
        self.clean()
        self.filters = [filters]

class VideoDashboardFrame(Module):
    
    def __init__(self, master):
        """
        EVERY PIXEL IS BASED ON THE RGB FRAME AND THEN CONVERTED TO THERM COORDS
        """
        self.runtime_filters = {'rgb': [], 'therm':[]}

        super().__init__(master)
        
        # Video 1 (RGB)

        rgb_camera               = capture.WebcamCamera(cam_id=0)
        self.rgb_stream          = capture.WebcamStream(rgb_camera)

        self.rgb_filters         = FilterFeed()
        self.rgb_pfilters        = FilterFeed()
        self.rgb_frame           = VideoFrame(self, 
                                                stream=self.rgb_stream, 
                                                filter_feed=self.rgb_filters, 
                                                perma_filter_feed=self.rgb_pfilters)

        self.rgb_frame.grid(row=0, column=0, padx=10, pady=10)

        # Video 2 (Therm)
        self.therm_filters       = FilterFeed()
        self.therm_pfilters      = FilterFeed()
        therm_camera             = capture.OpgalCamera()
        self.therm_stream        = capture.PipeStream(therm_camera, Setup.VIDEO_PIPE)

        self.therm_frame         = VideoFrame(self, stream=self.therm_stream,
                                                    filter_feed=self.therm_filters,
                                                    perma_filter_feed=self.therm_pfilters)
       
        self.therm_frame.grid(row=0, column=1, padx=10, pady=10)

        # Cursor of rgb on thermal
        self.corresponding_cursor = (-1,-1)
        
        # Temperature label
        self.current_temp = tk.StringVar()
        self.current_temp.set("Temperature: 0")

        self.temp_label = tk.Label(self, textvariable=self.current_temp)
        self.temp_label.grid(row=1, column=0)

        # Calibration frame
        self.calibration_frame = CalibrationFrame(self)        
        self.calibration_frame.grid(row=1, column=1)

        self.img_matching_pts = {'rgb':[None, None, None], 'therm':[None, None, None]}

        self.init_bindings()

    def init_bindings(self):
        self.rgb_frame.panel.bind('<Button-1>', self.pick_temperature)

    def close(self):
        self.rgb_stream.close()
        self.therm_stream.close()

    def select_matching_point(self, x, y, pic, ix):
        assert pic in ['rgb', 'therm']
        self.img_matching_pts[pic][ix] = (x,y)
        print("Clicked on matching point {}".format((x,y)))
        if pic == 'rgb':
            widget = self.rgb_frame
        else:
            widget = self.therm_frame

    def check_readiness(self):
        if None in self.img_matching_pts['rgb'] or None in self.img_matching_pts['therm']:
            return False
        if not self.calibration_frame.panel1_temperature or not self.calibration_frame.panel2_temperature:
            return False

        self.ready_text.set("Ready to measure temperature")
        return True

    def get_matching_points(self, widget):
        if widget == self.rgb_frame:
            return self.img_matching_pts['rgb'] 
        elif widget == self.therm_frame:
            return self.img_matching_pts['therm'] 
    
    def convert_point_rgb2therm(self, point):
        rgb_3points = self.img_matching_pts['rgb']
        therm_3points = self.img_matching_pts['therm']

        if None in rgb_3points or None in therm_3points:
            return None 

        converted_p = utils.camera_project_point(rgb_3points, therm_3points, point)
        return converted_p

    def update_mask_filters(self):
        self.rgb_filters.clean()

        # Matching point
        for matching_pt in self.img_matching_pts['rgb']:
            if not matching_pt:
                continue
            filt = self.rgb_filters.create_filter(Filters.draw_x, matching_pt,
                                            color=255, size=15, thickness=2)
            self.rgb_filters.add_filter(filt, index=0)

        self.therm_filters.clean()
        for matching_pt in self.img_matching_pts['therm']:
            if not matching_pt:
                continue
            filt = self.therm_filters.create_filter(Filters.draw_x, matching_pt,
                                            color=255, size=15, thickness=2)
            self.therm_filters.add_filter(filt, index=0)
        # Corresponding Cursor
        if self.corresponding_cursor:
            filt = self.therm_filters.create_filter(Filters.draw_x, self.corresponding_cursor, color=255, size=25, thickness=2)
            self.therm_filters.add_filter(filt, name="CorrespondingCursor")

        self.runtime_filters = {'rgb':[], 'therm':[]}


    def widget_press_callback(self, event, widget):

        if event.type == tk.EventType.Motion:
            self.panel_motion_callback(event, widget)

        elif event.type == tk.EventType.KeyPress:
            self.panel_press_callback(event, widget)

        else:
            #333
            print("Uncaught Event")
            print("Event:", type(event.type))
            print("Event name:", event.type)

        self.update_mask_filters()

    def panel_motion_callback(self, event, widget):
        """
        Draw the position of the rgb cursor on the therm frame
        """
        mouse_pos = (event.x, event.y)
        converted_pos = self.convert_point_rgb2therm(mouse_pos)
        if widget == self.rgb_frame:
            if converted_pos is not None:
                filt = lambda f: Filters.draw_x(f, converted_pos, color=255, size=13, thickness=3)
                filt.__name__ = "CorrespondingCursorDraw"
                self.runtime_filters['rgb'].append(filt)
                self.corresponding_cursor = tuple(converted_pos)


    def panel_press_callback(self, event, widget):
        char = event.char.lower()
        if widget == self.rgb_frame:
            fmap = {
                'd': partial(self.debugme),
                'l':partial(self.select_temp_panel1, x=event.x, y=event.y),
                'h':partial(self.select_temp_panel2, x=event.x, y=event.y),
                '1':partial(self.select_matching_point, x=event.x, y=event.y, pic='rgb', ix=0),
                '2':partial(self.select_matching_point, x=event.x, y=event.y, pic='rgb', ix=1),
                '3':partial(self.select_matching_point, x=event.x, y=event.y, pic='rgb', ix=2),
            }
        elif widget == self.therm_frame: 
            fmap = {
                '1':partial(self.select_matching_point, x=event.x, y=event.y, pic='therm', ix=0),
                '2':partial(self.select_matching_point, x=event.x, y=event.y, pic='therm', ix=1),
                '3':partial(self.select_matching_point, x=event.x, y=event.y, pic='therm', ix=2),
            }
        
        if char in fmap.keys():
            f=fmap[char]
            f()

    def debugme(self):
        print("FILTERS:", self.rgb_filters.filters)
        print("PFILTERS:", self.rgb_pfilters.filters_names)

    def select_temp_panel1(self, x,y):
        """
        PIXELS ARE RGB --> CONVERT THEM
        """
        therm_pt = self.convert_point_rgb2therm((x,y))
        self.calibration_frame.select_panel1(*therm_pt)

        therm_filt = self.therm_filters.create_filter(Filters.draw_x, therm_pt, color=255, thickness=3, size=3)
        rgb_filt = self.rgb_filters.create_filter(Filters.draw_x, (x,y), color=255, thickness=3, size=3)

        self.therm_pfilters.add_filter(therm_filt, name="panel1_coords", overwrite=True)
        self.rgb_pfilters.add_filter(rgb_filt, name="panel1_coords", overwrite=True)

    def select_temp_panel2(self, x,y):
        """
        PIXELS ARE RGB --> CONVERT THEM
        """
        therm_pt = self.convert_point_rgb2therm((x,y))
        self.calibration_frame.select_panel2(*therm_pt)

        therm_filt = self.therm_filters.create_filter(Filters.draw_x, therm_pt, color=255, thickness=3, size=3)
        rgb_filt = self.rgb_filters.create_filter(Filters.draw_x, (x,y), color=255, thickness=3, size=3)

        self.therm_pfilters.add_filter(therm_filt, name="panel2_coords", overwrite=True)
        self.rgb_pfilters.add_filter(rgb_filt, name="panel2_coords", overwrite=True)

    def get_temperature(self, frame, point):
        return self.calibration_frame.get_temperature(frame, point)

    def pick_temperature(self, event):
        """
        Pixel is related to rgb 
        """
        # Convert pixel
        point = (event.x, event.y)
        converted_point = self.convert_point_rgb2therm(point)
        temp = self.get_temperature(self.therm_stream.current_frame, converted_point)
        self.update_temperature(temp)
        return temp

    def update_temperature(self, temperature):
        self.current_temp.set("Temperature: {:2.1f}".format(temperature))

class ReportFrame(Module):
    
    def __init__(self, master):
        super().__init__(master)
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
root.geometry("1500x800")
root.wm_title('Temperature check')

main = App(root)
main.grid(row=0, column=0, padx=20, pady=20)

main.mainloop()
