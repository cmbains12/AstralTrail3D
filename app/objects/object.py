from matrices import (
    Matrix, 
    default_orientation, 
    vector_matrix, 
    translation_matrix, 
    scaling_matrix,
    rotation_matrix
)
from vector import Vector
from constants import *


class Object:
    _UNIT_VERTICES: Matrix = vector_matrix([
        Vector(0, 0, 0, 1)
    ])
    _EDGES: list[tuple[int, int, tuple]] = []
    _POINTS: list[tuple[int, tuple]] = [
        (0, RED)
    ]
    _FRAGMENTS_BLUEPRINT: list[tuple[int, int, int, tuple]] = []
    
    def __init__(
            self, 
            position: Vector=Vector(), 
            orientation: Matrix=default_orientation(), 
            scale: Vector=Vector(1.0, 1.0, 1.0),
            colour: tuple[int, int, int]=WHITE
        ):
        self._position = position
        self._orientation = orientation
        self._scale = scale
        self._colour = colour
        self._fragments = self.initiate_fragments()


    @property
    def colour(self) -> tuple[int, int, int]:
        return self._colour

    @colour.setter
    def colour(self, new_colour: tuple[int, int, int]):
        self._colour = new_colour 

    @property
    def scale(self) -> Vector:
        return self._scale
    
    @scale.setter
    def scale(self, new_scale: Vector):
        self._scale = new_scale

    @property
    def position(self) -> Vector:
        return self._position.copy()
    
    @position.setter
    def position(self, new_position: Vector):
        self._position = new_position
    
    @property
    def orientation(self) -> Matrix:
        return self._orientation.copy()
    
    @orientation.setter
    def orientation(self, new_orientation: Matrix):
        self._orientation = new_orientation

    @property
    def orientation_list(self) -> list[Vector]:
        return self.orientation.column_vectors()
    
    @property
    def orientation_x(self) -> Vector:
        return self.orientation_list[0].copy()
    
    @property
    def orientation_y(self) -> Vector:
        return self.orientation_list[1].copy()
    
    @property
    def orientation_z(self) -> Vector:
        return self.orientation_list[2].copy()
    
    @property
    def edges(self) -> list[tuple[int, int, tuple]]:
        return self._EDGES.copy()
    
    @property
    def points(self) -> list[tuple[int, tuple]]:
        return self._POINTS.copy()
    
    @property
    def fragments(self) -> list['Fragment']:
        return self._fragments

    @property
    def vertices(self) -> Matrix:
        position_xfrm = self.position_transform()
        rotation_xfrm = self.rotation_transform()
        scale_xfrm = self.scale_transform()

        vertices =  scale_xfrm * self._UNIT_VERTICES.copy()
        vertices = rotation_xfrm * vertices
        vertices = position_xfrm * vertices

        return vertices
    
    def initiate_fragments(self) -> list['Fragment']:
        fragments = []
        blueprints = self._FRAGMENTS_BLUEPRINT.copy()
        for fragment_blueprint in blueprints:
            p1_index, p2_index, p3_index, colour = fragment_blueprint
            colour = self.colour
            vertices = self.vertices.column_vectors()
            p1 = vertices[p1_index]
            p2 = vertices[p2_index]
            p3 = vertices[p3_index]
            fragment = Fragment(points=[p1, p2, p3], colour=colour)
            fragments.append(fragment)

        return fragments
    
    def scale_transform(self) -> Matrix:
        scale_mtx = scaling_matrix(self.scale)

        return scale_mtx

    def position_transform(self) -> Matrix:
        transl_mtx = translation_matrix(self.position)

        return transl_mtx
    
    def reverse_position_transform(self) -> Matrix:
        transl_mtx = translation_matrix(-self.position)

        return transl_mtx
    
    def rotation_transform(self) -> Matrix:
        vector_list = self.orientation_list
        vector_list.append(Vector())
        rotation_mtx = vector_matrix(vector_list)
        rotation_mtx[3,0], rotation_mtx[3,1], rotation_mtx[3,2] = 0, 0, 0

        return rotation_mtx
    
    def reverse_rotation_transform(self) -> Matrix:
        rotation_mtx = self.rotation_transform().transpose()

        return rotation_mtx
    
    def step(self, direction: str | Vector, distance: int | float):
        if direction == 'forward':
            self.position += self.orientation_z * distance
        elif direction == 'back':
            self.position -= self.orientation_z * distance
        elif direction == 'left':
            self.position += self.orientation_x * distance
        elif direction == 'right':
            self.position -= self.orientation_x * distance
        elif direction == 'up':
            self.position += self.orientation_y * distance
        elif direction == 'down':
            self.position -= self.orientation_y * distance
        elif isinstance(direction, Vector):
            self.position += direction * distance
        else:
            raise ValueError(f'Invalid direction: {direction}')
        
    def look(self, direction: str | Vector, angle: int | float):
        if direction == 'left':
            rotation_mtx = rotation_matrix(YAXIS, angle)
        elif direction == 'right':
            rotation_mtx = rotation_matrix(YAXIS, -angle)
        elif direction == 'up':
            rotation_mtx = rotation_matrix(self.orientation_x, angle)
        elif direction == 'down':
            rotation_mtx = rotation_matrix(self.orientation_x, -angle)
        elif isinstance(direction, Vector):
            rotation_mtx = rotation_matrix(direction, angle)
        else:
            raise ValueError(f'Invalid direction: {direction}')
        
        self.orientation = rotation_mtx * self.orientation
    

class Fragment(Object):
    _UNIT_VERTICES: Matrix = vector_matrix([
        Vector(0, 0, 0),
        Vector(0, 0.5, 0),
        Vector(-0.25 * 3 ** 0.5, -0.25, 0),
        Vector(0.25 * 3 ** 0.5, -0.25, 0)
    ])
    _EDGES: list[tuple[int, int, tuple[int, int, int]]] = [
        (1, 2, GREY),
        (2, 3, GREY),
        (3, 1, GREY)
    ]

    def __init__(
            self, 
            points: list[Vector, Vector, Vector]=[], 
            position: Vector=Vector(), 
            orientation: Matrix=default_orientation(),
            illumination: float=1.0,
            **kwargs
        ):
        self._illumination = illumination

        if points != []:
            p1, p2, p3 = points

            posx = (p1.x + p2.x + p3.x) / 3
            posy = (p1.y + p2.y + p3.y) / 3
            posz = (p1.z + p2.z + p3.z) / 3
            position = Vector(posx, posy, posz)

            vec1 = p2 - p1
            vec2 = p3 - p1
            ori_z = vec1.cross(vec2).normalized
            ori_y = (p1 - position).normalized
            ori_x = ori_y.cross(ori_z).normalized
            orientation = vector_matrix([ori_x, ori_y, ori_z])

            transl_mtx = translation_matrix(-position)

            rotation_mtx = vector_matrix([ori_x, ori_y, ori_z, Vector()])
            rotation_mtx[3,0], rotation_mtx[3,1], rotation_mtx[3,2] = 0, 0, 0
            rotation_mtx = rotation_mtx.transpose()
            
            points_mtx = vector_matrix(points)
            points_mtx = transl_mtx * points_mtx
            points_mtx = rotation_mtx * points_mtx

            UNIT_VERTS = [Vector(0, 0, 0)]
            for point in points_mtx.column_vectors():
                UNIT_VERTS.append(point)
            self._UNIT_VERTICES = vector_matrix(UNIT_VERTS)
        super().__init__(position=position, orientation=orientation, **kwargs)

    @property
    def illumination(self) -> float:
        return self._illumination
    
    @illumination.setter
    def illumination(self, new_illumination: float):
        if new_illumination < 0:
            new_illumination = 0.1
        elif new_illumination > 1:
            new_illumination = 1.0
        
        self._illumination = new_illumination

    @property
    def normal(self) -> Vector:
        normal = self.orientation_z

        return normal

    @property
    def fragments(self) -> list['Fragment']:
        return [self]

class Origin(Object):
    _UNIT_VERTICES: Matrix = vector_matrix([
        Vector(0, 0, 0),
        Vector(1, 0, 0),
        Vector(0, 1, 0),
        Vector(0, 0, 1)
    ])
    _EDGES: list[tuple[int, int, tuple[int, int, int]]] = [
        (0, 1, RED),
        (0, 2, GREEN),
        (0, 3, BLUE)
    ]
    _POINTS: list[tuple[int, tuple[int, int, int]]] = [
        (0, WHITE)
    ]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        
    

    