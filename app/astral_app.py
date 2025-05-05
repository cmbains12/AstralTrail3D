import pyglet
import numpy as np

from constants import *
from renderer import Renderer
from camera import Camera
from cube import Cube

class AstralApp:
    def __init__(self):
        config = pyglet.gl.Config(
            double_buffer=True, 
            sample_buffers=1, 
            samples=4,
            depth_size=24,
        )

        self.window = pyglet.window.Window(
            CONFIG_DEFAULTS['window']['width'], 
            CONFIG_DEFAULTS['window']['height'], 
            "Astral App", 
            config=config
        )
        self.window.set_exclusive_mouse(True)

        self.renderer = Renderer(self.window)
        self.clock = pyglet.clock.get_default()
        self.clock.schedule_interval(
            self.update, 
            1.0 / CONFIG_DEFAULTS['window']['fps']
        )

        cam_pos = CONFIG_DEFAULTS['camera']['position']
        self.camera = Camera(
            position=cam_pos, 
            aspect=self.window.width / self.window.height,
            orientation_z=cam_pos/np.linalg.norm(cam_pos),
            fov=CONFIG_DEFAULTS['camera']['fov'],
            near_plane=CONFIG_DEFAULTS['camera']['near_plane'],
            far_plane=CONFIG_DEFAULTS['camera']['far_plane']
        )

        self.objects = {
            'cube1': Cube('cube1'),
            'cube2': Cube('cube2', position=np.array([1.5, 0.0, 0.0], dtype=np.float32)),
            'cube3': Cube('cube3', position=np.array([0.0, 1.5, 0.0], dtype=np.float32)),
            'cube4': Cube('cube4', position=np.array([0.0, 0.0, 1.5], dtype=np.float32)),
        }

        self.renderer.objects = self.objects

        self.keys = KEYS_INITIAL_STATE.copy()

        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.W:
                self.keys['key_w'] = True
            elif symbol == pyglet.window.key.A:
                self.keys['key_a'] = True
            elif symbol == pyglet.window.key.S:
                self.keys['key_s'] = True
            elif symbol == pyglet.window.key.D:
                self.keys['key_d'] = True
            elif symbol == pyglet.window.key.ESCAPE:
                self.keys['key_esc'] = True
            elif symbol == pyglet.window.key.SPACE:
                self.keys['key_space'] = True
            elif symbol == pyglet.window.key.LSHIFT:
                self.keys['key_lshift'] = True
            elif symbol == pyglet.window.key.Q:
                self.keys['key_q'] = True
            elif symbol == pyglet.window.key.E:
                self.keys['key_e'] = True

        @self.window.event
        def on_key_release(symbol, modifiers):
            if symbol == pyglet.window.key.W:
                self.keys['key_w'] = False
            elif symbol == pyglet.window.key.A:
                self.keys['key_a'] = False
            elif symbol == pyglet.window.key.S:
                self.keys['key_s'] = False
            elif symbol == pyglet.window.key.D:
                self.keys['key_d'] = False
            elif symbol == pyglet.window.key.ESCAPE:
                self.keys['key_esc'] = False
            elif symbol == pyglet.window.key.SPACE:
                self.keys['key_space'] = False
            elif symbol == pyglet.window.key.LSHIFT:
                self.keys['key_lshift'] = False
            elif symbol == pyglet.window.key.Q:
                self.keys['key_q'] = False
            elif symbol == pyglet.window.key.E:
                self.keys['key_e'] = False

        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            self.camera.look_around(dx, dy)

        @self.window.event
        def on_close():
            self.clock.unschedule(self.update)
            pyglet.app.exit()
            return pyglet.event.EVENT_HANDLED
        
        @self.window.event
        def on_draw():
            self.renderer.on_draw(self.objects)

    def update(self, dt):
        delta_time = dt

        if any([
            'key_w', 
            'key_a', 
            'key_s', 
            'key_d',
            'key_q',
            'key_e',
            'key_space',
            'key_lshift',
        ]) is True in self.keys.values():
            
            if self.keys['key_w']:
                self.camera.move_forward(dt)
            if self.keys['key_a']:
                self.camera.move_left(dt)
            if self.keys['key_s']:
                self.camera.move_backward(dt)
            if self.keys['key_d']:
                self.camera.move_right(dt)
            '''
            if self.keys['key_q']:
                self.camera.turn_left(dt)
            if self.keys['key_e']:
                self.camera.turn_right(dt)
            '''
            if self.keys['key_space']:
                self.camera.move_up(dt)
            if self.keys['key_lshift']:
                self.camera.move_down(dt)

        self.renderer.update_uniforms(
            view_matrix=self.camera.view_matrix,
            projection_matrix=self.camera.projection_matrix
        )

    def run(self):
        pyglet.app.run()


if __name__ == "__main__":
    app = AstralApp()
    app.run()
