
import pyglet
import pyglet.gl as gl
import numpy as np
import ctypes as ct

triangle_mesh = np.array([
    [-0.05, 0.05, 0.0],
    [-0.05, -0.05, 0.0],
    [0.05, -0.05, 0.0],
], np.float32)

vertex_shader_source_string = b'''
#version 330 core

layout(location = 0) in vec3 aPos;
layout(location = 1) in mat4 model;

void main() {
    gl_Position = model * vec4(aPos, 1.0);
}
'''

fragment_shader_source_string = b'''
#version 330 core

out vec4 fragColour;

void main() {
    fragColour = vec4(0.8, 0.4, 0.2, 1.0);
}
'''

def main():
    window = initiate_window()

    models, model_count = configure_scene()

    configure_gl()

    render_program = create_render_program()

    buffers = setup_render_buffers(models)

    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glUseProgram(render_program)
        gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, 3, model_count)
    
    window.push_handlers(on_draw)

    pyglet.app.run()

def setup_render_buffers(models):
    gl.glBindVertexArray(0)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    buffers = {}

    vao_triangle = gl.GLuint()
    vbo_triangle = gl.GLuint()
    vbo_triangle_instances = gl.GLuint()

    gl.glGenVertexArrays(1, ct.byref(vao_triangle))
    gl.glGenBuffers(1, ct.byref(vbo_triangle))
    gl.glGenBuffers(1, ct.byref(vbo_triangle_instances))

    gl.glBindVertexArray(vao_triangle)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_triangle)
    gl.glBufferData(
        gl.GL_ARRAY_BUFFER,
        triangle_mesh.nbytes,
        triangle_mesh.ctypes.data_as(ct.POINTER(ct.POINTER(ct.c_float))),
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
    gl.glEnableVertexAttribArray(0)

    buffers['vao-triangle'] = vao_triangle
    buffers['vbo-triangle'] = vbo_triangle
    buffers['vbo_triangle_instances'] = vbo_triangle_instances

    return buffers

def create_render_program():
    program = gl.glCreateProgram()
    vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

    vertex_shader_source_buffer = ct.create_string_buffer(vertex_shader_source_string)
    fragment_shader_source_buffer = ct.create_string_buffer(fragment_shader_source_string)

    v_shader_source_pointer = ct.cast(
        ct.pointer(ct.pointer(vertex_shader_source_buffer)), 
        ct.POINTER(ct.POINTER(ct.c_char))
    )
    f_shader_source_pointer = ct.cast(
        ct.pointer(ct.pointer(fragment_shader_source_buffer)), 
        ct.POINTER(ct.POINTER(ct.c_char))
    )    
    v_length = ct.c_int(len(vertex_shader_source_string))
    f_length = ct.c_int(len(fragment_shader_source_string))

    gl.glShaderSource(vertex_shader, 1, v_shader_source_pointer, ct.byref(v_length))
    gl.glShaderSource(fragment_shader, 1, f_shader_source_pointer, ct.byref(f_length))

    gl.glCompileShader(vertex_shader)
    gl.glCompileShader(fragment_shader)

    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)

    gl.glLinkProgram(program)

    return program

def configure_gl():
    gl.glClearColor(0.1, 0.1, 0.1, 1.0)

def configure_scene():
    models = {
        'test-triangles': []
    }

    grid_size = 4

    sep = 0.2

    model_count = 0

    for i in range(grid_size):
        for j in range(grid_size):
            posx = i * sep
            posy = j * sep
            model = np.eye(4, dtype=np.float32)
            model[0, 3] = posx
            model[1, 3] = posy

            models['test-triangles'].append(model.T.flatten())

            model_count += 1

    models['test-triangles'] = np.array(models['test-triangles'], dtype=np.float32)

    return models, model_count

def initiate_window():

    width = 1280
    height = 720
    caption = 'triangles'

    return pyglet.window.Window(width, height, caption)

if __name__=='__main__':
    main()
