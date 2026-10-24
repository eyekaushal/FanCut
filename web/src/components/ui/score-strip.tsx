"use client";

import { useEffect, useRef } from "react";

import { CompactMatchCard } from "@/components/ui/match-card";
import { t, type Language } from "@/lib/i18n";
import type { ScoreLine } from "@/lib/overlay";

/** Every match in one row. The match on air is kept in view when it changes. */
export function ScoreStrip({
  matches,
  lang,
  fanClub,
  selected,
  onSelect,
}: {
  matches: ScoreLine[];
  lang: Language;
  fanClub?: string | null;
  selected?: string;
  onSelect?: (matchId: string) => void;
}) {
  const list = useRef<HTMLUListElement>(null);
  const onAir = matches.find((m) => m.on_air)?.match_id;

  useEffect(() => {
    if (!onAir || !list.current) return;
    const card = list.current.querySelector<HTMLElement>(`[data-match="${onAir}"]`);
    card?.scrollIntoView({ inline: "center", block: "nearest", behavior: "smooth" });
  }, [onAir]);

  return (
    <nav aria-label={t(lang, "allMatches")}>
      <ul ref={list} className="no-scrollbar -mx-(--gutter) flex snap-x gap-3 overflow-x-auto px-(--gutter) py-1">
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
    </nav>
  );
}
