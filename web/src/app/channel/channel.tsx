"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { FantasyPanel } from "@/components/ui/fantasy-panel";
import { LanguageSwitch } from "@/components/ui/language-switch";
import { LeagueTable } from "@/components/ui/league-table";
import { MatchCard } from "@/components/ui/match-card";
import { Panel } from "@/components/ui/panel";
import { Pill } from "@/components/ui/pill";
import { Pitch } from "@/components/ui/pitch";
import { ReasonCard } from "@/components/ui/reason-card";
import { ScoreStrip } from "@/components/ui/score-strip";
import { api, type FanProfile, type Matchday } from "@/lib/api";
import { matchOnAir, narrationOnAir } from "@/lib/channel-state";
import { LANGUAGES, t, type Language } from "@/lib/i18n";
import { useChannel } from "@/lib/use-channel";

const DEFAULT_SPEED = 30; // match seconds per wall second: a matchday in about three minutes

function isLanguage(value: string | null): value is Language {
  return LANGUAGES.some((l) => l.id === value);
}

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
  const requestedLang = params.get("lang");

  const [profile, setProfile] = useState<FanProfile | null>(null);
  const [matchday, setMatchday] = useState<Matchday | null>(null);
  const [channelId, setChannelId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const lang: Language = isLanguage(requestedLang) ? requestedLang : (profile?.language ?? "en");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [profiles, md] = await Promise.all([api.demoProfiles(), api.matchday()]);
        if (cancelled) return;
        setMatchday(md);
        setProfile(profiles[profileId] ?? null);
        const created = await api.createChannel({
          profile_id: profileId,
          language: isLanguage(requestedLang) ? requestedLang : undefined,
          speed,
        });
        if (!cancelled) setChannelId(created.channel_id);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [profileId, requestedLang, speed]);

  const { state, connection } = useChannel(channelId);
  const onAir = matchOnAir(state);
  const colors = useMemo(() => (matchday ? api.clubColors(matchday) : {}), [matchday]);
  const fanClub = useMemo(
    () => matchday?.fixtures.flatMap((f) => [f.home, f.away]).find((c) => c.id === profile?.club_id)?.name ?? null,
    [matchday, profile]
  );
  const fanPosition = state.table.find((r) => r.team_id === profile?.club_id)?.position ?? null;

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
        <LanguageSwitch value={lang} onChange={setLang} />
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
          {onAir && state.cut ? (
            <MatchCard match={onAir} lang={lang} fanClub={fanClub} fanClubPosition={fanPosition} seed={cutSeed(state.cut.match_id)}>
              <ReasonCard cut={state.cut} narration={narrationOnAir(state)} lang={lang} />
            </MatchCard>
          ) : (
            <div className="grain h-[320px] animate-pulse rounded-card bg-bg-elevated" aria-busy />
          )}

          <div className="rounded-panel border border-hairline bg-bg-elevated p-3 sm:p-4">
            <div className="aspect-[105/68] w-full">
              {onAir ? (
                <Pitch actions={state.actions} homeColor={onAir.home_color} awayColor={onAir.away_color} />
              ) : null}
            </div>
            {onAir && (
              <div className="t-caption mt-2 flex justify-between text-fg-muted">
                <span>{onAir.home} →</span>
                <span>← {onAir.away}</span>
              </div>
            )}
          </div>

          {state.matches.length > 0 && (
            <ScoreStrip matches={state.matches} lang={lang} fanClub={fanClub} selected={state.cut?.match_id} />
          )}
        </div>

        <aside className="space-y-5">
          <Panel title={t(lang, "asItStands")} aside={state.table[0] ? `${t(lang, "liveTable")} · ${state.table[0].played} ${t(lang, "played")}` : undefined}>
            {state.table.length ? (
              <LeagueTable rows={state.table} lang={lang} fanClubId={profile?.club_id} colors={colors} limit={8} compact />
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

function ConnectionPill({ connection, ended, lang }: { connection: string; ended: boolean; lang: Language }) {
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

/** The same match always gets the same silk; a cut to another match gets a new fold. */
function cutSeed(matchId: string): number {
  return Number(matchId.slice(-2)) || 0;
}
