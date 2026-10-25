"use client";

import { AnimatePresence, motion, useReducedMotion } from "motion/react";

import { FactChips } from "@/components/ui/chip";
import { fontClass, t, type Language } from "@/lib/i18n";
import { reduced, spring } from "@/lib/motion";
import type { CutData, NarrationData } from "@/lib/overlay";

/**
 * Why this match is on air. The API's reference line shows the instant the cut is
 * made; when the Narrator's line arrives for the same decision, it takes its place.
 * Nothing here is written by the UI.
 */
export function ReasonCard({
  cut,
  narration,
  lang,
  onCard = true,
}: {
  cut: CutData;
  narration?: NarrationData | null;
  lang: Language;
  onCard?: boolean;
}) {
  const prefersReduced = useReducedMotion();
  const line = narration && narration.decision_id === cut.decision_id ? narration : null;
  const text = line?.text ?? cut.text;
  const kind =
    cut.kind === "replay"
      ? t(lang, "replay")
      : cut.kind === "live"
        ? t(lang, cut.facts.moment?.type === "red_card" ? "redCard" : "goal")
        : t(lang, "whyThisCut");
  const muted = onCard ? "text-on-card-muted" : "text-fg-muted";

  return (
    <div>
      <div className={`t-micro mb-2 flex items-center gap-2 uppercase ${muted}`}>
        <span>{kind}</span>
        {!line && cut.kind !== "replay" && cut.kind !== "live" && (
          <span className="normal-case tracking-normal" aria-live="polite">
            · {t(lang, "narrating")}
          </span>
        )}
      </div>
      <AnimatePresence mode="wait" initial={false}>
        <motion.p
          key={line ? `n${line.decision_id}` : `c${cut.decision_id}`}
          lang={lang === "hi" ? "hi" : undefined}
          className={`t-body max-w-[46ch] ${fontClass(lang)} ${lang === "hi" ? "text-[19px] leading-[1.55]" : ""}`}
          initial={{ opacity: 0, y: prefersReduced ? 0 : 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: prefersReduced ? 0 : -6 }}
          transition={prefersReduced ? reduced : spring.settle}
        >
          {text}
        </motion.p>
      </AnimatePresence>
      <div className="mt-4">
        <FactChips facts={cut.facts} lang={lang} tone={onCard ? "card" : "page"} />
      </div>
    </div>
  );
}
