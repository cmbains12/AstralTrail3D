

class ShaderSources:
    vertex_shader_source_string = b'''
    #version 330 core

    layout(location = 0) in vec3 aPos;
    layout(location = 1) in vec3 aNorm;
    layout(location = 2) in vec2 aTexCoord;
    layout(location = 3) in vec3 aTan;
    layout(location = 4) in vec3 aBitan;
    layout(location = 5) in mat4 model;

    uniform mat4 view;
    uniform mat4 proj;

    out vec3 fragNormal;
    out vec2 texCoord;
    out mat3 TBN;
    out vec3 fragPos;

    void main() {
        vec4 wPos = model * vec4(aPos, 1.0);
        fragPos = vec3(wPos);
        vec4 vPos = view * wPos;
        gl_Position = proj * vPos;

        mat3 normalMatrix = transpose(inverse(mat3(model)));

        fragNormal = normalMatrix * aNorm;

        texCoord = aTexCoord;


        vec3 t = normalize(normalMatrix * aTan);
        vec3 n = normalize(normalMatrix * aNorm);
        t = normalize(t - dot(t, n) * n);
        vec3 b = cross(n, t);

        TBN = mat3(t, b, n);
    }
    '''

    fragment_shader_source_string = b'''
    #version 330 core

    in vec3 fragNormal;
    in vec2 texCoord;
    in mat3 TBN;
    in vec3 fragPos;

    uniform vec3 lightDir;
    uniform vec3 viewPos;

    uniform sampler2D textureSampler;
    uniform sampler2D normalMap;
    uniform sampler2D roughnessMap;
    uniform sampler2D aoMap;
    uniform sampler2D heightMap;

    out vec4 fragColour;

    void main() {
        vec3 normalMapSample = texture(normalMap, texCoord).rgb;
        vec3 tangentNorm = normalMapSample * 2.0 - 1.0;

        vec3 normal = normalize(TBN * tangentNorm);
        //vec3 normal = normalize(TBN * (texture(normalMap, texCoord).rgb * 2.0 - 1.0));
        //vec3 normal = normalize(fragNormal);

        vec3 light = normalize(-lightDir);
        vec3 viewDir = normalize(viewPos - fragPos);

        float ao = texture(aoMap, texCoord).r;
        
        float diff = max(dot(normal, light), 0.0);

        vec3 half = normalize(light + viewDir);

        float spec = pow(max(dot(normal, half), 0.0), 32.0);

        float roughness = texture(roughnessMap, texCoord).r;
        spec *= 1.0 - roughness;

        vec3 base = texture(textureSampler, texCoord).rgb;

        float ambi = 0.2;

        vec3 final = (ambi * ao) * base + diff * base + spec * vec3(1.0);

        fragColour = vec4(final, 1.0);
    }
    '''
