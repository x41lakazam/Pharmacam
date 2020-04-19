from setup import Setup
import pickle

def get_temperature(value):
    scale = pickle.load(open(Setup.SCALE_FILE, 'rb'))
    return scale * value
