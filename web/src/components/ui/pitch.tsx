"use client";

import { useEffect, useRef } from "react";

import { cardColor, oklchCss } from "@/lib/color";
import type { ActionData } from "@/lib/overlay";

const LENGTH = 105;
const WIDTH = 68;
const FADE_MS = 7000; // a play lingers this long, then is gone
const PAD = 2.5; // metres of margin around the lines

type Props = {
  actions: ActionData[];
  homeColor: string;
  awayColor: string;
  className?: string;
};

type Timed = { action: ActionData; at: number };

/**
 * A broadcast pitch graphic on a 2D canvas: the lines of a 105 × 68 pitch, and the
 * recent plays of the match on air drawn in each club's colour, fading as they age.
 * Home attacks to the right. The loop runs only while something is still fading.
 */
export function Pitch({ actions, homeColor, awayColor, className = "" }: Props) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const timed = useRef<Timed[]>([]);
  const seen = useRef<ActionData | null>(null);

  // Stamp each new action with its arrival time; the reducer keeps them in order.
  useEffect(() => {
    const last = seen.current;
    const start = last ? actions.lastIndexOf(last) + 1 : 0;
    const fresh = actions.slice(start);
    if (actions.length && actions[0] !== timed.current[0]?.action && start === 0) timed.current = [];
    const now = performance.now();
    timed.current.push(...fresh.map((action) => ({ action, at: now })));
    if (actions.length) seen.current = actions[actions.length - 1];
  }, [actions]);

  useEffect(() => {
    const el = canvas.current;
    if (!el) return;
    const ctx = el.getContext("2d");
    if (!ctx) return;

    const home = oklchCss({ ...cardColor(homeColor), l: 0.68 });
    const away = oklchCss({ ...cardColor(awayColor), l: 0.68 });
    let frame = 0;
    let running = true;

    const draw = () => {
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      const { width: cssW, height: cssH } = el.getBoundingClientRect();
      if (el.width !== cssW * ratio || el.height !== cssH * ratio) {
        el.width = cssW * ratio;
        el.height = cssH * ratio;
      }
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      ctx.clearRect(0, 0, cssW, cssH);

      // Metres → pixels, keeping the pitch's aspect inside the canvas.
      const scale = Math.min(cssW / (LENGTH + PAD * 2), cssH / (WIDTH + PAD * 2));
      const ox = (cssW - LENGTH * scale) / 2;
      const oy = (cssH - WIDTH * scale) / 2;
      const X = (m: number) => ox + m * scale;
      const Y = (m: number) => oy + m * scale;

      drawLines(ctx, X, Y, scale);

      const now = performance.now();
      timed.current = timed.current.filter((t) => now - t.at < FADE_MS);
      let anyAlive = false;
      for (const { action, at } of timed.current) {
        const age = (now - at) / FADE_MS;
        const alpha = Math.max(0, 1 - age * age);
        if (alpha <= 0) continue;
        anyAlive = true;
        drawAction(ctx, action, action.side === "away" ? away : home, alpha, X, Y, scale);
      }
      if (anyAlive && running) frame = requestAnimationFrame(draw);
      else frame = 0;
    };

    // Redraw on size change and whenever new plays arrive; otherwise stay idle.
    const observer = new ResizeObserver(() => {
      if (!frame) frame = requestAnimationFrame(draw);
    });
    observer.observe(el);
    const kick = () => {
      if (!frame) frame = requestAnimationFrame(draw);
    };
    kick();
    const interval = setInterval(kick, 250); // picks up arrivals cheaply between frames
    return () => {
      running = false;
      clearInterval(interval);
      observer.disconnect();
      if (frame) cancelAnimationFrame(frame);
    };
  }, [homeColor, awayColor]);

  return (
    <canvas
      ref={canvas}
      className={`block h-full w-full ${className}`}
      role="img"
      aria-label="Pitch graphic of recent plays in the match on air"
    />
  );
}

type Map = (m: number) => number;

function drawLines(ctx: CanvasRenderingContext2D, X: Map, Y: Map, scale: number) {
  ctx.save();
  ctx.strokeStyle = "oklch(1 0 0 / 0.22)";
  ctx.lineWidth = Math.max(1, scale * 0.16);
  ctx.lineJoin = "round";
  const rect = (x: number, y: number, w: number, h: number) => ctx.strokeRect(X(x), Y(y), w * scale, h * scale);
  rect(0, 0, LENGTH, WIDTH);
  // Halfway line and circle.
  ctx.beginPath();
  ctx.moveTo(X(LENGTH / 2), Y(0));
  ctx.lineTo(X(LENGTH / 2), Y(WIDTH));
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(X(LENGTH / 2), Y(WIDTH / 2), 9.15 * scale, 0, Math.PI * 2);
  ctx.stroke();
  // Penalty areas, six-yard boxes, goals.
  for (const [x0, dir] of [
    [0, 1],
    [LENGTH, -1],
  ] as const) {
    rect(dir === 1 ? x0 : x0 - 16.5, (WIDTH - 40.32) / 2, 16.5, 40.32);
    rect(dir === 1 ? x0 : x0 - 5.5, (WIDTH - 18.32) / 2, 5.5, 18.32);
    rect(dir === 1 ? x0 - 2 : x0, (WIDTH - 7.32) / 2, 2, 7.32);
    ctx.beginPath();
    ctx.arc(X(x0 + dir * 11), Y(WIDTH / 2), scale * 0.35, 0, Math.PI * 2);
    ctx.fillStyle = "oklch(1 0 0 / 0.22)";
    ctx.fill();
  }
  ctx.restore();
}

function drawAction(
  ctx: CanvasRenderingContext2D,
  a: ActionData,
  color: string,
  alpha: number,
  X: Map,
  Y: Map,
  scale: number
) {
  if (a.x === null || a.y === null) return;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineCap = "round";
  const x = X(a.x);
  const y = Y(a.y);
  const hasEnd = a.end_x !== null && a.end_y !== null;
  const ex = hasEnd ? X(a.end_x!) : x;
  const ey = hasEnd ? Y(a.end_y!) : y;

  switch (a.type) {
    case "pass":
    case "carry":
      ctx.lineWidth = Math.max(1.5, scale * 0.28);
      if (a.type === "carry") ctx.setLineDash([scale * 0.9, scale * 0.9]);
      if (a.outcome === false) ctx.globalAlpha = alpha * 0.45;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(ex, ey);
      ctx.stroke();
      ctx.setLineDash([]);
      dot(ctx, ex, ey, scale * 0.55);
      break;
    case "shot":
    case "goal":
    case "save": {
      ctx.lineWidth = Math.max(2, scale * 0.4);
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(ex, ey);
      ctx.stroke();
      const r = scale * (0.7 + 2.2 * (a.xg ?? 0.1));
      dot(ctx, x, y, r);
      if (a.type === "goal") {
        ctx.lineWidth = Math.max(2, scale * 0.35);
        ctx.beginPath();
        ctx.arc(x, y, r + scale * 1.6 + (1 - alpha) * scale * 4, 0, Math.PI * 2);
        ctx.stroke();
      }
      break;
    }
    case "tackle":
    case "interception":
    case "foul": {
      const s = scale * 0.9;
      ctx.lineWidth = Math.max(1.5, scale * 0.3);
      ctx.beginPath();
      ctx.moveTo(x - s, y - s);
      ctx.lineTo(x + s, y + s);
      ctx.moveTo(x + s, y - s);
      ctx.lineTo(x - s, y + s);
      ctx.stroke();
      break;
    }
    case "card": {
      const w = scale * 1.1;
      ctx.fillRect(x - w / 2, y - w * 0.7, w, w * 1.4);
      break;
    }
    default:
      ctx.lineWidth = Math.max(1.5, scale * 0.3);
      ctx.beginPath();
      ctx.arc(x, y, scale * 0.9, 0, Math.PI * 2);
      ctx.stroke();
  }
  ctx.restore();
}

function dot(ctx: CanvasRenderingContext2D, x: number, y: number, r: number) {
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();
}
