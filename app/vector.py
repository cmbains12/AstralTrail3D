import numpy

class Vector:
    def __init__(self, *args: numpy.ndarray | int | float):
        self._components = numpy.array([0, 0, 0, 1], dtype=float)
        if args:
            if isinstance(args[0], numpy.ndarray):
                if len(args[0]) == 3:
                    self._components = numpy.append(args[0], 1)
                elif len(args[0]) == 4:
                    self._components = args[0]
                elif len(args[0]) == 2:
                    self._components = numpy.append(args[0], [0, 1])
            elif len(args) == 4:
                self._components = numpy.array(args, dtype=float)
            elif len(args) == 3:
                self._components = numpy.array([*args, 1], dtype=float)
            elif len(args) == 2:
                self._components = numpy.array([*args, 0, 1], dtype=float)
            elif len(args) == 1:
                if isinstance(args[0], (int, float)):
                    self._components = numpy.array(
                        [args[0], 0, 0, 1], 
                        dtype=float
                    )
                else:
                    raise TypeError("Invalid argument type")
            else:
                raise TypeError("Invalid number of arguments")
    
    @property
    def components(self) -> numpy.ndarray:
        return self._components
    
    @components.setter
    def components(self, value: numpy.ndarray | list[int | float]):
        if isinstance(value, numpy.ndarray):
            self._components = value
        elif isinstance(value, list):
            if all(isinstance(i, (int, float)) for i in value):
                self._components = numpy.array(value, dtype=float)
            else:
                raise TypeError("Invalid list element type")
        else:
            raise TypeError("Invalid argument type")
    
    @property
    def x(self) -> float:
        return self._components[0]
    
    @x.setter
    def x(self, value: float | int):
        if not isinstance(value, (int, float)):
            raise TypeError("Invalid argument type")
        self._components[0] = value
    
    @property
    def y(self) -> float:
        return self._components[1]
    
    @y.setter
    def y(self, value: float | int):
        if not isinstance(value, (int, float)):
            raise TypeError("Invalid argument type")
        self._components[1] = value
    
    @property
    def z(self) -> float:
        return self._components[2]
    
    @z.setter
    def z(self, value: float | int):
        if not isinstance(value, (int, float)):
            raise TypeError("Invalid argument type")
        self._components[2] = value
    
    @property
    def w(self) -> float:
        return self._components[3]
    
    @w.setter
    def w(self, value: float | int):
        if not isinstance(value, (int, float)):
            raise TypeError("Invalid argument type")
        self._components[3] = value
    
    @property
    def magnitude(self) -> float:
        mag = numpy.linalg.norm(self._components[:3])
        return mag
    
    def __add__(self, other: 'Vector') -> 'Vector':
        if not isinstance(other, Vector):
            raise TypeError("Invalid argument type")
        return Vector(self._components[:3] + other.components[:3])
    
    def __sub__(self, other: 'Vector') -> 'Vector':
        if not isinstance(other, Vector):
            raise TypeError("Invalid argument type")
        return Vector(self._components[:3] - other.components[:3])
    
    def __rmul__(self, other: float | int) -> 'Vector':
        if not isinstance(other, (int, float, numpy.float64)):
            return NotImplemented
        
        array = self._components[:3] * other
        
        result = Vector(array)

        return result
    
    def __mul__(self, other):
        return NotImplemented
    
    def __truediv__(self, other: float | int) -> 'Vector':
        if not isinstance(other, (int, float, )):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return Vector(self._components[:3] / other)
    
    def __neg__(self) -> 'Vector':
        return Vector(-self._components[:2])
    
    def __getitem__(self, key: int) -> float:
        if not isinstance(key, int):
            raise TypeError("Invalid argument type")
        if key < 0 or key > 3:
            raise IndexError("Index out of range")
        return self._components[key]
    
    def __setitem__(self, key: int, value: float | int):
        if not isinstance(key, int):
            raise TypeError("Invalid argument type")
        if key < 0 or key > 3:
            raise IndexError("Index out of range")
        if not isinstance(value, (int, float)):
            raise TypeError("Invalid argument type")
        self._components[key] = value

    def __str__(self) -> str:
        return str(self._components[:3])
    
    def __repr__(self) -> str:
        return f"Vector({self._components[:3]})"
    
    def __eq__(self, other: 'Vector') -> bool:
        if not isinstance(other, Vector):
            return False
        return numpy.array_equal(self._components[:3], other.components[:3])
    
    def __ne__(self, other: 'Vector') -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self._components.tobytes())
    
    def copy(self) -> 'Vector':
        return Vector(self._components.copy())

    def normalize(self) -> 'Vector':
        if self.magnitude == 0:
            raise ZeroDivisionError("Cannot normalize a zero vector")
        vec = Vector(self._components[:3] / self.magnitude)
        return vec
    
    def dot(self, other: 'Vector') -> float:
        if not isinstance(other, Vector):
            raise TypeError("Invalid argument type")
        return numpy.dot(self._components[:3], other.components[:3])
    
    def cross(self, other: 'Vector') -> 'Vector':
        if not isinstance(other, Vector):
            raise TypeError("Invalid argument type")
        return Vector(
            self._components[1] * other.components[2] - 
            self._components[2] * other.components[1],
            self._components[2] * other.components[0] - 
            self._components[0] * other.components[2],
            self._components[0] * other.components[1] - 
            self._components[1] * other.components[0], 1
        )
    

    
    
    
    
    

        
            