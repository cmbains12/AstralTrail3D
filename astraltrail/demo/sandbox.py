import pyglet
import pyglet.gl as gl
from pyglet.window import key
import numpy as np
import ctypes as ct
from scipy.ndimage import distance_transform_edt as edt 
from scipy.ndimage import zoom, gaussian_filter
import skfmm

from astraltrail.src.engine.ecs.component import ComponentManager
from astraltrail.src.engine.ecs.entity import EntityManager
from astraltrail.src.engine.ecs.system import SystemManager
from marching_cubes_triangle_table import TRIANGLE_TABLE, EDGE_TABLE

corner_offsets = np.array([
    [0, 0, 0],
    [1, 0, 0],
    [1, 1, 0],
    [0, 1, 0],
    [0, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 1, 1],
], dtype=np.int32)

edge_corner_pairs = [
    [0,1], [1,2], [2,3], [3,0],
    [4,5], [5,6], [6,7], [7,4],
    [0,4], [1,5], [2,6], [3,7]
]

fps = 60.0
width = 1280
height = 720
caption = 'Astral Ion'
config = gl.Config(
    double_buffer = True,
    depth_size = 24,
)

window = pyglet.window.Window(
    width,
    height,
    caption,
    config=config
)

keys = pyglet.window.key.KeyStateHandler()
mouse = {
    'x': 0.0,
    'y': 0.0,
    'dx': 0.0,
    'dy': 0.0,
    'left': False,
    'right': False
}
x_rate = 3
y_rate = 3
z_rate = 3

h_sensitivity = 3
v_sensitivity = 3
t_sensitivity = 1

window.set_exclusive_mouse()

@window.event
def on_mouse_motion(x, y, dx, dy):
    mouse['x'] = x
    mouse['y'] = y
    mouse['dx'] = dx
    mouse['dy'] = dy

rast_vertex_shader_source_string = b'''
    #version 330 core

    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec3 aNorm;

    uniform mat4 view;
    uniform mat4 proj;

    out vec3 FragNorm;
    out vec3 FragPos;

    void main() {
        mat4 model = mat4(1.0);
        vec4 wPos = model * vec4(aPos, 1.0);
        vec4 pPos = view * wPos;
        vec4 NDC = proj * pPos;
        gl_Position = NDC;

        mat3 normalMatrix = mat3(model);

        FragNorm = normalize(normalMatrix * aNorm);

        FragPos = vec3(wPos);
    }
'''

rast_fragment_shader_source_string = b'''
    #version 330 core

    in vec3 FragNorm;
    in vec3 FragPos;

    uniform vec3 lightPos;

    out vec4 FragColour;

    void main() {
        vec3 colour = vec3(0.8, 0.2, 0.1);

        float ambient = 0.15;

        vec3 lightDir = normalize(lightPos - FragPos);

        float diffuse = max(0.0, dot(lightDir, normalize(FragNorm)));

        float intensity = ambient + diffuse;

        FragColour = vec4(intensity * colour, 1.0);
    }
'''
rmarch_vertex_shader_source_string = b'''

'''
rmarch_fragment_shader_source_string = b'''

'''

rast_program = None
rmarch_program = None

light_position = np.array([1000.0, 300.0, -150.0], dtype=np.float32)

camera = {
    'pos': np.array([0.0, 1.5, -5.0], dtype=np.float32),
    'yaw': 0.0,
    'pitch': 0.0,                
    'roll': 0.0,
    'fov': 45.0,
    'near': 0.01,
    'far': 100.0,
    'aspect': width / height            
}

def main(mode='minecraft'):
    print(f'[SANDBOX]-{mode.upper()}')
    
    voxel_scale = 0.1
    sdf_zoom = 4

    iso = -0.1
    voxel_chunk = generate_voxel_grid('cube', size=16)

    if mode=='minecraft':
        mesh, normals, vertex_count = generate_naive_surface_mesh(voxel_chunk, cube_scale=voxel_scale)
    elif mode=='cube-march':
        sdf_field = voxel_to_sdf_cubical(voxel_chunk, upsample=sdf_zoom, smoothing_sigma=0.1)
        smoothed_field = gaussian_filter(sdf_field, sigma=0.4)
        mesh, normals, vertex_count = cube_march(sdf_field=smoothed_field, iso_level=iso, scale=voxel_scale)

    rast_vao = send_to_gl(mesh, normals)

    global rast_program, rmarch_program
    rast_program = create_shader_program('raster')
    #rmarch_program = create_shader_program('rmarch')

    setup_gl(rast_program)
    initiate_uniforms(rast_program)

    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glUseProgram(rast_program)
        gl.glBindVertexArray(rast_vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, vertex_count)
    
    window.push_handlers(
        keys,
        on_draw=on_draw
    )

    pyglet.clock.schedule_interval(update, 1 / fps)
    pyglet.app.run()

def compute_normal(sdf, pos, delta=0.5):
    dx = trilinear_sdf_sample(sdf, pos + [delta, 0, 0]) - trilinear_sdf_sample(sdf, pos - [delta, 0, 0])
    dy = trilinear_sdf_sample(sdf, pos + [0, delta, 0]) - trilinear_sdf_sample(sdf, pos - [0, delta, 0])
    dz = trilinear_sdf_sample(sdf, pos + [0, 0, delta]) - trilinear_sdf_sample(sdf, pos - [0, 0, delta])
    normal = np.array([dx, dy, dz], dtype=np.float32)
    norm = np.linalg.norm(normal)
    return normal / norm if norm > 0 else np.array([0.0, 1.0, 0.0], dtype=np.float32)

def interpolate_vertex(p1, p2, v1, v2, iso_level):
    if abs(v1 - v2) < 1e-12:
        return (p1 + p2) * 0.5
    t = np.clip((iso_level - v1) / (v2 - v1), 0.0, 1.0)
    return p1 + t * (p2 - p1)

def cube_march(sdf_field, iso_level=0.0, scale=0.05):
    size_x, size_y, size_z = sdf_field.shape
    vertices = []
    normals = []

    for x in range(size_x - 1):
        for y in range(size_y - 1):
            for z in range(size_z - 1):
                cube_corner_positions = []
                cube_corner_values = []

                for i in range(8):
                    offset = corner_offsets[i]
                    pos = np.array([x, y, z], dtype=np.float32) + offset  # floating point position in grid coords
                    val = trilinear_sdf_sample(sdf_field, pos)            # interpolate SDF
                    world_pos = pos * scale                         # convert to world space
                    cube_corner_positions.append(world_pos)
                    cube_corner_values.append(val)

                cube_index = 0
                for i in range(8):
                    if cube_corner_values[i] < iso_level:  # Use <= for full face capture
                        cube_index |= (1 << i)

                if EDGE_TABLE[cube_index] == 0:
                    continue

                edge_vertices = [None] * 12
                for i in range(12):
                    if EDGE_TABLE[cube_index] & (1 << i):
                        a, b = edge_corner_pairs[i]
                        p1 = cube_corner_positions[a]
                        p2 = cube_corner_positions[b]
                        v1 = cube_corner_values[a]
                        v2 = cube_corner_values[b]
                        edge_vertices[i] = interpolate_vertex(p1, p2, v1, v2, iso_level)

                tri_indices = TRIANGLE_TABLE[cube_index]
                for i in range(0, len(tri_indices), 3):
                    a, b, c = tri_indices[i], tri_indices[i + 1], tri_indices[i + 2] 
                    if a == -1 or b == -1 or c == -1:
                        break
                    va = edge_vertices[a]
                    vb = edge_vertices[b]
                    vc = edge_vertices[c]


                    if va is None or vb is None or vc is None:
                        continue

                    vertices.extend([va, vc, vb])

                    for v in (va, vc, vb):
                        grid_pos = v / scale
                        normal = compute_normal(sdf_field, grid_pos, delta=0.5)
                        normals.append(normal)




    vertex_array = np.array(vertices, dtype=np.float32)
    normal_array = np.array(normals, dtype=np.float32)
    vertex_count = len(vertex_array)
    return vertex_array, normal_array, vertex_count

from scipy.ndimage import map_coordinates

def trilinear_sdf_sample(sdf, pos):
    coords = np.array(pos, dtype=np.float32).reshape(3, 1)
    return map_coordinates(sdf, coords, order=1, mode='nearest')[0]

def update(dt):
    update_uniforms(dt)
    mouse['dx'] = 0
    mouse['dy'] = 0

def initiate_uniforms(program):
    gl.glUseProgram(program)

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

    global light_position

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
    f = 1 / np.tan(np.radians(fov) / 2)
    z = (near + far) / (near - far)
    z_offset = (2 * near * far) / (near - far)
    proj = np.zeros((4, 4), dtype=np.float32)
    proj[0, 0] = f / aspect
    proj[1, 1] = f
    proj[2, 2] = z
    proj[2, 3] = z_offset
    proj[3, 2] = -1.0
    
    return proj

def update_uniforms(delta_t):
    global rast_program, light_position
    view_loc = gl.glGetUniformLocation(rast_program, b'view')
    light_loc = gl.glGetUniformLocation(rast_program, b'lightPos')

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

def setup_gl(program):
    gl.glUseProgram(program)
    gl.glClearColor(0.1, 0.1, 0.1, 1.0)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_CULL_FACE)
    gl.glFrontFace(gl.GL_CCW)    

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
    
def create_shader_program(type='raster'):
    if type=='raster':
        vshader = rast_vertex_shader_source_string
        fshader = rast_fragment_shader_source_string
    elif type=='rmarch':
        vshader = rmarch_vertex_shader_source_string
        fshader = rmarch_fragment_shader_source_string

    vertex_shader = create_shader(vshader, gl.GL_VERTEX_SHADER)
    fragment_shader = create_shader(fshader, gl.GL_FRAGMENT_SHADER)

    program = gl.glCreateProgram()

    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)

    gl.glLinkProgram(program)

    return program

def send_to_gl(mesh, normals):
    vao = gl.GLuint()
    vbo_mesh = gl.GLuint()
    vbo_normals = gl.GLuint()

    gl.glGenVertexArrays(1, ct.byref(vao))
    gl.glGenBuffers(1, ct.byref(vbo_mesh))
    gl.glGenBuffers(1, ct.byref(vbo_normals))

    gl.glBindVertexArray(vao)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_mesh)
    gl.glBufferData(
        gl.GL_ARRAY_BUFFER,
        mesh.nbytes,
        mesh.ctypes.data_as(ct.POINTER(ct.c_float)),
        gl.GL_STATIC_DRAW
    )
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(
        0,
        3,
        gl.GL_FLOAT,
        gl.GL_FALSE,
        0,
        ct.c_void_p(0)
    )
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_normals)
    gl.glBufferData(
        gl.GL_ARRAY_BUFFER,
        normals.nbytes,
        normals.ctypes.data_as(ct.POINTER(ct.c_float)),
        gl.GL_STATIC_DRAW
    )
    gl.glEnableVertexAttribArray(1)
    gl.glVertexAttribPointer(
        1, 
        3,
        gl.GL_FLOAT,
        gl.GL_FALSE,
        0,
        ct.c_void_p(0)
    )
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

    return vao

def greedy_mesh(voxels):
    assert voxels.ndim == 3
    size_x, size_y, size_z = voxels.shape
    quads = []

    for axis in range(3):  # 0=x, 1=y, 2=z
        u = (axis + 1) % 3
        v = (axis + 2) % 3
        dims = [size_x, size_y, size_z]

        for d in range(dims[axis] + 1):
            mask = np.zeros((dims[u], dims[v]), dtype=np.int8)

            for i in range(dims[u]):
                for j in range(dims[v]):
                    pos1 = [0, 0, 0]
                    pos2 = [0, 0, 0]
                    pos1[axis] = d
                    pos2[axis] = d - 1
                    pos1[u] = pos2[u] = i
                    pos1[v] = pos2[v] = j

                    solid1 = 0 <= pos1[axis] < dims[axis] and voxels[tuple(pos1)]
                    solid2 = 0 <= pos2[axis] < dims[axis] and voxels[tuple(pos2)]

                    if solid1 and not solid2:
                        mask[i, j] = 1  # face on negative side (back face)
                    elif solid2 and not solid1:
                        mask[i, j] = -1  # face on positive side (front face)

            visited = np.zeros_like(mask, dtype=bool)

            for i in range(dims[u]):
                for j in range(dims[v]):
                    if visited[i, j] or mask[i, j] == 0:
                        continue

                    normal = mask[i, j]
                    w, h = 1, 1
                    while j + w < dims[v] and mask[i, j + w] == normal and not visited[i, j + w]:
                        w += 1
                    while i + h < dims[u] and np.all(mask[i + h, j:j + w] == normal) and not np.any(visited[i + h, j:j + w]):
                        h += 1

                    visited[i:i + h, j:j + w] = True

                    origin = [0, 0, 0]
                    origin[u] = i
                    origin[v] = j
                    origin[axis] = d if normal == -1 else d - 1

                    size = [1, 1, 1]
                    size[u] = h
                    size[v] = w

                    normal_vec = [0, 0, 0]
                    normal_vec[axis] = normal

                    quads.append((tuple(origin), tuple(size), tuple(normal_vec)))

    return quads

import numpy as np

def generate_naive_surface_mesh(voxels, cube_scale=0.1):
    # Face directions and CORRECTED CCW corner order (from outside the cube)
    faces = {
        'px': ([1, 0, 0], [(1, 1, 0), (1, 1, 1), (1, 0, 1), (1, 0, 0)]),   # +X
        'nx': ([-1, 0, 0], [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),  # -X
        'py': ([0, 1, 0], [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),   # +Y
        'ny': ([0, -1, 0], [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),  # -Y
        'pz': ([0, 0, 1], [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),   # +Z
        'nz': ([0, 0, -1], [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]),  # -Z
    }

    vertices = []
    normals = []

    sx, sy, sz = voxels.shape

    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                if not voxels[x, y, z]:
                    continue

                for normal, corner_offsets in faces.values():
                    nx, ny, nz = x + normal[0], y + normal[1], z + normal[2]

                    if not (0 <= nx < sx and 0 <= ny < sy and 0 <= nz < sz and voxels[nx, ny, nz]):
                        quad = [(x + ox, y + oy, z + oz) for ox, oy, oz in corner_offsets]
                        quad = np.array(quad, dtype=np.float32) * cube_scale

                        # Emit two CCW triangles
                        tri1 = [quad[0], quad[1], quad[2]]
                        tri2 = [quad[0], quad[2], quad[3]]

                        vertices.extend(tri1 + tri2)
                        normals.extend([normal] * 6)

    vertex_array = np.array(vertices, dtype=np.float32)
    normal_array = np.array(normals, dtype=np.float32)
    vertex_count = len(vertex_array)

    return vertex_array, normal_array, vertex_count

def reconstruct_chunk_from_sdf(sdf_field):
    solid_voxels = (sdf_field <= 0).astype(np.int8)
    return solid_voxels

def voxel_to_sdf_cubical(voxel_grid, voxel_size=1.0, upsample=4, smoothing_sigma=0.5, max_distance=None):
    # Create a higher-res grid
    grid_shape = np.array(voxel_grid.shape) * upsample
    hi_res = np.zeros(grid_shape, dtype=bool)

    # For each voxel == 1, fill the corresponding high-res cube
    for index in np.argwhere(voxel_grid):
        start = index * upsample
        end = start + upsample
        hi_res[start[0]:end[0], start[1]:end[1], start[2]:end[2]] = True

    # Optional smoothing to round edges
    if smoothing_sigma > 0:
        hi_res = gaussian_filter(hi_res.astype(np.float32), sigma=smoothing_sigma) > 0.5

    # Compute signed distance field: outside - inside
    outside = edt(~hi_res)
    inside = edt(hi_res)
    sdf = outside - inside

    # Optional distance clamp
    if max_distance:
        sdf = np.clip(sdf, -max_distance, max_distance)

    return sdf.astype(np.float32)

def generate_sdf_field(
    voxel_chunk,
    voxel_upsample=2.0,         # modest upsample
    smoothing_sigma=0.8,        # gentle smoothing
    max_distance=None,
    iso_threshold=0.5
):
    assert voxel_chunk.ndim == 3

    # Step 1: Upsample (improves gradient quality and rounding)
    if voxel_upsample != 1.0:
        voxel_data = zoom(voxel_chunk.astype(np.float32), zoom=voxel_upsample, order=1)
    else:
        voxel_data = voxel_chunk.astype(np.float32)

    # Step 2: Smooth the binary cube slightly to soften edges
    if smoothing_sigma > 0:
        voxel_data = gaussian_filter(voxel_data, sigma=smoothing_sigma)

    # Step 3: Compute binary masks for inside/outside
    inside_mask = voxel_data > iso_threshold
    outside_mask = ~inside_mask

    # Step 4: Signed distance field
    outside = fast_sdf_from_voxels(outside_mask)
    inside = fast_sdf_from_voxels(inside_mask)
    sdf = outside - inside  # Positive outside, negative inside

    # Optional clamp
    if max_distance is not None:
        sdf = np.clip(sdf, -max_distance, max_distance)

    return sdf.astype(np.float32)


def fast_sdf_from_voxels(mask):
    # mask: 1 inside, 0 outside
    phi = np.where(mask, -1.0, 1.0)
    return skfmm.distance(phi)

def generate_voxel_grid(config='cube', size=16):
    grid = np.zeros((size, size, size), dtype=np.int8)

    if config == 'cube':
        grid[1, 1, 1] = 1

    return grid

if __name__=='__main__':
    mode='cube-march'
    main(mode)