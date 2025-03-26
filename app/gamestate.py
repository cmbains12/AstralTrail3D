
import pygame

from vector import Vector
from matrices import vector_matrix, default_orientation, random_orientation
from constants import *
from objects.camera import Camera
from objects.object import Object, Fragment, Origin
from objects.platonics import Cube

class Gamestate:
    def __init__(self, app):
        self.app = app
        self.objects: list[Object] = []
        self.disp_width: int = app.WINDOW_WIDTH
        self.disp_height: int = app.WINDOW_HEIGHT
        self.camera = self.initiate_camera()
        self.initiate_test_environment()
        self.initiate_test_objects()

    def initiate_camera(self):
        camera_position = Vector(0, 0, -5)
        camera_orientation = default_orientation()
        camera = Camera(
            shape=(self.disp_width, self.disp_height), 
            position = camera_position, 
            orientation = camera_orientation
        )

        return camera

    def initiate_test_environment(self):
        self.light_vector = Vector(1, -0.5, 0.5).normalized

        self.global_origin = Origin(position=Vector(0, 0, 0))
        self.objects.append(self.global_origin)

    def initiate_test_objects(self):
        #test_fragment = Fragment(position=Vector(0, 0, 0))
        #self.objects.append(test_fragment)

        for i in range(0, 10):
            for j in range(0, 10):
                orientation = random_orientation()
                test_cube = Cube(position=Vector(2+2*i, 0, 2+2*j), orientation=orientation)
                self.objects.append(test_cube)

        orientation0 = default_orientation()

        

        test_cube0 = Cube(position=Vector(-4,4,2), orientation=orientation0, scale=Vector(2, 2, 2))
        self.objects.append(test_cube0)


    def update(
            self, 
            events: list[pygame.event.Event], 
            keys: pygame.key.ScancodeWrapper, 
            mouse: tuple[int,int], 
            duration: float
        ):

        if keys[pygame.K_w]:
            self.camera.step('forward', duration)
        if keys[pygame.K_s]:
            self.camera.step('back', duration)
        if keys[pygame.K_a]:
            self.camera.step('left', duration)
        if keys[pygame.K_d]:
            self.camera.step('right', duration)
        if keys[pygame.K_SPACE]:
            self.camera.step('up', duration)
        if keys[pygame.K_LSHIFT]:
            self.camera.step('down', duration)
        if keys[pygame.K_q]:
            self.camera.look('left', duration)
        if keys[pygame.K_e]:
            self.camera.look('right', duration)
        if keys[pygame.K_r]:
            self.camera.look('up', duration)
        if keys[pygame.K_f]:
            self.camera.look('down', duration)
        if keys[pygame.K_z]:
            self.camera.reset_roll_z()
        if keys[pygame.K_x]:
            self.camera.reset_roll_x()
        if keys[pygame.K_c]:
            self.camera.reset_roll_y()

        for obj in self.objects:
            for fragment in obj.fragments:
                illumination = -self.light_vector.dot(fragment.normal)
                fragment.illumination = illumination



