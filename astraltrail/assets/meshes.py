import numpy as np
from abc import ABC, abstractmethod

class Object(ABC):
    @property
    @abstractmethod
    def mesh(self):
        pass

class Cube(Object):
    @property
    def mesh(self):
        return np.array([self.vertices[i] for i in self.mesh_indices], dtype=np.float32)
    
    @property
    def vertices(self):
        return np.array([
            [-0.05, 0.05, 0.05],
            [-0.05, -0.05, 0.05],
            [0.05, -0.05, 0.05],
            [0.05, 0.05, 0.05],
            [0.05, 0.05, -0.05],
            [0.05, -0.05, -0.05],
            [-0.05, -0.05, -0.05],
            [-0.05, 0.05, -0.05]
        ], dtype=np.float32)
    
    @property
    def aabb(self) -> np.ndarray:
        return np.array([
            self.vertices[6], 
            self.vertices[3]
        ], dtype=np.float32)

    @property
    def mesh_indices(self):
        return np.array([
            0, 1, 2, 2, 3, 0,
            4, 5, 6, 6, 7, 4,
            7, 6, 1, 1, 0, 7,
            3, 2, 5, 5, 4, 3,
            7, 0, 3, 3, 4, 7,
            1, 6, 5, 5, 2, 1
        ], dtype=np.uint32)


class Square(Object):
    @property
    def mesh(self):
        return np.array([self.vertices[i] for i in self.mesh_indices], dtype=np.float32)
    
    @property
    def vertices(self):
        return np.array([
            [-0.05, 0.05, 0.0],
            [-0.05, -0.05, 0.0],
            [0.05, -0.05, 0.0],
            [0.05, 0.05, 0.0]
        ], dtype=np.float32)
    
    @property
    def aabb(self) -> np.ndarray:
        return np.array([
            self.vertices[1], 
            self.vertices[3]
        ], dtype=np.float32)

    @property
    def mesh_indices(self):
        return np.array([
            0, 1, 2, 
            2, 3, 0
        ], dtype=np.uint32)
    

class Triangle(Object):
    def __init__(self):
        pass

    @property
    def mesh(self) -> np.ndarray:
        return np.array([self.vertices[i] for i in self.mesh_indices], dtype=np.float32)
    
    @property
    def vertices(self) -> np.ndarray:
        return np.array([
            [0.0, 0.05, 0.0],
            [-0.05, -0.05, 0.0],
            [0.05, -0.05, 0.0]
        ], np.float32)
    
    @property
    def aabb(self) -> np.ndarray:
        return np.array([
            self.vertices[1], 
            [self.vertices[2][0], self.vertices[0][1]]
        ], dtypes=np.float32)

    @property
    def mesh_indices(self) -> np.ndarray:
        return np.array([
            0, 1, 2
        ], dtype=np.uint32)
    
class Pyramid(Object):
    def __init__(self):
        pass

    @property
    def mesh(self) -> np.ndarray:
        return np.array([self.vertices[i] for i in self.mesh_indices], dtype=np.float32)
    
    @property
    def vertices(self) -> np.ndarray:
        return np.array([
            [0.0, 0.05, 0.0],
            [-0.05, -0.05, -0.05],
            [0.05, -0.05, -0.05],
            [0.0, -0.05, 0.05]
        ], np.float32)
    
    @property
    def aabb(self) -> np.ndarray:
        return np.array([
            self.vertices[1], 
            [self.vertices[2][0], self.vertices[0][1]]
        ], dtypes=np.float32)

    @property
    def mesh_indices(self) -> np.ndarray:
        return np.array([
            0, 1, 2, 
            2, 3, 0,
            0, 3, 1,
            1, 2, 3
        ], dtype=np.uint32)