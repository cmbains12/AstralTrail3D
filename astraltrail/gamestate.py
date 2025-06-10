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
        self.sprint = False

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

        pitch[1, 1], pitch[2, 2] = cp, cp
        pitch[1, 2], pitch[2, 1] = -sp, sp 

        roll[0, 0], roll[1, 1] = cr, cr
        roll[0, 1], roll[1, 0] = -sr, sr

        rot =  yaw @ pitch @ roll

        view = rot.T @ pos        

        return view       

    def move(self, direction, delta):
        speed = self.speed
        if self.sprint:
            speed *= 5.0
        distance = delta * speed
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
        self.counts = {
            'triangles': 0,
            'squares': 0,
            'cubes': 0,
            'pyramids': 0,
            'teapots': 0,
        }
        self.key_handler = key.KeyStateHandler()
        self.camera = Camera(
            pos=np.array([0.0, 0.0, -5.0], dtype=np.float32),
            aspect=window.wind_width / window.wind_height
        )
        _ = np.array([-0.35, -0.65, 0.45], dtype=np.float32)
        #self.light_direction = _ / np.linalg.norm(_)

        init_pos = np.array([35.0, 65.0, 45.0], dtype=np.float32)
        __ = np.cross(np.array([0.0, 1.0, 0.0], dtype=np.float32), init_pos)
        axis = np.cross(init_pos, __)
        axis = axis / np.linalg.norm(axis)

        self.light = {
            'position': np.array([35.0, 65.0, 45.0], dtype=np.float32),
            'pos_init': np.array([35.0, 65.0, 45.0], dtype=np.float32),
            'axis': axis,
            'rate': 1.0,
        }

        self.active = False
        self.window.set_exclusive_mouse(True)

    def configure_scene(self):
        if self.configuration['name'] == 'test':
            self.models = {
            }
            self.configure_test_cubes(grid=0, sep=0.2)
            self.configure_test_pyramids(grid=0, sep=0.2)
            self.configure_test_squares(grid=0, sep=0.2)
            self.configure_test_triangles(grid=0, sep=0.2)
            self.configure_test_teapots(grid=10, sep=10)
            
            return self.models, self.counts
        
        elif self.configuration['name'] == 'blockcraft':
            self.models = {}
            self.configure_test_cubes(grid=1, sep=0.2)

            return self.models, self.counts
        
        else:
            raise ValueError(f'Unknown PlayState configuration: {self.configuration}')
        
    def configure_test_chunk(self, chunk_config):
        if chunk_config == 'full':
            chunk_model = np.eye(4, dtype=np.float32)
            self.counts['chunks'] += 1

    def configure_test_teapots(self, grid, sep):
        teapots = []

        for i in range(grid):
            for j in range(grid):
                for k in range(grid):
                    posx = -i * sep - sep / 2
                    posy = j * sep + sep / 2
                    posz = k * sep + sep / 2

                    teacup = np.eye(4, dtype=np.float32)
                    teacup[0, 3] = posx
                    teacup[1, 3] = posy
                    teacup[2, 3] = posz

                    teapots.append(teacup.T.flatten())

                    self.counts['teapots'] += 1

        self.models['test-teapots'] = np.array(teapots, dtype=np.float32)

    def configure_test_cubes(self, grid, sep):
        cubes = []

        for i in range(grid):
            for j in range(grid):
                for k in range(grid):
                    posx = i * sep + sep / 2
                    posy = j * sep + sep / 2
                    posz = k * sep + sep / 2

                    cube = np.eye(4, dtype=np.float32)
                    cube[0, 3] = posx
                    cube[1, 3] = posy
                    cube[2, 3] = posz

                    cubes.append(cube.T.flatten())

                    self.counts['cubes'] += 1

        self.models['test-cubes'] = np.array(cubes, dtype=np.float32)

    def configure_test_pyramids(self, grid, sep):
        pyramids = []

        for i in range(grid):
            for j in range(grid):
                for k in range(grid):
                    posx = -i * sep - sep / 2
                    posy = -j * sep - sep / 2
                    posz = -k * sep - sep / 2
                    pyramid = np.eye(4, dtype=np.float32)
                    pyramid[0, 3] = posx
                    pyramid[1, 3] = posy
                    pyramid[2, 3] = posz

                    pyramids.append(pyramid.T.flatten())

                    self.counts['pyramids'] += 1

        self.models['test-pyramids'] = np.array(pyramids, dtype=np.float32)

    def configure_test_squares(self, grid, sep):
        squares = []

        for i in range(grid):
            for j in range(grid):
                for k in range(grid):
                    posx = i * sep + sep / 2
                    posy = j * sep + sep / 2
                    posz = k * sep + sep / 2

                    square = np.eye(4, dtype=np.float32)
                    square[0, 3] = posx
                    square[1, 3] = posy
                    square[2, 3] = posz

                    squares.append(square.T.flatten())

                    self.counts['squares'] += 1

        self.models['test-squares'] = np.array(squares, dtype=np.float32)

    def configure_test_triangles(self, grid, sep):
        triangles = []

        for i in range(grid):
            for j in range(grid):
                for k in range(grid):
                    posx = -i * sep - sep / 2
                    posy = -j * sep - sep / 2
                    posz = -k * sep - sep / 2
                    triangle = np.eye(4, dtype=np.float32)
                    triangle[0, 3] = posx
                    triangle[1, 3] = posy
                    triangle[2, 3] = posz

                    triangles.append(triangle.T.flatten())

                    self.counts['triangles'] += 1

        self.models['test-triangles'] = np.array(triangles, dtype=np.float32)


    def update(self, dt):
        self.handle_keys(dt)
        self.update_light(dt)

    def update_light(self, dt):
        old_pos = np.array([
            self.light['position'][0],
            self.light['position'][1],
            self.light['position'][2],
            1.0
        ], dtype=np.float32)

        axis = self.light['axis'].copy()
        angle = dt * self.light['rate']

        c, s = np.cos(angle), np.sin(angle)

        t = 1 - c

        x, y, z = axis

        matrix = np.array([
            [c + x * x * t, x * y * t - z * s, x * z * t + y * s, 0.0],
            [y * x * t + z * s, c + y * y * t, y * z * t - x * s, 0.0],
            [z * x * t - y * s, z * y * t + x * s, c + z * z * t, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        new_pos = matrix @ old_pos

        self.light['position'] = new_pos

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

        if self.key_handler[key.LSHIFT]:
            self.camera.sprint = True
        else:
            self.camera.sprint = False

    def on_mouse_motion(self, x, y, dx, dy):
        hori_sensitivity = 0.002
        verti_sensitivity = 0.002
        self.camera.yaw += dx * hori_sensitivity
        self.camera.pitch = max(
            min(
                self.camera.pitch + dy * verti_sensitivity, 
                np.radians(89.9)
            ), np.radians(-89.9)
        )




        


    




