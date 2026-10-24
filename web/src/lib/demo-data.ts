/**
 * A frozen moment of the real matchday (seed 34) at the 24th minute, captured from the
 * API for Arjun's channel, plus the same cut's reference line in all three languages
 * from the API's template narrator. Shapes are the `overlay.v1` payloads, so the
 * gallery renders exactly what the live channel will.
 */

import type { Language } from "@/lib/i18n";
import type { CutData, NarrationData, ScoreLine, TableLine } from "@/lib/overlay";

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

/** team_id → club colour, as `/matchday` reports it. */
export const clubColors: Record<string, string> = {
  calderbrook: "#3A6B8C", thornwick: "#1D3557", ashvale: "#B23A48", riverford: "#1F7A5C",
  oakbridge: "#7A1F2B", saltmarsh: "#457B9D", fenwick: "#6B3E26", northbrook: "#C8102E",
  elmhurst: "#2F4F2F", copperhill: "#B5651D", bramblefield: "#4A6741", wyndmoor: "#6D597A",
  silverbeck: "#8D99AE", hawkridge: "#9C2C2C", stonegate: "#5B4B8A", westhaven: "#E0A526",
  kingsmere: "#2E5EAA", glenhallow: "#2A9D8F", harbourside: "#0E7C86", linden: "#556B2F",
}; // prettier-ignore

export const fan = { name: "Arjun", club: "Kingsmere City", clubId: "kingsmere" };

const CUT_TEXT: Record<Language, string> = {
  en: "Cutting to Kingsmere City 0-1 Glenhallow Athletic, 24': your club Kingsmere City is playing.",
  hi: "अब Kingsmere City 0-1 Glenhallow Athletic पर, 24': आपका क्लब Kingsmere City खेल रहा है।",
  hinglish: "Ab chalte hain Kingsmere City 0-1 Glenhallow Athletic par, 24': aapka club Kingsmere City khel raha hai.",
};

/** The cut that put md34-09 on air at 24', as the API narrates it in each language. */
export function cut(lang: Language): CutData {
  return {
    decision_id: 9,
    kind: "cut",
    trigger: "relevance",
    match_id: "md34-09",
    text: CUT_TEXT[lang],
    language: lang,
    facts: {
      kind: "cut",
      minute: 24,
      home_team: "Kingsmere City",
      away_team: "Glenhallow Athletic",
      home_goals: 0,
      away_goals: 1,
      moment: null,
      match_stakes: "title_race",
      fan_club: "Kingsmere City",
      fan_club_is_playing_in_this_match: true,
      fan_club_table_rival_in_this_match: null,
      players_the_fan_follows_on_pitch: ["Rohan Mehta"],
      fan_fantasy_captain_on_pitch: null,
      fan_fantasy_players_on_pitch: ["Bastien Quaye"],
      fan_club_position_now: 2,
      fan_club_position_at_kickoff: 2,
      suspense_out_of_10: null,
      pressure_out_of_10: null,
    },
    chosen: { match_id: "md34-09", value: 1.85, drama: 0.41, stake: 2.3, reasons: ["your_club", "followed_player:kgc-09", "fantasy_player:glh-10", "stakes:title_race"] },
    alternatives: [
      { match_id: "md34-03", value: 1.31, drama: 0.46, stake: 0.8, reasons: ["rival:oakbridge", "stakes:title_race"] },
      { match_id: "md34-01", value: 1.2, drama: 0.37, stake: 0.8, reasons: ["rival:thornwick", "stakes:title_race"] },
      { match_id: "md34-07", value: 0.98, drama: 0.44, stake: 0.3, reasons: ["fantasy_player:slv-10"] },
    ],
    value: 1.85,
  };
}

const REPLAY_TEXT: Record<Language, string> = {
  en: "Replay from Oakbridge Town 1-0 Saltmarsh Town, 24': Pierre Delacroix scores for Oakbridge Town.",
  hi: "Oakbridge Town 1-0 Saltmarsh Town से रीप्ले, 24': Oakbridge Town के लिए Pierre Delacroix का गोल।",
  hinglish: "Oakbridge Town 1-0 Saltmarsh Town se replay, 24': Pierre Delacroix ka goal, Oakbridge Town ke liye.",
};

/** The must-show replay of the goal at md34-03, a table rival of the fan's club. */
export function replay(lang: Language): CutData {
  return {
    decision_id: 7,
    kind: "replay",
    trigger: "must_show",
    match_id: "md34-03",
    text: REPLAY_TEXT[lang],
    language: lang,
    facts: {
      kind: "replay",
      minute: 24,
      home_team: "Oakbridge Town",
      away_team: "Saltmarsh Town",
      home_goals: 1,
      away_goals: 0,
      moment: { type: "goal", player: "Pierre Delacroix", player_team: "Oakbridge Town", minute: 24 },
      match_stakes: "title_race",
      fan_club: "Kingsmere City",
      fan_club_is_playing_in_this_match: false,
      fan_club_table_rival_in_this_match: "Oakbridge Town",
      players_the_fan_follows_on_pitch: [],
      fan_fantasy_captain_on_pitch: null,
      fan_fantasy_players_on_pitch: [],
      fan_club_position_now: 2,
      fan_club_position_at_kickoff: 2,
      suspense_out_of_10: null,
      pressure_out_of_10: null,
    },
    chosen: { match_id: "md34-03", value: 1.31, drama: 0.46, stake: 0.8, reasons: ["rival:oakbridge", "stakes:title_race"] },
    alternatives: [{ match_id: "md34-09", value: 1.85, drama: 0.41, stake: 2.3, reasons: ["your_club", "stakes:title_race"] }],
    value: 1.31,
  };
}

/**
 * A Narrator line for the cut above, as the model wrote and the Fact Checker passed it
 * on 24 Oct (English only; the model's Hindi and Hinglish lines are captured in Block 10).
 */
export const narration: NarrationData = {
  decision_id: 9,
  text: "Over to Kingsmere City, a goal down to Glenhallow Athletic after 24 minutes: your club, in a title race, with Rohan Mehta on the pitch.",
  source: "model",
  drafts: 1,
  language: "en",
};
