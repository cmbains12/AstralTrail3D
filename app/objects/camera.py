from objects.objects import Object

class Camera(Object):
    def __init__(self, fov=90, znear=0.1, zfar=10
    , **kwargs):
        super().__init__(**kwargs)
        self.fov = fov
        self.znear = znear
        self.zfar = zfar