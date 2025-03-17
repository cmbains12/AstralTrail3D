import pygame
from pygame.event import Event
from pygame.key import ScancodeWrapper
from time import time
from math import tan

from gamestate import Gamestate
from matrices import Matrix, translation_matrix, scaling_matrix, vector_matrix, rotation_matrix
from vector import Vector
from objects import Object
from constants import *

pygame.init()

class AstralApp:
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FPS = 30
    def __init__(self):
        self.window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.gamestate = Gamestate()
        self.running = False

    def run(self):
        self.running = True
        last_time = time()
        while self.running:
            events,keys,mouse = self.get_user_input()
            duration = time() - last_time
            self.gamestate.update(events,keys,mouse,duration)
            self.render_objects()
            last_time = time()
            self.clock.tick(self.FPS)
        pygame.quit()

    def render_objects(self):
        objects = self.cull_z(self.gamestate.objects)
        #objects = self.sort_objects_z(objects)
        self.window.fill(BLACK)
        for obj in objects:
            self.render_object(obj)
        pygame.display.flip()

    def cull_z(self, object_list):
        culled_object_list = object_list.copy()

        for i in range(len(object_list)):
            position_vector = object_list[i].position
            position_view = self.transform_view(position_vector)
            if position_view.z < self.gamestate.camera.near_distance:
                culled_object_list.remove(object_list[i])

            sorted_culled_object_list = sorted(culled_object_list, key=lambda obj: self.transform_view(obj.position).z, reverse=True)

        return sorted_culled_object_list  

    def render_object(self,obj: Object):
        vertices = obj.vertices
        
        if vertices != None:
            fragments = obj.fragments
            edges = obj.edges
            points = obj.points

            vertices = self.transform_to_screen(vertices)
            vertex_list = vertices.column_vectors()
            render = True
            for vertex in vertex_list:
                if vertex.w == -1:
                    render = False
                    break

            if render:
                self.render_points(points, vertex_list)
                self.render_edges(edges, vertex_list)
                self.render_fragments(fragments, vertex_list)

    def render_points(self, points: list[tuple[int,tuple]], vertex_list: list[Vector]):
        for point in points:
            vertex_number, colour = point
            vertex = vertex_list[vertex_number]
            screen_coordinates = (int(round(vertex.x)), int(round(vertex.y)))
            pygame.draw.circle(self.window, colour, screen_coordinates, 2)

    def render_edges(self, edges: list[tuple[int,int,tuple]], vertex_list: list[Vector]):
        for edge in edges:
            start_vertex_number, end_vertex_number, colour = edge
            start_vertex = vertex_list[start_vertex_number]
            end_vertex = vertex_list[end_vertex_number]
            start_screen_coordinates = (start_vertex.x, start_vertex.y)
            end_screen_coordinates = (end_vertex.x, end_vertex.y)
            pygame.draw.line(self.window, colour, start_screen_coordinates, end_screen_coordinates)

    def render_fragments(self, fragments: list[tuple[int,int,int,tuple]], vertex_list: list[Vector]):
        for fragment in fragments:
            vertex1_number = fragment[0]
            vertex2_number = fragment[1]
            vertex3_number = fragment[2]  
            colour = fragment[3]

            vertex1 = vertex_list[vertex1_number]
            vertex2 = vertex_list[vertex2_number]
            vertex3 = vertex_list[vertex3_number]

            fragment_normal_view = (vertex2 - vertex1).cross(vertex3 - vertex1)
            if fragment_normal_view.z > 0:
                v1_coords = (vertex1.x, vertex1.y)
                v2_coords = (vertex2.x, vertex2.y)
                v3_coords = (vertex3.x, vertex3.y)
                pygame.draw.polygon(self.window, colour, [v1_coords, v2_coords, v3_coords])

    def transform_to_screen(self, vertices: Matrix) -> Matrix:
        vertices = self.transform_view(vertices)

        vertices, z_list = self.transform_perspective(vertices)
        vertices = self.transform_screen(vertices)
        for i in range(vertices.columns):
            vertices[3, i] = z_list[i]
        return vertices
    
    def transform_view(self, vertices: Matrix) -> Matrix:
        translation_vector = -1 * self.gamestate.camera.position
        translation_mtx = translation_matrix(translation_vector)
        angle_roll = -self.gamestate.camera.get_roll_z_angle()
        angle_yaw = -self.gamestate.camera.get_roll_y_angle()
        angle_pitch = -self.gamestate.camera.get_roll_x_angle()
        roll_mtx = rotation_matrix(ZAXIS, angle_roll)
        yaw_mtx = rotation_matrix(YAXIS, angle_yaw)
        _ = rotation_matrix(YAXIS, -angle_yaw)
        pitch_axis = (_ * XAXIS).normalized
        pitch_mtx = rotation_matrix(pitch_axis, angle_pitch)
        #transformation_mtx = pitch_mtx * yaw_mtx * roll_mtx * translation_mtx
        #vertices = transformation_mtx * vertices

        vertices = translation_mtx * vertices
        vertices = pitch_mtx * vertices
        vertices = yaw_mtx * vertices
        vertices = roll_mtx * vertices


        return vertices

    def transform_perspective(self, vertices: Matrix) -> Matrix:
        angle = self.gamestate.camera.field_of_view
        f = 1 / tan(angle / 2)
        aspect_ratio = self.WINDOW_WIDTH / self.WINDOW_HEIGHT
        zfar = self.gamestate.camera.far_distance
        znear = self.gamestate.camera.near_distance
        z = zfar / (zfar - znear)
        perspective_matrix = Matrix(
            [f,0,0,0],
            [0,f*aspect_ratio,0,0],
            [0,0,z,-z*znear],
            [0,0,1,0]
        )
        vertices = perspective_matrix * vertices
        vertices = vertices.column_vectors()
        z_list = []
        for vertex in vertices:
            z_list.append(vertex.w)
            if vertex.w < znear or vertex.w > zfar:
                vertex.w = -1
            else:
                vertex.x = vertex.x / vertex.w
                vertex.y = vertex.y / vertex.w
                vertex.w = 1
        vertices = vector_matrix(vertices)
        return vertices, z_list
    
    def transform_screen(self, vertices: Matrix) -> Matrix:
        displace = translation_matrix(Vector(self.WINDOW_WIDTH / 2, self.WINDOW_HEIGHT / 2, 1))
        scale = scaling_matrix(Vector(-self.WINDOW_WIDTH / 2, -self.WINDOW_HEIGHT / 2, 1))
        transformation_mtx = displace * scale
        vertices = transformation_mtx * vertices
        return vertices

    def sort_objects_z(self, objects: list[Object]) -> list[Object]:
        znear = self.gamestate.camera.near_distance
        positions_list = []
        for obj in objects:
            positions_list.append(obj.position)
        positions_mtx = vector_matrix(positions_list)
        positions_mtx_view = self.transform_view(positions_mtx)
        positions_list_view = positions_mtx_view.column_vectors()
        culled_objects = objects.copy()
        for i in range(len(culled_objects)):
            if positions_list_view[i].z < znear:
                culled_objects.remove(objects[i])
        
        sorted_culled_objects = sorted(culled_objects, key=lambda obj: -obj.position.z)        

        return sorted_culled_objects

    def get_user_input(self) -> tuple[list[Event],ScancodeWrapper,tuple[int,int]]:
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_rel()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

        return events, keys, mouse


if __name__ == "__main__":
    app = AstralApp()
    app.run()