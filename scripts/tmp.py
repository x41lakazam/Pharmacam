class VideosFrame(Module):
    
    def __init__(self):
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

        self.current_temp = tk.StringVar()
        self.current_temp.set("Temperature: 0")

        self.init_temp_label()

        self.calibration_frame = CalibrationFrame(self)        
        self.calibration_frame.grid(row=1, column=1)

    def init_temp_label(self):
        self.temp_label = tk.Label(self, textvariable=self.current_temp)
        self.temp_label.grid(row=1, column=0)

    def key_press_handler(self, event):
        # TODO: Only for temp widget
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
        return self.calibration_frame.get_temperature(frame, point)
    
class VideoFrame(Module):

    def __init__(self, master=None, stream=None):

        tk.Frame.__init__(self, master)
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

        self.selected_color.set('None')
        self.color_select = tk.OptionMenu(self, self.selected_color, *colors) 
        
        self.color_select.grid(row=0, column=0)
        
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
        self.master.key_press_handler(event)

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
        #if self.master.calibration_frame.panel1_coords[0] != -1:
        #    frame = Filters.draw_x(frame, self.master.calibration_frame.panel1_coords)
        #if self.master.calibration_frame.panel2_coords[0] != -1:
        #    frame = Filters.draw_x(frame, self.master.calibration_frame.panel2_coords)
        # TODO

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


