import random

def generate_infinite_fractal_coords():
    center_x = random.uniform(-1.5, 0.3)
    center_y = random.uniform(-1.0, 1.0)
    
    zoom_size = random.uniform(0.005, 0.5)
    
    x_min = center_x - (zoom_size / 2)
    x_max = center_x + (zoom_size / 2)
    
    y_min = center_y - (zoom_size / 2)
    y_max = center_y + (zoom_size / 2)
    
    return x_min, x_max, y_min, y_max
