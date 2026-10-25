/**
 * The raw `overlay.v1` stream as it arrived, for the Studio's inspector. Pure helpers
 * over a bounded list, newest last.
 */

import type { Overlay } from "@/lib/overlay";

/** How many raw events the inspector keeps; actions arrive several a second. */
export const LOG_KEPT = 300;

export type OverlayType = Overlay["type"];

export const OVERLAY_TYPES: OverlayType[] = [
  "cut",
  "narration",
  "scoreboard",
  "table",
  "fantasy",
  "focus",
  "players",
  "action",
  "end",
];

export function appendLog(log: Overlay[], overlay: Overlay, keep = LOG_KEPT): Overlay[] {
  const next = log.length >= keep ? log.slice(log.length - keep + 1) : log.slice();
  next.push(overlay);
  return next;
}

/** Events of one type, or all of them, newest first. */
export function selectLog(log: Overlay[], type: OverlayType | "all", limit = 40): Overlay[] {
  const picked = type === "all" ? log : log.filter((o) => o.type === type);
  return picked.slice(-limit).reverse();
}

export function countByType(log: Overlay[]): Record<OverlayType, number> {
  const counts = Object.fromEntries(OVERLAY_TYPES.map((t) => [t, 0])) as Record<OverlayType, number>;
  for (const o of log) counts[o.type] += 1;
  return counts;
}

/** Matchday seconds as a broadcast clock: 1440 → "24:00". */
export function clock(t: number): string {
  const total = Math.max(0, Math.floor(t));
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}
