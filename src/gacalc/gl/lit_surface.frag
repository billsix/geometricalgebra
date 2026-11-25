#version 330 core

// Blinn-Phong lighting, per fragment.  N is the surface normal, L the
// direction to the light, V the direction to the eye, and H = normalize(L + V)
// the halfway vector; the specular term is pow(dot(N, H), shininess).

out vec4 color;

in VS_OUT {
  vec3 normal;
  vec3 light;
  vec3 eye;
} fs_in;

uniform vec3 material_color;
uniform float shininess;

const float AMBIENT = 0.18;

void main()
{
  vec3 N = normalize(fs_in.normal);
  vec3 L = normalize(fs_in.light);
  vec3 V = normalize(fs_in.eye);
  // A height field can be seen from below: light the side that faces the eye.
  if (dot(N, V) < 0.0) {
    N = -N;
  }
  vec3 H = normalize(L + V);
  float diffuse = max(0.0, dot(N, L));
  float specular = 0.0;
  if (diffuse > 0.0) {
    specular = pow(max(0.0, dot(N, H)), shininess);
  }
  color = vec4(
      material_color * (AMBIENT + (1.0 - AMBIENT) * diffuse) + vec3(specular),
      1.0);
}
