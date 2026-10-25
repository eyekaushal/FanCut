"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { FantasyPanel } from "@/components/ui/fantasy-panel";
import { LanguageSwitch } from "@/components/ui/language-switch";
import { LeagueTable } from "@/components/ui/league-table";
import { Panel } from "@/components/ui/panel";
import { Pill } from "@/components/ui/pill";
import { Pitch } from "@/components/ui/pitch";
import { PlayerCam } from "@/components/ui/player-cam";
import { RecapCard } from "@/components/ui/recap-card";
import { ScoreStrip } from "@/components/ui/score-strip";
import { Stage } from "@/components/ui/stage";
import { api, type Recap } from "@/lib/api";
import { actionsShown, matchShown, narrationOnAir, playersShown } from "@/lib/channel-state";
import { t, type Language } from "@/lib/i18n";
import { isLanguage, useFanChannel } from "@/lib/use-fan-channel";
import { useVoice } from "@/lib/use-voice";

const DEFAULT_SPEED = 30; // match seconds per wall second: a matchday in about three minutes

/**
 * One fan's channel. `?profile=` is a profile id (the demo fans are `arjun` and `maya`),
 * `?lang=` the narration language, `?speed=` the playback speed. The channel is created
 * on arrival and streamed until the matchday ends.
 */
export function Channel() {
  const params = useSearchParams();
  const router = useRouter();
  const profileId = params.get("profile") ?? "arjun";
  const speed = Number(params.get("speed")) || DEFAULT_SPEED;
  const channel = useFanChannel(profileId, params.get("lang"), speed);
  const { profile, state, connection, lang, fanClub, fanPosition, error, setFocus, channelId } = channel;
  const shown = matchShown(state);
  const recap = useRecap(channelId, state.ended);
  const players = playersShown(state);
  // The cam remembers which match it was picked for; a new match on screen lets it go.
  const [camPick, setCamPick] = useState<{ match: string | null; name: string | null }>({ match: null, name: null });
  const shownId = shown?.match_id ?? null;
  const cam = camPick.match === shownId ? camPick.name : null;
  const setCam = (name: string | null) => setCamPick({ match: shownId, name });
  // Hinglish is read aloud as Hindi (the API sends the Hindi line as voice_text).
  const { voice, toggle: toggleVoice, say } = useVoice(lang === "hinglish" ? "hi" : lang);

  // Speak each decision once: the Narrator's line when it lands, else the reference line
  // after a short grace so a fast model is not talked over by the template. Keys carry
  // the channel id, so a new channel (new language) speaks from its first line.
  const narration = narrationOnAir(state);
  const cut = state.cut;
  useEffect(() => {
    if (!cut) return;
    const key = `${channelId}:n${cut.decision_id}`;
    if (cut.voice_text) return say(cut.voice_text, key);
    if (narration) return say(narration.text, key);
    const timer = setTimeout(() => say(cut.text, key), 4000);
    return () => clearTimeout(timer);
  }, [cut, narration, say, channelId]);
  useEffect(() => {
    if (recap) say(recap.voice_text ?? recap.text, `${channelId}:recap`);
  }, [recap, say, channelId]);

  // Focus: tap a match in the strip to lock the pitch to it; tap again, or the button, to release.
  const toggleFocus = (matchId: string) => setFocus(state.focus === matchId ? null : matchId);

  const setLang = (next: Language) => {
    const q = new URLSearchParams(params);
    q.set("lang", next);
    router.replace(`/channel?${q}`);
  };

  return (
    <main className="mx-auto w-full max-w-(--page) px-(--gutter) pb-16 sm:px-(--gutter-wide)">
      <header className="flex flex-wrap items-center justify-between gap-4 py-5">
        <div className="flex items-center gap-3">
          <Link href="/" className="t-headline">
            FanCut
          </Link>
          {profile && <span className="t-caption text-fg-muted">{profile.name}</span>}
          <ConnectionPill connection={connection} ended={state.ended} lang={lang} />
        </div>
        <div className="flex items-center gap-3">
          <Link
            href={`/studio?profile=${profileId}${isLanguage(params.get("lang")) ? `&lang=${params.get("lang")}` : ""}`}
            className="pressable t-caption hidden h-9 items-center rounded-control px-3 font-semibold text-fg-muted hover:bg-fg/6 hover:text-fg sm:inline-flex"
          >
            Studio
          </Link>
          {voice !== "unavailable" && (
            <Button size="small" variant={voice === "on" ? "primary" : "secondary"} aria-pressed={voice === "on"} onClick={toggleVoice}>
              {t(lang, "voice")}
            </Button>
          )}
          <LanguageSwitch value={lang} onChange={setLang} />
        </div>
      </header>

      {error && (
        <Panel className="mb-6">
          <p className="t-body">Could not reach the API at the configured address.</p>
          <p className="t-caption mt-1 text-fg-muted">{error}</p>
          <Button className="mt-4" onClick={() => router.refresh()}>
            Try again
          </Button>
        </Panel>
      )}

      <div className="grid gap-5 lg:grid-cols-[minmax(0,7fr)_minmax(280px,3fr)]">
        <div className="min-w-0 space-y-5">
          {recap && <RecapCard recap={recap} lang={lang} />}
          <Stage state={state} lang={lang} fanClub={fanClub} fanPosition={fanPosition} onRelease={() => setFocus(null)} />

          <div className="rounded-panel border border-hairline bg-bg-elevated p-3 sm:p-4">
            <div className="aspect-[105/68] w-full">
              {shown ? (
                <Pitch actions={actionsShown(state)} homeColor={shown.home_color} awayColor={shown.away_color} highlight={cam} />
              ) : null}
            </div>
            {shown && (
              <div className="t-caption mt-2 flex justify-between text-fg-muted">
                <span>{shown.home} →</span>
                <span>← {shown.away}</span>
              </div>
            )}
            {players && (
              <div className="mt-4 border-t border-hairline pt-4">
                <PlayerCam players={players.players} selected={cam} onSelect={setCam} lang={lang} />
              </div>
            )}
          </div>

          {state.matches.length > 0 && (
            <ScoreStrip matches={state.matches} lang={lang} fanClub={fanClub} selected={shown?.match_id} onSelect={toggleFocus} />
          )}
        </div>

        <aside className="space-y-5">
          <Panel
            title={t(lang, "asItStands")}
            aside={state.table[0] ? `${t(lang, "liveTable")} · ${state.table[0].played} ${t(lang, "played")}` : undefined}
          >
            {state.table.length ? (
              <LeagueTable rows={state.table} lang={lang} fanClubId={profile?.club_id} limit={8} compact />
            ) : (
              <p className="t-callout text-fg-muted">—</p>
            )}
          </Panel>
          {profile && profile.fantasy_squad.length > 0 && <FantasyPanel fantasy={state.fantasy} lang={lang} />}
          {state.cuts.length > 1 && (
            <Panel title="Director's notes" aside={`${state.cuts.length}`}>
              <ol className="t-caption space-y-2 text-fg-muted">
                {[...state.cuts]
                  .reverse()
                  .slice(0, 8)
                  .map((c) => (
                    <li key={c.decision_id} className="flex gap-3 border-t border-hairline pt-2">
                      <span className="tabular w-8 shrink-0 text-fg-faint">{c.facts.minute}′</span>
                      <span className="min-w-0">
                        <span className="t-micro mr-2 uppercase">{c.kind}</span>
                        {c.facts.home_team} {c.facts.home_goals}–{c.facts.away_goals} {c.facts.away_team}
                      </span>
                    </li>
                  ))}
              </ol>
            </Panel>
          )}
        </aside>
      </div>
    </main>
  );
}

/** The recap, fetched once the matchday has ended; a new channel starts without one. */
function useRecap(channelId: string | null, ended: boolean): Recap | null {
  const [recap, setRecap] = useState<{ channelId: string; recap: Recap } | null>(null);
  useEffect(() => {
    if (!channelId || !ended) return;
    let cancelled = false;
    api
      .recap(channelId)
      .then((r) => !cancelled && setRecap({ channelId, recap: r }))
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [channelId, ended]);
  return recap && recap.channelId === channelId ? recap.recap : null;
}

export function ConnectionPill({ connection, ended, lang }: { connection: string; ended: boolean; lang: Language }) {
  if (ended) return <Pill tone="neutral">{t(lang, "fullTime")}</Pill>;
  if (connection === "live") {
    return (
      <Pill tone="neutral">
        <i className="live-dot block size-2 rounded-full bg-live" aria-hidden />
        {t(lang, "live")}
      </Pill>
    );
  }
  if (connection === "lost") return <Pill tone="neutral">Reconnecting…</Pill>;
  return <Pill tone="neutral">Connecting…</Pill>;
}
