from vector import Vector
from objects.camera import Camera
from objects.objects import Origin
from states.gamestate import GameState
from constants import KEY

class PlayState(GameState):
    def __init__(self, window, game_funcs, domains, draw_batches, **kwargs):
        super().__init__(window, game_funcs, domains, draw_batches, **kwargs)
        
        self.player_camera = Camera(position=Vector(2,2,-5))
        self.static_camera = Camera(position=Vector(2,4,-5), orientation_z=Vector(0,-4,5))
        self.physical_objects = []
        self.meta_objects = {
            'origin_global': Origin()
        }
        self.ambient_light_intensity = 0.05
        self.inf_light_direction = Vector(1,-4,1)

    def parse_input(self, input):
        if KEY.ESCAPE in input["keys"]:
            input["keys"].remove(KEY.ESCAPE)
            self.game_funcs["change_state"]("pause")

    def update(self, delta_time, user_input):
        super().update(delta_time, user_input)
        points, lines, fragments = self.decompose_objects()
        self.window.clear()
        if points:
            self.render(points, "Point")
        if lines:
            self.render(lines, "Line")
        if fragments:
            self.render(fragments, "Fragment")

    def decompose_objects(self) -> tuple[list, list, list]:
        points = []
        lines = []
        fragments = []

        for obj in self.physical_objects:
            pts, lns, frags = obj.decompose()
            points.extend(pts)
            lines.extend(lns)
            fragments.extend(frags)

        for obj in self.meta_objects.values():
            pts, lns, frags = obj.decompose()
            points.extend(pts)
            lines.extend(lns)
            fragments.extend(frags)

        return points, lines, fragments





