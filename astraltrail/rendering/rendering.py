import pyglet
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
            #'teapot': Teapot()._f_count,
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
            },
        }

    def setup_object_buffer(self, model_name, mesh_matrix, norms_matrix, texture_matrix, instance_matrix, instance_count, tangent_matrix, bitangent_matrix):
        self.objects[model_name]['count'] = instance_count

        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        vao = gl.GLuint()
        vbo = gl.GLuint()
        vbo_norms = gl.GLuint()
        vbo_textures = gl.GLuint()
        vbo_instances = gl.GLuint()
        vbo_tangents = gl.GLuint()
        vbo_bitangents = gl.GLuint()        

        gl.glGenVertexArrays(1, ct.byref(vao))
        gl.glGenBuffers(1, ct.byref(vbo))
        gl.glGenBuffers(1, ct.byref(vbo_norms))
        gl.glGenBuffers(1, ct.byref(vbo_textures))
        gl.glGenBuffers(1, ct.byref(vbo_instances))
        gl.glGenBuffers(1, ct.byref(vbo_tangents))
        gl.glGenBuffers(1, ct.byref(vbo_bitangents))        

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

        textures = texture_matrix
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_textures)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            textures.nbytes,
            textures.ctypes.data_as(ct.POINTER(ct.c_float)),
            gl.GL_STATIC_DRAW
        )
        gl.glVertexAttribPointer(
            2,
            2,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            0,
            ct.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(2)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_tangents)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            tangent_matrix.nbytes,
            tangent_matrix.ctypes.data_as(ct.POINTER(ct.c_float)),
            gl.GL_STATIC_DRAW
        )
        gl.glVertexAttribPointer(
            3,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            0,
            ct.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(3)     

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_bitangents)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            bitangent_matrix.nbytes,
            bitangent_matrix.ctypes.data_as(ct.POINTER(ct.c_float)),
            gl.GL_STATIC_DRAW
        )
        gl.glVertexAttribPointer(
            4,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            0,
            ct.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(4)             

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
                loc = 5 + i
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
        self.buffers[f'vbo_{model_name}-textures'] = vbo_textures
        self.buffers[f'vbo-{model_name}-instances'] = vbo_instances
        self.buffers[f'vbo-{model_name}-tangents'] = vbo_tangents
        self.buffers[f'vbo-{model_name}-bitangents'] = vbo_bitangents        

    def setup_render_buffers(self, **kwargs):
        counts = kwargs.get('counts')
        self.models = kwargs.get('models', None)
        meshes = {
            'triangle': Triangle().mesh.copy(),
            'square': Square().mesh.copy(),
            'cube': Cube().mesh.copy(),
            'pyramid': Pyramid().mesh.copy(),
            #'teapot': Teapot().mesh.copy(),
        }
        norms = {
            'triangle': Triangle().mesh_normals.copy(),
            'square': Square().mesh_normals.copy(),
            'cube': Cube().mesh_normals.copy(),
            'pyramid': Pyramid().mesh_normals.copy(),
            #'teapot': Teapot().mesh_normals.copy(),
        }
        textures = {
            'triangle': Triangle().texture_coordinates.copy(),
            'square': Square().texture_coordinates.copy(),
            'cube': Cube().texture_coordinates.copy(),
            'pyramid': Pyramid().texture_coordinates.copy(),
            #'teapot': Teapot().texture_coordinates.copy(),
        }
        tangents = {
            'triangle': compute_tangents(meshes.get('triangle'), norms.get('triangle'), textures.get('triangle')),
            'square': compute_tangents(meshes.get('square'), norms.get('square'), textures.get('square')),
            'cube': compute_tangents(meshes.get('cube'), norms.get('cube'), textures.get('cube')),
            'pyramid': compute_tangents(meshes.get('pyramid'), norms.get('pyramid'), textures.get('pyramid')),
        }
        
        self.setup_object_buffer(
            model_name='triangle', 
            mesh_matrix=meshes.get('triangle'), 
            norms_matrix=norms.get('triangle'), 
            texture_matrix=textures.get('triangle'),
            instance_matrix=self.models.get('test-triangles'), 
            instance_count=counts.get('triangles', 0),
            tangent_matrix=tangents.get('triangle')[0],
            bitangent_matrix=tangents.get('triangle')[1]
        )

        self.setup_object_buffer(
            model_name='square', 
            mesh_matrix=meshes.get('square'), 
            norms_matrix=norms.get('square'), 
            texture_matrix=textures.get('square'),
            instance_matrix=self.models.get('test-squares'), 
            instance_count=counts.get('squares', 0),
            tangent_matrix=tangents.get('square')[0],
            bitangent_matrix=tangents.get('square')[1]
        )
        self.setup_object_buffer(
            model_name='cube', 
            mesh_matrix=meshes.get('cube'), 
            norms_matrix=norms.get('cube'), 
            texture_matrix=textures.get('cube'),
            instance_matrix=self.models.get('test-cubes'), 
            instance_count=counts.get('cubes', 0),
            tangent_matrix=tangents.get('cube')[0],
            bitangent_matrix=tangents.get('cube')[1]
        )
        self.setup_object_buffer(
            model_name='pyramid', 
            mesh_matrix=meshes.get('pyramid'), 
            norms_matrix=norms.get('pyramid'), 
            texture_matrix=textures.get('pyramid'),
            instance_matrix=self.models.get('test-pyramids'), 
            instance_count=counts.get('pyramid', 0),
            tangent_matrix=tangents.get('pyramid')[0],
            bitangent_matrix=tangents.get('pyramid')[1]
        )
        '''
        self.setup_object_buffer(
            model_name='teapot', 
            mesh_matrix=meshes.get('teapot'), 
            norms_matrix=norms.get('teapot'), 
            texture_matrix=textures.get('teapot'),
            instance_matrix=self.models.get('test-teapots'), 
            instance_count=counts.get('teapots', 0)
        )
        '''

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

    def load_texture_map(self, unit, texture_name, file_name):
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, '..', 'assets', 'textures', texture_name, file_name)
        
        if not os.path.exists(full_path):
            return None        
        
        texture = pyglet.image.load(full_path).get_texture()

        gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture.id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

        return texture
    
    def set_textures(self, name):
        if name == 'cobble':
            self.base_colour = self.load_texture_map(0, name, 'Wall_Stone_025_basecolor.png')
            self.height = self.load_texture_map(1, name, 'Wall_Stone_025_height.png')
            self.normal = self.load_texture_map(2, name, 'Wall_Stone_025_normal.png')
            self.roughness = self.load_texture_map(3, name, 'Wall_Stone_025_roughness.png')
            self.ambient_occlusion = self.load_texture_map(4, name, '/Wall_Stone_025_ambientOcclusion.png')
        elif name == 'cliffrock':
            self.base_colour = self.load_texture_map(0, name, 'Stylized_Cliff_Rock_006_basecolor.png')
            self.height = self.load_texture_map(1, name, 'Stylized_Cliff_Rock_006_height.png')
            self.normal = self.load_texture_map(2, name, 'Stylized_Cliff_Rock_006_normal.png')
            self.roughness = self.load_texture_map(3, name, 'Stylized_Cliff_Rock_006_roughness.png')
            self.ambient_occlusion = self.load_texture_map(4, name, 'Stylized_Cliff_Rock_006_ambientOcclusion.png')
        elif name == 'bark':
            self.base_colour = self.load_texture_map(0, name, 'Bark_06_BaseColor.jpg')
            self.height = self.load_texture_map(1, name, 'Bark_06_Height.png')
            self.normal = self.load_texture_map(2, name, 'Bark_06_Normal.jpg')
            self.roughness = self.load_texture_map(3, name, 'Bark_06_Roughness.jpg')
            self.ambient_occlusion = self.load_texture_map(4, name, 'Bark_06_AmbientOcclusion.jpg')
        elif name == 'rockmoss':
            self.base_colour = self.load_texture_map(0, name, 'Rock_Moss_001_basecolor.jpg')
            self.height = self.load_texture_map(1, name, 'Rock_Moss_001_height.png')
            self.normal = self.load_texture_map(2, name, 'Rock_Moss_001_normal.jpg')
            self.roughness = self.load_texture_map(3, name, 'Rock_Moss_001_roughness.jpg')
            self.ambient_occlusion = self.load_texture_map(4, name, 'Rock_Moss_001_ambientOcclusion.jpg')
        elif name == 'paintedmetal':
            self.base_colour = self.load_texture_map(0, name, 'Metal_Painted_001_basecolor.jpg')
            self.height = self.load_texture_map(1, name, 'Metal_Painted_001_height.png')
            self.normal = self.load_texture_map(2, name, 'Metal_Painted_001_normal.jpg')
            self.roughness = self.load_texture_map(3, name, 'Metal_Painted_001_roughness.jpg')
            self.ambient_occlusion = self.load_texture_map(4, name, 'Metal_Painted_001_ambientOcclusion.jpg')

    def on_draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glUseProgram(self.render_program)
        self.update_view(self.window.play_state.camera)
        self.update_light_position(self.window.play_state.light['position'])
        self.update_texture()
        self.update_normal()
        self.update_height()
        self.update_roughness()
        self.update_ao()
        self.update_view_position(self.window.play_state.camera.position)

        for model in self.objects.values():
            self.draw_object(model['name'], model['count'])

    def update_texture(self):
        gl.glUseProgram(self.render_program)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.base_colour.id)
        tex_loc = gl.glGetUniformLocation(self.render_program, b'textureSampler')
        gl.glUniform1i(tex_loc, 0)

    def update_normal(self):
        gl.glUseProgram(self.render_program)
        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.normal.id)
        tex_loc = gl.glGetUniformLocation(self.render_program, b'normalMap')
        gl.glUniform1i(tex_loc, 2)

    def update_height(self):
        gl.glUseProgram(self.render_program)
        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.height.id)
        tex_loc = gl.glGetUniformLocation(self.render_program, b'heightMap')
        gl.glUniform1i(tex_loc, 1)       

    def update_roughness(self):
        gl.glUseProgram(self.render_program)
        gl.glActiveTexture(gl.GL_TEXTURE3)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.roughness.id)
        tex_loc = gl.glGetUniformLocation(self.render_program, b'roughnessMap')
        gl.glUniform1i(tex_loc, 3)     

    def update_ao(self):
        if self.ambient_occlusion is not None:
            gl.glUseProgram(self.render_program)
            gl.glActiveTexture(gl.GL_TEXTURE4)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.ambient_occlusion.id)
            tex_loc = gl.glGetUniformLocation(self.render_program, b'aoMap')
            gl.glUniform1i(tex_loc, 4)        

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

    def update_light_position(self, light_position):
        gl.glUseProgram(self.render_program)

        light_loc = gl.glGetUniformLocation(self.render_program, b'lightPos')

        gl.glUniform3fv(
            light_loc,
            1,
            light_position.ctypes.data_as(ct.POINTER(ct.c_float))
        )

    def update_view_position(self, view_pos):
        gl.glUseProgram(self.render_program)
        view_loc = gl.glGetUniformLocation(self.render_program, b'viewPos')
        gl.glUniform3fv(
            view_loc,
            1,
            view_pos.ctypes.data_as(ct.POINTER(ct.c_float))
        )

    def draw_object(self, object_model, object_count):
        face_count = self.f_count[f'{object_model}']
        vertex_draw_count = 3 * face_count
        gl.glBindVertexArray(self.buffers[f'vao-{object_model}'])
        gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, vertex_draw_count, object_count)