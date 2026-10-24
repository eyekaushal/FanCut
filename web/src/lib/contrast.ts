/** WCAG 2 contrast between two OKLCH colours, the second composited over a backdrop if translucent. */

import { oklchToLinearRgb } from "@/lib/color";
import type { Oklch } from "@/design/tokens";

function luminance(color: Oklch, backdrop?: Oklch): number {
  let [r, g, b] = oklchToLinearRgb({ l: color.l, c: color.c, h: color.h });
  if (color.a !== undefined && backdrop) {
    const [br, bg, bb] = oklchToLinearRgb({ l: backdrop.l, c: backdrop.c, h: backdrop.h });
    r = r * color.a + br * (1 - color.a);
    g = g * color.a + bg * (1 - color.a);
    b = b * color.a + bb * (1 - color.a);
  }
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** Contrast ratio of `text` on `surface` (both opaque, or text translucent over the surface). */
export function contrast(text: Oklch, surface: Oklch): number {
  const a = luminance(text, surface);
  const b = luminance(surface);
  const [hi, lo] = a > b ? [a, b] : [b, a];
  return (hi + 0.05) / (lo + 0.05);
}

/** WCAG AA: 4.5:1 for body text, 3:1 for large text (18 px+ or 14 px bold) and UI parts. */
export const AA = { text: 4.5, large: 3 };
