/** The FanCut API over HTTP. The live channel itself streams over SSE (see `use-channel.ts`). */

import type { Language, Stakes } from "@/lib/i18n";
import type { CutFacts, Moment, RankedMatch } from "@/lib/overlay";

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

export type RecapFacts = {
  fan_name: string;
  fan_club: string | null;
  fan_club_opponent: string | null;
  fan_club_goals: number | null;
  fan_club_opponent_goals: number | null;
  fan_club_position_now: number | null;
  fan_club_position_at_kickoff: number | null;
  matches_shown: number;
  cuts: number;
  replays: number;
  moments_shown: { minute: number; type: "goal" | "red_card"; player: string; player_team: string }[];
  fantasy_total: number | null;
  fantasy_best_player: string | null;
  fantasy_best_points: number | null;
  most_dramatic_home_team: string;
  most_dramatic_away_team: string;
  most_dramatic_home_goals: number;
  most_dramatic_away_goals: number;
  most_dramatic_excitement_out_of_10: number | null;
};

export type Recap = {
  facts: RecapFacts;
  reference: string;
  text: string;
  source: "model" | "template";
  language: Language;
};

/** The Narrator's line for a decision, with the Fact Checker's record of getting there. */
export type AuditNarration = {
  text: string;
  language: Language;
  source: "model" | "template";
  drafts: number; // model drafts written (0 when no model is configured)
  rejected: string[]; // why earlier drafts were rejected, as the checker phrased it
};

/** One Director decision as the audit trail records it. */
export type AuditEntry = {
  decision_id: number;
  t: number;
  minute: number;
  kind: "open" | "cut" | "replay";
  trigger: "start" | "relevance" | "must_show" | "off_air";
  match_id: string;
  previous_match_id: string | null;
  chosen: RankedMatch;
  alternatives: RankedMatch[];
  moment: Moment | null;
  facts: CutFacts;
  reference: string;
  narration: AuditNarration | null; // null until the Narrator has answered
};

export type DirectorRules = {
  min_dwell_s: number;
  hysteresis: number;
  decision_interval_s: number;
  alternatives_kept: number;
};

export type AuditTrail = {
  schema_version: "audit.v1";
  channel_id: string;
  fan: string;
  language: Language;
  ended: boolean;
  api_version: string;
  model_deployment: string | null;
  director: DirectorRules;
  decisions: AuditEntry[];
};

export type ChannelReport = {
  personal_moments: number;
  personal_covered: number;
  personal_coverage: number;
  decisive_goals: number;
  live_goals: number;
  live_goals_random: number;
  live_goals_never_switch: number;
  live_coverage: number;
  live_coverage_random: number;
  live_coverage_never_switch: number;
  cuts: number;
  replays: number;
  early_cuts: number;
};

export type DirectorEvaluation = {
  seeds: number[];
  fans: string[];
  seconds: number;
  personal_moments: number;
  personal_covered: number;
  personal_coverage: number;
  decisive_goals: number;
  live_coverage: number;
  live_coverage_random: number;
  live_coverage_never_switch: number;
  cuts: number;
  early_cuts: number;
  distinctness_min: number;
  distinctness_max: number;
  distinctness_mean: number;
  per_matchday: { seed: number; fan: string; neutral: boolean; report: ChannelReport }[];
  distinctness: { seed: number; share: number }[];
};

export type Evaluation = {
  status: "measuring" | "ready";
  progress: { done: number; total: number };
  director: DirectorEvaluation | null;
  grounding: {
    review: {
      method: string;
      date: string;
      lines: number;
      languages: number;
      false_claims: number;
      unsupported_additions: number;
      target: number;
    };
    automated: string;
    live: {
      channels: number;
      lines: number;
      model: number;
      template: number;
      drafts: number;
      rejected_drafts: number;
      rejections: { problem: string; count: number }[];
    };
  };
  safety: {
    model_deployment: string | null;
    speech: boolean;
    director: DirectorRules;
    controls: { name: string; detail: string }[];
  };
};

export type Contract = {
  schema_version: "overlay.v1";
  transport: string;
  envelope: Record<string, unknown>;
  events: { type: string; description: string }[];
};

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
  health: () =>
    request<{ status: string; version: string; environment: string; model: boolean; speech: boolean }>("/health"),
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
  /** Every decision the channel made so far, with its evidence and the Narrator's record. */
  audit: (channelId: string) => request<AuditTrail>(`/channels/${channelId}/audit`),
  auditUrl: (channelId: string) => `${API_URL}/channels/${channelId}/audit`,
  /** Measured results for the Trust screen; `measuring` until the Director numbers are in. */
  evaluation: () => request<Evaluation>("/evaluation"),
  contract: () => request<Contract>("/contract/overlay.v1"),
  /** The fan's matchday in a few sentences; 409 until the matchday has ended. */
  recap: (channelId: string) => request<Recap>(`/channels/${channelId}/recap`),
  /** Spoken audio for a line, as a blob URL; throws 503 when Speech is not configured. */
  async speak(text: string, language: Language): Promise<string> {
    const response = await fetch(`${API_URL}/speech`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ text, language }),
    });
    if (!response.ok) throw new Error(`speech failed: ${response.status}`);
    return URL.createObjectURL(await response.blob());
  },
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
