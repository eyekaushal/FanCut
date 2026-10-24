"use client";

import { motion, useReducedMotion } from "motion/react";

import { LANGUAGES, t, type Language } from "@/lib/i18n";
import { reduced, spring } from "@/lib/motion";

/** A segmented control. The highlight slides between segments; it never jumps. */
export function LanguageSwitch({ value, onChange }: { value: Language; onChange: (lang: Language) => void }) {
  const prefersReduced = useReducedMotion();
  return (
    <div role="radiogroup" aria-label={t(value, "language")} className="inline-flex rounded-control bg-fg/8 p-1">
      {LANGUAGES.map(({ id, label }) => {
        const selected = id === value;
        return (
          <button
            key={id}
            type="button"
            role="radio"
            aria-checked={selected}
            onClick={() => onChange(id)}
            className={`pressable relative h-9 rounded-[8px] px-4 t-caption font-semibold ${id === "hi" ? "font-devanagari" : ""} ${
              selected ? "text-bg" : "text-fg-muted hover:text-fg"
            }`}
          >
            {selected && (
              <motion.span
                layoutId="language-switch-thumb"
                className="absolute inset-0 -z-10 rounded-[8px] bg-fg"
                transition={prefersReduced ? reduced : spring.snap}
              />
            )}
            {label}
          </button>
        );
      })}
    </div>
  );
}
