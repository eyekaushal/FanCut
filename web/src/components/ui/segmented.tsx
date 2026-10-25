"use client";

import { motion, useReducedMotion } from "motion/react";
import { useId } from "react";

import { reduced, spring } from "@/lib/motion";

export type Segment<T extends string> = { id: T; label: string; className?: string };

/** A segmented control. The highlight slides between segments; it never jumps. */
export function Segmented<T extends string>({
  value,
  options,
  onChange,
  label,
}: {
  value: T;
  options: Segment<T>[];
  onChange: (value: T) => void;
  label: string;
}) {
  const prefersReduced = useReducedMotion();
  const thumb = useId();
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex rounded-control bg-fg/8 p-1">
      {options.map(({ id, label: text, className = "" }) => {
        const selected = id === value;
        return (
          <button
            key={id}
            type="button"
            role="radio"
            aria-checked={selected}
            onClick={() => onChange(id)}
            className={`pressable relative h-9 rounded-[8px] px-4 t-caption font-semibold ${className} ${
              selected ? "text-bg" : "text-fg-muted hover:text-fg"
            }`}
          >
            {selected && (
              <motion.span
                layoutId={thumb}
                className="absolute inset-0 -z-10 rounded-[8px] bg-fg"
                transition={prefersReduced ? reduced : spring.snap}
              />
            )}
            {text}
          </button>
        );
      })}
    </div>
  );
}
