/**
 * Spring presets for Motion, in Apple's two parameters: damping and response.
 * The house rule: critically damped everywhere, bounce only after a gesture that
 * carried momentum. `response` is how quickly a value reaches its target, in seconds;
 * it is not a duration, since a spring has no fixed one.
 */

import type { Transition } from "motion/react";

export const spring = {
  /** Most UI: a panel appearing, a card settling, a value changing. */
  settle: { type: "spring", bounce: 0, visualDuration: 0.35 } satisfies Transition,
  /** Quick acknowledgements: a chip toggling, a pill updating. */
  snap: { type: "spring", bounce: 0, visualDuration: 0.22 } satisfies Transition,
  /** After a flick or a throw: a little overshoot, because the gesture had momentum. */
  throw: { type: "spring", bounce: 0.2, visualDuration: 0.4 } satisfies Transition,
  /** The cut: the whole stage moving; settled well inside 600 ms. */
  stage: { type: "spring", bounce: 0, visualDuration: 0.42 } satisfies Transition,
} as const;

/** Cross-fade for people who asked for reduced motion: still feedback, no travel. */
export const reduced = { duration: 0.2, ease: "easeOut" } satisfies Transition;

/**
 * Where a flick would come to rest, from Apple's Designing Fluid Interfaces sample code.
 * Used to choose the snap target from the projected end point, not the release point.
 */
export function project(velocity: number, decelerationRate = 0.998): number {
  return ((velocity / 1000) * decelerationRate) / (1 - decelerationRate);
}

/** Progressive resistance past a boundary, so an edge feels soft rather than frozen. */
export function rubberband(overshoot: number, dimension: number, constant = 0.55): number {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
