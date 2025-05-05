import os
import sys
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from camera import Camera

def test_camera_initial_position():
    cam = Camera(position=np.array([1.0, 2.0, 3.0], dtype=np.float32))
    assert np.allclose(cam.position, [1.0, 2.0, 3.0])

def test_camera_moves_forward():
    cam = Camera(position=np.array([0.0, 0.0, 0.0], dtype=np.float32), 
                 orientation_z=np.array([0.0, 0.0, 1.0], dtype=np.float32))
    cam.move_forward(1.0)
    assert np.allclose(cam.position, [0.0, 0.0, -1.0])

def test_camera_moves_right():
    cam = Camera(position=np.array([0.0, 0.0, 0.0], dtype=np.float32), 
                 orientation_x=np.array([1.0, 0.0, 0.0], dtype=np.float32))
    cam.move_right(1.0)
    assert np.allclose(cam.position, [1.0, 0.0, 0.0])

def test_view_matrix_translation():
    cam = Camera(position=np.array([5.0, 0.0, 0.0], dtype=np.float32))
    vm = cam.view_matrix.reshape(4, 4).T
    assert np.allclose(vm[:3, 3], [-5.0, 0.0, 0.0], atol=1e-5)
