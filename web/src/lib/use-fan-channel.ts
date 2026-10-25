"use client";

import { useEffect, useMemo, useState } from "react";

import { api, type FanProfile, type Matchday } from "@/lib/api";
import { LANGUAGES, type Language } from "@/lib/i18n";
import { useChannel, type Connection } from "@/lib/use-channel";
import type { ChannelState } from "@/lib/channel-state";
import type { Overlay } from "@/lib/overlay";

export function isLanguage(value: string | null | undefined): value is Language {
  return LANGUAGES.some((l) => l.id === value);
}

export type FanChannel = {
  profile: FanProfile | null;
  matchday: Matchday | null;
  channelId: string | null;
  error: string | null;
  state: ChannelState;
  connection: Connection;
  /** The raw overlay.v1 stream as it arrived, most recent last (bounded). */
  log: Overlay[];
  /** The narration language: requested, else the profile's. */
  lang: Language;
  fanClub: string | null;
  fanPosition: number | null;
  colors: Record<string, string>;
  setFocus: (matchId: string | null) => void;
};

/**
 * One fan's channel from arrival to full time: loads the profile and the matchday,
 * creates the channel over the API, then streams it. Used by the channel screen and,
 * twice over, by the split view.
 */
export function useFanChannel(profileId: string, requestedLang: string | null, speed: number): FanChannel {
  const [profile, setProfile] = useState<FanProfile | null>(null);
  const [matchday, setMatchday] = useState<Matchday | null>(null);
  const [channelId, setChannelId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const lang: Language = isLanguage(requestedLang) ? requestedLang : (profile?.language ?? "en");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [fan, md] = await Promise.all([api.profile(profileId), api.matchday()]);
        if (cancelled) return;
        setMatchday(md);
        setProfile(fan);
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

  const { state, connection, log } = useChannel(channelId);
  const colors = useMemo(() => (matchday ? api.clubColors(matchday) : {}), [matchday]);
  const fanClub = useMemo(
    () => matchday?.fixtures.flatMap((f) => [f.home, f.away]).find((c) => c.id === profile?.club_id)?.name ?? null,
    [matchday, profile]
  );
  const fanPosition = state.table.find((r) => r.team_id === profile?.club_id)?.position ?? null;
  const setFocus = (matchId: string | null) => {
    if (channelId) void api.setFocus(channelId, matchId).catch(() => undefined);
  };

  return { profile, matchday, channelId, error, state, connection, log, lang, fanClub, fanPosition, colors, setFocus };
}
