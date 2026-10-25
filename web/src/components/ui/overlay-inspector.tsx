"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import type { Contract } from "@/lib/api";
import type { Overlay } from "@/lib/overlay";
import { OVERLAY_TYPES, clock, countByType, selectLog, type OverlayType } from "@/lib/overlay-log";

type Filter = OverlayType | "all";

/**
 * The raw `overlay.v1` stream, event by event, for anyone who has to render it
 * elsewhere. Filter by type, pause to read, open an event for its JSON, copy it.
 * The contract's own description of each type sits under the filter.
 */
export function OverlayInspector({ log, contract }: { log: Overlay[]; contract: Contract | null }) {
  const [filter, setFilter] = useState<Filter>("all");
  const [paused, setPaused] = useState(false);
  const [frozen, setFrozen] = useState<Overlay[]>([]);
  const [open, setOpen] = useState<number | null>(null);

  // Pausing keeps the list as it was; the stream keeps flowing into `log` underneath.
  const togglePause = () => {
    if (!paused) setFrozen(log);
    setPaused(!paused);
  };

  const shown = paused ? frozen : log;
  const counts = countByType(shown);
  const rows = selectLog(shown, filter);
  const description = filter === "all" ? contract?.transport : contract?.events.find((e) => e.type === filter)?.description;

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <ul className="flex flex-wrap gap-1.5" aria-label="Event types">
          <FilterChip active={filter === "all"} onClick={() => setFilter("all")} label="All" count={shown.length} />
          {OVERLAY_TYPES.map((type) => (
            <FilterChip key={type} active={filter === type} onClick={() => setFilter(type)} label={type} count={counts[type]} />
          ))}
        </ul>
        <Button size="small" variant={paused ? "primary" : "secondary"} aria-pressed={paused} onClick={togglePause}>
          {paused ? "Resume" : "Pause"}
        </Button>
      </div>

      {description && <p className="t-caption mt-3 max-w-[64ch] text-fg-muted">{description}</p>}

      <ol className="no-scrollbar mt-4 max-h-[60vh] divide-y divide-hairline overflow-y-auto" aria-live="off">
        {rows.length === 0 && <li className="t-callout py-3 text-fg-muted">Nothing yet.</li>}
        {rows.map((o) => (
          <EventRow key={o.seq} overlay={o} open={open === o.seq} onToggle={() => setOpen(open === o.seq ? null : o.seq)} />
        ))}
      </ol>
    </div>
  );
}

function FilterChip({ active, onClick, label, count }: { active: boolean; onClick: () => void; label: string; count: number }) {
  return (
    <li>
      <button
        type="button"
        aria-pressed={active}
        onClick={onClick}
        className={`pressable t-caption inline-flex h-7 items-center gap-1.5 rounded-chip px-2.5 transition-colors duration-(--t-fast) ${
          active ? "bg-fg text-bg" : "bg-fg/8 text-fg-muted hover:text-fg"
        }`}
      >
        {label}
        <span className={`tabular ${active ? "text-bg/70" : "text-fg-faint"}`}>{count}</span>
      </button>
    </li>
  );
}

function EventRow({ overlay, open, onToggle }: { overlay: Overlay; open: boolean; onToggle: () => void }) {
  const [copied, setCopied] = useState(false);
  const json = JSON.stringify(overlay, null, 2);
  const summary = summarize(overlay);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(json);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      // The clipboard can be unavailable (insecure context); the JSON is on screen anyway.
    }
  };
  return (
    <li>
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className="-mx-2 flex w-[calc(100%+16px)] items-baseline gap-3 rounded-control px-2 py-2 text-left hover:bg-fg/4"
      >
        <span className="t-caption tabular w-10 shrink-0 text-fg-faint">{overlay.seq}</span>
        <span className="t-caption tabular w-12 shrink-0 text-fg-muted">{clock(overlay.t)}</span>
        <span className="t-caption w-20 shrink-0 font-semibold">{overlay.type}</span>
        <span className="t-caption min-w-0 flex-1 truncate text-fg-muted">{summary}</span>
      </button>
      {open && (
        <div className="relative mb-2">
          <pre className="t-micro max-h-80 overflow-auto rounded-control bg-fg/4 p-3 font-mono leading-relaxed text-fg-muted">{json}</pre>
          <Button size="small" className="absolute top-2 right-2" onClick={copy}>
            {copied ? "Copied" : "Copy JSON"}
          </Button>
        </div>
      )}
    </li>
  );
}

/** One line about an event, from its own fields. */
function summarize(o: Overlay): string {
  switch (o.type) {
    case "cut":
      return `${o.data.kind} · ${o.data.match_id} · ${o.data.trigger} · ${o.data.value.toFixed(2)}`;
    case "narration":
      return `#${o.data.decision_id} · ${o.data.source} · ${o.data.text}`;
    case "action":
      return `${o.data.type} · ${o.data.player ?? "—"} · ${o.data.match_id}`;
    case "scoreboard":
      return `${o.data.matches.length} matches · on air ${o.data.matches.find((m) => m.on_air)?.match_id ?? "—"}`;
    case "table":
      return `${o.data.rows.length} rows · 1st ${o.data.rows[0]?.short ?? "—"}`;
    case "fantasy":
      return `${o.data.total} points · ${o.data.players.length} players`;
    case "focus":
      return o.data.match_id ? `locked to ${o.data.match_id}` : "released";
    case "players":
      return `${o.data.players.length} on the pitch · ${o.data.match_id}`;
    case "end":
      return "full time everywhere";
  }
}
