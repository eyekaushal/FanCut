import { describe, expect, it } from "vitest";

import type { AuditEntry } from "@/lib/api";
import { cut } from "@/lib/demo-data";
import { marginOf, narrationStatus, narrationSummary, rejectionTally } from "./audit";

function entry(overrides: Partial<AuditEntry> = {}): AuditEntry {
  const c = cut("en");
  return {
    decision_id: c.decision_id,
    t: 1440,
    minute: 24,
    kind: c.kind,
    trigger: c.trigger,
    match_id: c.match_id,
    previous_match_id: "md34-01",
    chosen: c.chosen,
    alternatives: c.alternatives,
    moment: null,
    facts: c.facts,
    reference: c.text,
    narration: null,
    ...overrides,
  };
}

describe("marginOf", () => {
  it("is the chosen relevance minus the best alternative's", () => {
    const e = entry({
      chosen: { ...cut("en").chosen, value: 1.5 },
      alternatives: [{ ...cut("en").alternatives[0], value: 1.18 }],
    });
    expect(marginOf(e)).toBe(0.32);
  });

  it("is null when nothing else was live", () => {
    expect(marginOf(entry({ alternatives: [] }))).toBeNull();
  });
});

describe("narrationStatus", () => {
  const written = { text: "x", language: "en" as const, source: "model" as const, drafts: 2, rejected: ["number 3 is not in the facts"] };

  it("is writing until the Narrator answers, then names the source", () => {
    expect(narrationStatus(entry())).toBe("writing");
    expect(narrationStatus(entry({ narration: written }))).toBe("model");
    expect(narrationStatus(entry({ narration: { ...written, source: "template" } }))).toBe("template");
  });

  it("tallies rejections and drafts across the trail", () => {
    const entries = [
      entry({ narration: written }),
      entry({ narration: { ...written, rejected: ["number 3 is not in the facts", "Oakbridge Town is not in the facts"] } }),
      entry(),
    ];
    expect(rejectionTally(entries)).toEqual([
      { problem: "number 3 is not in the facts", count: 2 },
      { problem: "Oakbridge Town is not in the facts", count: 1 },
    ]);
    expect(narrationSummary(entries)).toEqual({ answered: 2, model: 2, drafts: 4 });
  });
});
