import frames_io_handler as io

class PipeStream:

    def __init__(self, filename):
        self.filename       = filename
        self.current_frame  = None

        # Do one read to get current_frame
        self.read()
        self.height         = self.current_frame.shape[0]
        self.width          = self.current_frame.shape[1]
        
    def read(self):
        frame = io.open_frame(self.filename)
        self.current_frame = frame.copy()
        return frame

    def stop(self):
        return 1

if __name__ == "__main__":
    from setup import Setup
    import time
    import matplotlib.pyplot as plt

    #TEST
    stream = PipeStream(Setup.VIDEO_PIPE)
    for n in range(10):
        frame = stream.read()
        plt.matshow(frame)
        plt.show()
        time.sleep(.2)
        
        
