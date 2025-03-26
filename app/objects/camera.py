from math import tan

from objects.object import Object
from constants import *
from matrices import Matrix, translation_matrix, vector_matrix
from vector import Vector

class Camera(Object):
    def __init__(
            self, 
            shape: tuple[int, int], 
            fov: int | float=PI/3, 
            znear: int | float=0.1, 
            zfar: int | float=500, 
            **kwargs):
        
        self._fov = fov
        self._znear = znear
        self._zfar = zfar
        self._shape = shape

        super().__init__(**kwargs)

    @property
    def fov(self):

        return self._fov
    
    @fov.setter
    def fov(self, new_fov):
        self._fov = new_fov

    @property
    def znear(self):

        return self._znear
    
    @znear.setter
    def znear(self, new_znear):
        self._znear = new_znear

    @property
    def zfar(self):

        return self._zfar
    
    @zfar.setter
    def zfar(self, new_zfar):
        self._zfar = new_zfar

    @property
    def shape(self):

        return self._shape
    
    def view_matrix(self) -> Matrix:
        orientation_mtx = self.view_orient_matrix()
        position_mtx = self.view_pos_matrix()
        view_matrix = orientation_mtx * position_mtx

        return view_matrix
    
    def view_pos_matrix(self) -> Matrix:
        view_position_matrix = translation_matrix(-self.position)

        return view_position_matrix
    
    def view_orient_matrix(self) -> Matrix:
        vector_list = self.orientation_list

        vector_list.append(Vector())
        orient_matrix = vector_matrix(vector_list)
        orient_matrix[3,0], orient_matrix[3,1], orient_matrix[3,2] = 0, 0, 0

        orient_matrix = orient_matrix.transpose()

        return orient_matrix
    
    def perspective_matrix(self) -> Matrix:
        width = self.shape[0]
        height = self.shape[1]
        ar = width / height
        f = 1 / tan(self.fov / 2)
        z_factor = self.zfar / (self.zfar - self.znear)

        perspective_matrix = Matrix(
            [f / ar, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, z_factor, -self.znear * z_factor],
            [0, 0, 1, 0]
        )

        return perspective_matrix
    
    def screen_matrix(self) -> Matrix:
        width = self.shape[0]
        height = self.shape[1]

        screen_matrix = Matrix(
            [-width/2, 0, 0, width/2],
            [0, -height/2, 0, height/2],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        )

        return screen_matrix
    
