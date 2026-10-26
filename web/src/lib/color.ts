/**
 * Club colours arrive as hex from the API. On screen they become gradients, so they are
 * moved into OKLCH (perceptually even lightness and chroma) and lifted into a band where
 * white text stays readable and the gradient is vivid rather than muddy.
 */

export type Oklch = { l: number; c: number; h: number };

// White text on a card needs 4.5:1 for small type; that holds up to about L 0.56.
const CARD_LIGHTNESS = { min: 0.46, max: 0.56 };
const CARD_CHROMA = { min: 0.09, max: 0.19 };

export function hexToOklch(hex: string): Oklch {
  const value = hex.replace("#", "");
  if (!/^[0-9a-fA-F]{6}$/.test(value)) throw new Error(`not a 6-digit hex colour: ${hex}`);
  const [r, g, b] = [0, 2, 4].map((i) => toLinear(parseInt(value.slice(i, i + 2), 16) / 255));

  // Björn Ottosson's OKLab transform.
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s;
  const a = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s;
  const bb = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;

  const c = Math.hypot(a, bb);
  const h = ((Math.atan2(bb, a) * 180) / Math.PI + 360) % 360;
  return { l: L, c, h };
}

function toLinear(channel: number): number {
  return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
}

/** OKLCH back to linear sRGB (0-1, clamped), for shaders that work in linear light. */
export function oklchToLinearRgb({ l: L, c, h }: Oklch): [number, number, number] {
  const a = c * Math.cos((h * Math.PI) / 180);
  const b = c * Math.sin((h * Math.PI) / 180);
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3;
  const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
  return [
    clamp01(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
    clamp01(-1.2684380046 * l + 2.6097574011 * m - 0.0041960863 * s),
    clamp01(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s),
  ];
}

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

/** The club's colour, lifted into the card band. Hue is kept, so the club stays recognisable. */
export function cardColor(hex: string): Oklch {
  const { l, c, h } = hexToOklch(hex);
  return {
    l: clamp(l, CARD_LIGHTNESS.min, CARD_LIGHTNESS.max),
    c: clamp(c, CARD_CHROMA.min, CARD_CHROMA.max),
    h,
  };
}

export function oklchCss({ l, c, h }: Oklch, alpha = 1): string {
  const base = `${l.toFixed(3)} ${c.toFixed(3)} ${h.toFixed(1)}`;
  return alpha === 1 ? `oklch(${base})` : `oklch(${base} / ${alpha})`;
}

/** A club's hue at a chosen lightness and chroma, optionally translucent. */
function tone(hex: string, l: number, c: number, alpha = 1): string {
  const { h } = hexToOklch(hex);
  return oklchCss({ l, c: clamp(c, 0.06, 0.24), h }, alpha);
}

/**
 * Two clubs meeting on one card, built as a lit surface rather than a flat fill:
 * a dark base, each club's colour glowing in from its own corner, and a diagonal
 * fold (a bright ridge beside a dark crease) where the two meet. Layers are listed
 * top-down, as CSS paints them.
 */
export function matchSurface(homeHex: string, awayHex: string): string {
  const seam = 104;
  return [
    // Light falling from above.
    `linear-gradient(180deg, oklch(1 0 0 / 0.07) 0%, oklch(1 0 0 / 0) 45%)`,
    // Ridges of the folds catching the light: a main one on each side of the seam and
    // a thinner one further out, so the surface ripples rather than creases once.
    `linear-gradient(${seam + 6}deg, ${tone(homeHex, 0.74, 0.12, 0)} 30%, ${tone(homeHex, 0.74, 0.12, 0.42)} 40%, ${tone(homeHex, 0.74, 0.12, 0)} 48%)`,
    `linear-gradient(${seam + 2}deg, ${tone(homeHex, 0.74, 0.12, 0)} 10%, ${tone(homeHex, 0.74, 0.12, 0.2)} 18%, ${tone(homeHex, 0.74, 0.12, 0)} 25%)`,
    `linear-gradient(${seam + 10}deg, ${tone(awayHex, 0.7, 0.12, 0)} 54%, ${tone(awayHex, 0.7, 0.12, 0.34)} 64%, ${tone(awayHex, 0.7, 0.12, 0)} 76%)`,
    `linear-gradient(${seam + 4}deg, ${tone(awayHex, 0.7, 0.12, 0)} 80%, ${tone(awayHex, 0.7, 0.12, 0.18)} 88%, ${tone(awayHex, 0.7, 0.12, 0)} 96%)`,
    // Each club's glow, fading out before it reaches the other club.
    `radial-gradient(100% 140% at 8% 10%, ${tone(homeHex, 0.58, 0.14)} 0%, ${tone(homeHex, 0.58, 0.14, 0)} 64%)`,
    `radial-gradient(100% 140% at 94% 92%, ${tone(awayHex, 0.56, 0.14)} 0%, ${tone(awayHex, 0.56, 0.14, 0)} 64%)`,
    // The base: each club's hue, deep, falling into a dark valley at the seam. The two
    // hues never meet directly; a red and a green blended head-on would turn to mud.
    `linear-gradient(${seam}deg, ${tone(homeHex, 0.32, 0.09)} 0%, ${tone(homeHex, 0.32, 0.09)} 36%, ${tone(homeHex, 0.2, 0.05)} 49%, ${tone(awayHex, 0.2, 0.05)} 51%, ${tone(awayHex, 0.3, 0.09)} 64%, ${tone(awayHex, 0.3, 0.09)} 100%)`,
  ].join(", ");
}

