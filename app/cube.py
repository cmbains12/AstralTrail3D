import numpy as np

class Cube:
    vertex0 = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
    vertex1 = np.array([-1.0, 1.0, 1.0, 1.0], dtype=np.float32)
    vertex2 = np.array([-1.0, -1.0, 1.0, 1.0], dtype=np.float32)
    vertex3 = np.array([1.0, -1.0, 1.0, 1.0], dtype=np.float32)
    vertex4 = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
    vertex5 = np.array([1.0, 1.0, -1.0, 1.0], dtype=np.float32)
    vertex6 = np.array([1.0, -1.0, -1.0, 1.0], dtype=np.float32)
    vertex7 = np.array([-1.0, -1.0, -1.0, 1.0], dtype=np.float32)
    vertex8 = np.array([-1.0, 1.0, -1.0, 1.0], dtype=np.float32)

    _vertices = np.array([vertex0,
        vertex1, vertex2, vertex3, vertex4,
        vertex5, vertex6, vertex7, vertex8
    ], dtype=np.float32)

    
    def __init__(self, id, **kwargs):
        self.id = id
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.orientation_x = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        self.orientation_y = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.orientation_z = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        self.orientation = np.array([
            self.orientation_x, 
            self.orientation_y, 
            self.orientation_z
        ], dtype=np.float32)
        self.scale = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        
        if 'position' in kwargs:
            self.position = kwargs['position']
        
        if 'orientation' in kwargs:
            self.orientation = kwargs['orientation']
            self.orientation_x = self.orientation[0]
            self.orientation_y = self.orientation[1]
            self.orientation_z = self.orientation[2]

        if 'scale' in kwargs:
            self.scale = kwargs['scale']

        params = [kwargs[param] for param in ['orientation_x', 'orientation_y', 'orientation_z'] if param in kwargs]
        if len(params) == 1:
            if 'orientation_z' in kwargs:
                self.orientation_z = kwargs['orientation_z']
                self.orientation_x = np.cross(np.array([0.0, 1.0, 0.0], dtype=np.float32), self.orientation_z)
                self.orientation_y = np.cross(self.orientation_z, self.orientation_x)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)
            elif 'orientation_x' in kwargs:
                self.orientation_x = kwargs['orientation_x']
                self.orientation_z = np.cross(self.orientation_x, np.array([0.0, 1.0, 0.0], dtype=np.float32))
                self.orientation_y = np.cross(self.orientation_z, self.orientation_x)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)
            elif 'orientation_y' in kwargs:
                self.orientation_y = kwargs['orientation_y']
                self.orientation_z = np.cross(np.array([1.0, 0.0, 0.0], dtype=np.float32), self.orientation_y)
                self.orientation_x = np.cross(self.orientation_y, self.orientation_z)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)
        elif len(params) == 2:
            if not 'orientation_y' in kwargs:
                self.orientation_y = np.cross(self.orientation_z, self.orientation_x)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)
            elif not 'orientation_z' in kwargs:
                self.orientation_z = np.cross(self.orientation_x, self.orientation_y)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)
            elif not 'orientation_x' in kwargs:
                self.orientation_x = np.cross(self.orientation_y, self.orientation_z)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)
        elif len(params) == 3:
            self.orientation_x = kwargs['orientation_x']
            self.orientation_y = kwargs['orientation_y']
            self.orientation_z = kwargs['orientation_z']
            self.orientation = np.array([
                self.orientation_x,
                self.orientation_y,
                self.orientation_z
            ], dtype=np.float32)
            
    @property
    def model_matrix(self):
        translation_matrix = np.array([
            [1.0, 0.0, 0.0, self.position[0]],
            [0.0, 1.0, 0.0, self.position[1]],
            [0.0, 0.0, 1.0, self.position[2]],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        orientation_matrix = np.array([
            [self.orientation_x[0], self.orientation_x[1], self.orientation_x[2], 0.0],
            [self.orientation_y[0], self.orientation_y[1], self.orientation_y[2], 0.0],
            [self.orientation_z[0], self.orientation_z[1], self.orientation_z[2], 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        scale_matrix = np.array([
            [self.scale[0], 0.0, 0.0, 0.0],
            [0.0, self.scale[1], 0.0, 0.0],
            [0.0, 0.0, self.scale[2], 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        return (translation_matrix @ orientation_matrix @ scale_matrix).T.flatten()
    
    @property
    def vertices(self):
        transformed = (self.model_matrix.reshape(4, 4).T @ self._vertices.T).T
        return transformed[:, :3]
        
    @property
    def normals(self):
        order = self.draw_order('fragments').reshape(-1, 3)
        vertices = [self.vertices[i] for i in order]
        normals = np.zeros_like(vertices, dtype=np.float32)
        for i in range(len(order)):
            vertex_indices = order[i]
            v0 = self.vertices[vertex_indices[0]]
            v1 = self.vertices[vertex_indices[1]]
            v2 = self.vertices[vertex_indices[2]]
            normal = np.cross(v1 - v0, v2 - v0)
            normal /= np.linalg.norm(normal)
            normals[i] = normal

        return normals.flatten()
    
    def vertices_indexed(self, draw_type='fragments'):
        vertices = self.vertices

        if draw_type == 'fragments':
            order = self.draw_order('fragments')
            index_vertices = np.array([[vertices[i] for i in order]])
        elif draw_type == 'lines':
            order = self.draw_order('lines')
            index_vertices = np.array([[vertices[i] for i in order]])

        return index_vertices.flatten()

        
    def draw_order(self, draw_type='fragments'):
        if draw_type == 'fragments':
            return np.array([
                1, 2, 3,
                1, 3, 4,
                5, 6, 7,
                5, 7, 8,
                8, 7, 2,
                8, 2, 1,
                4, 3, 6,
                4, 6, 5,
                8, 1, 4,
                8, 4, 5,
                2, 7, 6,
                2, 6, 3
            ], dtype=np.uint32)
        
        elif draw_type == 'lines':
            return np.array([
                1, 2,
                2, 3,
                3, 4,
                4, 1,
                5, 6,
                6, 7,
                7, 8,
                8, 5,
                1, 8,
                2, 7,
                3, 6,
                4, 5
            ], dtype=np.uint32)


            




