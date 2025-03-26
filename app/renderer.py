import pygame

from constants import *
from gamestate import Gamestate
from matrices import Matrix, vector_matrix
from objects.object import Origin

class Renderer:
    def __init__(self, app, screen: pygame.Surface, gamestate: Gamestate):
        self._parent = app
        self._screen = screen
        self._gamestate = gamestate
        self._width, self._height = self.screen.get_size()
        self._view_transf = self.gamestate.camera.view_matrix()
        self._perspective_transf = self.gamestate.camera.perspective_matrix()
        self._screen_transf = self.gamestate.camera.screen_matrix()

    @property
    def parent(self):
        return self._parent
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def view_transf(self) -> Matrix:
        return self.gamestate.camera.view_matrix()
    
    @property
    def perspective_transf(self) -> Matrix:   
        return self.gamestate.camera.perspective_matrix()
    
    @property
    def screen_transf(self) -> Matrix:
        return self.gamestate.camera.screen_matrix()

    @property
    def screen(self) -> pygame.Surface:
        return self._screen
    
    @property
    def gamestate(self) -> Gamestate:
        return self._gamestate

    def render_frame(self, wirefr: bool=True, fragments: bool=True, points: bool=True, origin: bool=True):
        self.screen.fill(BLACK)

        draw_wireframes = wirefr
        draw_fragments = fragments
        draw_points = points
        draw_origin = origin

        object_list = self.gamestate.objects

        object_list.sort(key=lambda obj: (self.gamestate.camera.view_pos_matrix() * obj.position).magnitude, reverse=True)

        for obj in object_list:
            if isinstance(obj, Origin) and not draw_origin:
                continue

            self.render_object(obj, draw_wireframes, draw_fragments, draw_points)

    def render_object(self, obj, wirefr: bool, fragments: bool, points: bool):
        vertices = obj.vertices
        vertices_view = (self.view_transf * vertices).column_vectors()
        omit = False
        for vertex in vertices_view:
            if self.gamestate.camera.znear > vertex[2] or vertex[2] >self.gamestate.camera.zfar:
                omit = True
                break

        if omit:
            return
        
        vertices_view = vector_matrix(vertices_view)

        vertices_perspective = (self.perspective_transf * vertices_view).column_vectors()
        for vertex in vertices_perspective:
            vertex[0] /= vertex[3]
            vertex[1] /= vertex[3]
            vertex[3] = 1

        omit = True
        for vertex in vertices_perspective:
            if -1 < vertex[0] < 1 or -1 < vertex[1] < 1:
                omit = False
                break

        if omit:
            return
        
        vertices_screen = (self.screen_transf * vector_matrix(vertices_perspective)).column_vectors()
        screen_coords = [(int(vertex[0]), int(vertex[1])) for vertex in vertices_screen]

        if wirefr:
            edges = obj.edges
            for edge in edges:
                start = screen_coords[edge[0]]
                end = screen_coords[edge[1]]
                edge_colour = edge[2]
                pygame.draw.line(self.screen, edge_colour, start, end, 1)

        if points:
            points = obj.points
            for point in points:
                screen_coord = screen_coords[point[0]]
                point_colour = point[1]
                pygame.draw.circle(self.screen, point_colour, screen_coord, 3)

        if fragments:
            fragments = obj.fragments
            fragments.sort(key=lambda fragment: (self.gamestate.camera.view_pos_matrix() * fragment.position).magnitude, reverse=True)
            for fragment in fragments:
                self.render_fragment(fragment)

    def render_fragment(self, fragment):
        fragment_vertices = fragment.vertices

        fragment_vertices_view = self.view_transf * fragment_vertices

        fragment_vertices_view_list = fragment_vertices_view.column_vectors()

        vec1 = fragment_vertices_view_list[2] - fragment_vertices_view_list[1]
        vec2 = fragment_vertices_view_list[3] - fragment_vertices_view_list[1]

        normal = vec1.cross(vec2).normalized

        view_pos = fragment_vertices_view_list[0]

        dot_product = view_pos.dot(normal)

        if dot_product > 0:
            return
        
        fragment_vertices_perspective_raw = (self.perspective_transf * fragment_vertices_view).column_vectors()

        for vertex in fragment_vertices_perspective_raw:
            vertex[0] /= vertex[3]
            vertex[1] /= vertex[3]
            vertex[3] = 1
            
        fragment_vertices_perspective = vector_matrix(fragment_vertices_perspective_raw)

        draw_fragment = False
        for vertex in fragment_vertices_perspective.column_vectors():
            if -1 < vertex[0] < 1 and -1 < vertex[1] < 1:
                draw_fragment = True
                break

        

        if not draw_fragment:
            return
        
        fragment_vertices_screen = (self.screen_transf * fragment_vertices_perspective).column_vectors()

        screen_coords = []
        for i in range(4):
            coord = (int(fragment_vertices_screen[i].x), int(fragment_vertices_screen[i].y))
            screen_coords.append(coord)
        
        hue = []
        for elem in fragment.colour:
            hue_elem = elem * fragment.illumination
            hue.append(hue_elem)
        hue = tuple(hue)

        pygame.draw.polygon(self.screen, hue, screen_coords[1:])

        edges = fragment.edges

        for edge in edges:
            start = screen_coords[edge[0]]
            end = screen_coords[edge[1]]
            edge_colour = edge[2]
            pygame.draw.line(self.screen, edge_colour, start, end, 1)

        points = fragment.points

        for point in points:
            screen_coord = screen_coords[point[0]]
            point_colour = point[1]
            #pygame.draw.circle(self.screen, point_colour, screen_coord, 3)


        



            
            
                


                
            
            





        
