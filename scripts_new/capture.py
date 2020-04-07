import matplotlib.pyplot as plt
import threading
import os
import numpy as np 
from enum import Enum
from abc import ABC, abstractmethod
import webserver
import cv2 as cv

class CaptureMode(Enum):
    PIPESTREAM = 'pipe stream'
    LIVESTREAM = 'live stream'

############ Stream wrappers #############

class Stream(ABC):

    def __init__(self, camera):
        self.camera = camera

        assert self.check_cam_compatibility(), "Camera {} is not compatible with {}".format(camera, self)

        self.current_frame = None

        # Do one read to get current frame
        self.read()
        self.heigth         = self.current_frame.shape[0]
        self.width          = self.current_frame.shape[1]

        self.to_close = [] # List of things to apply .close() on them when closing the stream

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

    def display(self):
        while True:
            frame = self.read()
            cv.imshow('Frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'): break

    def close(self):
        for proc in to_close:
            proc.close()

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

class WebcamStream(Stream):
    def __init__(self, camera):
        super().__init__(camera)

    def check_cam_compatibility(self):
        return CaptureMode.LIVESTREAM in self.camera.__class__.CAPTURE_MODES

    def read(self):
        frame = camera.read()
        self.current_frame = frame.copy()
        return frame

class PipeStream(Stream):

    def __init__(self, camera, filename):

        super().__init__(camera) 
        self.filename       = filename

    def check_cam_compatibility(self):
        return CaptureMode.PIPESTREAM in self.camera.__class__.CAPTURE_MODES

    def read(self):
        frame = camera.read_frame_file(self.filename)
        self.current_frame = frame.copy()
        return frame


############# Camera wrappers ###############

class Camera(ABC):

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

class WebcamCamera(Camera):
    CAPTURE_MODES = [CaptureMode.LIVESTREAM]

    def __init__(self, cam_id=0):
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

class OpgalThermapp(PipedCamera):
    
    HEIGHT = 288
    ROWS   = 384

    def __init__(self):
        pass

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
    stream.display()
