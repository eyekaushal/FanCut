"use client";

import { AnimatePresence, motion, useReducedMotion } from "motion/react";

import { FocusCard } from "@/components/ui/focus-card";
import { MatchCard } from "@/components/ui/match-card";
import { ReasonCard } from "@/components/ui/reason-card";
import { matchOnAir, matchShown, narrationOnAir, rankingOf, type ChannelState } from "@/lib/channel-state";
import { t, type Language } from "@/lib/i18n";
import { reduced, spring } from "@/lib/motion";

/**
 * The picture: the match on screen and, when it changes, the cut. The outgoing card
 * slides away to the left and the incoming one lands from the right, both on the
 * stage spring, so a cut always travels the same path. A replay interrupts with a
 * sting; the stream itself pauses on it (see ReplayHold) so it can be seen.
 */
export function Stage({
  state,
  lang,
  fanClub,
  fanPosition,
  onRelease,
}: {
  state: ChannelState;
  lang: Language;
  fanClub: string | null;
  fanPosition: number | null;
  onRelease: () => void;
}) {
  const prefersReduced = useReducedMotion();
  const cut = state.cut;
  const shown = matchShown(state);
  const onAir = matchOnAir(state);
  const focused = state.focus !== null;
  const replay = cut?.kind === "replay" && !focused;

  if (!shown || !cut) {
    return <div className="grain h-[320px] animate-pulse rounded-card bg-bg-elevated" aria-busy />;
  }

  const travel = prefersReduced ? 0 : 48;
  const key = `${shown.match_id}:${replay ? "replay" : "live"}`;

  return (
    <div className="relative">
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.div
          key={key}
          initial={{ x: travel, opacity: 0, scale: prefersReduced ? 1 : 0.985 }}
          animate={{ x: 0, opacity: 1, scale: 1 }}
          exit={{ x: -travel, opacity: 0, scale: prefersReduced ? 1 : 0.985 }}
          transition={prefersReduced ? reduced : spring.stage}
        >
          <MatchCard
            match={shown}
            lang={lang}
            fanClub={fanClub}
            fanClubPosition={fanPosition}
            seed={Number(shown.match_id.slice(-2)) || 0}
            replay={replay ? { minute: cut.facts.moment?.minute ?? cut.facts.minute } : null}
          >
            {focused ? (
              <FocusCard
                ranking={rankingOf(state, shown.match_id)}
                onAir={cut.chosen}
                onAirName={onAir ? `${onAir.home} ${onAir.home_goals}–${onAir.away_goals} ${onAir.away}` : null}
                lang={lang}
                onRelease={onRelease}
              />
            ) : (
              <ReasonCard cut={cut} narration={narrationOnAir(state)} lang={lang} />
            )}
          </MatchCard>
        </motion.div>
      </AnimatePresence>
      <span className="sr-only" aria-live="polite">
        {replay ? t(lang, "replay") : ""} {cut.text}
      </span>
    </div>
  );
}
