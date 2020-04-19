import matplotlib.pyplot as plt
import threading
import os
import numpy as np 
from enum import Enum
from abc import ABC, abstractmethod
import webserver
import cv2 as cv
from video_filters import Filters

class CaptureMode(Enum):
    PIPESTREAM = 'pipe stream'
    LIVESTREAM = 'live stream'

############ Stream wrappers #############

class Stream(ABC):

    def __init__(self, camera):
        self.to_close = [] # List of things to apply .close() on them when closing the stream
        self.filters  = camera.filters
        self.current_frame = None

        self.camera = camera

        assert self.check_cam_compatibility(), "Camera {} is not compatible with {}".format(camera, self)


        # Do one read to get current frame
        self.read()
        self.heigth         = self.current_frame.shape[0]
        self.width          = self.current_frame.shape[1]

    def save_frame(self, filename, secure=False):
        if not secure and os.path.exists(filename):
            os.remove(filename)

        frame = self.read()
        plt.imsave(filename, frame)
        return filename

    def show_frame(self):
        frame = self.read()
        plt.matshow(frame)
        plt.show()

    def add_filter(self, filter_f):
        self.filters.append(filter_f)

    def close(self):
        pass

    def run_webstream(self, host='0.0.0.0', port=8686):
        server    = webserver.WebServerStream(self, host=host, port=port)
        ws_thread = threading.Thread(target=server.run)
        ws_thread.start()
        print("[Capture] Running webserver")
        return True

    def run_socketstream(self, host='0.0.0.0', port=8687):
        socket        = webserver.SocketStream(self, host=host, port=port)
        socket_thread = threading.Thread(target=socket.run)
        socket_thread.start()
        print("[Capture] Running socket stream")

        self.to_close.append(socket)
    
    def read(self, *args, **kwargs):
        frame = self._read(*args, **kwargs)
        if frame is None:
            print("Cant read from", self)
            return None
        self.current_frame = frame.copy()
        for f in self.filters:
            frame = f(frame)
        return frame

    def display(self):
        while True:
            frame = self.read()
            cv.imshow('Frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'): break

    def close(self):
        for proc in self.to_close:
            proc.close()

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

class WebcamStream(Stream):
    def __init__(self, camera):
        super().__init__(camera)

    def check_cam_compatibility(self):
        return CaptureMode.LIVESTREAM in self.camera.__class__.CAPTURE_MODES

    def _read(self):
        frame = self.camera.read()
        self.current_frame = frame.copy()
        return frame

class PipeStream(Stream):

    def __init__(self, camera, filename):

        self.filename       = filename
        super().__init__(camera) 

    def check_cam_compatibility(self):
        return CaptureMode.PIPESTREAM in self.camera.__class__.CAPTURE_MODES

    def _read(self):
        frame = self.camera.read_frame_file(self.filename)
        self.current_frame = frame.copy()
        return frame


############# Camera wrappers ###############

class Camera(ABC):
    
    def __init__(self):
        self.filters = []

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

class WebcamCamera(Camera):
    CAPTURE_MODES = [CaptureMode.LIVESTREAM]

    def __init__(self, cam_id=0):
        super().__init__()
        self.capture = cv.VideoCapture(cam_id)

    def read(self):
        ret, frame = self.capture.read()
        return frame

    def close(self):
        self.capture.release()

class PipedCamera(Camera):

    CAPTURE_MODES = [CaptureMode.PIPESTREAM]

    @abstractmethod
    def read_frame_file(self, filename):
        pass

class OpgalCamera(PipedCamera):
    
    HEIGHT = 288
    ROWS   = 384

    def __init__(self):
        super().__init__()
        self.filters.append(Filters.flip_horizontal)

    def read_frame_file(self, filename):
        fdump  = open(filename, 'r')

        offset = 64
        fdump.seek(offset)

        rows            = 288
        cols            = 384
        pixels_count    = rows*cols


        mat = None

        if fdump is not None:
            mat = np.fromfile(fdump, dtype=np.uint16, count=pixels_count)
            mat = np.reshape(mat, (rows, cols))

        return mat

if __name__ == "__main__":
    camera = WebcamCamera(0)
    stream = WebcamStream(camera)

    therm_cam = OpgalCamera()
    stream2 = PipeStream(therm_cam, '/opt/eyerop/bin/camera_out')

    stream.save_frame('rgbframe.png')
    stream2.save_frame('thermframe.png')


