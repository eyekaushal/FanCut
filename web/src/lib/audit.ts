/**
 * Reading the audit trail. Everything here is arithmetic over the API's numbers; the
 * Studio shows what the Director recorded and never re-scores a decision.
 */

import type { AuditEntry } from "@/lib/api";

/** How clearly the chosen match won: its relevance minus the best alternative's. */
export function marginOf(entry: AuditEntry): number | null {
  const best = entry.alternatives[0];
  return best ? Math.round((entry.chosen.value - best.value) * 1000) / 1000 : null;
}

export type NarrationStatus = "writing" | "model" | "template";

/** Where the line on air came from, or that the Narrator has not answered yet. */
export function narrationStatus(entry: AuditEntry): NarrationStatus {
  if (!entry.narration) return "writing";
  return entry.narration.source;
}

/** Fact Checker rejections across the trail, most frequent first. */
export function rejectionTally(entries: AuditEntry[]): { problem: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const entry of entries) {
    for (const problem of entry.narration?.rejected ?? []) counts.set(problem, (counts.get(problem) ?? 0) + 1);
  }
  return [...counts].map(([problem, count]) => ({ problem, count })).sort((a, b) => b.count - a.count);
}

/** The decisions the Narrator has answered, and how many of those it wrote itself. */
export function narrationSummary(entries: AuditEntry[]): { answered: number; model: number; drafts: number } {
  let answered = 0;
  let model = 0;
  let drafts = 0;
  for (const entry of entries) {
    if (!entry.narration) continue;
    answered += 1;
    drafts += entry.narration.drafts;
    if (entry.narration.source === "model") model += 1;
  }
  return { answered, model, drafts };
}
