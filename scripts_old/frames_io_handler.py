import matplotlib.pyplot as plt
import os
import numpy as np 

def read_bin(binFileName, cols, rows, dtype = np.uint16):
    fDump = open(binFileName, "r")
    fOffset = 64
    fDump.seek(fOffset)
    pixelCount = cols*rows
    if None != fDump:
        A = np.fromfile(fDump, dtype=dtype, count=pixelCount)
        A = np.reshape(A,(rows,cols))
        fDump.close()
        return A
    return None

def open_frame(frame_path):
    A = read_bin(frame_path, 384, 288)
    return A

def show_frame(frame_path):
    A = open_frame(frame_path)
    plt.matshow(A)
    plt.show()

def save_frame(frame_path, filename, secure=True, totype=None):
    if not secure and os.path.exists(filename):
        os.remove(filename)

    A = open_frame(frame_path)
    if totype:
        A = A.astype(totype)
    plt.imsave(filename, A)
    return filename

def get_frames(dir_path):
    files   = os.scandir(dir_path)
    frames  = [f.name for f in files if f.name.startswith('frame_')] 
    return frames

def get_frame_nb(frame_name):
    frame_nb = frame_name.split('_')[-1]
    try:
        return int(frame_nb)
    except:
        return False

def get_last_frame(dir_path):
    frames = get_frames(dir_path)
    frames.sort(key=lambda f_name: get_frame_nb(f_name))
    last = frames[-1]
    abs_path = os.path.join(dir_path, last)
    return abs_path


if __name__ == '__main__':
    frame = '/home/debian/opgal/dump/frame_9.bin'
    save_frame(frame, 'frame.png')

