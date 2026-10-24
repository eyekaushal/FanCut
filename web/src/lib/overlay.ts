/**
 * The `overlay.v1` contract as the API sends it over SSE. Field names and values match
 * `api/src/fancut/api/overlay.py` and `channel.py` exactly; the UI renders these and
 * invents nothing.
 */

import type { Language, Stakes } from "@/lib/i18n";

export type MatchStatus = "live" | "half_time" | "full_time";

export type ScoreLine = {
  match_id: string;
  home: string;
  away: string;
  home_short: string;
  away_short: string;
  home_color: string;
  away_color: string;
  home_goals: number;
  away_goals: number;
  minute: number;
  status: MatchStatus;
  stakes: Stakes;
  on_air: boolean;
};

export type TableLine = {
  position: number;
  team_id: string;
  team: string;
  short: string;
  played: number;
  points: number;
  goal_difference: number;
  change: number; // places gained (+) or lost (-) since kickoff
};

export type Moment = {
  type: "goal" | "red_card";
  player: string;
  player_team: string;
  minute: number;
};

export type CutFacts = {
  kind: "open" | "cut" | "replay";
  minute: number;
  home_team: string;
  away_team: string;
  home_goals: number;
  away_goals: number;
  moment: Moment | null;
  match_stakes: Stakes;
  fan_club: string | null;
  fan_club_is_playing_in_this_match: boolean;
  fan_club_table_rival_in_this_match: string | null;
  players_the_fan_follows_on_pitch: string[];
  fan_fantasy_captain_on_pitch: string | null;
  fan_fantasy_players_on_pitch: string[];
  fan_club_position_now: number | null;
  fan_club_position_at_kickoff: number | null;
  suspense_out_of_10: number | null;
  pressure_out_of_10: number | null;
};

export type CutData = {
  decision_id: number;
  kind: CutFacts["kind"];
  trigger: "start" | "relevance" | "must_show" | "off_air";
  match_id: string;
  text: string; // the correct reference line, shown at once
  language: Language;
  facts: CutFacts;
  alternatives: { match_id: string; value: number }[];
  value: number;
};

export type NarrationData = {
  decision_id: number;
  text: string;
  source: "model" | "template";
  drafts: number;
  language: Language;
};

export type FantasyData = {
  total: number;
  players: { name: string; points: number; captain: boolean }[];
};

export type Overlay =
  | { type: "cut"; seq: number; t: number; data: CutData }
  | { type: "narration"; seq: number; t: number; data: NarrationData }
  | { type: "scoreboard"; seq: number; t: number; data: { matches: ScoreLine[] } }
  | { type: "table"; seq: number; t: number; data: { rows: TableLine[] } }
  | { type: "fantasy"; seq: number; t: number; data: FantasyData }
  | { type: "end"; seq: number; t: number; data: Record<string, never> };
