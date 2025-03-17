
import pygame

from objects import Object, Origin, Camera, Fragment
from vector import Vector
from matrices import vector_matrix
from constants import *

class Gamestate:
    def __init__(self):
        self._objects = []
        self.global_origin = Origin()
        self._objects.append(self.global_origin)
        triangle = Fragment(position=Vector(0,0,3))
        self._objects.append(triangle)
        camera_z = Vector(0,0,1).normalized
        camera_x = YAXIS.cross(camera_z)
        camera_y = camera_z.cross(camera_x)
        camera_orientation = vector_matrix([camera_x, camera_y, camera_z])
        self._camera = Camera(position=Vector(0,0,-5), orientation=camera_orientation, field_of_view=PI/3)

    @property
    def objects(self) -> list[Object]:
        objs = self._objects.copy()
        return objs
    
    @property
    def camera(self) -> Camera:
        return self._camera

    def update(self, events: list[pygame.event.Event], keys: pygame.key.ScancodeWrapper, mouse: tuple[int,int], duration: float):
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
