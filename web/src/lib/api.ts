/** The FanCut API over HTTP. The live channel itself streams over SSE (see `use-channel.ts`). */

import type { Language, Stakes } from "@/lib/i18n";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type Fixture = {
  match_id: string;
  home: { id: string; name: string; short: string; color: string };
  away: { id: string; name: string; short: string; color: string };
  stakes: Stakes;
};

export type Matchday = {
  id: string;
  kickoff_utc: string;
  fixtures: Fixture[];
  table: { position: number; team_id: string; team: string; short: string; points: number; goal_difference: number }[];
};

export type FanProfile = {
  schema_version: "profile.v1";
  name: string;
  club_id: string | null;
  player_ids: string[];
  fantasy_squad: string[];
  captain_id: string | null;
  language: Language;
  depth: "casual" | "analyst";
};

export type CompiledProfile = {
  profile: FanProfile;
  readback: string;
  questions: string[];
};

export type ChannelRequest = {
  profile_id: string;
  language?: Language;
  speed?: number; // match seconds per wall second, 1–600
  until_minute?: number;
};

export type ChannelCreated = { channel_id: string; stream: string; audit: string };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(`${init?.method ?? "GET"} ${path} failed: ${response.status} ${detail}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; version: string; environment: string; model: boolean }>("/health"),
  matchday: () => request<Matchday>("/matchday"),
  demoProfiles: () => request<Record<string, FanProfile>>("/profiles/demo"),
  compileProfile: (message: string) =>
    request<{ profile_id: string; compiled: CompiledProfile }>("/profiles/compile", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
  addProfile: (profile: FanProfile) =>
    request<{ profile_id: string }>("/profiles", { method: "POST", body: JSON.stringify(profile) }),
  createChannel: (body: ChannelRequest) =>
    request<ChannelCreated>("/channels", { method: "POST", body: JSON.stringify(body) }),
  audit: (channelId: string) => request<unknown[]>(`/channels/${channelId}/audit`),
  /** Lock the pitch to one match while the Director keeps deciding; null releases. */
  setFocus: (channelId: string, matchId: string | null) =>
    request<{ focus: string | null }>(`/channels/${channelId}/focus`, {
      method: "POST",
      body: JSON.stringify({ match_id: matchId }),
    }),
  /** team_id → colour, for the table's dots. */
  clubColors(matchday: Matchday): Record<string, string> {
    const colors: Record<string, string> = {};
    for (const f of matchday.fixtures) {
      colors[f.home.id] = f.home.color;
      colors[f.away.id] = f.away.color;
    }
    return colors;
  },
};
