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
  kind: "open" | "cut" | "replay" | "live";
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

/** A match's relevance to this fan with the evidence behind it. */
export type RankedMatch = {
  match_id: string;
  value: number;
  drama: number;
  stake: number;
  /** Machine-readable, e.g. "your_club", "rival:oakbridge", "fantasy_player:ash-09", "half_time". */
  reasons: string[];
};

export type CutData = {
  decision_id: number;
  kind: CutFacts["kind"];
  trigger: "start" | "relevance" | "must_show" | "off_air" | "moment";
  match_id: string;
  text: string; // the correct reference line, shown at once
  language: Language;
  /** On a Hinglish channel, the Hindi reference line for the voice; null elsewhere. */
  voice_text: string | null;
  facts: CutFacts;
  chosen: RankedMatch;
  alternatives: RankedMatch[];
  value: number;
};

export type NarrationData = {
  decision_id: number;
  text: string;
  source: "model" | "template";
  drafts: number;
  language: Language;
};

/**
 * A play in the match on air. Metres on a 105 × 68 pitch; home attacks towards
 * x = 105 and away towards x = 0, with no switch at half-time.
 */
export type ActionData = {
  match_id: string;
  minute: number;
  type:
    | "pass"
    | "carry"
    | "shot"
    | "goal"
    | "save"
    | "tackle"
    | "interception"
    | "corner"
    | "free_kick"
    | "foul"
    | "card"
    | "offside";
  side: "home" | "away" | null;
  player: string | null;
  x: number | null;
  y: number | null;
  end_x: number | null;
  end_y: number | null;
  outcome: boolean | null;
  xg: number | null;
};

/** One player's numbers so far, computed in code from the event stream. */
export type PlayerStats = {
  player_id: string;
  name: string;
  passes: number;
  passes_completed: number;
  pass_difficulty: number; // mean rating of the passes attempted, 0–1
  longest_pass_m: number;
  fastest_pass_mps: number;
  carries: number;
  distance_carried_m: number;
  top_speed_mps: number;
  bursts: number; // carries in the league's fastest 1%
  shots: number;
  goals: number;
  xg: number;
  fastest_shot_mps: number;
  tackles: number;
  interceptions: number;
};

export type PlayersData = {
  match_id: string;
  players: PlayerStats[]; // everyone on the pitch in the match on screen
};

export type FantasyData = {
  total: number;
  players: { name: string; points: number; captain: boolean }[];
};

export type Overlay =
  | { type: "cut"; seq: number; t: number; data: CutData }
  | { type: "narration"; seq: number; t: number; data: NarrationData }
  | { type: "action"; seq: number; t: number; data: ActionData }
  | { type: "scoreboard"; seq: number; t: number; data: { matches: ScoreLine[] } }
  | { type: "table"; seq: number; t: number; data: { rows: TableLine[] } }
  | { type: "fantasy"; seq: number; t: number; data: FantasyData }
  | { type: "focus"; seq: number; t: number; data: { match_id: string | null; ranking: RankedMatch | null } }
  | { type: "players"; seq: number; t: number; data: PlayersData }
  | { type: "end"; seq: number; t: number; data: Record<string, never> };
