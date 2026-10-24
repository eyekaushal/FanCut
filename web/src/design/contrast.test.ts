import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import { AA, contrast } from "@/lib/contrast";
import { oklchToLinearRgb } from "@/lib/color";
import { clubSurface, palette, tokensCss, type Oklch } from "./tokens";

const schemes = ["light", "dark"] as const;

describe("tokens.css", () => {
  it("is generated from tokens.ts and up to date (run `npm run tokens`)", () => {
    const written = readFileSync(new URL("../app/tokens.css", import.meta.url), "utf8");
    expect(written).toBe(tokensCss());
  });
});

describe.each(schemes)("%s palette contrast (WCAG AA)", (scheme) => {
  const p = palette[scheme];

  it.each([
    ["fg", "bg"],
    ["fg", "bgElevated"],
    ["fgMuted", "bg"],
    ["fgMuted", "bgElevated"],
  ] as const)("%s on %s reads as body text (≥ 4.5:1)", (text, surface) => {
    expect(contrast(p[text], p[surface])).toBeGreaterThanOrEqual(AA.text);
  });

  it.each([
    ["fgFaint", "bg"],
    ["fgFaint", "bgElevated"],
  ] as const)("%s on %s is only used for captions at 13 px medium and up (≥ 3:1)", (text, surface) => {
    expect(contrast(p[text], p[surface])).toBeGreaterThanOrEqual(AA.large);
  });

  it("the live signal is visible on both page surfaces (≥ 3:1)", () => {
    expect(contrast(p.live, p.bg)).toBeGreaterThanOrEqual(AA.large);
    expect(contrast(p.live, p.bgElevated)).toBeGreaterThanOrEqual(AA.large);
  });

  it("the focus ring is visible on the page (≥ 3:1)", () => {
    expect(contrast(p.focus, p.bg)).toBeGreaterThanOrEqual(AA.large);
  });
});

describe("club surfaces", () => {
  const { l, c, typicalLight, peakLight, peakWhite } = clubSurface;
  // The surface at a given light, as an achromatic OKLCH of equal luminance.
  const lit = (hue: number, light: number, white = 0): Oklch => {
    const [r, g, b] = oklchToLinearRgb({ l, c, h: hue });
    let lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) * light;
    lum = lum * (1 - white) + white;
    return { l: Math.cbrt(lum), c: 0, h: 0 };
  };
  const hues = [0, 60, 110, 150, 200, 262, 300];

  it.each(hues)("white body text reads on a hue-%s club surface at typical light (≥ 4.5:1)", (hue) => {
    expect(contrast(palette.dark.onCard, lit(hue, typicalLight))).toBeGreaterThanOrEqual(AA.text);
  });

  it.each(hues)("white text holds large-text contrast on a hue-%s crest (≥ 3:1)", (hue) => {
    expect(contrast(palette.dark.onCard, lit(hue, peakLight, peakWhite))).toBeGreaterThanOrEqual(AA.large);
  });

  it.each(hues)("muted white text holds large-text contrast on a hue-%s surface at typical light", (hue) => {
    expect(contrast(palette.dark.onCardMuted, lit(hue, typicalLight))).toBeGreaterThanOrEqual(AA.large);
  });
});
