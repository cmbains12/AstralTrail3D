from abc import ABC, abstractmethod
import numpy as np


class GameState(ABC):
    pass


class PlayState(GameState):
    def __init__(self, state_config):
        self.configuration = state_config
        self.models = {}
        self.square_count = 0
        self.triangle_count = 0

    def configure_scene(self):
        if self.configuration == 'test':
            self.models = {
                'test-squares': [],
                'test-triangles': []
            }
            self.configure_test_squares(grid=5, sep=0.2)
            self.configure_test_triangles(grid=5, sep=0.2)
            return self.models, self.square_count, self.triangle_count
        else:
            raise ValueError(f'Unknown PlayState configuration: {self.configuration}')
        

    def configure_test_squares(self, grid, sep):
        squares = []

        for i in range(grid):
            for j in range(grid):
                posx = i * sep + sep / 2
                posy = j * sep + sep / 2
                square = np.eye(4, dtype=np.float32)
                square[0, 3] = posx
                square[1, 3] = posy

                squares.append(square.T.flatten())

                self.square_count += 1

        self.models['test-squares'] = np.array(squares, dtype=np.float32)

    def configure_test_triangles(self, grid, sep):
        triangles = []

        for i in range(grid):
            for j in range(grid):
                posx = -i * sep - sep / 2
                posy = -j * sep - sep / 2
                triangle = np.eye(4, dtype=np.float32)
                triangle[0, 3] = posx
                triangle[1, 3] = posy

                triangles.append(triangle.T.flatten())

                self.triangle_count += 1

        self.models['test-triangles'] = np.array(triangles, dtype=np.float32)

