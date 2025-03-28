from objects.object import Object
from matrices import vector_matrix
from vector import Vector
from constants import *

class Cube(Object):
    _UNIT_VERTICES = vector_matrix([
        Vector(0, 0, 0), #centre
        Vector(-0.5, 0.5, 0.5), #front, top, left
        Vector(-0.5, -0.5, 0.5), #front, bottom, left
        Vector(0.5, -0.5, 0.5), #front, bottom, right
        Vector(0.5, 0.5, 0.5), #front, top, right
        Vector(0.5, 0.5, -0.5), #back, top, left
        Vector(0.5, -0.5, -0.5), #back, bottom, left
        Vector(-0.5, -0.5, -0.5), #back, bottom, right
        Vector(-0.5, 0.5, -0.5)  #back, top, right
    ])
    _EDGES = [
        (1, 2, GREY), (2, 3, GREY), (3, 4, GREY), (4, 1, GREY),
        (5, 6, GREY), (6, 7, GREY), (7, 8, GREY), (8, 5, GREY),
        (1, 8, GREY), (2, 7, GREY), (3, 6, GREY), (4, 5, GREY)
    ]
    _POINTS = [
        (0, RED)
    ]
    _FRAGMENTS_BLUEPRINT = [
        (1, 2, 4, WHITE), (2, 3, 4, WHITE), # front face
        (5, 6, 8, WHITE), (6, 7, 8, WHITE), # back face
        (8, 1, 5, WHITE), (1, 4, 5, WHITE), # top face
        (2, 7, 3, WHITE), (7, 6, 3, WHITE), # bottom face
        (4, 3, 5, WHITE), (3, 6, 5, WHITE), # right face
        (8, 7, 1, WHITE), (7, 2, 1, WHITE) # left face
    ]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
