import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { cut, replay } from "@/lib/demo-data";
import type { Overlay } from "@/lib/overlay";
import { ReplayHold } from "./replay-hold";

let seq = 0;
const at = (type: Overlay["type"], data: unknown): Overlay => ({ type, seq: ++seq, t: 0, data }) as Overlay;

describe("ReplayHold", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it("passes events straight through until a replay arrives", () => {
    const delivered: Overlay[] = [];
    const hold = new ReplayHold((o) => delivered.push(o), 2500);
    hold.push(at("cut", cut("en")));
    hold.push(at("scoreboard", { matches: [] }));
    expect(delivered).toHaveLength(2);
  });

  it("holds everything after a replay, then flushes in order", () => {
    const delivered: Overlay[] = [];
    const hold = new ReplayHold((o) => delivered.push(o), 2500);
    hold.push(at("cut", replay("en")));
    hold.push(at("cut", cut("en")));
    hold.push(at("scoreboard", { matches: [] }));
    expect(delivered.map((o) => o.type)).toEqual(["cut"]);
    vi.advanceTimersByTime(2499);
    expect(delivered).toHaveLength(1);
    vi.advanceTimersByTime(1);
    expect(delivered.map((o) => o.type)).toEqual(["cut", "cut", "scoreboard"]);
    expect(delivered.map((o) => o.seq)).toEqual([1 + seq - 3, 2 + seq - 3, 3 + seq - 3]);
  });

  it("a second replay in the queue starts its own hold", () => {
    const delivered: Overlay[] = [];
    const hold = new ReplayHold((o) => delivered.push(o), 1000);
    hold.push(at("cut", replay("en")));
    hold.push(at("cut", cut("en")));
    hold.push(at("cut", { ...replay("en"), decision_id: 11 }));
    hold.push(at("cut", { ...cut("en"), decision_id: 12 }));
    vi.advanceTimersByTime(1000);
    expect(delivered).toHaveLength(3); // the second replay is now on screen, its cut waits
    vi.advanceTimersByTime(1000);
    expect(delivered).toHaveLength(4);
  });

  it("drops what it was holding when disposed", () => {
    const delivered: Overlay[] = [];
    const hold = new ReplayHold((o) => delivered.push(o), 1000);
    hold.push(at("cut", replay("en")));
    hold.push(at("cut", cut("en")));
    hold.dispose();
    vi.advanceTimersByTime(2000);
    expect(delivered).toHaveLength(1);
  });
});
