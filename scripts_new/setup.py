
class Setup:

    # Named pipe of the camera output (from ipccap)
    VIDEO_PIPE = '/opt/eyerop/bin/camera_out'           

    # FPS of the video in the gui
    VIDEO_FPS  = 30

    # Pickle calibration file --> map temperature to ThermAppMD pixels
    SCALE_FILE = './resources/temperature_scale.pck'
    
    # Temperature considered like sick
    TEMP_THRESHOLD = 38.0
    
    # Trained cascade model for face detection
    FD_HAAR_MODEL = "resources/classifiers/haarcascade_frontalface_default.xml"


