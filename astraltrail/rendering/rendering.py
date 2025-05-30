import pyglet
import pyglet.gl as gl
import ctypes as ct

from rendering.shader_sources import ShaderSources as Shaders
from assets.meshes import *

class Renderer:
    def __init__(self):
        self.render_program = Renderer.create_render_program()
        self.buffers = {}

    def setup_render_buffers(self, models, square_count, triangle_count):
        self.square_count = square_count
        self.triangle_count = triangle_count
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        vao_square = gl.GLuint()
        vao_triangle = gl.GLuint()

        vbo_square = gl.GLuint()
        vbo_triangle = gl.GLuint()

        vbo_square_instances = gl.GLuint()
        vbo_triangle_instances = gl.GLuint()
        
        gl.glGenVertexArrays(1, ct.byref(vao_square))
        gl.glGenVertexArrays(1, ct.byref(vao_triangle))

        gl.glGenBuffers(1, ct.byref(vbo_square))
        gl.glGenBuffers(1, ct.byref(vbo_triangle))

        gl.glGenBuffers(1, ct.byref(vbo_square_instances))
        gl.glGenBuffers(1, ct.byref(vbo_triangle_instances))

        gl.glBindVertexArray(vao_square)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_square)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            Square().mesh.nbytes,
            Square().mesh.ctypes.data_as(ct.POINTER(ct.POINTER(ct.c_float))),
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

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_square_instances)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, 
            models['test-squares'].nbytes,
            models['test-squares'].ctypes.data_as(ct.POINTER(ct.c_float)),
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

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_triangle)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            Triangle().mesh.nbytes,
            Triangle().mesh.ctypes.data_as(ct.POINTER(ct.POINTER(ct.c_float))),
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
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_triangle_instances)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, 
            models['test-triangles'].nbytes,
            models['test-triangles'].ctypes.data_as(ct.POINTER(ct.c_float)),
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

    def on_draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glUseProgram(self.render_program)
        self.draw_squares(self.square_count)
        self.draw_triangles(self.triangle_count)

    def draw_triangles(self, triangle_count):
        gl.glBindVertexArray(self.buffers['vao-triangle'])
        gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, 3, triangle_count)

    def draw_squares(self, square_count):
        gl.glBindVertexArray(self.buffers['vao-square'])
        gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, 6, square_count)
