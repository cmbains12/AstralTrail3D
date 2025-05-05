import os
import sys
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from cube import Cube

def test_cube_model_matrix_identity():
    cube = Cube("test_cube")
    expected = np.identity(4, dtype=np.float32).flatten()
    actual = cube.model_matrix
    assert np.allclose(actual, expected)

def test_cube_vertices_shape():
    cube = Cube("test_cube")
    vertices = cube.vertices
    assert vertices.shape == (9, 3)

def test_cube_normals_unit_vectors():
    cube = Cube("test_cube")
    normals = cube.normals.reshape(-1, 3)
    magnitudes = np.linalg.norm(normals, axis=1)
    assert np.allclose(magnitudes, 1.0)
