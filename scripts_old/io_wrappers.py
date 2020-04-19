import matplotlib.pyplot as plt
import os
import numpy as np 
from enum import Enum
from abc import ABC, abstractmethod

class CaptureMode(Enum):
    PIPESTREAM = 'pipe stream'

# Stream types
class Stream(ABC):

    def __init__(self, camera):
        self.camera = camera
        assert self.check_cam_compatibility(), "Camera {} is not compatible with {}".format(camera, self)

    def close(self):
        pass

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)


class PipeStream(Stream):

    def __init__(self, camera, filename):

        super().__init__(camera)

        self.filename       = filename
        self.current_frame  = None

        # Do one read to get current frame
        self.read()
        self.heigth         = self.current_frame.shape[0]
        self.width          = self.current_frame.shape[1]

    def check_cam_compatibility(self):
        return CaptureMode.PIPESTREAM in self.camera.__class__.CAPTURE_MODES

    def read(self):
        frame = camera.read_frame_file(self.filename)
        self.current_frame  = frame.copy()
        return frame

# Camera wrappers
class Camera(ABC):
    pass

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


        if fdump is not None:
            mat = np.fromfile(fdump, dtype=np.uint16, count=pixels_counter)
            mat = np.reshape(mat, (rows, cols))

        return fdump

