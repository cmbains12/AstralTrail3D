from abc import ABC, abstractmethod
import numpy as np
from pyglet.window import key

class Camera:
    def __init__(self, **kwargs):
        self.position = kwargs.get(
            'pos',
            np.array([0.0, 0.0, 0.0], dtype=np.float32)
        )
        self.yaw = np.radians(kwargs.get(
            'yaw',
            0.0
        ))
        self.pitch = np.radians(kwargs.get(
            'pitch',
            0.0
        ))
        self.roll = np.radians(kwargs.get(
            'roll',
            0.0
        ))
        self.fov = np.radians(kwargs.get(
            'fov',
            45.0
        ))
        self.near = kwargs.get(
            'near',
            0.01
        )
        self.far = kwargs.get(
            'far',
            1000
        )
        self.aspect = kwargs.get(
            'aspect',
            1.0
        )
        self.speed = kwargs.get(
            'speed',
            1.0
        )

    @property
    def proj(self):
        f = 1 / np.tan(self.fov / 2)
        z_factor = (self.near + self.far) / (self.near - self.far)
        z_offset = (2 * self.near * self.far) / (self.near - self.far)
        proj = np.zeros((4, 4), dtype=np.float32)
        proj[0, 0] = f / self.aspect
        proj[1, 1] = f
        proj[2, 2] = z_factor
        proj[2, 3] = z_offset        
        proj[3, 2] = -1.0

        return proj

    @property
    def view(self):
        yaw = np.eye(4, dtype=np.float32)
        pitch = np.eye(4, dtype=np.float32)
        roll = np.eye(4, dtype=np.float32)
        pos = np.eye(4, dtype=np.float32)

        pos[:3, 3] = -self.position

        cy, sy = np.cos(self.yaw + np.radians(180.0)), np.sin(self.yaw + np.radians(180.0))
        cp, sp = np.cos(self.pitch), np.sin(self.pitch)
        cr, sr = np.cos(self.roll), np.sin(self.roll)

        yaw[0, 0], yaw[2, 2] = cy, cy
        yaw[0, 2], yaw[2, 0] = -sy, sy  

        pitch[0, 0], pitch[2, 2] = cp, cp
        pitch[0, 2], pitch[2, 0] = sp, -sp 

        roll[0, 0], roll[2, 2] = cr, cr
        roll[0, 2], roll[2, 0] = -sr, sr

        rot = yaw.T @ pitch.T @ roll.T

        view = rot @ pos        

        return view       

    def move(self, direction, delta):
        distance = delta * self.speed
        cy, sy = np.cos(self.yaw), np.sin(self.yaw)
        forward = np.eye(3, dtype=np.float32)
        forward[0, 0], forward[2, 2] = cy, cy
        forward[0, 2], forward[2, 0] = -sy, sy
        forward = forward @ np.array([0.0, 0.0, 1.0], dtype=np.float32)

        abs_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        left = np.cross(abs_up, forward)

        if direction=='forward':
            self.position += distance * forward

        if direction=='back':
            self.position -= distance * forward

        if direction=='left':
            self.position += distance * left

        if direction=='right':
            self.position -= distance * left

        if direction=='climb':
            self.position += distance * abs_up

        if direction=='descend':
            self.position -= distance * abs_up




class GameState(ABC):
    pass

class PlayState(GameState):
    def __init__(self, window, state_config):
        self.window = window
        self.configuration = state_config
        self.models = {}
        self.square_count = 0
        self.triangle_count = 0
        self.key_handler = key.KeyStateHandler()
        self.camera = Camera(
            pos=np.array([0.0, 0.0, -5.0], dtype=np.float32),
            aspect=window.wind_width / window.wind_height
        )

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

    def update(self, dt):
        self.handle_keys(dt)

    def handle_keys(self, dt):
        if self.key_handler[key.ESCAPE]:
            self.window.on_close()

        if self.key_handler[key.W]:
            self.camera.move('forward', dt)
        if self.key_handler[key.A]:
            self.camera.move('left', dt)
        if self.key_handler[key.S]:
            self.camera.move('back', dt)
        if self.key_handler[key.D]:
            self.camera.move('right', dt)
        if self.key_handler[key.SPACE]:
            self.camera.move('climb', dt)
        if self.key_handler[key.LCTRL]:
            self.camera.move('descend', dt)
