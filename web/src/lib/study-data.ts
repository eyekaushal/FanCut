/**
 * A frozen moment of the real matchday (seed 34) at the 24th minute, captured from the
 * API's overlay.v1 stream for Arjun's channel. The shapes match the API payloads, so the
 * study renders exactly what the live channel will.
 */

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
  status: "live" | "half_time" | "full_time";
  stakes: "title_race" | "top_four" | "relegation" | "derby" | "mid_table";
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
  change: number;
};

export const STAKES_LABEL: Record<ScoreLine["stakes"], string> = {
  title_race: "Title race",
  top_four: "Top four",
  relegation: "Relegation",
  derby: "Derby",
  mid_table: "Mid-table",
};

// prettier-ignore
export const scoreboard: ScoreLine[] = [
  { match_id: "md34-01", home: "Calderbrook FC", away: "Thornwick United", home_short: "CAL", away_short: "THW", home_color: "#3A6B8C", away_color: "#1D3557", home_goals: 2, away_goals: 0, minute: 24, status: "live", stakes: "title_race", on_air: false },
  { match_id: "md34-02", home: "Ashvale Rovers", away: "Riverford Athletic", home_short: "ASH", away_short: "RIV", home_color: "#B23A48", away_color: "#1F7A5C", home_goals: 0, away_goals: 1, minute: 24, status: "live", stakes: "top_four", on_air: false },
  { match_id: "md34-03", home: "Oakbridge Town", away: "Saltmarsh Town", home_short: "OAK", away_short: "SLT", home_color: "#7A1F2B", away_color: "#457B9D", home_goals: 1, away_goals: 0, minute: 24, status: "live", stakes: "title_race", on_air: false },
  { match_id: "md34-04", home: "Fenwick Forest", away: "Northbrook United", home_short: "FEN", away_short: "NBU", home_color: "#6B3E26", away_color: "#C8102E", home_goals: 1, away_goals: 0, minute: 24, status: "live", stakes: "top_four", on_air: false },
  { match_id: "md34-05", home: "Elmhurst Wanderers", away: "Copperhill City", home_short: "ELM", away_short: "CPH", home_color: "#2F4F2F", away_color: "#B5651D", home_goals: 0, away_goals: 1, minute: 24, status: "live", stakes: "relegation", on_air: false },
  { match_id: "md34-06", home: "Bramblefield FC", away: "Wyndmoor Albion", home_short: "BRM", away_short: "WYN", home_color: "#4A6741", away_color: "#6D597A", home_goals: 0, away_goals: 0, minute: 24, status: "live", stakes: "top_four", on_air: false },
  { match_id: "md34-07", home: "Silverbeck Rovers", away: "Hawkridge Wanderers", home_short: "SLV", away_short: "HWK", home_color: "#8D99AE", away_color: "#9C2C2C", home_goals: 2, away_goals: 0, minute: 24, status: "live", stakes: "relegation", on_air: false },
  { match_id: "md34-08", home: "Stonegate Albion", away: "Westhaven Town", home_short: "STA", away_short: "WHT", home_color: "#5B4B8A", away_color: "#E0A526", home_goals: 0, away_goals: 0, minute: 24, status: "live", stakes: "mid_table", on_air: false },
  { match_id: "md34-09", home: "Kingsmere City", away: "Glenhallow Athletic", home_short: "KGC", away_short: "GLH", home_color: "#2E5EAA", away_color: "#2A9D8F", home_goals: 0, away_goals: 1, minute: 24, status: "live", stakes: "title_race", on_air: true },
  { match_id: "md34-10", home: "Harbourside Rangers", away: "Linden Park", home_short: "HBR", away_short: "LDP", home_color: "#0E7C86", away_color: "#556B2F", home_goals: 1, away_goals: 1, minute: 24, status: "live", stakes: "relegation", on_air: false },
];

// prettier-ignore
export const table: TableLine[] = [
  { position: 1, team_id: "oakbridge", team: "Oakbridge Town", short: "OAK", played: 34, points: 58, goal_difference: 29, change: 0 },
  { position: 2, team_id: "kingsmere", team: "Kingsmere City", short: "KGC", played: 34, points: 55, goal_difference: 21, change: 0 },
  { position: 3, team_id: "thornwick", team: "Thornwick United", short: "THW", played: 34, points: 51, goal_difference: 11, change: 0 },
  { position: 4, team_id: "copperhill", team: "Copperhill City", short: "CPH", played: 34, points: 51, goal_difference: 1, change: 4 },
  { position: 5, team_id: "ashvale", team: "Ashvale Rovers", short: "ASH", played: 34, points: 50, goal_difference: 33, change: -1 },
  { position: 6, team_id: "wyndmoor", team: "Wyndmoor Albion", short: "WYN", played: 34, points: 49, goal_difference: 0, change: 0 },
];

/** The cut that put md34-09 on air at 24', as the API narrated it for Arjun (Hindi). */
export const cut = {
  kind: "cut",
  trigger: "relevance",
  match_id: "md34-09",
  text: "अब Kingsmere City 0-1 Glenhallow Athletic पर, 24': आपका क्लब Kingsmere City खेल रहा है।",
  language: "hi",
  facts: {
    fan_club: "Kingsmere City",
    match_stakes: "title_race",
    players_the_fan_follows_on_pitch: ["Rohan Mehta"],
    fan_fantasy_players_on_pitch: ["Bastien Quaye"],
    fan_club_position_now: 2,
  },
} as const;

export const fanClubId = "kingsmere";
