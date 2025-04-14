from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.math import Vec3, Mat4
from math import radians, tan

vertex_shader_source = """
#version 330
layout(location = 0) in vec3 vertices;
layout(location = 1) in vec4 colours;

out vec4 newColour;

uniform mat4 viewMatrix;
uniform mat4 perspectiveMatrix;

void main() {
    gl_Position = perspectiveMatrix * viewMatrix * vec4(vertices, 1.0f);

    newColour = colours;
}
"""



fragment_shader_source = """
#version 330
in vec4 newColour;
out vec4 outColour;

void main() {
    outColour = newColour;
}
"""

vertex_shader = Shader(vertex_shader_source, 'vertex')
fragment_shader = Shader(fragment_shader_source, 'fragment')
shader_program = ShaderProgram(vertex_shader, fragment_shader)


class Renderer:
    def __init__(self):
        self.window_width = 1
        self.window_height = 1
        self.shader_program = shader_program

    def set_projection_matrix(self, width, height, fov, znear, zfar):
        self.window_width = width
        self.window_height = height
        self.fov = fov
        self.znear = znear
        self.zfar = zfar

        aspect_ratio = self.window_width / self.window_height


        
        perspective_matrix = Mat4.perspective_projection(
            aspect_ratio, znear, zfar, fov
        )

        print("Perspective Matrix: ")
        print(f"{perspective_matrix}")
        

        view_pos_vec = Vec3(x=2, y=2, z=-5)
        view_dir_vec = Vec3(x=0, y=1, z=0)
        view_dir_angle = radians(180.0)

        view_matrix_trans = Mat4.from_translation(-view_pos_vec)
        view_matrix_rot = Mat4.from_rotation(view_dir_angle, view_dir_vec)
        view_matrix = view_matrix_rot @ view_matrix_trans


        self.shader_program['viewMatrix'] = view_matrix
        self.shader_program['perspectiveMatrix'] = perspective_matrix



