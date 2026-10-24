/**
 * Draws the silk surface two clubs share on a card: folded fabric lit from above, home
 * colour on the left, away on the right, a dark valley where they meet. One hidden WebGL
 * context renders every card to a static image, so the page pays nothing per frame.
 */

import { clubSurface } from "@/design/tokens";
import { hexToOklch, oklchToLinearRgb, type Oklch } from "@/lib/color";

const MAX_PIXEL_RATIO = 2;

const VERTEX = `
attribute vec2 a;
void main() { gl_Position = vec4(a, 0.0, 1.0); }
`;

// Simplex noise after Ian McEwan / Ashima Arts (MIT), then domain-warped fbm for the folds.
const FRAGMENT = `
precision highp float;
uniform vec2 u_res;
uniform vec3 u_home;
uniform vec3 u_away;
uniform float u_seed;
uniform float u_detail;
uniform float u_peak;
uniform float u_white;

vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec3 permute(vec3 x) { return mod289(((x * 34.0) + 1.0) * x); }
float snoise(vec2 v) {
  const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
  vec2 i = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod289(i);
  vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
  vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);
  m = m * m; m = m * m;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
  vec3 g;
  g.x = a0.x * x0.x + h.x * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}
float fbm(vec2 p) {
  float v = 0.0, a = 0.5;
  for (int i = 0; i < 3; i++) { v += a * snoise(p); p = p * 2.0 + 17.0; a *= 0.45; }
  return v;
}
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
vec3 toSrgb(vec3 c) { return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c)); }

void main() {
  vec2 uv = gl_FragCoord.xy / u_res;
  uv.y = 1.0 - uv.y;
  // Fabric space: stretched along the seam's direction so folds run as long sweeps.
  vec2 p = vec2(uv.x * u_res.x / u_res.y, uv.y) * u_detail;
  const float tilt = 0.31; // radians; the folds lean with the seam
  mat2 lean = mat2(cos(tilt), -sin(tilt), sin(tilt), cos(tilt));
  p = lean * p;
  p.y *= 0.38;
  p += u_seed;

  // Warp the space, then read one smooth field from it.
  vec2 q = vec2(fbm(p), fbm(p + vec2(5.2, 1.3)));
  float f = fbm(p + 0.7 * q);

  // Where the two clubs meet: a diagonal, bent by the fabric.
  float seam = (uv.x - 0.5) + (uv.y - 0.5) * 0.32 + f * 0.18;
  float t = smoothstep(-0.07, 0.07, seam);
  vec3 base = mix(u_home, u_away, t);

  // Folds: the field sliced into bands, each lit on one edge and shaded on the other.
  float band = fract(f * 2.2 + q.y * 0.8);
  float ridge = pow(smoothstep(0.0, 0.55, band), 2.0) * (1.0 - smoothstep(0.55, 1.0, band));
  float sheen = pow(1.0 - abs(band - 0.55) * 2.0, 6.0);
  float light = 0.42 + 0.44 * ridge + 0.26 * sheen;

  // A dark valley at the seam so the hues never blend into mud.
  light *= 1.0 - 0.45 * exp(-pow(seam / 0.11, 2.0));
  // Each club glows from its own corner; light falls from above.
  light += 0.16 * exp(-length(uv - vec2(0.08, 0.10)) * 1.8) * (1.0 - t);
  light += 0.16 * exp(-length(uv - vec2(0.94, 0.92)) * 1.8) * t;
  light += 0.06 * (1.0 - uv.y);

  // Crests are capped (the contrast audit depends on it) and go towards white rather
  // than clipping per channel, which would shift the hue.
  light = min(light, u_peak);
  vec3 c = base * min(light, 1.0);
  c = mix(c, vec3(1.0), (max(light - 1.0, 0.0) / max(u_peak - 1.0, 0.001)) * u_white);
  c += (hash(gl_FragCoord.xy) - 0.5) * 0.012; // grain against banding
  gl_FragColor = vec4(toSrgb(clamp(c, 0.0, 1.0)), 1.0);
}
`;

export type SilkSpec = {
  home: string;
  away: string;
  width: number;
  height: number;
  /** Changes the fold pattern; the same seed always draws the same fabric. */
  seed?: number;
  /** How many folds cross the card. Small cards want fewer. */
  detail?: number;
};

/** The club's hue at the surface tone the tokens define (deep enough for white text). */
function clubRgb(hex: string): [number, number, number] {
  const { c, h }: Oklch = hexToOklch(hex);
  return oklchToLinearRgb({ l: clubSurface.l, c: Math.min(Math.max(c, 0.1), clubSurface.c), h });
}

class SilkRenderer {
  private canvas: HTMLCanvasElement;
  private gl: WebGLRenderingContext;
  private uniforms: Record<string, WebGLUniformLocation | null>;

  constructor() {
    this.canvas = document.createElement("canvas");
    const gl = this.canvas.getContext("webgl", { preserveDrawingBuffer: true, antialias: false });
    if (!gl) throw new Error("WebGL unavailable");
    this.gl = gl;

    const program = gl.createProgram()!;
    for (const [type, source] of [
      [gl.VERTEX_SHADER, VERTEX],
      [gl.FRAGMENT_SHADER, FRAGMENT],
    ] as const) {
      const shader = gl.createShader(type)!;
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        throw new Error(gl.getShaderInfoLog(shader) ?? "shader failed to compile");
      }
      gl.attachShader(program, shader);
    }
    gl.linkProgram(program);
    gl.useProgram(program);

    const quad = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, quad);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const position = gl.getAttribLocation(program, "a");
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);

    this.uniforms = Object.fromEntries(
      ["u_res", "u_home", "u_away", "u_seed", "u_detail", "u_peak", "u_white"].map((name) => [
        name,
        gl.getUniformLocation(program, name),
      ])
    );
  }

  /** Renders one card and hands back a PNG as an object URL. The caller revokes it. */
  async render({ home, away, width, height, seed = 0, detail = 1.6 }: SilkSpec): Promise<string> {
    const ratio = Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO);
    const { gl, canvas } = this;
    canvas.width = Math.max(1, Math.round(width * ratio));
    canvas.height = Math.max(1, Math.round(height * ratio));
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform2f(this.uniforms.u_res, canvas.width, canvas.height);
    gl.uniform3f(this.uniforms.u_home, ...clubRgb(home));
    gl.uniform3f(this.uniforms.u_away, ...clubRgb(away));
    gl.uniform1f(this.uniforms.u_seed, seed * 7.31);
    gl.uniform1f(this.uniforms.u_detail, detail);
    gl.uniform1f(this.uniforms.u_peak, clubSurface.peakLight);
    gl.uniform1f(this.uniforms.u_white, clubSurface.peakWhite);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/png"));
    if (!blob) throw new Error("could not read the rendered surface");
    return URL.createObjectURL(blob);
  }
}

let renderer: SilkRenderer | null | undefined;

/** The shared renderer, or null where WebGL is missing (the CSS surface stays). */
export function silkRenderer(): SilkRenderer | null {
  if (renderer === undefined) {
    try {
      renderer = new SilkRenderer();
    } catch {
      renderer = null;
    }
  }
  return renderer;
}
