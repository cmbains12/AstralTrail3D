from math import acos
import random

class Vector:
    def __init__(self, *components):
        if len(components) == 0:
            components = (0,0,0,1)
        
        if len(components) < 4:
            components = list(components) + [0,] * (4 - len(components))
            components[3] = 1

        self._components = list(components)

    @property
    def components(self) -> list[int | float]:
        components = self._components.copy()

        return components
    
    @components.setter
    def components(self, new_components: list[int | float]):
        self._components = new_components
    
    @property
    def magnitude(self) -> int | float:
        magnitude = (self.x ** 2 + self.y ** 2 + self.z ** 2) ** (0.5)

        return magnitude
    
    @property
    def normalized(self) -> 'Vector':
        vector = Vector()
        magnitude = self.magnitude
        if magnitude != 0:
            vector.x = self.x / magnitude
            vector.y = self.y / magnitude
            vector.z = self.z / magnitude

        return vector
    
    @property
    def x(self) -> int | float:
        x = self._components[0]

        return x
    
    @x.setter
    def x(self, value: int | float):
        self._components[0] = value

    @property
    def y(self) -> int | float:
        y = self._components[1]

        return y
    
    @y.setter
    def y(self, value: int | float):
        self._components[1] = value

    @property
    def z(self) -> int | float:
        z = self._components[2]

        return z
    
    @z.setter
    def z(self, value: int | float):
        self._components[2] = value

    @property
    def w(self) -> int | float:
        w = self._components[3]

        return w
    
    @w.setter
    def w(self, value: int | float):
        self._components[3] = value

    def __str__(self) -> str:
        string = f"Vector({self.x}, {self.y}, {self.z}, {self.w})"
        return string

    def __len__(self) -> int:
        length = len(self._components)

        return length
    
    def __getitem__(self, key: int | tuple[int,int]) -> int | float:
        item = self._components[key]

        return item
    
    def __setitem__(self, key: int | tuple[int,int], value: int | float):
        self._components[key] = value

    def __add__(self, other: 'Vector') -> 'Vector':
        vector = Vector()
        for i in range(len(self._components)):
            vector[i] = self[i] + other[i]

        return vector
    
    def __sub__(self, other: 'Vector') -> 'Vector':
        vector = Vector()
        for i in range(len(self._components)):
            vector[i] = self[i] - other[i]

        return vector

    def __mul__(self, scalar: int | float) -> 'Vector':
        if isinstance(scalar, (int, float)):
            vector = Vector()
            vector.x = self.x * scalar
            vector.y = self.y * scalar
            vector.z = self.z * scalar
            return vector

        return NotImplemented
    
    def __rmul__(self, scalar: int | float) -> 'Vector':
        if isinstance(scalar, (int, float)):
            return self.__mul__(scalar)
        
        return NotImplemented
    
    def __neg__(self) -> 'Vector':
        vector = Vector()
        for i in range(3):
            vector[i] = -self[i]

        return vector
    
    def __truediv__(self, scalar: int | float) -> 'Vector':
        if scalar != 0:
            vector = Vector()
            vector.x = self.x / scalar
            vector.y = self.y / scalar
            vector.z = self.z / scalar
            return vector
        
        raise ZeroDivisionError
    
    def __eq__(self, other: 'Vector') -> bool:
        for i in range(len(self._components)):
            if self[i] != other[i]:
                return False
            
        return True
    
    def __ne__(self, other: 'Vector') -> bool:
        return not self.__eq__(other)
    
    def __iter__(self):
        return iter(self._components[0:2])
    
    def dot(self, other: 'Vector') -> int | float:
        dot = 0
        for i in range(3):
            dot = dot + self[i] * other[i]

        return dot

    def cross(self, other: 'Vector') -> 'Vector':
        vector = Vector()
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        vector.x = x
        vector.y = y
        vector.z = z
        return vector

    def angle(self, other: 'Vector') -> int | float:
        if self.magnitude == 0 or other.magnitude == 0:
            return 0
        
        dot = self.dot(other)
        normalized_dot = dot / (self.magnitude * other.magnitude)
        normalized_dot = self.clamp(normalized_dot, -1.0, 1.0)
        dot_angle = acos(normalized_dot)
        return dot_angle
    
    def clamp(self, value, min_value, max_value):
        return max(min_value, min(value, max_value))

    def project_plane(self, plane: str) -> 'Vector':
        vector = Vector()
        if plane == 'xz' or plane == 'zx':
            vector.x = self.x
            vector.z = self.z
        if plane == 'xy' or plane == 'yx':
            vector.x = self.x
            vector.y = self.y
        if plane == 'yz' or plane == 'zy':
            vector.y = self.y
            vector.z = self.z

        return vector
    
    def project_plane_angle(self, plane: str) -> int | float:
        projected_vector = self.project_plane(plane)
        angle = self.angle(projected_vector)

        return angle
    
    def copy(self) -> 'Vector':
        vector = Vector()
        for i in range(len(self)):
            vector[i] = self[i]
        
        return vector
    
def random_vector() -> Vector:
    vector = Vector(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
    return vector
    
    