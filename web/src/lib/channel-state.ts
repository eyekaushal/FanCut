/**
 * What one fan's channel knows, built by applying `overlay.v1` events in order.
 * Pure: the same events always produce the same state, which is what the tests check.
 */

import type {
  ActionData,
  CutData,
  FantasyData,
  NarrationData,
  Overlay,
  PlayersData,
  RankedMatch,
  ScoreLine,
  TableLine,
} from "@/lib/overlay";

/** How many pitch actions the renderer keeps; older ones have faded anyway. */
export const ACTIONS_KEPT = 40;

export type ChannelState = {
  /** The decision currently on air (a replay interrupts, then its cut takes over). */
  cut: CutData | null;
  /** Narrator lines by decision id; the reason card picks the one for the cut on air. */
  narrations: Record<number, NarrationData>;
  /** Every cut so far, newest last, for the history and the Director's notes. */
  cuts: CutData[];
  matches: ScoreLine[];
  table: TableLine[];
  fantasy: FantasyData | null;
  /** Recent plays, newest last; the pitch shows those of the match on screen. */
  actions: ActionData[];
  /** The match the fan locked the pitch to, or null when the Director has the picture. */
  focus: string | null;
  /** The Director's latest ranking of the focused match, refreshed as the matchday moves. */
  focusRanking: RankedMatch | null;
  /** Per-player numbers for the match on screen, refreshed with the scoreboard. */
  players: PlayersData | null;
  /** Matchday seconds of the latest event. */
  t: number;
  seq: number;
  ended: boolean;
};

export const initialState: ChannelState = {
  cut: null,
  narrations: {},
  cuts: [],
  matches: [],
  table: [],
  fantasy: null,
  actions: [],
  focus: null,
  focusRanking: null,
  players: null,
  t: 0,
  seq: 0,
  ended: false,
};

export function applyOverlay(state: ChannelState, overlay: Overlay): ChannelState {
  // SSE can redeliver on reconnect; an event we have already applied is dropped.
  if (overlay.seq <= state.seq) return state;
  const next = { ...state, t: overlay.t, seq: overlay.seq };

  switch (overlay.type) {
    case "cut":
      return { ...next, cut: overlay.data, cuts: [...state.cuts, overlay.data] };
    case "narration":
      return { ...next, narrations: { ...state.narrations, [overlay.data.decision_id]: overlay.data } };
    case "action":
      return { ...next, actions: [...state.actions, overlay.data].slice(-ACTIONS_KEPT) };
    case "scoreboard":
      return { ...next, matches: overlay.data.matches };
    case "table":
      return { ...next, table: overlay.data.rows };
    case "fantasy":
      return { ...next, fantasy: overlay.data };
    case "focus":
      return { ...next, focus: overlay.data.match_id, focusRanking: overlay.data.ranking };
    case "players":
      return { ...next, players: overlay.data };
    case "end":
      return { ...next, ended: true };
  }
}

/** The Narrator's line for the decision on air, if it has arrived. */
export function narrationOnAir(state: ChannelState): NarrationData | null {
  return state.cut ? (state.narrations[state.cut.decision_id] ?? null) : null;
}

/** The scoreboard line of the match on air. */
export function matchOnAir(state: ChannelState): ScoreLine | null {
  return state.cut ? (state.matches.find((m) => m.match_id === state.cut?.match_id) ?? null) : null;
}

/** The match on screen: the fan's focus if set, otherwise the Director's pick. */
export function matchShown(state: ChannelState): ScoreLine | null {
  if (state.focus) return state.matches.find((m) => m.match_id === state.focus) ?? null;
  return matchOnAir(state);
}

/** The plays to draw for the match on screen. */
export function actionsShown(state: ChannelState): ActionData[] {
  const shown = state.focus ?? state.cut?.match_id;
  return shown ? state.actions.filter((a) => a.match_id === shown) : [];
}

/**
 * The Director's ranking of `matchId`: the live one if it is the focus, else what the
 * latest cut knew (its own pick or one of the alternatives it beat), else nothing.
 */
export function rankingOf(state: ChannelState, matchId: string): RankedMatch | null {
  if (state.focus === matchId && state.focusRanking) return state.focusRanking;
  if (!state.cut) return null;
  if (state.cut.chosen.match_id === matchId) return state.cut.chosen;
  return state.cut.alternatives.find((a) => a.match_id === matchId) ?? null;
}

/** The players' numbers, if they are for the match on screen. */
export function playersShown(state: ChannelState): PlayersData | null {
  const shown = state.focus ?? state.cut?.match_id;
  return state.players && state.players.match_id === shown ? state.players : null;
}
