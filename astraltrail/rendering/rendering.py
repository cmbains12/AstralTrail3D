import pyglet.gl as gl
import ctypes as ct

from rendering.shader_sources import ShaderSources as Shaders
from assets.meshes import *

class Renderer:
    def __init__(self, window):
        self.window = window
        self.render_program = Renderer.create_render_program()
        self.buffers = {}
        self.f_count = {
            'triangle': Triangle()._f_count,
            'square': Square()._f_count,
            'cube': Cube()._f_count,
            'pyramid': Pyramid()._f_count,
            'teapot': Teapot()._f_count,
        }
        self.objects = {
            'triangle': {
                'name': 'triangle',
                'count': 0,
            }, 'square': {
                'name': 'square',
                'count': 0,
            }, 'cube': {
                'name': 'cube',
                'count': 0,
            }, 'pyramid': {
                'name': 'pyramid',
                'count': 0,
            }, 'teapot': {
                'name': 'teapot',
                'count': 0,
            },
        }

    def setup_object_buffer(self, model_name, mesh_matrix, norms_matrix, instance_matrix, instance_count):
        self.objects[model_name]['count'] = instance_count

        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        vao = gl.GLuint()
        vbo = gl.GLuint()
        vbo_norms = gl.GLuint()
        vbo_instances = gl.GLuint()

        gl.glGenVertexArrays(1, ct.byref(vao))
        gl.glGenBuffers(1, ct.byref(vbo))
        gl.glGenBuffers(1, ct.byref(vbo_norms))
        gl.glGenBuffers(1, ct.byref(vbo_instances))

        gl.glBindVertexArray(vao)

        mesh = mesh_matrix
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            mesh.nbytes,
            mesh.ctypes.data_as(ct.POINTER(ct.c_float)),
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

        norms = norms_matrix
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_norms)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            norms.nbytes,
            norms.ctypes.data_as(ct.POINTER(ct.c_float)),
            gl.GL_STATIC_DRAW
        )
        gl.glVertexAttribPointer(
            1,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            0,
            ct.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(1)  

        instances = instance_matrix
        
        if instance_matrix is not None:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_instances)
            gl.glBufferData(
                gl.GL_ARRAY_BUFFER, 
                instances.nbytes,
                instances.ctypes.data_as(ct.POINTER(ct.c_float)),
                gl.GL_STATIC_DRAW
            )
            for i in range(4):
                loc = 2 + i
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

        self.buffers[f'vao-{model_name}'] = vao
        self.buffers[f'vbo-{model_name}'] = vbo
        self.buffers[f'vbo-{model_name}-norms'] = vbo_norms
        self.buffers[f'vbo-{model_name}-instances'] = vbo_instances

    def setup_render_buffers(self, **kwargs):
        self.models = kwargs.get('models', None)
        meshes = {
            'triangle': Triangle().mesh.copy(),
            'square': Square().mesh.copy(),
            'cube': Cube().mesh.copy(),
            'pyramid': Pyramid().mesh.copy(),
            'teapot': Teapot().mesh.copy(),
        }
        norms = {
            'triangle': Triangle().mesh_normals.copy(),
            'square': Square().mesh_normals.copy(),
            'cube': Cube().mesh_normals.copy(),
            'pyramid': Pyramid().mesh_normals.copy(),
            'teapot': Teapot().mesh_normals.copy(),
        }

        self.setup_object_buffer(
            model_name='triangle', 
            mesh_matrix=meshes.get('triangle'), 
            norms_matrix=norms.get('triangle'), 
            instance_matrix=self.models.get('test-triangles'), 
            instance_count=kwargs.get('triangle_count', 0)
        )

        self.setup_object_buffer(
            model_name='square', 
            mesh_matrix=meshes.get('square'), 
            norms_matrix=norms.get('square'), 
            instance_matrix=self.models.get('test-squares'), 
            instance_count=kwargs.get('square_count', 0)
        )
        self.setup_object_buffer(
            model_name='cube', 
            mesh_matrix=meshes.get('cube'), 
            norms_matrix=norms.get('cube'), 
            instance_matrix=self.models.get('test-cubes'), 
            instance_count=kwargs.get('cube_count', 0)
        )
        self.setup_object_buffer(
            model_name='pyramid', 
            mesh_matrix=meshes.get('pyramid'), 
            norms_matrix=norms.get('pyramid'), 
            instance_matrix=self.models.get('test-pyramids'), 
            instance_count=kwargs.get('pyramid_count', 0)
        )
        self.setup_object_buffer(
            model_name='teapot', 
            mesh_matrix=meshes.get('teapot'), 
            norms_matrix=norms.get('teapot'), 
            instance_matrix=self.models.get('test-teapots'), 
            instance_count=kwargs.get('teapot_count', 0)
        )

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
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        

    def on_draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glUseProgram(self.render_program)
        self.update_view(self.window.play_state.camera)

        for model in self.objects.values():
            self.draw_object(model['name'], model['count'])
         
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

    def draw_object(self, object_model, object_count):
        face_count = self.f_count[f'{object_model}']
        vertex_draw_count = 3 * face_count
        gl.glBindVertexArray(self.buffers[f'vao-{object_model}'])
        gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, vertex_draw_count, object_count)