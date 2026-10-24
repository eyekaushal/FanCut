import { describe, expect, it } from "vitest";

import { cut, narration, replay, scoreboard, table } from "@/lib/demo-data";
import type { ActionData, Overlay } from "@/lib/overlay";
import { ACTIONS_KEPT, applyOverlay, initialState, matchOnAir, narrationOnAir } from "./channel-state";

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

  it("clears the pitch when the picture cuts to another match, and keeps it otherwise", () => {
    const onAir = play([at("cut", cut("en")), at("action", pass("md34-09"))]);
    expect(onAir.actions).toHaveLength(1);
    const stayed = applyOverlay(onAir, at("cut", { ...cut("en"), decision_id: 10 }));
    expect(stayed.actions).toHaveLength(1);
    const moved = applyOverlay(onAir, at("cut", replay("en")));
    expect(moved.actions).toHaveLength(0);
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
