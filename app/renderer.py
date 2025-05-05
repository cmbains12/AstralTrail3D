import pyglet
from pyglet.gl import *
from pyglet.graphics.shader import ShaderProgram, Shader
from pyglet.graphics import Batch
import numpy as np

from constants import *


class Renderer:
    vertex_shader_source = '''
    #version 330 core

    in vec3 position;
    in vec4 colour;
    in vec3 normal;

    uniform mat4 modelMatrix;
    uniform mat4 viewMatrix;
    uniform mat4 projectionMatrix;

    out vec4 frag_colour;

    out float diffuse;

    void main() {
        vec3 diffuse_light = normalize(vec3(-1.8, -5.0, 0.87));
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);

        mat3 modelViewNormalMatrix = transpose(inverse(mat3(modelMatrix)));

        vec3 frag_normal = normalize(modelViewNormalMatrix * normalize(normal));

        frag_colour = colour;

        diffuse = max(-dot(frag_normal, diffuse_light), 0.0);

    }
    '''

    fragment_shader_source = '''
    #version 330 core

    in vec4 frag_colour;
    in float diffuse;

    out vec4 out_colour;



    void main() {
        
        float ambient = 0.2;
        
        out_colour = (diffuse + ambient) * frag_colour;
    }
    '''
    vertex_shader = Shader(vertex_shader_source, 'vertex')
    fragment_shader = Shader(fragment_shader_source, 'fragment')

    def __init__(self, window):
        self.objects = {}
        self.program = ShaderProgram(self.vertex_shader, self.fragment_shader)
        self.window = window
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)

        self.update_uniforms(
            model_matrix=np.identity(4, dtype=np.float32).flatten(),
            view_matrix=np.identity(4, dtype=np.float32).flatten(),
            projection_matrix=np.identity(4, dtype=np.float32).flatten()
        )

    def on_draw(self, objects):
        self.program.use()      

        self.window.clear()

        for obj in objects.values():
            batch = pyglet.graphics.Batch()
            frags = self.program.vertex_list(
                36, GL_TRIANGLES,
                position=('f',obj.vertices_indexed('fragments')),
                colour=('Bn', 
                    COLOURS['red']
                    * 36),
                normal=('f', (obj.normals)),
                batch=batch
            )
            lins = self.program.vertex_list(
                24, GL_LINES,
                position=('f', obj.vertices_indexed('lines')),
                colour=('Bn', (COLOURS['darkGray'] * 24)),
                batch=batch
            )

            self.program['modelMatrix'] = obj.model_matrix.flatten()
            batch.draw()

        self.program.stop()

    def update_uniforms(self, 
        model_matrix=None,
        view_matrix=None, 
        projection_matrix=None,
    ):
        
        if model_matrix is not None:
            self.program['modelMatrix'] = model_matrix
        if view_matrix is not None:
            self.program['viewMatrix'] = view_matrix
        if projection_matrix is not None:
            self.program['projectionMatrix'] = projection_matrix

