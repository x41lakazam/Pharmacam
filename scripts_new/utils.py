from setup import Setup

def calibrate_temperature(temp1, temp2, px1_val, px2_val):
    """
    Returns a mapping function 
    temp1 & temp2 are the two real temperatures of the picked points
    px1_val & px2_val are the two pixels values
    """
    m = (temp1 - temp2) / (px1_val - px2_val) 

    p = self.panel1_temperature - m * px2_val
    temp_function = lambda dl: m*dl + p

    return temp_function
