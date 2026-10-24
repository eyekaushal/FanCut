"use client";

import { LayoutGroup } from "motion/react";
import { useEffect, useId, useRef } from "react";

import { CompactMatchCard } from "@/components/ui/match-card";
import { t, type Language } from "@/lib/i18n";
import type { ScoreLine } from "@/lib/overlay";

/**
 * Every match in one row. The match on screen is kept in view when it changes.
 * `bleed` lets the row run to the page edges; turn it off inside a column.
 */
export function ScoreStrip({
  matches,
  lang,
  fanClub,
  selected,
  onSelect,
  bleed = true,
}: {
  matches: ScoreLine[];
  lang: Language;
  fanClub?: string | null;
  selected?: string;
  onSelect?: (matchId: string) => void;
  bleed?: boolean;
}) {
  const list = useRef<HTMLUListElement>(null);
  const group = useId();
  const onAir = selected ?? matches.find((m) => m.on_air)?.match_id;

  // Centre the card on screen by scrolling the strip itself; never the page.
  useEffect(() => {
    const strip = list.current;
    if (!onAir || !strip) return;
    const card = strip.querySelector<HTMLElement>(`[data-match="${onAir}"]`);
    if (!card) return;
    const left = card.offsetLeft - (strip.clientWidth - card.offsetWidth) / 2;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    strip.scrollTo({ left, behavior: reduced ? "auto" : "smooth" });
  }, [onAir]);

  return (
    <nav aria-label={t(lang, "allMatches")}>
      <LayoutGroup id={group}>
      <ul
        ref={list}
        className={`no-scrollbar flex snap-x gap-3 overflow-x-auto py-1 ${bleed ? "-mx-(--gutter) px-(--gutter)" : "px-1"}`}
      >
        {matches.map((match) => (
          <li key={match.match_id} data-match={match.match_id} className="flex shrink-0">
            <CompactMatchCard
              match={match}
              lang={lang}
              fanClub={fanClub}
              selected={selected === match.match_id}
              onSelect={onSelect}
            />
          </li>
        ))}
      </ul>
      </LayoutGroup>
    </nav>
  );
}
