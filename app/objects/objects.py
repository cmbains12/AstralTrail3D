from vector import Vector
from matrices import Matrix, default_orientation, vector_matrix


class Object:
    def __init__(
            self, 
            position=Vector(),
            orientation = None,
            orientation_x = Vector(1, 0, 0, 1),
            orientation_y = Vector(0, 1, 0, 1), 
            orientation_z = Vector(0, 0, 1, 1),
            scale = Vector(1, 1, 1, 1),
            id='none',
            name='none',
            **kwargs,
        ):        
        if not isinstance(id, str) and id is not None:
            raise TypeError("ID must be a string")

        if not isinstance(position, Vector):
            raise TypeError("Position must be a Vector")
        
        if not isinstance(scale, Vector):
            raise TypeError("Scale must be a Vector")
        
        if not isinstance(orientation_x, Vector):
            raise TypeError("Orientation X must be a Vector")
        
        if not isinstance(orientation_y, Vector):
            raise TypeError("Orientation Y must be a Vector")
        
        if not isinstance(orientation_z, Vector):
            raise TypeError("Orientation Z must be a Vector")
        
        if orientation:
            if not isinstance(orientation, Matrix):
                raise TypeError("Orientation must be a Matrix")
            if orientation_x or orientation_y or orientation_z:
                raise ValueError("Cannot define both orientation matrix and orientation vectors")

            orientation_vectors = orientation.column_vectors()
            orientation_x = orientation_vectors[0]
            orientation_y = orientation_vectors[1]
            orientation_z = orientation_vectors[2]

            xdoty = orientation_x.dot(orientation_y)
            ydotz = orientation_y.dot(orientation_z)
            zdotx = orientation_z.dot(orientation_x)

            if xdoty != 0 or ydotz != 0 or zdotx != 0:
                raise ValueError("Orientation vectors must be orthogonal")
            
        else:
            x_input = orientation_x != Vector(1, 0, 0, 1)
            y_input = orientation_y != Vector(0, 1, 0, 1)
            z_input = orientation_z != Vector(0, 0, 1, 1)

            if x_input and y_input and z_input:
                raise Exception("No more than two orientation vectors can be defined")
            
            elif z_input and x_input:
                x_dot_z = orientation_x.dot(orientation_z)
                if x_dot_z != 0:
                    raise ValueError("Orientation X and Z must be orthogonal")
                self._orientation_z = orientation_z.normalize()
                self._orientation_x = orientation_x.normalize()
                self._orientation_y = self._orientation_z.cross(self._orientation_x).normalize()
                self._orientation = vector_matrix([orientation_x, orientation_y, orientation_z])

            elif z_input and y_input:
                y_dot_z = orientation_y.dot(orientation_z)
                if y_dot_z != 0:
                    raise ValueError("Orientation Y and Z must be orthogonal")
                self._orientation_z = orientation_z.normalize()
                self._orientation_y = orientation_y.normalize()
                self._orientation_x = self._orientation_y.cross(self._orientation_z).normalize()
                self._orientation = vector_matrix([self._orientation_x, self._orientation_y, self._orientation_z])

            elif x_input and y_input:
                x_dot_y = orientation_x.dot(orientation_y)
                if x_dot_y != 0:
                    raise ValueError("Orientation X and Y must be orthogonal")
                self._orientation_x = orientation_x.normalize()
                self._orientation_y = orientation_y.normalize()
                self._orientation_z = self._orientation_x.cross(self._orientation_y)
                self._orientation_z = self._orientation_z.normalize()
                self._orientation = vector_matrix([
                    self._orientation_x, 
                    self._orientation_y, 
                    self._orientation_z
                ])
            elif z_input:
                self._orientation_z = orientation_z.normalize()
                self._orientation_x = Vector(0, 1, 0, 1).cross(self._orientation_z)
                if self._orientation_x.magnitude == 0:
                    self._orientation_x = Vector(1, 0, 0, 1)
                self._orientation_x = self._orientation_x.normalize()
                self._orientation_y = self._orientation_z.cross(self._orientation_x)
                self._orientation_y = self._orientation_y.normalize()
                self._orientation = vector_matrix([
                    self._orientation_x, 
                    self._orientation_y, 
                    self._orientation_z
                ])
            elif y_input:
                self._orientation_y = orientation_y.normalize()
                self._orientation_x = self._orientation_y.cross(Vector(0, 0, 1, 1)).normalize()
                self._orientation_z = self._orientation_y.cross(self._orientation_x).normalize()
                self._orientation = vector_matrix([
                    self._orientation_x, 
                    self._orientation_y, 
                    self._orientation_z
                ])
            elif x_input:
                self._orientation_x = orientation_x.normalize()
                self._orientation_y = Vector(0, 0, 1, 1).cross(self._orientation_x).normalize()
                self._orientation_z = self._orientation_x.cross(self._orientation_y).normalize()
                self._orientation = vector_matrix([
                    self._orientation_x, 
                    self._orientation_y, 
                    self._orientation_z
                ])
            else:
                self._orientation_x = Vector(1, 0, 0, 1)
                self._orientation_y = Vector(0, 1, 0, 1)
                self._orientation_z = Vector(0, 0, 1, 1)
                self._orientation = default_orientation()

        self._scale = scale

        self._position = position
        self._type = 'none'
        self._id = id
        self._name = name
        self._visibility = False

        self._vertices: Matrix=None,
        self._lines: list[Object]=[],
        self._fragments: list[Object]=[],
        self._points: list[Object]=[],        

    @property
    def position(self) -> Vector:
        return self._position.copy()
    
    @position.setter
    def position(self, value: Vector):
        if not isinstance(value, Vector):
            raise TypeError("Position must be a Vector")
        self._position = value.copy()

    @property
    def orientation(self) -> Matrix:
        return self._orientation.copy()
    
    @orientation.setter
    def orientation(self, value: Matrix):
        if not isinstance(value, Matrix):
            raise TypeError("Orientation must be a Matrix")
        self._orientation = value.copy()

    @property
    def orientation_x(self) -> Vector:
        return self._orientation_x.copy()
    
    @property
    def orientation_y(self) -> Vector:
        return self._orientation_y.copy()
    
    @property
    def orientation_z(self) -> Vector:
        return self._orientation_z.copy()
    
    @orientation_x.setter
    def orientation_x(self, value: Vector):
        if not isinstance(value, Vector):
            raise TypeError("Orientation X must be a Vector")
        
        self._orientation_z =value.cross(Vector(0, 1, 0, 1)).normalize()
        self._orientation_x = value.normalize()
        self._orientation_y = self._orientation_z.cross(self._orientation_x).normalize()

        self._orientation = vector_matrix([self._orientation_x, self._orientation_y, self._orientation_z])

    @orientation_y.setter
    def orientation_y(self, value: Vector):
        if not isinstance(value, Vector):
            raise TypeError("Orientation Y must be a Vector")
        
        self._orientation_z = Vector(1, 0, 0, 1).cross(value).normalize()
        self._orientation_y = value.normalize()
        self._orientation_x = self._orientation_y.cross(self._orientation_z).normalize()

        self._orientation = vector_matrix([self._orientation_x, self._orientation_y, self._orientation_z])

    @orientation_z.setter
    def orientation_z(self, value: Vector):
        if not isinstance(value, Vector):
            raise TypeError("Orientation Z must be a Vector")
        
        self._orientation_z = value.normalize()
        self._orientation_x = Vector(0, 1, 0, 1).cross(value).normalize()
        self._orientation_y = self._orientation_z.cross(self._orientation_x).normalize()

        self._orientation = vector_matrix([self._orientation_x, self._orientation_y, self._orientation_z])

    @property
    def scale(self) -> Vector:
        return self._scale.copy()
    
    @scale.setter
    def scale(self, value: Vector):
        if not isinstance(value, Vector):
            raise TypeError("Scale must be a Vector")
        self._scale = value.copy()

    @property
    def type(self) -> str:
        return self._type.copy()
    
    @type.setter
    def type(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Type must be a string")
        self._type = value.copy()

    @property
    def id(self) -> str:
        return self._id.copy()
    
    @id.setter
    def id(self, value: str):
        if not isinstance(value, str):
            raise TypeError("ID must be a string")
        self._id = value.copy()

    @property
    def vertices(self) -> Matrix:
        return self._vertices
    
    @property
    def points(self) -> list['Object']:
        return self._points
    
    @property
    def lines(self) -> list['Object']:
        return self._lines
    
    @property
    def fragments(self) -> list['Object']:
        return self._fragments

    def _constructor(self):
        pass

    def __str__(self) -> str:
        return f"Object({self._type}, {self._id}, {self._position}, {self._orientation}, {self._scale})"
    
    def __repr__(self) -> str:
        return f"Object({self._type}, {self._id}, {self._position}, {self._orientation}, {self._scale})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Object):
            return False
        return (
            self._type == other._type and
            self._id == other._id and
            self._position == other._position and
            self._orientation == other._orientation and
            self._scale == other._scale
        )
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash((self._type, self._id, self._position, self._orientation, self._scale))
    
    def __bool__(self) -> bool:
        return bool(self._type) and bool(self._id) and bool(self._position) and bool(self._orientation) and bool(self._scale)
    
    def decompose(self) -> tuple[list, list, list]:
        return self._points, self._lines, self._fragments

class Point(Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = 'point'
        self._vertices = vector_matrix([Vector(0, 0, 0, 1)])
        self._visibility = True


class Line(Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = 'line'
        self._vertices = vector_matrix([Vector(0, 0, 0, 1), Vector(0, 0, 1, 1)])
        self._visibility = True


class Fragment(Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = 'fragment'
        self._vertices = vector_matrix([Vector(0, 0, 0, 1), Vector(0, 1, 0, 1), Vector(1, 0, 0, 1)])
        self._visibility = True


class Origin(Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = 'origin'

        self._vertices = vector_matrix([
            Vector(0, 0, 0, 1), 
            Vector(1, 0, 0, 1), 
            Vector(0, 1, 0, 1), 
            Vector(0, 0, 1, 1)
        ])

        self._lines = [
            Line(position=Vector(0, 0, 0, 1), orientation_z=Vector(1, 0, 0, 1)), 
            Line(position=Vector(0, 0, 0, 1), orientation_z=Vector(0, 1, 0, 1)), 
            Line(position=Vector(0, 0, 0, 1), orientation_z=Vector(0, 0, 1, 1))
        ]

        self._points = [
            Point(position=Vector(0, 0, 0, 1))
        ]

        self._fragments = []
            


        
        






                

            

        
