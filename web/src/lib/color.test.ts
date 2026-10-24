import { describe, expect, it } from "vitest";

import { cardColor, hexToOklch, matchSurface, oklchCss } from "./color";

describe("hexToOklch", () => {
  it("maps white and black to the ends of the lightness scale", () => {
    expect(hexToOklch("#ffffff").l).toBeCloseTo(1, 2);
    expect(hexToOklch("#000000").l).toBeCloseTo(0, 2);
  });

  it("keeps a pure red on the red hue", () => {
    const red = hexToOklch("#ff0000");
    expect(red.h).toBeGreaterThan(25);
    expect(red.h).toBeLessThan(35);
    expect(red.c).toBeGreaterThan(0.2);
  });

  it("rejects anything that is not a 6-digit hex colour", () => {
    expect(() => hexToOklch("#fff")).toThrow();
  });
});

describe("cardColor", () => {
  it("lifts a dark club colour into the readable band without changing its hue", () => {
    const original = hexToOklch("#2F4F2F"); // Elmhurst's deep green
    const lifted = cardColor("#2F4F2F");
    expect(lifted.l).toBeGreaterThanOrEqual(0.46);
    expect(lifted.l).toBeLessThanOrEqual(0.56);
    expect(lifted.c).toBeGreaterThanOrEqual(0.09);
    expect(lifted.h).toBeCloseTo(original.h, 5);
  });

  it("pulls a bright, loud colour down into the same band", () => {
    const lifted = cardColor("#E0A526"); // Westhaven's gold
    expect(lifted.l).toBeLessThanOrEqual(0.56);
    expect(lifted.c).toBeLessThanOrEqual(0.19);
  });
});

describe("gradients", () => {
  it("writes valid oklch() with an optional alpha", () => {
    expect(oklchCss({ l: 0.5, c: 0.1, h: 200 })).toBe("oklch(0.500 0.100 200.0)");
    expect(oklchCss({ l: 0.5, c: 0.1, h: 200 }, 0.4)).toBe("oklch(0.500 0.100 200.0 / 0.4)");
  });

  it("lays the home club's glow top-left and the away club's bottom-right over a dark base", () => {
    const surface = matchSurface("#2E5EAA", "#2A9D8F");
    const homeHue = hexToOklch("#2E5EAA").h.toFixed(1);
    const awayHue = hexToOklch("#2A9D8F").h.toFixed(1);
    expect(surface).toContain(`at 8% 10%, oklch(0.580 0.140 ${homeHue})`);
    expect(surface).toContain(`at 94% 92%, oklch(0.560 0.140 ${awayHue})`);
    // The base layer is painted last and stays deep enough for white text.
    expect(surface.split(", linear-gradient").at(-1)).toContain(`oklch(0.320 0.090 ${homeHue}) 0%`);
  });
});
