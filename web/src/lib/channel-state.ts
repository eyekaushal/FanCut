/**
 * What one fan's channel knows, built by applying `overlay.v1` events in order.
 * Pure: the same events always produce the same state, which is what the tests check.
 */

import type { ActionData, CutData, FantasyData, NarrationData, Overlay, ScoreLine, TableLine } from "@/lib/overlay";

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
  /** Recent plays in the match on air, newest last. */
  actions: ActionData[];
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
      return {
        ...next,
        cut: overlay.data,
        cuts: [...state.cuts, overlay.data],
        // A new picture means a new pitch; a replay keeps its own moment's plays.
        actions: overlay.data.match_id === state.cut?.match_id ? state.actions : [],
      };
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
