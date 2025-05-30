
import pyglet
import pyglet.gl as gl

from rendering.rendering import Renderer
from gamestate import *

width = 1280
height = 720
caption = 'squares and triangles'


class AstralApp(pyglet.window.Window):
    def __init__(self, **kwargs):
        self.wind_width = kwargs.get('width', 800)
        self.wind_height = kwargs.get('height', 600)
        self.wind_caption = kwargs.get('caption', '')
        self.state_config = kwargs.get('config', '')
        config = gl.Config(double_buffer=True, dpeth_size=24)
        super().__init__(width, height, caption, config=config)
        play_state = PlayState(self.state_config)
        models, square_count, triangle_count = play_state.configure_scene()

        self.render = Renderer()
        self.render.configure_gl()
        self.render.setup_render_buffers(models, square_count, triangle_count)

        self.push_handlers(self.render.on_draw)

    def run(self):
        pyglet.app.run()

def main():
    astral_app = AstralApp(width=width, height=height, caption=caption, config='test')    
    astral_app.run()



if __name__=='__main__':
    main()
