/**
 * The design tokens, in one place. `src/app/tokens.css` is generated from this file
 * (`npm run tokens`), and `contrast.test.ts` audits every text/surface pair here, so
 * the numbers are checked by CI rather than by eye.
 *
 * Surfaces are neutral: the only colour on screen belongs to a club. Values are OKLCH
 * so light and dark stay perceptually matched. This file has no imports so that the
 * token script can run it directly under Node.
 */

export type Oklch = { l: number; c: number; h: number; a?: number };

const oklch = (l: number, c: number, h: number, a?: number): Oklch => ({ l, c, h, a });

export type Palette = {
  bg: Oklch; // the page
  bgElevated: Oklch; // panels on the page
  fg: Oklch; // primary text
  fgMuted: Oklch; // secondary text
  fgFaint: Oklch; // tertiary text, labels
  hairline: Oklch; // dividers
  onCard: Oklch; // text on a club surface
  onCardMuted: Oklch;
  live: Oklch; // the one signal colour: something is live
  focus: Oklch; // keyboard focus ring
};

export const palette: Record<"light" | "dark", Palette> = {
  light: {
    bg: oklch(0.97, 0.004, 260),
    bgElevated: oklch(1, 0, 0),
    fg: oklch(0.17, 0.01, 260),
    fgMuted: oklch(0.45, 0.015, 260),
    fgFaint: oklch(0.56, 0.012, 260),
    hairline: oklch(0, 0, 0, 0.08),
    onCard: oklch(1, 0, 0),
    onCardMuted: oklch(1, 0, 0, 0.74),
    live: oklch(0.62, 0.22, 27),
    focus: oklch(0.55, 0.18, 262),
  },
  dark: {
    bg: oklch(0.14, 0.008, 260),
    bgElevated: oklch(0.2, 0.01, 260),
    fg: oklch(0.96, 0.004, 260),
    fgMuted: oklch(0.72, 0.012, 260),
    fgFaint: oklch(0.58, 0.012, 260),
    hairline: oklch(1, 0, 0, 0.1),
    onCard: oklch(1, 0, 0),
    onCardMuted: oklch(1, 0, 0, 0.74),
    live: oklch(0.68, 0.22, 27),
    focus: oklch(0.75, 0.14, 262),
  },
};

/**
 * The club surface the silk shader draws. `l`/`c` is the club's tone; the shader scales
 * it by a light factor that sits around `typicalLight` and is capped at `peakLight`,
 * then pushes the brightest crests `peakWhite` of the way to white. White body text is
 * audited at the typical light and large text at the peak. Rule that follows: text
 * under 15 px on a club surface sits on a scrim (a pill), never bare.
 */
export const clubSurface = { l: 0.47, c: 0.15, typicalLight: 0.7, peakLight: 1.2, peakWhite: 0.04 };

/**
 * Type scale. Tracking is size-specific (tight when large, slightly open when small),
 * and leading runs the other way. Sizes are px; the body is 17 like the platform.
 */
export type TypeStyle = { size: string; weight: number; tracking: string; leading: number };

export const type: Record<string, TypeStyle> = {
  display: { size: "clamp(40px, 5.5vw, 68px)", weight: 600, tracking: "-0.03em", leading: 0.98 },
  score: { size: "clamp(64px, 11vw, 120px)", weight: 600, tracking: "-0.04em", leading: 0.9 },
  title1: { size: "28px", weight: 600, tracking: "-0.02em", leading: 1.12 },
  title2: { size: "22px", weight: 600, tracking: "-0.015em", leading: 1.2 },
  headline: { size: "17px", weight: 600, tracking: "-0.005em", leading: 1.35 },
  body: { size: "17px", weight: 400, tracking: "0", leading: 1.5 },
  callout: { size: "15px", weight: 400, tracking: "0", leading: 1.45 },
  caption: { size: "13px", weight: 500, tracking: "0.01em", leading: 1.4 },
  micro: { size: "11px", weight: 600, tracking: "0.04em", leading: 1.3 },
};

export const radius = { card: "22px", panel: "18px", control: "12px", chip: "999px" };

/** Motion: three durations and one ease for CSS; springs live in `lib/motion.ts`. */
export const motion = {
  fast: "180ms",
  base: "320ms",
  slow: "600ms",
  ease: "cubic-bezier(0.2, 0, 0, 1)",
};

export const space = { gutter: "16px", gutterWide: "24px", page: "1120px" };

// -- CSS generation --------------------------------------------------------------

export function oklchCss({ l, c, h, a }: Oklch): string {
  const base = `${l} ${c} ${h}`;
  return a === undefined ? `oklch(${base})` : `oklch(${base} / ${a})`;
}

const kebab = (name: string) => name.replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`);

function paletteVars(p: Palette, indent: string): string {
  return Object.entries(p)
    .map(([name, value]) => `${indent}--${kebab(name)}: ${oklchCss(value)};`)
    .join("\n");
}

export function tokensCss(): string {
  const typeClasses = Object.entries(type)
    .map(
      ([name, t]) =>
        `.t-${name} {\n  font-size: ${t.size};\n  font-weight: ${t.weight};\n  letter-spacing: ${t.tracking};\n  line-height: ${t.leading};\n}`
    )
    .join("\n");
  return `/* Generated from src/design/tokens.ts by \`npm run tokens\`. Do not edit by hand. */

:root {
  color-scheme: light dark;
${paletteVars(palette.light, "  ")}

  --radius-card: ${radius.card};
  --radius-panel: ${radius.panel};
  --radius-control: ${radius.control};
  --radius-chip: ${radius.chip};

  --t-fast: ${motion.fast};
  --t-base: ${motion.base};
  --t-slow: ${motion.slow};
  --ease: ${motion.ease};

  --gutter: ${space.gutter};
  --gutter-wide: ${space.gutterWide};
  --page: ${space.page};
}

@media (prefers-color-scheme: dark) {
  :root {
${paletteVars(palette.dark, "    ")}
  }
}

${typeClasses}
`;
}
