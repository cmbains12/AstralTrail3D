import numpy as np
from abc import ABC, abstractmethod

class Object(ABC):
    @property
    @abstractmethod
    def mesh(self):
        pass

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
        ], np.float32)

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
    def mesh_indices(self) -> np.ndarray:
        return np.array([
            0, 1, 2
        ], dtype=np.uint32)