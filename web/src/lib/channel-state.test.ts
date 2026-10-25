import { describe, expect, it } from "vitest";

import { cut, narration, replay, scoreboard, table } from "@/lib/demo-data";
import type { ActionData, Overlay } from "@/lib/overlay";
import {
  ACTIONS_KEPT,
  actionsShown,
  applyOverlay,
  initialState,
  matchOnAir,
  matchShown,
  narrationOnAir,
  playersShown,
  rankingOf,
} from "./channel-state";

let seq = 0;
const at = (type: Overlay["type"], data: unknown, t = 0): Overlay =>
  ({ type, seq: ++seq, t, data }) as Overlay;

const pass = (match_id: string, minute = 1): ActionData => ({
  match_id, minute, type: "pass", side: "home", player: "Felix Whitlock",
  x: 52.5, y: 34, end_x: 67.4, end_y: 42.4, outcome: true, xg: null,
}); // prettier-ignore

function play(events: Overlay[]) {
  return events.reduce(applyOverlay, initialState);
}

describe("applyOverlay", () => {
  it("puts a cut on air and remembers every cut", () => {
    const state = play([at("cut", replay("en")), at("cut", cut("en"), 1440)]);
    expect(state.cut?.decision_id).toBe(9);
    expect(state.cuts.map((c) => c.decision_id)).toEqual([7, 9]);
    expect(state.t).toBe(1440);
  });

  it("keeps the narration only for the decision on air", () => {
    const state = play([at("cut", cut("en")), at("narration", narration)]);
    expect(narrationOnAir(state)?.text).toBe(narration.text);
    const later = applyOverlay(state, at("cut", replay("en")));
    expect(narrationOnAir(later)).toBeNull(); // decision 7 has no narration yet
    expect(later.narrations[9]).toBeDefined(); // but the earlier one is kept for history
  });

  it("drops an event it has already applied, as a reconnect can redeliver", () => {
    const first = at("scoreboard", { matches: scoreboard });
    const state = play([first]);
    expect(applyOverlay(state, first)).toBe(state);
  });

  it("keeps every recent play and lets the pitch pick the match on screen", () => {
    const state = play([
      at("cut", cut("en")),
      at("action", pass("md34-09")),
      at("action", pass("md34-03")),
      at("cut", replay("en")),
    ]);
    expect(state.actions).toHaveLength(2);
    expect(actionsShown(state).map((a) => a.match_id)).toEqual(["md34-03"]);
  });

  it("locks the pitch to the fan's focus and releases it", () => {
    const base = play([at("cut", cut("en")), at("action", pass("md34-09")), at("action", pass("md34-05"))]);
    const ranking = { match_id: "md34-05", value: 0.6, drama: 0.3, stake: 0.3, reasons: ["stakes:relegation"] };
    const focused = applyOverlay(base, at("focus", { match_id: "md34-05", ranking }));
    expect(matchShown(focused)).toBeNull(); // no scoreboard yet
    expect(actionsShown(focused).map((a) => a.match_id)).toEqual(["md34-05"]);
    expect(rankingOf(focused, "md34-05")).toBe(ranking); // live, even though no cut ranked it
    const released = applyOverlay(focused, at("focus", { match_id: null, ranking: null }));
    expect(actionsShown(released).map((a) => a.match_id)).toEqual(["md34-09"]);
    expect(rankingOf(released, "md34-05")).toBeNull();
  });

  it("explains any match the latest cut ranked", () => {
    const state = play([at("cut", cut("en"))]);
    expect(rankingOf(state, "md34-09")?.reasons).toContain("your_club");
    expect(rankingOf(state, "md34-03")?.value).toBe(1.31);
    expect(rankingOf(state, "md34-10")).toBeNull();
  });

  it("keeps players' numbers only for the match on screen", () => {
    const stats = { player_id: "kgc-09", name: "Rohan Mehta", passes: 3, passes_completed: 2, pass_difficulty: 0.4, longest_pass_m: 22, fastest_pass_mps: 14, carries: 2, distance_carried_m: 18, top_speed_mps: 3.1, bursts: 0, shots: 1, goals: 0, xg: 0.08, fastest_shot_mps: 20, tackles: 0, interceptions: 1 };
    const state = play([at("cut", cut("en")), at("players", { match_id: "md34-09", players: [stats] })]);
    expect(playersShown(state)?.players[0]?.name).toBe("Rohan Mehta");
    const elsewhere = applyOverlay(state, at("focus", { match_id: "md34-05", ranking: null }));
    expect(playersShown(elsewhere)).toBeNull();
  });

  it("keeps only the most recent plays", () => {
    const opening = at("cut", cut("en"));
    const events = Array.from({ length: ACTIONS_KEPT + 5 }, (_, i) => at("action", pass("md34-09", i)));
    const state = play([opening, ...events]);
    expect(state.actions).toHaveLength(ACTIONS_KEPT);
    expect(state.actions.at(-1)?.minute).toBe(ACTIONS_KEPT + 4);
  });

  it("replaces the scoreboard, table and fantasy wholesale, and ends", () => {
    const state = play([
      at("scoreboard", { matches: scoreboard }),
      at("table", { rows: table }),
      at("fantasy", { total: 27, players: [{ name: "Theo Ashworth", points: 4, captain: true }] }),
      at("cut", cut("en")),
      at("end", {}),
    ]);
    expect(matchOnAir(state)?.home).toBe("Kingsmere City");
    expect(state.table[0]?.team).toBe("Oakbridge Town");
    expect(state.fantasy?.total).toBe(27);
    expect(state.ended).toBe(true);
  });
});
