
import pyglet
import pyglet.gl as gl

from rendering.rendering import Renderer
from gamestate import *

width = 1280
height = 720
caption = 'cubes and pyramids'
fps = 60.0

class AstralApp(pyglet.window.Window):
    def __init__(self, **kwargs):
        self.wind_width = kwargs.get('width', 800)
        self.wind_height = kwargs.get('height', 600)
        self.wind_caption = kwargs.get('caption', '')
        self.state_config = kwargs.get('config', '')
        config = gl.Config(double_buffer=True, depth_size=24)
        super().__init__(self.wind_width, self.wind_height, self.wind_caption, config=config)
        self.play_state = PlayState(self, self.state_config)
        models, cube_count, pyramid_count, square_count, triangle_count = self.play_state.configure_scene()

        self.render = Renderer(self)
        self.render.configure_gl()
        self.render.setup_render_buffers(models=models, cube_count=cube_count, pyramid_count=pyramid_count, square_count=square_count, triangle_count=triangle_count)

        self.render.update_proj(self.play_state.camera)
        self.push_handlers(
            self.render.on_draw,
            self.play_state.key_handler,
            self.play_state.on_mouse_motion
        )

        pyglet.clock.schedule_interval(self.play_state.update, 1 / fps)

    def run(self):
        pyglet.app.run()

    def on_close(self):
        super().on_close()

def main():
    astral_app = AstralApp(width=width, height=height, caption=caption, config='test')
    astral_app.run()


if __name__=='__main__':
    main()
