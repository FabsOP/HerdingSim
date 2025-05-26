import numpy as np
import math

def dot(v1, v2):
    """Calculate the dot product of two vectors."""
    return np.dot(v1, v2)

def magnitude(v):
    """Calculate the magnitude (length) of a vector."""
    return np.linalg.norm(v)

def ssq(v):
    """Calculate the squared magnitude of a vector."""
    return np.dot(v, v)

def unit(v):
    """Return the unit vector in the direction of v as a numpy array."""
    mag = magnitude(v)
    if mag == 0:
        return np.array([0, 0])  # Avoid division by zero
    return np.array(v) / mag

def vectorAngle(vector):
    """The angle of a vector [0,360] anti-clockwise from the positive x-axis [1,0]"""
    vx = vector[0]
    vy = vector[1]
    
    # Use atan2 which handles all quadrants correctly
    theta_radians = math.atan2(vy, vx)
    
    # Convert to degrees and use modulo to handle negative angles
    theta_degrees = (theta_radians * 180 / math.pi) % 360
    
    return int(theta_degrees)