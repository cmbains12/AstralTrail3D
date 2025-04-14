import pyglet
from pyglet.gl import GL_LINES, GL_POINTS, GL_TRIANGLES


from constants import KEY


class GameState:
    def __init__(self, window, game_funcs, domains, draw_batches):
        self.game_funcs = game_funcs
        self.domains = domains
        self.window = window
        self.draw_batches = draw_batches

        self.shader_program = self.game_funcs["shader_program"]

    def __repr__(self):
        return self.__class__.__name__
    def __str__(self):
        return self.__class__.__name__

    def parse_input(self, input):
        pass

    def update(self, delta_time, user_input):
        self.parse_input(user_input)

    def render(self, objects, type):
        if type not in ["Point", "Line", "Fragment"]:
            raise ValueError(f"Invalid type: {type}.")
        if type == "Line":
            for obj in objects:
                line_start_pos = obj.position
                line_vec = obj.scale.z * obj.orientation_z
                line_end_pos = obj.position + line_vec
                p1 = (line_start_pos.x, line_start_pos.y, line_start_pos.z)
                p2 = (line_end_pos.x, line_end_pos.y, line_end_pos.z)
                self.shader_program.vertex_list(2, GL_LINES,
                    batch=self.draw_batches["lines"],
                    vertices=('f',(p1[0], p1[1], p1[2], p2[0], p2[1], p2[2])),
                    colours=('Bn',(255, 0, 0, 255, 0, 255, 0, 255))
                )
        elif type == "Point":
            self.shader_program.vertex_list(1, GL_POINTS,
                batch=self.draw_batches["points"],
                vertices=('f',(-0.25, -0.20, 0.0)),
                colours=('Bn',(255, 255, 255, 255))
            )
        elif type == "Fragment":
            self.shader_program.vertex_list(3, GL_TRIANGLES,
                batch=self.draw_batches["fragments"],
                vertices=('f',(0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.5, 0.0, 0.0)),
                colours = ('Bn',(255, 0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 255))
            )   
        else:
            raise ValueError(f"Invalid type: {type}.")
        
                
        