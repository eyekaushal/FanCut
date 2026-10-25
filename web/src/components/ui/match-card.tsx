"use client";

import { motion, useReducedMotion } from "motion/react";

import { MatchSurface } from "@/components/match-surface";
import { Crest } from "@/components/ui/crest";
import { Pill, StatusPill } from "@/components/ui/pill";
import { reduced, spring } from "@/lib/motion";
import { ordinal, stakesLabel, t, type Language } from "@/lib/i18n";
import type { ScoreLine } from "@/lib/overlay";

// Above the club's name, as on a scoreboard; a soft shadow lifts it off the silk.
const CARD_CREST = "mb-4 size-12 drop-shadow-[0_2px_8px_rgb(0_0_0/0.28)] sm:size-16";

/** Full name where there is room; the club's three-letter code where there is not. */
function TeamName({ full, short, className = "" }: { full: string; short: string; className?: string }) {
  return (
    <p className={`t-title1 ${className}`}>
      <span className="sm:hidden" aria-label={full}>
        {short}
      </span>
      <span className="hidden sm:inline">{full}</span>
    </p>
  );
}

function Score({ home, away }: { home: number; away: number }) {
  return (
    <p className="t-score tabular">
      {home}
      <span className="mx-2 opacity-45 sm:mx-4">–</span>
      {away}
    </p>
  );
}

/**
 * The match on air: both clubs on one silk surface, the score between them.
 * `fanClubPosition` is the fan's club's live table position, shown under its name.
 */
export function MatchCard({
  match,
  lang,
  fanClub,
  fanClubPosition,
  seed = 0,
  replay = null,
  children,
}: {
  match: ScoreLine;
  lang: Language;
  fanClub?: string | null;
  fanClubPosition?: number | null;
  seed?: number;
  /** Set while a replay is on screen: the sting replaces the live pill. */
  replay?: { minute: number } | null;
  children?: React.ReactNode;
}) {
  const prefersReduced = useReducedMotion();
  const sideNote = (side: "home" | "away", name: string) => {
    const parts = [t(lang, side)];
    if (name === fanClub && fanClubPosition) {
      parts.push(t(lang, "position", { n: ordinal(lang, fanClubPosition) }));
    }
    return parts.join(" · ");
  };
  return (
    <article className="grain rounded-card p-6 text-on-card sm:p-8" aria-label={`${match.home} v ${match.away}`}>
      <MatchSurface home={match.home_color} away={match.away_color} seed={seed} />
      <div className="flex items-center justify-between">
        {replay ? (
          <motion.span
            initial={{ scale: prefersReduced ? 1 : 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={prefersReduced ? reduced : spring.throw}
          >
            <Pill tone="solid">
              <span className="tabular uppercase">
                {t(lang, "replay")} · {t(lang, "minute", { n: replay.minute })}
              </span>
            </Pill>
          </motion.span>
        ) : (
          <StatusPill status={match.status} minute={match.minute} lang={lang} />
        )}
        <span className="t-caption uppercase text-on-card-muted">{stakesLabel(lang, match.stakes)}</span>
      </div>
      <div className="mt-10 grid grid-cols-[1fr_auto_1fr] items-center gap-4 sm:mt-12 sm:gap-8">
        <div className="min-w-0">
          <Crest short={match.home_short} size={64} className={CARD_CREST} />
          <TeamName full={match.home} short={match.home_short} />
          <p className="t-caption mt-1 text-on-card-muted">{sideNote("home", match.home)}</p>
        </div>
        <Score home={match.home_goals} away={match.away_goals} />
        <div className="min-w-0 text-right">
          <Crest short={match.away_short} size={64} className={`${CARD_CREST} ml-auto`} />
          <TeamName full={match.away} short={match.away_short} />
          <p className="t-caption mt-1 text-on-card-muted">{sideNote("away", match.away)}</p>
        </div>
      </div>
      {children && <div className="mt-10 border-t border-white/15 pt-5 sm:mt-12">{children}</div>}
    </article>
  );
}

/** One match in the strip: crests, codes and goals, the fan's club marked with a dot. */
export function CompactMatchCard({
  match,
  lang,
  fanClub,
  selected = false,
  onSelect,
}: {
  match: ScoreLine;
  lang: Language;
  fanClub?: string | null;
  selected?: boolean;
  onSelect?: (matchId: string) => void;
}) {
  const row = (name: string, short: string, goals: number) => (
    <div className="flex items-center justify-between t-headline">
      <span className="flex items-center gap-1.5">
        {name === fanClub && <i className="block size-1.5 rounded-full bg-white" aria-label={t(lang, "yourClub")} />}
        <Crest short={short} size={18} className="mr-0.5" />
        {short}
      </span>
      <span className="tabular">{goals}</span>
    </div>
  );
  const label =
    match.status === "live" ? (match.on_air ? t(lang, "onAir") : "") : t(lang, match.status === "half_time" ? "halfTime" : "fullTime");
  const Tag = onSelect ? "button" : "div";
  const prefersReduced = useReducedMotion();
  return (
    <Tag
      type={onSelect ? "button" : undefined}
      onClick={onSelect ? () => onSelect(match.match_id) : undefined}
      aria-pressed={onSelect ? selected : undefined}
      aria-label={`${match.home} ${match.home_goals}, ${match.away} ${match.away_goals}`}
      className="grain pressable relative w-[156px] shrink-0 snap-start rounded-panel p-3.5 text-left text-on-card"
    >
      <MatchSurface home={match.home_color} away={match.away_color} size="small" />
      {selected && (
        // One ring per strip, sliding to whichever card is on screen.
        <motion.span
          layoutId="strip-ring"
          className="pointer-events-none absolute inset-0 rounded-panel ring-2 ring-white ring-offset-2 ring-offset-bg"
          transition={prefersReduced ? reduced : spring.settle}
          aria-hidden
        />
      )}
      <div className="t-micro h-4 uppercase">
        {match.on_air ? label : <span className="text-on-card-muted">{label}</span>}
      </div>
      <div className="mt-2.5 space-y-1">
        {row(match.home, match.home_short, match.home_goals)}
        {row(match.away, match.away_short, match.away_goals)}
      </div>
    </Tag>
  );
}
