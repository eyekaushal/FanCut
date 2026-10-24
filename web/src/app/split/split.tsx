"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Pitch } from "@/components/ui/pitch";
import { ScoreStrip } from "@/components/ui/score-strip";
import { Stage } from "@/components/ui/stage";
import { actionsShown, matchShown } from "@/lib/channel-state";
import { useFanChannel, type FanChannel } from "@/lib/use-fan-channel";

const DEFAULT_SPEED = 30;
const SAMPLE_MS = 1000;

/**
 * One matchday, two fans, two channels side by side: the challenge's own test that
 * the same intelligence reaches two people as two genuinely different experiences.
 * `?a=` and `?b=` are profile ids; both channels run at the same speed.
 */
export function Split() {
  const params = useSearchParams();
  const speed = Number(params.get("speed")) || DEFAULT_SPEED;
  const a = useFanChannel(params.get("a") ?? "arjun", null, speed);
  const b = useFanChannel(params.get("b") ?? "maya", null, speed);
  const distinct = useDistinctness(a, b);

  return (
    <main className="mx-auto w-full max-w-[1400px] px-(--gutter) pb-16 sm:px-(--gutter-wide)">
      <header className="flex flex-wrap items-center justify-between gap-4 py-5">
        <div className="flex items-baseline gap-3">
          <Link href="/" className="t-headline">
            FanCut
          </Link>
          <span className="t-caption text-fg-muted">Same matchday · two fans</span>
        </div>
        {distinct && (
          <p className="t-caption tabular text-fg-muted" aria-live="polite">
            Different matches <span className="text-fg">{Math.round(distinct.share * 100)}%</span> of the time so far
          </p>
        )}
      </header>

      <div className="grid gap-6 lg:grid-cols-2">
        <Column channel={a} />
        <Column channel={b} />
      </div>
    </main>
  );
}

function Column({ channel }: { channel: FanChannel }) {
  const { profile, state, lang, fanClub, fanPosition, setFocus, error } = channel;
  const shown = matchShown(state);
  return (
    <section aria-label={profile?.name ?? "Fan"} className="min-w-0 space-y-4">
      <div className="flex items-baseline justify-between">
        <h2 className="t-title2">{profile?.name ?? "…"}</h2>
        <p className="t-caption text-fg-muted">
          {profile?.club_id ? fanClub : "Neutral"} · {profile?.depth} · {lang}
        </p>
      </div>
      {error && <p className="t-caption text-fg-muted">{error}</p>}
      <Stage state={state} lang={lang} fanClub={fanClub} fanPosition={fanPosition} onRelease={() => setFocus(null)} />
      <div className="rounded-panel border border-hairline bg-bg-elevated p-3">
        <div className="aspect-[105/68] w-full">
          {shown ? <Pitch actions={actionsShown(state)} homeColor={shown.home_color} awayColor={shown.away_color} /> : null}
        </div>
      </div>
      {state.matches.length > 0 && (
        <ScoreStrip matches={state.matches} lang={lang} fanClub={fanClub} selected={shown?.match_id} bleed={false} />
      )}
    </section>
  );
}

/** The share of sampled seconds on which the two channels showed different matches. */
function useDistinctness(a: FanChannel, b: FanChannel): { share: number; samples: number } | null {
  const [tally, setTally] = useState({ different: 0, samples: 0 });
  const matchA = a.state.cut?.match_id;
  const matchB = b.state.cut?.match_id;
  const live = !!matchA && !!matchB && !a.state.ended && !b.state.ended;

  useEffect(() => {
    if (!live) return;
    const timer = setInterval(() => {
      setTally((t) => ({ different: t.different + (matchA !== matchB ? 1 : 0), samples: t.samples + 1 }));
    }, SAMPLE_MS);
    return () => clearInterval(timer);
  }, [live, matchA, matchB]);

  return tally.samples ? { share: tally.different / tally.samples, samples: tally.samples } : null;
}
