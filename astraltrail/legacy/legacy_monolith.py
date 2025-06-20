import pyglet
from pyglet.window import key
import pyglet.gl as gl
import ctypes as ct
import numpy as np
import random
from dataclasses import dataclass, field

fps = 60.0
width = 1280
height = 720
caption = 'Astral Proton'
config = gl.Config(double_buffer=True, depth_size=24)
keys = pyglet.window.key.KeyStateHandler()
mouse = {
    'x': 0.0,
    'y': 0.0,
    'dx': 0.0,
    'dy': 0.0,
    'left': False,
    'right': False
}

window = pyglet.window.Window(
    width, 
    height, 
    caption, 
    config=config
)
window.set_exclusive_mouse()

@window.event
def on_mouse_motion(x, y, dx, dy):
    mouse['x'] = x
    mouse['y'] = y
    mouse['dx'] = dx
    mouse['dy'] = dy

light_position = np.array([1000.0, 300.0, -150.0], dtype=np.float32)

camera = {
    'pos': np.array([0.0, 1.5, -5.0], dtype=np.float32),
    'yaw': 0.0,
    'pitch': 0.0,                
    'roll': 0.0,
    'fov': 0.0,
    'near': 0.0,
    'far': 0.0,
    'aspect': width / height            
}

x_rate = 3
y_rate = 3
z_rate = 3

h_sensitivity = 3
v_sensitivity = 3
t_sensitivity = 1

vertex_shader_source_string = b'''
    #version 330 core

    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec3 aNorm;
    layout (location = 2) in mat4 model;

    uniform mat4 view;
    uniform mat4 proj;

    out vec3 FragNorm;
    out vec3 FragPos;

    void main() {
        vec4 wPos = model * vec4(aPos, 1.0);
        vec4 pPos = view * wPos;
        vec4 NDC = proj * pPos;
        gl_Position = NDC;

        mat3 normalMatrix = mat3(model);

        FragNorm = normalize(normalMatrix * aNorm);

        FragPos = vec3(wPos);
    }
'''

fragment_shader_source_string = b'''
    #version 330 core

    in vec3 FragNorm;
    in vec3 FragPos;

    uniform vec3 lightPos;

    out vec4 FragColour;

    void main() {
        vec3 colour = vec3(0.8, 0.2, 0.1);

        float ambient = 0.15;

        vec3 lightDir = normalize(lightPos - FragPos);

        float diffuse = max(0.0, dot(lightDir, FragNorm));

        float intensity = ambient + diffuse;

        FragColour = vec4(intensity * colour, 1.0);
    }
'''

next_id = 0
active_entities = set()

def grow_capacity():
    global positions, alive
    old_cap = len(alive)
    new_cap = old_cap * 2

    def grow(arr: np.ndarray, shape):
        return np.concatenate([arr, np.zeros(shape, dtype=arr.dtype)], axis=0)

    positions = grow(positions, (old_cap, 3))
    alive = np.concatenate([alive, np.zeros(old_cap, dtype=bool)])

def create_entity():
    global entity_count
    global alive
    if free_indices:
        idx = free_indices.pop()
    else:
        if entity_count >= len(alive):
            grow_capacity()
        idx = entity_count
        entity_count += 1
    alive[idx] = True

def destroy_entity(idx):
    alive[idx] = False
    free_indices.append(idx)
    
NUM_CAMERAS = 10
ENT_CAP = 1024
# approx 8 million vertices as an inital capacity 
# 320 MB per buffer, about 230,000 fully rendered cubes, reaching approximately 2.5GB to 3GB VRAM
# This is a liberal estimate using worse-case rendering scenario of a highly complex chunk.
VERTEX_CAP = 2 ** 23 
entity_count = 0
free_indices = []
alive = None
positions = None
orientations = None
camera_parameters = None
movement_states = None

static_mesh_pool = {}

def initiate_ecs():
    global positions, orientations, movement_states, camera_parameters, alive

    positions = np.zeros((ENT_CAP, 3), dtype=np.float32)
    orientations = np.zeros((ENT_CAP, 3), dtype=np.float32)

    camera_parameters = np.zeros((NUM_CAMERAS, 4), dtype=np.float32)
    camera_parameters[:, 0] = 120.0 # fov default
    camera_parameters[:, 1] = 0.01 # near plane default
    camera_parameters[:, 2] = 1000.0 # far_plane default
    camera_parameters[:, 3] = 1.0 # aspect ratio default

    movement_states = np.zeros((ENT_CAP, 6), dtype=np.float32)

    alive = np.zeros(ENT_CAP, dtype=bool)

@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

@dataclass
class Orientation:
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0

@dataclass
class CameraConfigation:
    fov: float = 45.0
    near: float = 0.01
    far: float = 1000.0
    aspect: float = 1.0

@dataclass
class Movement:
    dx: float = 0.0
    dy: float = 0.0
    dz: float = 0.0
    dyaw: float = 0.0
    dpitch: float = 0.0
    droll: float = 0.0

@dataclass
class MeshInstance:
    vertices: np.ndarray = field(default_factory=lambda: np.zeros((0, 3), dtype=np.float32))
    normals: np.ndarray = field(default_factory=lambda: np.zeros((0, 3), dtype=np.float32))
    model: np.ndarray = field(default_factory=lambda: np.eye(4, dtype=np.float32))

@dataclass
class LightConfiguration:
    intensity: float = 1.0
    colour: tuple = (1.0, 1.0, 1.0)

@dataclass
class InputState:
    mouse_dx: float = 0
    mouse_dy: float = 0
    mouse_x: float = 0
    mouse_y: float = 0
    keymap: dict = field(default_factory=dict)

@dataclass
class ClockState:
    cum_time: float = 0.0

def create_shader(source_string, shader_type):
    shader_buffer = ct.create_string_buffer(source_string)
    shader_length = ct.c_int(len(source_string))
    shader_pointer = ct.cast(
        ct.pointer(ct.pointer(shader_buffer)),
        ct.POINTER(ct.POINTER(ct.c_char))
    )
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(
        shader, 
        1, 
        shader_pointer, 
        ct.byref(shader_length)
    )

    gl.glCompileShader(shader)

    return shader
    
def create_shader_program():
    vertex_shader = create_shader(vertex_shader_source_string, gl.GL_VERTEX_SHADER)
    fragment_shader = create_shader(fragment_shader_source_string, gl.GL_FRAGMENT_SHADER)

    program = gl.glCreateProgram()

    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)

    gl.glLinkProgram(program)

    return program

def update(dt, program):
    update_uniforms(program, dt)
    mouse['dx'] = 0
    mouse['dy'] = 0

def setup_gl(program):
    gl.glUseProgram(program)
    gl.glClearColor(0.1, 0.1, 0.1, 1.0)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_CULL_FACE)
    gl.glFrontFace(gl.GL_CCW)

def setup_vao():
    vao = gl.GLuint()
    gl.glGenVertexArrays(1, ct.byref(vao))

    return vao

def set_attribute_pointer(pointer, length, stride, offset):
    gl.glEnableVertexAttribArray(pointer)
    gl.glVertexAttribPointer(
        pointer,
        length,
        gl.GL_FLOAT,
        gl.GL_FALSE,
        stride,
        ct.c_void_p(offset)
    )

def setup_vbo(shape, vbo, array: np.ndarray, type, pointer):
    gl.glGenBuffers(1, ct.byref(vbo))
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(
        gl.GL_ARRAY_BUFFER,
        array.nbytes,
        array.ctypes.data_as(ct.POINTER(ct.c_float)),
        type
    )

    if shape=='mat4':
        for i in range(4):
            loc = pointer + i
            set_attribute_pointer(loc, 4, 64, i * 16)
            gl.glVertexAttribDivisor(loc, 1)

    elif shape=='vec3':
        set_attribute_pointer(pointer, 3, 12, 0)


    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)


def setup_buffers(mesh, normals):
    vao = setup_vao()

    gl.glBindVertexArray(vao)
    
    mesh_vbo = gl.GLuint()
    setup_vbo('vec3', mesh_vbo, mesh, gl.GL_STATIC_DRAW, 0)

    normals_vbo = gl.GLuint()
    setup_vbo('vec3', normals_vbo, normals, gl.GL_STATIC_DRAW, 1)

    models_vbo = gl.GLuint()
    model = np.eye(4, dtype=np.float32)
    setup_vbo('mat4', models_vbo, model, gl.GL_STATIC_DRAW, 2)

    return vao

def get_occlusion_map(chunk_data, address):
    x, y, z = address
    size = chunk_data.shape[0]
    offsets = [
        (0, 0, 1), (0, 0, -1),
        (-1, 0, 0), (1, 0, 0),
        (0, 1, 0), (0, -1, 0),
    ]
    occlusion_map = [0] * 6
    for face, (dx, dy, dz) in enumerate(offsets):
        delx, dely, delz = x + dx, y + dy, z + dz
        check_address = (x + delx, y + dely, z + delz)
        if 0 <= delx < size and 0 <= dely < size and 0 <= delz < size:
            if chunk_data[delx, dely, delz] > 0:
                occlusion_map[face] = 1

    return occlusion_map

def test_mesh_chunk_manual(chunk_data, size):
    mesh = []
    normals = []
    cube_count = 0

    for i in range(size):
        for j in range(size):
            for k in range(size):
                address = (i, j, k)
                if chunk_data[address] == 1:
                    occlusion_map = get_occlusion_map(chunk_data, address)
                    msh, nrms = test_mesh_single_cube(occlusion_map, offset=address)
                    mesh.extend(msh)
                    normals.extend(nrms)
                    cube_count += 1

    return mesh, normals, cube_count

def test_mesh_single_cube(occlusion_map:list[int]=(0,0,0,0,0,0), offset:tuple[int]=(0,0,0)):
    # Left face is the one facing +x
    # Front Face is the on facing +z
    # Top Face is the one facing +y
    off_x, off_y, off_z = offset
    vertices = [
        [-0.5 + off_x, 0.5 + off_y, 0.5 + off_z], # front-top-right
        [-0.5 + off_x, -0.5 + off_y, 0.5 + off_z], # front-bottom-right
        [0.5 + off_x, -0.5 + off_y, 0.5 + off_z], # front-bottom-left
        [0.5 + off_x, 0.5 + off_y, 0.5 + off_z], # front-top-left
        [0.5 + off_x, 0.5 + off_y, -0.5 + off_z], # back-top-left
        [0.5 + off_x, -0.5 + off_y, -0.5 + off_z], # back-bottom-left
        [-0.5 + off_x, -0.5 + off_y, -0.5 + off_z], # back-bottom-right
        [-0.5 + off_x, 0.5 + off_y, -0.5 + off_z] # back-top-right
    ]

    normals = [
        [0.0, 0.0, 1.0], # front +z
        [0.0, 0.0, -1.0], # back -z
        [-1.0, 0.0, 0.0], # right -x
        [1.0, 0.0, 0.0], # left +x
        [0.0, 1.0, 0.0], # top +y
        [0.0, -1.0, 0.0] # bottom -y
    ]

    mesh_order = [
        0, 1, 2, 2, 3, 0, # front +z
        4, 5, 6, 6, 7, 4, # back -z
        7, 6, 1, 1, 0, 7, # right -x
        3, 2, 5, 5, 4, 3, # left +x
        7, 0, 3, 3, 4, 7, # top +y
        1, 6, 5, 5, 2, 1 # bottom -y
    ]

    mesh = []
    norms = []

    for index in range(6):
        if occlusion_map[index] < 1:
            face_vertices = mesh_order[index * 6 : (index + 1) * 6]
            mesh.extend([vertices[i] for i in face_vertices])
            norms.extend([normals[index]] * 6)
    
    return mesh, norms

def generate_view_matrix(pos, y, p, r):
    posx, posy, posz = pos
    yaw = np.radians(y + 180.0)
    pitch = np.radians(p)
    roll = np.radians(r)

    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cr, sr = np.cos(roll), np.sin(roll)   

    yaw_matrix = np.eye(4, dtype=np.float32)
    yaw_matrix[0, 0] = cy 
    yaw_matrix[2, 2] = cy 
    yaw_matrix[0, 2] = -sy 
    yaw_matrix[2, 0] = sy 

    pitch_matrix = np.eye(4, dtype=np.float32)
    pitch_matrix[1, 1] = cp 
    pitch_matrix[2, 2] = cp 
    pitch_matrix[1, 2] = sp 
    pitch_matrix[2, 1] = -sp

    roll_matrix = np.eye(4, dtype=np.float32)
    roll_matrix[0, 0] = cr 
    roll_matrix[1, 1] = cr
    roll_matrix[0, 1] = -sr
    roll_matrix[1, 0] = sr  

    pos_matrix = np.eye(4, dtype=np.float32)
    pos_matrix[0, 3] = -posx
    pos_matrix[1, 3] = -posy      
    pos_matrix[2, 3] = -posz

    rotation_matrix = roll_matrix.T @ pitch_matrix.T @ yaw_matrix.T

    view = rotation_matrix @ pos_matrix

    return view

def generate_proj_matrix(fov, aspect, near, far):
    f = 1 / np.tan(fov / 2)
    z = (near + far) / (near - far)
    z_offset = (2 * near * far) / (near - far)
    proj = np.zeros((4, 4), dtype=np.float32)
    proj[0, 0] = f / aspect
    proj[1, 1] = f
    proj[2, 2] = z
    proj[2, 3] = z_offset
    proj[3, 2] = -1.0
    
    return proj

def get_camera_movement_state():
    dx = 0
    dy = 0
    dz = 0
    dyaw = 0
    dpitch = 0
    droll = 0

    if keys[key.ESCAPE]:
        window.close()

    if keys[key.W]:
        dz = 1

    if keys[key.A]:
        dx = 1

    if keys[key.S]:
        dz = -1

    if keys[key.D]:
        dx = -1

    if keys[key.SPACE]:
        dy = 1

    if keys[key.LCTRL]:
        dy = -1

    dyaw = mouse['dx']
    dpitch = -mouse['dy']

    rotation = (dyaw, dpitch, droll)
    movement = (dx, dy, dz)        

    return rotation, movement

def get_forward_vector(config):
    north = np.array([0.0, 0.0, 1.0], dtype=np.float32)

    yaw = np.radians(camera['yaw'])
    pitch = np.radians(camera['pitch'])

    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)

    yaw_matrix = np.eye(3, dtype=np.float32)
    yaw_matrix[0, 0] = cy
    yaw_matrix[0, 2] = -sy
    yaw_matrix[2, 0] = sy
    yaw_matrix[2, 2] = cy

    pitch_matrix = np.eye(3, dtype=np.float32)
    pitch_matrix[1, 1] = cp
    pitch_matrix[1, 2] = sp
    pitch_matrix[2, 1] = -sp
    pitch_matrix[2, 2] = cp

    if config==1:     
        forward = yaw_matrix @ pitch_matrix @ north
    elif config==0:
        forward = yaw_matrix @ north

    return forward

def get_left_vector(config):
    west = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    yaw = np.radians(camera['yaw'])
    roll = np.radians(camera['roll'])

    cy, sy = np.cos(yaw), np.sin(yaw)
    cr, sr = np.cos(roll), np.sin(roll)

    yaw_matrix = np.eye(3, dtype=np.float32)
    yaw_matrix[0, 0] = cy
    yaw_matrix[0, 2] = -sy
    yaw_matrix[2, 0] = sy
    yaw_matrix[2, 2] = cy

    roll_matrix = np.eye(3, dtype=np.float32)
    roll_matrix[0, 0] = cr
    roll_matrix[0, 1] = -sr
    roll_matrix[1, 0] = sr
    roll_matrix[1, 1] = cr

    if config==0:
        left = yaw_matrix @ west
    if config==1:
        left = yaw_matrix @ roll_matrix @ west

    return left

def get_up_vector(config):
    up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    if config==0:
        return up

def update_camera(delta_t):
    rotation, movement = get_camera_movement_state()
    dyaw, dpitch, droll = rotation
    dx, dy, dz = movement

    forward_vector = get_forward_vector(0)
    forward_movement = dz * z_rate * delta_t * forward_vector
    left_vector = get_left_vector(0)
    left_movement = dx * x_rate * delta_t * left_vector
    up_vector = get_up_vector(0)
    up_movement = dy * y_rate * delta_t * up_vector

    movement = forward_movement + left_movement + up_movement
    camera['pos'] += movement


    camera['yaw'] += dyaw * h_sensitivity * delta_t
    camera['pitch'] = max(min(camera['pitch'] + dpitch * v_sensitivity * delta_t, 89.9), -89.9)
    camera['roll'] += droll * t_sensitivity * delta_t


    return camera['pos'], camera['yaw'], camera['pitch'], camera['roll']

def update_uniforms(program, delta_t):
    view_loc = gl.glGetUniformLocation(program, b'view')
    light_loc = gl.glGetUniformLocation(program, b'lightPos')

    pos, yaw, pitch, roll = update_camera(delta_t)

    view = generate_view_matrix(pos, yaw, pitch, roll)

    gl.glUniformMatrix4fv(
        view_loc,
        1,
        gl.GL_FALSE,
        view.T.flatten().ctypes.data_as(ct.POINTER(ct.c_float))
    )

    gl.glUniform3fv(
        light_loc,
        1,
        light_position.ctypes.data_as(ct.POINTER(ct.c_float))
    )

def initiate_uniforms(program):
    view_loc = gl.glGetUniformLocation(program, b'view')
    proj_loc = gl.glGetUniformLocation(program, b'proj')
    light_loc = gl.glGetUniformLocation(program, b'lightPos')

    pos = np.array([0.0, 1.5, -5.0], dtype=np.float32)
    yaw = 0.0
    pitch = 0.0
    roll = 0.0
    fov = 45.0
    aspect = width / height
    near = 0.01
    far = 500.0

    view = generate_view_matrix(pos, yaw, pitch, roll)
    proj = generate_proj_matrix(fov, aspect, near, far)
    light_position = np.array([1000.0, 300.0, -150.0], dtype=np.float32)

    gl.glUniformMatrix4fv(
        view_loc,
        1,
        gl.GL_FALSE,
        view.T.flatten().ctypes.data_as(ct.POINTER(ct.c_float))
    )

    gl.glUniformMatrix4fv(
        proj_loc,
        1,
        gl.GL_FALSE,
        proj.T.flatten().ctypes.data_as(ct.POINTER(ct.c_float))
    )

    gl.glUniform3fv(
        light_loc,
        1,
        light_position.ctypes.data_as(ct.POINTER(ct.c_float))
    )

def generate_test_chunk(test, size):
    chunk_data = np.zeros((size, size, size), dtype=np.int8)
    for i in range(size):
        for j in range(size):
            for k in range(size):
                address = (i, j, k)
                if test == 'test-chunk-1':
                    if i == 15 or k == 15 or j == 0:
                        chunk_data[address] = 1
                elif test == 'random':
                    chunk_data[address] = random.randint(0,1)

                elif test == 'sphere':
                    half = size // 2
                    center = np.array([half, half, half])
                    pos = np.array([i, j, k])
                    radius = half - 1.5
                    if np.linalg.norm(pos - center) <= radius:
                        chunk_data[address] = 1


    return chunk_data

def main():
    def on_draw():
        gl.glUseProgram(program)
        gl.glBindVertexArray(vao)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glDrawArraysInstanced(gl.GL_TRIANGLES, 0, vertex_count, 1)

    program = create_shader_program()

    size = 64
    chunk_data = generate_test_chunk('sphere', size)

    mesh, normals, cube_count = test_mesh_chunk_manual(chunk_data, size)

    mesh = np.array(mesh, dtype=np.float32)
    normals = np.array(normals, dtype=np.float32)

    vao = setup_buffers(mesh, normals)
    vertex_count = 36 * cube_count

    setup_gl(program)

    initiate_uniforms(program)

    window.push_handlers(
        keys,
        on_draw=on_draw,
    )

    pyglet.clock.schedule_interval(lambda dt: update(dt, program), 1 / fps)

    pyglet.app.run()

if __name__=='__main__':
    main()

