import pyglet.gl as gl
import ctypes as ct

from rendering.shader_sources import ShaderSources as Shaders
from assets.meshes import *

class Renderer:
    def __init__(self, window):
        self.window = window
        self.render_program = Renderer.create_render_program()
        self.buffers = {}


    def setup_render_buffers(self, **kwargs):
        self.models = kwargs.get('models', None)
        self.square_count = kwargs.get('square_count', 0)
        self.triangle_count = kwargs.get('triangle_count', 0)
        self.cube_count = kwargs.get('cube_count', 0)
        self.pyramid_count = kwargs.get('pyramid_count', 0)
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        vao_square = gl.GLuint()
        vao_triangle = gl.GLuint()
        vao_cube = gl.GLuint()
        vao_pyramid = gl.GLuint()

        vbo_square = gl.GLuint()
        vbo_triangle = gl.GLuint()
        vbo_cube = gl.GLuint()
        vbo_pyramid = gl.GLuint()

        vbo_square_instances = gl.GLuint()
        vbo_triangle_instances = gl.GLuint()
        vbo_cube_instances = gl.GLuint()
        vbo_pyramid_instances = gl.GLuint()
        
        gl.glGenVertexArrays(1, ct.byref(vao_square))
        gl.glGenVertexArrays(1, ct.byref(vao_triangle))
        gl.glGenVertexArrays(1, ct.byref(vao_cube))
        gl.glGenVertexArrays(1, ct.byref(vao_pyramid))


        gl.glGenBuffers(1, ct.byref(vbo_square))
        gl.glGenBuffers(1, ct.byref(vbo_triangle))
        gl.glGenBuffers(1, ct.byref(vbo_cube))
        gl.glGenBuffers(1, ct.byref(vbo_pyramid))

        gl.glGenBuffers(1, ct.byref(vbo_square_instances))
        gl.glGenBuffers(1, ct.byref(vbo_triangle_instances))
        gl.glGenBuffers(1, ct.byref(vbo_cube_instances))
        gl.glGenBuffers(1, ct.byref(vbo_pyramid_instances))

        gl.glBindVertexArray(vao_square)
        square_mesh = Square().mesh.copy()
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_square)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            square_mesh.nbytes,
            square_mesh.ctypes.data_as(ct.POINTER(ct.c_float)),
            gl.GL_STATIC_DRAW
        )
        gl.glVertexAttribPointer(
            0,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            0,
            ct.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(0)

        squares = self.models.get('test-squares')
        
        if squares is not None:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_square_instances)
            gl.glBufferData(
                gl.GL_ARRAY_BUFFER, 
                squares.nbytes,
                squares.ctypes.data_as(ct.POINTER(ct.c_float)),
                gl.GL_STATIC_DRAW
            )
            for i in range(4):
                loc = 1 + i
                gl.glEnableVertexAttribArray(loc)
                gl.glVertexAttribPointer(
                    loc,
                    4,
                    gl.GL_FLOAT,
                    gl.GL_FALSE, 
                    64,
                    ct.c_void_p(i * 16)
                )
                gl.glVertexAttribDivisor(loc, 1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        gl.glBindVertexArray(vao_triangle)
        triangle_mesh = Triangle().mesh.copy()
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_triangle)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            triangle_mesh.nbytes,
            triangle_mesh.ctypes.data_as(ct.POINTER(ct.c_float)),
            gl.GL_STATIC_DRAW
        )
        gl.glVertexAttribPointer(
            0,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            0,
            ct.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(0)

        triangles = self.models.get('test-triangles')

        if triangles is not None:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_triangle_instances)
            gl.glBufferData(
                gl.GL_ARRAY_BUFFER, 
                triangles.nbytes,
                triangles.ctypes.data_as(ct.POINTER(ct.c_float)),
                gl.GL_STATIC_DRAW
            )
            for i in range(4):
                loc = 1 + i
                gl.glEnableVertexAttribArray(loc)
                gl.glVertexAttribPointer(
                    loc,
                    4,
                    gl.GL_FLOAT,
                    gl.GL_FALSE, 
                    64,
                    ct.c_void_p(i * 16)
                )
                gl.glVertexAttribDivisor(loc, 1)

        gl.glBindVertexArray(vao_cube)
        cube_mesh = Cube().mesh.copy()
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_cube)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            cube_mesh.nbytes,
            cube_mesh.ctypes.data_as(ct.POINTER(ct.c_float)),
            gl.GL_STATIC_DRAW
        )
        gl.glVertexAttribPointer(
            0,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            0,
            ct.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(0)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_cube_instances)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, 
            self.models['test-cubes'].nbytes,
            self.models['test-cubes'].ctypes.data_as(ct.POINTER(ct.c_float)),
            gl.GL_STATIC_DRAW
        )
        for i in range(4):
            loc = 1 + i
            gl.glEnableVertexAttribArray(loc)
            gl.glVertexAttribPointer(
                loc,
                4,
                gl.GL_FLOAT,
                gl.GL_FALSE, 
                64,
                ct.c_void_p(i * 16)
            )
            gl.glVertexAttribDivisor(loc, 1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        gl.glBindVertexArray(vao_pyramid)
        pyramid_mesh = Pyramid().mesh.copy()
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_pyramid)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            pyramid_mesh.nbytes,
            pyramid_mesh.ctypes.data_as(ct.POINTER(ct.c_float)),
            gl.GL_STATIC_DRAW
        )
        gl.glVertexAttribPointer(
            0,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            0,
            ct.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(0)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_pyramid_instances)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, 
            self.models['test-pyramids'].nbytes,
            self.models['test-pyramids'].ctypes.data_as(ct.POINTER(ct.c_float)),
            gl.GL_STATIC_DRAW
        )
        for i in range(4):
            loc = 1 + i
            gl.glEnableVertexAttribArray(loc)
            gl.glVertexAttribPointer(
                loc,
                4,
                gl.GL_FLOAT,
                gl.GL_FALSE, 
                64,
                ct.c_void_p(i * 16)
            )
            gl.glVertexAttribDivisor(loc, 1)


        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        gl.glBindVertexArray(0)

        self.buffers['vao-square'] = vao_square
        self.buffers['vbo-square'] = vbo_square
        self.buffers['vbo_square_instances'] = vbo_square_instances

        self.buffers['vao-triangle'] = vao_triangle
        self.buffers['vbo-triangle'] = vbo_triangle
        self.buffers['vbo_triangle_instances'] = vbo_triangle_instances

        self.buffers['vao-cube'] = vao_cube
        self.buffers['vbo-cube'] = vbo_cube
        self.buffers['vbo_cube_instances'] = vbo_cube_instances

        self.buffers['vao-pyramid'] = vao_pyramid
        self.buffers['vbo-pyramid'] = vbo_pyramid
        self.buffers['vbo_pyramid_instances'] = vbo_pyramid_instances

    @staticmethod
    def create_render_program():
        program = gl.glCreateProgram()
        vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

        vertex_shader_source_buffer = ct.create_string_buffer(Shaders.vertex_shader_source_string)
        fragment_shader_source_buffer = ct.create_string_buffer(Shaders.fragment_shader_source_string)

        v_shader_source_pointer = ct.cast(
            ct.pointer(ct.pointer(vertex_shader_source_buffer)), 
            ct.POINTER(ct.POINTER(ct.c_char))
        )
        f_shader_source_pointer = ct.cast(
            ct.pointer(ct.pointer(fragment_shader_source_buffer)), 
            ct.POINTER(ct.POINTER(ct.c_char))
        )    
        v_length = ct.c_int(len(Shaders.vertex_shader_source_string))
        f_length = ct.c_int(len(Shaders.fragment_shader_source_string))

        gl.glShaderSource(vertex_shader, 1, v_shader_source_pointer, ct.byref(v_length))
        gl.glShaderSource(fragment_shader, 1, f_shader_source_pointer, ct.byref(f_length))

        gl.glCompileShader(vertex_shader)
        gl.glCompileShader(fragment_shader)

        gl.glAttachShader(program, vertex_shader)
        gl.glAttachShader(program, fragment_shader)

        gl.glLinkProgram(program)

        return program

    @staticmethod
    def configure_gl():
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_CULL_FACE)
        

    def on_draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glUseProgram(self.render_program)
        self.update_view(self.window.play_state.camera)        
        self.draw_squares(self.square_count)
        self.draw_triangles(self.triangle_count)
        self.draw_cubes(self.cube_count)
        self.draw_pyramids(self.pyramid_count)

    def update_view(self, camera):
        gl.glUseProgram(self.render_program)
        
        view_loc = gl.glGetUniformLocation(self.render_program, b'view')

        gl.glUniformMatrix4fv(
            view_loc,
            1,
            gl.GL_FALSE,
            camera.view.T.flatten().ctypes.data_as(ct.POINTER(ct.c_float))
        )

    def update_proj(self, camera):
        gl.glUseProgram(self.render_program)

        proj_loc = gl.glGetUniformLocation(self.render_program, b'proj')

        gl.glUniformMatrix4fv(
            proj_loc,
            1,
            gl.GL_FALSE,
            camera.proj.T.flatten().ctypes.data_as(ct.POINTER(ct.c_float))
        )

    def draw_triangles(self, triangle_count):
        gl.glBindVertexArray(self.buffers['vao-triangle'])
        gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, 3, triangle_count)

    def draw_squares(self, square_count):
        gl.glBindVertexArray(self.buffers['vao-square'])
        gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, 6, square_count)

    def draw_cubes(self, cube_count):
        gl.glBindVertexArray(self.buffers['vao-cube'])
        gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, 36, cube_count)
    
    def draw_pyramids(self, pyramid_count):
        gl.glBindVertexArray(self.buffers['vao-pyramid'])
        gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, 12, pyramid_count)
