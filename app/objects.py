from math import cos, sin

from matrices import Matrix, default_orientation, vector_matrix, translation_matrix, rotation_matrix, scaling_matrix
from vector import Vector
from constants import *

class Object:
    _UNIT_FRAGMENTS = []
    _UNIT_EDGES = []
    _UNIT_POINTS = []
    _UNIT_VERTICES = None

    def __init__(self, position=Vector(0,0,0,1), orientation=default_orientation(), scale=1.0, step_speed=2.0, **kwargs):
        self._kwargs = kwargs
        self._position = position
        self._orientation = orientation
        self._scale = scale
        self._step_speed = step_speed
        print(position)
        
    @property
    def step_speed(self) -> int | float:
        return self._step_speed
    
    @step_speed.setter
    def step_speed(self, value: int | float):
        self._step_speed = value

    @property
    def position(self) -> Vector:
        pos = self._position.copy()
        return pos
    
    @position.setter
    def position(self, new_position: Vector):
        self._position = new_position
    
    @property
    def orientation(self) -> Matrix:
        orient = self._orientation.copy()
        return orient
    
    @orientation.setter
    def orientation(self, new_orientation: Matrix):
        self._orientation = new_orientation
    
    @property
    def orientation_vectors(self) -> list[Vector]:
        vector_list = (self._orientation.copy()).column_vectors()
        return vector_list
    
    @property
    def scale(self) -> float:
        return self._scale
    
    @scale.setter
    def scale(self, new_scale: int | float):
        self._scale = new_scale    
        
    @property
    def orientation_y(self) -> Vector:
        oriy = self.orientation_vectors[1].copy()
        return oriy
    
    @property
    def orientation_x(self) -> Vector:
        orix = self.orientation_vectors[0].copy()
        return orix
    
    @property
    def orientation_z(self) -> Vector:
        oriz = self.orientation_vectors[2].copy()
        return oriz
    
    @property
    def edges(self) -> list[int, int, tuple]:
        edges = self._UNIT_EDGES.copy()
        return edges
    
    @property
    def fragments(self) -> list[int, int, int, tuple]:
        fragments = self._UNIT_FRAGMENTS.copy()
        return fragments
    
    @property
    def points(self) -> list[int, tuple]:
        points = self._UNIT_POINTS.copy()
        return points
    
    @property
    def vertices(self) -> Matrix:
        if self._UNIT_VERTICES != None:
            vertices = self._UNIT_VERTICES.copy()
        else:
            return None
        vertices = self.transform_to_position_and_scale(vertices)
        return vertices
    
    def roll_z(self, angle: int | float):
        c = cos(angle)
        s = sin(angle)
        yaw_matrix = Matrix(
            [c,-s,0,0],
            [s,c,0,0],
            [0,0,1,0],
            [0,0,0,1]
        )
        new_orientation = yaw_matrix * self.orientation
        self._orientation = new_orientation
        
    def roll_y(self, angle: int | float):
        c = cos(angle)
        s = sin(angle)
        pitch_matrix = Matrix(
            [c,0,s,0],
            [0,1,0,0],
            [-s,0,c,0],
            [0,0,0,1]
        )

        new_orientation = pitch_matrix * self.orientation
        self._orientation = new_orientation

    def roll_x(self, angle: int | float):
        axis = self.orientation_x
        print(f'axis_{axis}')
        roll_matrix = rotation_matrix(axis, angle)

        new_orientation = roll_matrix * self.orientation
        self._orientation = new_orientation

    def reset_roll_x(self):
        angle = -self.get_roll_x_angle()
        axis = self.orientation_x
        rotation_mtx = rotation_matrix(axis, angle)
        self.orientation = rotation_mtx * self.orientation

    def reset_roll_y(self):
        angle = -self.get_roll_y_angle()
        axis = YAXIS
        rotation_mtx = rotation_matrix(axis, angle)
        self.orientation = rotation_mtx * self.orientation

    def reset_roll_z(self):
        angle = -self.get_roll_z_angle()
        axis = self.orientation_z
        rotation_mtx = rotation_matrix(axis, angle)
        self.orientation = rotation_mtx * self.orientation

    def step(self, direction, duration):
        distance = self.step_speed * duration
        z_direction = self.orientation_z.project_plane('xz')
        x_direction = self.orientation_x.project_plane('xz')
        if direction == 'forward':
            vector = z_direction * distance
        elif direction == 'back':
            vector = -1 * z_direction * distance
        elif direction == 'left':
            vector = x_direction * distance
        elif direction == 'right':
            vector = -1 * x_direction * distance
        elif direction == 'up':
            vector = YAXIS * distance
        elif direction == 'down':
            vector = -1 * YAXIS * distance

        movement_mtx = translation_matrix(vector)
        self.position = movement_mtx * self.position


    def transform_to_position_and_scale(self, vertices: Matrix) -> Matrix:
        roll_y_angle = self.get_roll_y_angle()
        roll_z_angle = self.get_roll_z_angle()
        roll_x_angle = self.get_roll_x_angle()


        translation_vector = self.position
        trans_mtx = translation_matrix(translation_vector)
        rot1_vec = Vector(0, 0, 1).cross(self.orientation_z)
        angle1 = Vector(0, 0, 1).angle(self.orientation_z)
        rot_mtx1 = rotation_matrix(rot1_vec, angle1)
        tempx = rot_mtx1 * Vector(1, 0, 0)
        rot2_vec = tempx.cross(self.orientation_x)
        angle2 = tempx.angle(self.orientation_x)
        rot_mtx2 = rotation_matrix(rot2_vec, angle2)
        scale_vec = Vector(self.scale, self.scale, self.scale)
        scale_mtx = scaling_matrix(scale_vec)

        vertices = scale_mtx * vertices
        vertices = rot_mtx1 * vertices
        vertices = rot_mtx2 * vertices
        vertices = trans_mtx * vertices

        return vertices
    
    def get_roll_x_angle(self) -> int | float:
        orientation_z = self.orientation.column_vectors()[2]
        orientation_z_projectedxz = orientation_z.project_plane('xz')

        angle = orientation_z.angle(orientation_z_projectedxz)
        if orientation_z.y >= 0:
            angle = -angle

        return angle

    def get_roll_y_angle(self) -> int | float:
        orientation_z = self.orientation.column_vectors()[2]
        orientation_z_projectedxz = orientation_z.project_plane('xz')

        angle = ZAXIS.angle(orientation_z_projectedxz)
        if orientation_z.x < 0:
            angle = -angle

        return angle

    def get_roll_z_angle(self) -> int | float:
        orientation_z = self.orientation_z
        orientation_z_projectedxz = orientation_z.project_plane('xz')
        axis1 = orientation_z.cross(orientation_z_projectedxz)
        angle1 = orientation_z.project_plane_angle('xz')
        mtx1 = rotation_matrix(axis1, angle1)
        tempx = mtx1 * self.orientation_x
        tempy = mtx1 * self.orientation_y

        rollz_angle = tempx.project_plane_angle('xz')

        x_y = tempx.y
        y_y = tempy.y

        if x_y >= 0 and y_y >=0:
            return rollz_angle
        elif x_y >=0 and y_y < 0:
            return PI / 2 - rollz_angle
        elif x_y < 0 and y_y >= 0:
            return -rollz_angle
        else:
            return -(PI / 2 - rollz_angle)

        


class Origin(Object):
    _UNIT_FRAGMENTS = []
    _UNIT_EDGES = [
        (0, 1, RED),
        (0, 2, BLUE),
        (0, 3, GREEN)
    ]
    _UNIT_POINTS = [(0, WHITE)]
    _UNIT_VERTICES = Matrix(
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1],
        [1,1,1,1]
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Fragment(Object):
    _UNIT_FRAGMENTS = [(0, 1, 2, WHITE)]
    _UNIT_EDGES = [
        (0, 1, BLACK),
        (1, 2, BLACK),
        (2, 0, BLACK)
    ]
    _UNIT_POINTS = []
    _UNIT_VERTICES = vector_matrix([
        Vector(0, 0.5, 0),
        Vector(-(3 ** 0.5) / 4, -0.25, 0),
        Vector((3 ** 0.5) / 4, -0.25, 0)
    ])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Camera(Object):
    def __init__(self, field_of_view: int | float=PI/2, near_distance: int | float=0.1, far_distance: int | float=500.0, look_speed=1.0, **kwargs):
        super().__init__(**kwargs)
        self._fov = field_of_view
        self._znear = near_distance
        self._zfar = far_distance
        self._look_speed = look_speed

    @property
    def field_of_view(self) -> float:
        return self._fov
    
    @field_of_view.setter
    def field_of_view(self, value: int | float):
        self._fov = value
    
    @property
    def near_distance(self) -> float:
        return self._znear
    
    @near_distance.setter
    def near_distance(self, value: int | float):
        self._znear = value

    @property
    def far_distance(self) -> float:
        return self._zfar
    
    @far_distance.setter
    def far_distance(self, value: int | float):
        self._zfar = value

    @property
    def look_speed(self) -> int | float:
        return self._look_speed

    def look(self, direction, duration):
        angle = self.look_speed * duration
        if direction == 'left':
            self.roll_y(angle)
        if direction == 'right':
            self.roll_y(-angle)
        if direction == 'up':
            self.roll_x(-angle)
        if direction == 'down':
            self.roll_x(angle)
