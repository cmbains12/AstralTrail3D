

class ShaderSources:
    vertex_shader_source_string = b'''
    #version 330 core

    layout(location = 0) in vec3 aPos;
    layout(location = 1) in vec3 aNorm;
    layout(location = 2) in mat4 model;

    uniform mat4 view;
    uniform mat4 proj;

    out vec3 fragNormal;

    void main() {
        vec4 wPos = model * vec4(aPos, 1.0);
        vec4 vPos = view * wPos;
        gl_Position = proj * vPos;

        fragNormal = transpose(inverse(mat3(model))) * aNorm;
    }
    '''

    fragment_shader_source_string = b'''
    #version 330 core

    in vec3 fragNormal;

    out vec4 fragColour;

    vec3 lightDirection = normalize(vec3(-0.35, -0.65, 0.45));

    void main() {
        float ambi = 0.2;
        float diff = max(dot(normalize(fragNormal), -lightDirection), ambi);
        float lighting = diff;
        fragColour = diff * vec4(0.8, 0.4, 0.2, 1.0);
    }
    '''
