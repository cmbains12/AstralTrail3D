import numpy as np
from abc import ABC, abstractmethod
import os


class Object(ABC):
    def __init__(self, obj_fp):
        self._vertices, self._faces, self._normals, self._texture_coords, self._v_count, self._f_count = import_object_file(obj_fp).values()
        self._mesh_indices, self._norm_indices, self._texture_indices = convert_faces_to_index_arrays(self._faces)
        self._tangents, self._bitangents = compute_tangents(self.mesh, self.mesh_normals, self.texture_coordinates)

    @property
    def mesh(self) -> np.ndarray:
        return np.array([self._vertices[i] for i in self._mesh_indices], dtype=np.float32)

    @property
    def mesh_normals(self) -> np.ndarray:
        return np.array([self._normals[i] for i in self._norm_indices], dtype=np.float32)

    @property
    def texture_coordinates(self) -> np.ndarray:
        try:
            return np.array([self._texture_coords[i] for i in self._texture_indices], dtype=np.float32)
        except:
            return None

    @property
    def vertices(self) -> np.ndarray:
        return self._vertices.copy()

    @property
    def normals(self) -> np.ndarray:
        return self._normals.copy()

    @property
    def aabb(self) -> np.ndarray:
        pass

    @property
    def mesh_indices(self) -> np.ndarray:
        return self._mesh_indices

    @property
    def norm_indices(self) -> np.ndarray:
        return self._norm_indices

    @property
    def texture_indices(self) -> np.ndarray:
        return self._texture_indices

'''
class Teapot(Object):
    def __init__(self):
        super().__init__(obj_fp='teapot.obj')
'''        

class Cube(Object):
    def __init__(self):
        super().__init__(obj_fp='cube.obj')
        

class Square(Object):
    def __init__(self):
        super().__init__(obj_fp='square.obj')


class Triangle(Object):
    def __init__(self):
        super().__init__(obj_fp='triangle.obj')
       

class Pyramid(Object):
    def __init__(self):
        super().__init__(obj_fp='pyramid.obj')

    
def import_object_file(file_name):
    base_path = os.path.dirname(__file__)
    full_path = os.path.join(base_path, 'objects', file_name)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f'OBJ file not found: {full_path}')
    
    vertices = []
    texture_coords = []
    normals = []
    faces = []

    face_count = 0
    vertex_count = 0

    with open(full_path) as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith('v '):
            vertices.append(list(map(float, line.strip().split()[1:])))
            vertex_count += 1
        elif line.startswith('vn '):
            normals.append(list(map(float, line.strip().split()[1:])))
        elif line.startswith('vt '):
            texture_coords.append(list(map(float, line.strip().split()[1:])))
        elif line.startswith('f '):
            face = []
            for v in line.strip().split()[1:]:
                if '/' in v:
                    parts = v.split('/')

                    v_index = int(parts[0]) - 1

                    if len(parts) == 2:
                        if len(normals) > 0:
                            vn_index = int(parts[1]) - 1
                            vt_index = None
                        elif len(texture_coords) > 0:
                            vt_index = int(parts[1]) - 1
                            vn_index = None
                        else:
                            raise ImportError(f'File: {file_name} does not contain valid data')

                    if len(parts) == 3:
                        if len(normals) > 0:
                            vn_index = int(parts[1]) - 1
                        else:
                            raise ImportError(f'File: {file_name} does not contain valid data')
                        
                        if len(texture_coords) > 0:
                            vt_index = int(parts[2]) - 1
                        else:
                            raise ImportError(f'File: {file_name} does not contain valid data')
                else:
                    v_index = int(v) - 1
                    vt_index = None
                    vn_index = None

                face.append((v_index, vn_index, vt_index))
            faces.append(face)
            face_count += 1

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

            new_faces.append([(v_index, norm_index, t_index) for v_index, _, t_index in face])

        faces = new_faces

    return {
        'vertices': np.array(vertices, dtype=np.float32),
        'faces': faces,
        'normals': np.array(normals, dtype=np.float32),
        'texture_coords': np.array(texture_coords, dtype=np.float32),
        'v_count': vertex_count,
        'f_count': face_count
    }
            
def convert_faces_to_index_arrays(faces):
    mesh_indices = []
    norm_indices = []
    texture_indices = []

    for face in faces:
        for item in face:
            if isinstance(item, tuple) and len(item) == 3:
                vert_index, norm_index, texture_index = item
            else:
                vert_index = item
                norm_index = 0
                texture_index = 0

            mesh_indices.append(vert_index)
            norm_indices.append(norm_index)
            texture_indices.append(texture_index)

    mesh_indices = np.array(mesh_indices, dtype=np.uint32) if mesh_indices[0] is not None else None
    norm_indices = np.array(norm_indices, dtype=np.uint32) if norm_indices[0] is not None else None
    texture_indices = np.array(texture_indices, dtype=np.uint32) if texture_indices[0] is not None else None

    return (
        mesh_indices,
        norm_indices,
        texture_indices
    )

def compute_tangents(vertices, normals, tex_coords):
    vertices = np.array(vertices, dtype=np.float32).reshape(-1, 3)
    tex_coords = np.array(tex_coords, dtype=np.float32).reshape(-1,2)

    tangents = np.zeros_like(vertices)
    bitangents = np.zeros_like(vertices)

    for i in range(0, len(vertices), 3):
        v0, v1, v2 = np.array(vertices[i:i+3])        

        uv0, uv1, uv2 = np.array(tex_coords[i:i+3])        

        delta_pos1 = v1 - v0
        delta_pos2 = v2 - v0
        deltauv1 = uv1 - uv0
        deltauv2 = uv2 - uv0

        r = (deltauv1[0] * deltauv2[1] - deltauv1[1] * deltauv2[0])
        if abs(r) < 1e-8:
            r = 1.0
        else: 
            r = 1.0 / r

        tangent = (delta_pos1 * deltauv2[1] - delta_pos2 * deltauv1[1]) * r
        bitangent = (delta_pos2 * deltauv1[0] - delta_pos1 * deltauv2[0]) * r

        for j in range(3):
            tangents[i + j] += tangent
            bitangents[i + j] += bitangent   

        tangents = np.array([t / np.linalg.norm(t) if np.linalg.norm(t) > 0 else t for t in tangents])
        bitangents = np.array([b / np.linalg.norm(b) if np.linalg.norm(b) > 0 else b for b in bitangents])

    return tangents.flatten(), bitangents.flatten()