"use client";

import { motion, useReducedMotion } from "motion/react";

import { reduced, spring } from "@/lib/motion";

/**
 * The feel, demonstrated: the card follows the pointer 1:1 from where it was grabbed,
 * rubber-bands at the edges, and on release springs home carrying the throw's velocity.
 * Grab it mid-flight and it follows again; nothing waits for an animation to finish.
 */
export function DragDemo() {
  const prefersReduced = useReducedMotion();
  return (
    <div className="relative h-36 overflow-hidden rounded-panel border border-dashed border-hairline">
      <motion.div
        drag
        dragSnapToOrigin
        dragElastic={0.35}
        dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
        dragTransition={{ bounceStiffness: 320, bounceDamping: 26 }}
        whileTap={{ scale: 0.97 }}
        transition={prefersReduced ? reduced : spring.throw}
        className="absolute top-1/2 left-1/2 flex h-20 w-32 -translate-x-1/2 -translate-y-1/2 cursor-grab touch-none items-center justify-center rounded-control bg-fg text-bg t-caption font-semibold select-none active:cursor-grabbing"
      >
        Drag · flick
      </motion.div>
    </div>
  );
}
