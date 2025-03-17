from math import cos, sin
from typing import Union

from vector import Vector

class Matrix:
    def __init__(self, *components: list[int | float] | int):
        if components == ():
            components = (
                [1,0,0,0],
                [0,1,0,0],
                [0,0,1,0],
                [0,0,0,1]
            )
        elif isinstance(components[0], int):
            rows, cols = components
            components = []
            for i in range(rows):
                row = [0,] * cols
                components.append(row)
            components = tuple(components)

        self._components = list(components)
        
    @property
    def components(self) -> list[list[int | float]]:
        components = self._components.copy()
        return components
    
    @property
    def rows(self) -> int:
        rows = len(self._components)
        return rows
    
    @property
    def columns(self) -> int:
        columns = len(self._components[0])
        return columns

    def __getitem__(self, key: int | tuple[int,int]) -> int | float:
        if isinstance(key, (int, float)):
            row = self._components[row]

        if isinstance(key, tuple):
            row, col = key
            value = self._components[row][col]
            return value
        
    def __setitem__(self, key: int | tuple[int,int], value: int | float):
        if isinstance(key, int):
            self._components[key] = value

        if isinstance(key, tuple):
            row, col = key
            self._components[row][col] = value

    def __mul__(self, other: Union[Vector,'Matrix']) -> Union[Vector,'Matrix']:
        if isinstance(other, Matrix):
            rows = other.rows
            columns = other.columns
            matrix = Matrix(rows, columns)
            for i in range(self.rows):
                for j in range(other.columns):
                    sum = 0
                    for k in range(self.columns):
                        sum = sum + self[i, k] * other[k, j]
                    matrix[i, j] = sum

            return matrix
        
        if isinstance(other, Vector):
            vector = Vector()
            for i in range(len(other)):
                sum = 0
                for j in range(self.columns):
                    sum = sum + self[i, j] * other[j]
                vector[i] = sum

            return vector
        
        return NotImplemented
    
    def __rmul__(self, scalar: int | float) -> 'Matrix':
        if isinstance(scalar, (int, float)):
            rows = self.rows
            columns = self.columns
            matrix = Matrix(rows, columns)
            for i in range():
                for j in range():
                    matrix[i, j] = self[i, j] * scalar

            return matrix
        
        return NotImplemented

    def column_vectors(self) -> list[Vector]:
        vector_list = []
        for i in range(self.columns):
            vector = Vector()
            for j in range(self.rows):
                vector[j] = self[j, i]
            vector_list.append(vector)
        return vector_list

    def transpose(self) -> 'Matrix':
        matrix = Matrix()
        for i in range(self.rows):
            for j in range(self.columns):
                matrix[j,i] = self[i,j]
        return matrix
    
    def copy(self) -> 'Matrix':
        matrix = Matrix()
        for i in range(self.rows):
            for j in range(self.columns):
                matrix[i, j] = self[i, j]

        return matrix

def identity_matrix() -> 'Matrix':
    return Matrix(
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
    )

def vector_matrix(vector_list: list[Vector]) -> 'Matrix':
    columns = len(vector_list)
    rows = len(vector_list[0])
    matrix = Matrix(rows, columns)
    for i in range(len(vector_list)):
        for j in range(len(vector_list[0])):
            matrix[j,i] = vector_list[i][j]
    return matrix

def scaling_matrix(scaling_vector: Vector) -> 'Matrix':
    sx = scaling_vector.x
    sy = scaling_vector.y
    sz = scaling_vector.z
    sw = scaling_vector.w
    matrix = Matrix()
    matrix[0,0] = sx
    matrix[1,1] = sy
    matrix[2,2] = sz
    matrix[3,3] = sw
    return matrix

def rotation_matrix(axis, angle: int | float) -> 'Matrix':
    axis = axis.normalized
    c = cos(angle)
    s = sin(angle)
    t = (1 - c)
    x = axis.x
    y = axis.y
    z = axis.z
    matrix = Matrix(
        [x*x*t + c, x*y*t - z*s, x*z*t + y*s, 0],
        [y*x*t + z*s, y*y*t + c, y*z*t - x*s, 0],
        [z*x*t - y*s, z*y*t + x*s, z*z*t + c, 0],
        [0,0,0,1]
    )
    return matrix

def translation_matrix(translation_vector) -> 'Matrix':
    matrix = Matrix()
    for i in range(len(translation_vector)):
        matrix[i, 3] = translation_vector[i]
    return matrix

def default_orientation() -> 'Matrix':
    matrix = Matrix(
        [1,0,0],
        [0,1,0],
        [0,0,1],
        [1,1,1]
    )
    return matrix