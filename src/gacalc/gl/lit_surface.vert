#version 330 core

// Lit surface vertex shader: passes the view-space normal, light direction and
// eye vector to lit_surface.frag, which does the Blinn-Phong lighting per
// fragment.

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal_in;

uniform mat4 mMatrix;
uniform mat4 vMatrix;
uniform mat4 pMatrix;
uniform vec3 light_direction;  // world space, unit vector pointing TO the light

out VS_OUT {
  vec3 normal;
  vec3 light;
  vec3 eye;
} vs_out;

vec4 project(vec4 cameraSpace);

void main()
{
  vec4 camera_space = vMatrix * mMatrix * vec4(position, 1.0);
  gl_Position = pMatrix * vMatrix * project(mMatrix * vec4(position, 1.0));
  vs_out.normal = mat3(vMatrix * mMatrix) * normal_in;
  vs_out.light = mat3(vMatrix) * light_direction;
  vs_out.eye = -camera_space.xyz;  // from the surface point TO the eye at the origin
}
