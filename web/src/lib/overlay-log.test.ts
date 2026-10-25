import { describe, expect, it } from "vitest";

import type { Overlay } from "@/lib/overlay";
import { appendLog, clock, countByType, selectLog } from "./overlay-log";

const at = (seq: number, type: Overlay["type"]): Overlay => ({ seq, t: seq, type, data: {} }) as Overlay;

describe("appendLog", () => {
  it("keeps the newest events and drops the oldest past the bound", () => {
    let log: Overlay[] = [];
    for (let i = 1; i <= 5; i++) log = appendLog(log, at(i, "action"), 3);
    expect(log.map((o) => o.seq)).toEqual([3, 4, 5]);
  });

  it("does not mutate the previous log", () => {
    const first = appendLog([], at(1, "cut"));
    const second = appendLog(first, at(2, "table"));
    expect(first).toHaveLength(1);
    expect(second).toHaveLength(2);
  });
});

describe("selectLog", () => {
  const log = [at(1, "cut"), at(2, "action"), at(3, "action"), at(4, "narration"), at(5, "action")];

  it("returns everything newest first", () => {
    expect(selectLog(log, "all").map((o) => o.seq)).toEqual([5, 4, 3, 2, 1]);
  });

  it("filters by type and respects the limit from the newest end", () => {
    expect(selectLog(log, "action").map((o) => o.seq)).toEqual([5, 3, 2]);
    expect(selectLog(log, "action", 2).map((o) => o.seq)).toEqual([5, 3]);
  });

  it("counts every type, including the ones not seen", () => {
    const counts = countByType(log);
    expect(counts.action).toBe(3);
    expect(counts.cut).toBe(1);
    expect(counts.end).toBe(0);
  });
});

describe("clock", () => {
  it("formats matchday seconds as minutes and seconds", () => {
    expect(clock(0)).toBe("0:00");
    expect(clock(1440)).toBe("24:00");
    expect(clock(5405.7)).toBe("90:05");
  });
});
