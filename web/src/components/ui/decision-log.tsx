"use client";

import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useState } from "react";

import { Pill } from "@/components/ui/pill";
import { ClubDots, RelevanceBars, type MatchNames } from "@/components/ui/relevance-bars";
import type { AuditEntry } from "@/lib/api";
import { marginOf } from "@/lib/audit";
import { fontClass, type Language } from "@/lib/i18n";
import { reduced, spring } from "@/lib/motion";
import { clock } from "@/lib/overlay-log";

const TRIGGER: Record<AuditEntry["trigger"], string> = {
  start: "kick-off",
  relevance: "more relevant",
  must_show: "must-show moment",
  off_air: "match went off air",
};

/**
 * The audit trail as a producer reads it: every decision, newest first, with the
 * ranking that made it, the reference line, and what the Narrator and the Fact Checker
 * did with it. Expanding a row shows the alternatives and the fact sheet.
 */
export function DecisionLog({ entries, names, lang }: { entries: AuditEntry[]; names: MatchNames; lang: Language }) {
  const prefersReduced = useReducedMotion();
  const [open, setOpen] = useState<number | null>(null);
  if (!entries.length) {
    return <p className="t-callout text-fg-muted">Waiting for the first decision…</p>;
  }
  return (
    <ol className="divide-y divide-hairline">
      <AnimatePresence initial={false}>
        {[...entries].reverse().map((entry) => (
          <motion.li
            key={entry.decision_id}
            layout={!prefersReduced}
            initial={{ opacity: 0, y: prefersReduced ? 0 : -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={prefersReduced ? reduced : spring.settle}
          >
            <DecisionRow
              entry={entry}
              names={names}
              lang={lang}
              open={open === entry.decision_id}
              onToggle={() => setOpen(open === entry.decision_id ? null : entry.decision_id)}
            />
          </motion.li>
        ))}
      </AnimatePresence>
    </ol>
  );
}

function DecisionRow({
  entry,
  names,
  lang,
  open,
  onToggle,
}: {
  entry: AuditEntry;
  names: MatchNames;
  lang: Language;
  open: boolean;
  onToggle: () => void;
}) {
  const to = names[entry.match_id];
  const from = entry.previous_match_id ? names[entry.previous_match_id] : null;
  const margin = marginOf(entry);
  const narration = entry.narration;
  const detailId = `decision-${entry.decision_id}-detail`;

  return (
    <article className="py-4">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        aria-controls={detailId}
        className="-mx-2 flex w-[calc(100%+16px)] min-w-0 items-start gap-3 rounded-control px-2 py-1 text-left hover:bg-fg/4"
      >
        <span className="t-caption tabular w-12 shrink-0 pt-1 text-fg-faint">{clock(entry.t)}</span>
        <span className="min-w-0 flex-1">
          <span className="flex flex-wrap items-center gap-2">
            <Pill tone={entry.kind === "replay" ? "solid" : "neutral"} className="uppercase">
              {entry.kind}
            </Pill>
            <span className="t-caption text-fg-muted">{TRIGGER[entry.trigger]}</span>
            {entry.moment && (
              <span className="t-caption text-fg-muted">
                · {entry.moment.minute}′ {entry.moment.type === "goal" ? "goal" : "red card"}, {entry.moment.player}
              </span>
            )}
          </span>
          <span className="t-body mt-2 flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
            {from && entry.kind !== "open" && (
              <>
                <span className="flex items-center gap-2 text-fg-muted">
                  <ClubDots home={from.homeColor} away={from.awayColor} />
                  {from.label}
                </span>
                <span className="text-fg-faint" aria-hidden>
                  →
                </span>
              </>
            )}
            <span className="flex items-center gap-2 font-medium">
              {to && <ClubDots home={to.homeColor} away={to.awayColor} />}
              {to?.label ?? entry.match_id}
            </span>
            <span className="t-caption tabular text-fg-muted">
              {entry.chosen.value.toFixed(2)}
              {margin !== null &&
                (margin >= 0 ? ` · +${margin.toFixed(2)} over the next match` : ` · −${Math.abs(margin).toFixed(2)} below the top match`)}
            </span>
          </span>
        </span>
        <span className={`t-caption mt-1 shrink-0 text-fg-faint transition-transform duration-(--t-fast) ${open ? "rotate-90" : ""}`} aria-hidden>
          ›
        </span>
      </button>

      <div className="mt-3 space-y-2 sm:pl-15">
        <Line label="Reference" text={entry.reference} lang={entry.narration?.language ?? lang} muted />
        {narration && narration.source === "model" && (
          <Line label={`Narrator · ${narration.drafts} ${narration.drafts === 1 ? "draft" : "drafts"}`} text={narration.text} lang={narration.language} />
        )}
        {narration && narration.source === "template" && (
          <p className="t-caption text-fg-faint">
            On air: the reference line{narration.drafts > 0 && `, after ${narration.drafts} rejected ${narration.drafts === 1 ? "draft" : "drafts"}`}
          </p>
        )}
        {!narration && (
          <p className="t-caption text-fg-faint" aria-live="polite">
            Narrator writing…
          </p>
        )}
        {narration && narration.rejected.length > 0 && (
          <ul className="t-caption space-y-1 text-fg-muted">
            {narration.rejected.map((problem, i) => (
              <li key={`${i}-${problem}`} className="flex gap-2">
                <span className="shrink-0 text-fg-faint">Fact Checker rejected:</span>
                <span className="min-w-0">{problem}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id={detailId}
            key="detail"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={spring.settle}
            className="overflow-hidden sm:pl-15"
          >
            <div className="mt-4 space-y-4 border-t border-hairline pt-4">
              <div>
                <p className="t-micro mb-2 uppercase text-fg-faint">The ranking at this moment</p>
                <RelevanceBars chosen={entry.chosen} alternatives={entry.alternatives} names={names} lang={lang} />
              </div>
              <div>
                <p className="t-micro mb-2 uppercase text-fg-faint">The fact sheet the Narrator was held to</p>
                <pre className="t-micro max-h-64 overflow-auto rounded-control bg-fg/4 p-3 font-mono leading-relaxed text-fg-muted">
                  {JSON.stringify(entry.facts, null, 2)}
                </pre>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </article>
  );
}

function Line({ label, text, lang, muted = false }: { label: string; text: string | null; lang: Language; muted?: boolean }) {
  return (
    <div className="flex gap-3">
      <span className="t-micro w-28 shrink-0 pt-0.5 uppercase text-fg-faint">{label}</span>
      {text && (
        <p lang={lang === "hi" ? "hi" : undefined} className={`t-callout min-w-0 ${fontClass(lang)} ${muted ? "text-fg-muted" : "text-fg"}`}>
          {text}
        </p>
      )}
    </div>
  );
}
