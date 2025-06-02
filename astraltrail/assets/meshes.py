import numpy as np
from abc import ABC, abstractmethod
import os


class Object(ABC):
    @property
    @abstractmethod
    def mesh(self):
        pass

class Cube(Object):
    def __init__(self):
        self._vertices, self._faces, self._normals = import_object_file('cube.obj').values()
        self._mesh_indices, self._norm_indices = convert_faces_to_index_arrays(self._faces)
        

    @property
    def mesh(self) -> np.ndarray:
        return np.array([self._vertices[i] for i in self._mesh_indices], dtype=np.float32)
    
    @property
    def mesh_normals(self) -> np.ndarray:
        return np.array([self._normals[i] for i in self._norm_indices], dtype=np.float32)
    
    @property
    def vertices(self) -> np.ndarray:
        return self._vertices.copy()
    
    @property
    def normals(self) -> np.ndarray:
        return self._normals.copy()
    
    @property
    def aabb(self) -> np.ndarray:
        return np.array([
            self.vertices[6], 
            self.vertices[3]
        ], dtype=np.float32)

    @property
    def mesh_indices(self) -> np.ndarray:
        return self._mesh_indices
    @property
    def norm_indices(self) -> np.ndarray:
        return self._norm_indices

class Square(Object):
    def __init__(self):
        self._vertices, self._faces, self._normals = import_object_file('square.obj').values()
        self._mesh_indices, self._norm_indices = convert_faces_to_index_arrays(self._faces)

    @property
    def mesh(self) -> np.ndarray:
        return np.array([self._vertices[i] for i in self._mesh_indices], dtype=np.float32)
    
    @property
    def mesh_normals(self) -> np.ndarray:
        return np.array([self._normals[i] for i in self._norm_indices], dtype=np.float32)
    
    @property
    def vertices(self) -> np.ndarray:
        return self._vertices.copy()
    
    @property
    def normals(self) -> np.ndarray:
        return self._normals.copy()
    
    @property
    def aabb(self) -> np.ndarray:
        return np.array([
            self.vertices[1], 
            [self.vertices[2][0], self.vertices[0][1]]
        ], dtype=np.float32)

    @property
    def mesh_indices(self) -> np.ndarray:
        return self._mesh_indices
    @property
    def norm_indices(self) -> np.ndarray:
        return self._norm_indices

class Triangle(Object):
    def __init__(self):
        self._vertices, self._faces, self._normals = import_object_file('triangle.obj').values()
        self._mesh_indices, self._norm_indices = convert_faces_to_index_arrays(self._faces)

    @property
    def mesh(self) -> np.ndarray:
        return np.array([self._vertices[i] for i in self._mesh_indices], dtype=np.float32)
    
    @property
    def mesh_normals(self) -> np.ndarray:
        return np.array([self._normals[i] for i in self._norm_indices], dtype=np.float32)
    
    @property
    def vertices(self) -> np.ndarray:
        return self._vertices.copy()
    
    @property
    def normals(self) -> np.ndarray:
        return self._normals.copy()
    
    @property
    def aabb(self) -> np.ndarray:
        return np.array([
            self.vertices[1], 
            [self.vertices[2][0], self.vertices[0][1]]
        ], dtype=np.float32)

    @property
    def mesh_indices(self) -> np.ndarray:
        return self._mesh_indices
    @property
    def norm_indices(self) -> np.ndarray:
        return self._norm_indices
       
class Pyramid(Object):
    def __init__(self):
        self._vertices, self._faces, self._normals = import_object_file('pyramid.obj').values()
        self._mesh_indices, self._norm_indices = convert_faces_to_index_arrays(self._faces)

    @property
    def mesh(self) -> np.ndarray:
        return np.array([self._vertices[i] for i in self._mesh_indices], dtype=np.float32)
    
    @property
    def mesh_normals(self) -> np.ndarray:
        return np.array([self._normals[i] for i in self._norm_indices], dtype=np.float32)
    
    @property
    def vertices(self) -> np.ndarray:
        return self._vertices.copy()
    
    @property
    def normals(self) -> np.ndarray:
        return self._normals.copy()
    
    @property
    def aabb(self) -> np.ndarray:
        return np.array([
            self.vertices[1], 
            [self.vertices[2][0], self.vertices[0][1]]
        ], dtype=np.float32)

    @property
    def mesh_indices(self) -> np.ndarray:
        return self._mesh_indices
    @property
    def norm_indices(self) -> np.ndarray:
        return self._norm_indices
    
def import_object_file(file_name):
    base_path = os.path.dirname(__file__)
    full_path = os.path.join(base_path, 'objects', file_name)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f'OBJ file not found: {full_path}')
    


    vertices = []
    normals = []
    faces = []

    with open(full_path) as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith('v '):
            vertices.append(list(map(float, line.strip().split()[1:])))
        elif line.startswith('vn '):
            normals.append(list(map(float, line.strip().split()[1:])))
        elif line.startswith('f '):
            face = []
            for v in line.strip().split()[1:]:
                if '/' in v:
                    parts = v.split('/')
                    v_index = int(parts[0]) - 1
                    vn_index = int(parts[1]) - 1 if len(parts) > 1 and parts[1] else None
                else:
                    v_index = int(v) - 1
                    vn_index = None
                face.append((v_index, vn_index))
            faces.append(face)

    if not normals:
        new_faces = []
        for face in faces:
            v0 = np.array(vertices[face[0][0]])
            v1 = np.array(vertices[face[1][0]])
            v2 = np.array(vertices[face[2][0]])

            l1 = v1 - v0
            l2 = v2 - v0

        

            norm = np.cross(l1, l2)
            norm = norm / np.linalg.norm(norm)

            norm_index = len(normals)
            normals.append(norm.tolist())

            new_faces.append([(v_index, norm_index) for v_index, _ in face])

        faces = new_faces


    return {
        'vertices': np.array(vertices, dtype=np.float32),
        'faces': faces,
        'normals': np.array(normals, dtype=np.float32)
    }
            
def convert_faces_to_index_arrays(faces):
    mesh_indices = []
    norm_indices = []

    for face in faces:
        for item in face:
            if isinstance(item, tuple) and len(item) == 2:
                vert_index, norm_index = item
            else:
                vert_index = item
                norm_index = 0
            mesh_indices.append(vert_index)
            norm_indices.append(norm_index)

    return (
        np.array(mesh_indices, dtype=np.uint32), 
        np.array(norm_indices, dtype=np.uint32)
    )