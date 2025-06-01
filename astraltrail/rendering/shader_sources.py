

class ShaderSources:

    vertex_shader_source_string = b'''
    #version 330 core

    layout(location = 0) in vec3 aPos;
    layout(location = 1) in mat4 model;

    uniform mat4 view;
    uniform mat4 proj;

    void main() {
        vec4 wPos = model * vec4(aPos, 1.0);
        vec4 vPos = view * wPos;
        gl_Position = proj * vPos;
    }
    '''

    fragment_shader_source_string = b'''
    #version 330 core

    out vec4 fragColour;

    void main() {
        fragColour = vec4(0.8, 0.4, 0.2, 1.0);
    }
    '''
