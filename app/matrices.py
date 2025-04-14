import numpy

from vector import Vector

class Matrix:
    def __init__(
            self,
            *args: numpy.ndarray | int | list[list[int | float]]
    ):
        if not args:
            self._components = numpy.eye(4, dtype=float)
            return

        if len(args) == 2:
            if not isinstance(args[0], int) or not isinstance(args[1], int):
                raise TypeError("Matrix dimensions must be integers")
            self._components = numpy.zeros((args[0], args[1]), dtype=float)
            return

        cols = len(args[0])

        if isinstance(args[0], numpy.ndarray):
            if args[0].ndim != 2:
                raise ValueError("Matrix must be 2-dimensional")
            if args[0].shape[0] == 0 or args[0].shape[1] == 0:
                raise ValueError("Matrix cannot be empty")
            self._components = args[0]
            return

        for row in args:
            if not isinstance(row, list):
                raise TypeError("Matrix rows must be lists")
            if len(row) != cols:
                raise ValueError("All rows must have the same number of columns")
            for element in row:
                if not isinstance(element, (int, float)):
                    raise TypeError("Matrix elements must be numbers")
                
        self._components = numpy.array(args, dtype=float)

    @property
    def components(self):
        return self._components

    @property
    def shape(self):
        return self._components.shape
    
    @property
    def T(self):
        return Matrix(self._components.T)
    
    @property
    def rows(self):
        return self._components.shape[0]
    
    @property
    def cols(self):
        return self._components.shape[1]

    def __getitem__(self, key):
        return self._components[key]

    def __setitem__(self, key, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Matrix elements must be numbers")
        self._components[key] = value

    def __mul__(self, other):
        result = numpy.dot(self._components, other._components)
        
        return Matrix(result)

    def __rmul__(self, other):
        if not isinstance(other, int | float):
            return NotImplemented
        return Matrix(numpy.dot(other._components, self._components))     
    
    def __add__(self, other):
        return NotImplemented
    
    def __sub__(self, other):
        return NotImplemented
    
    def __truediv__(self, other):
        if not isinstance(other, int | float):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError("division by zero")
        return self.__mul__(other**-1)
    
    def __neg__(self):
        return Matrix(-self._components)
    
    def __str__(self):
        return str(self._components)
    
    def __repr__(self):
        return f"Matrix({self._components})"
    
    def __eq__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError("Comparison is only supported between Matrix instances")
        return numpy.array_equal(self._components, other._components)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self._components.tobytes())
    
    def __bool__(self):
        return numpy.any(self._components)
    
    def column_vectors(self):
        return [Vector(self._components[:, i]) for i in range(self._components.shape[1])]

def default_orientation():
    array_list = numpy.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1]
    ], dtype=float)

    return Matrix(array_list)

def vector_matrix(vectors: list[Vector]):
    array_list = numpy.array([vector._components for vector in vectors])

    return Matrix(array_list)