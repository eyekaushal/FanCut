import { reasonLabels, type Language } from "@/lib/i18n";
import type { RankedMatch } from "@/lib/overlay";

export type MatchNames = Record<string, { label: string; homeColor: string; awayColor: string }>;

/**
 * The Director's ranking at one decision: the match it chose on top, then the
 * alternatives it beat, each bar as long as its relevance. Numbers are the Director's.
 */
export function RelevanceBars({
  chosen,
  alternatives,
  names,
  lang,
}: {
  chosen: RankedMatch;
  alternatives: RankedMatch[];
  names: MatchNames;
  lang: Language;
}) {
  const rows = [chosen, ...alternatives];
  const max = Math.max(...rows.map((r) => r.value), 0.001);
  return (
    <ol className="space-y-2">
      {rows.map((r, i) => {
        const name = names[r.match_id];
        const reasons = reasonLabels(lang, r.reasons);
        return (
          <li key={r.match_id} className="grid grid-cols-[minmax(0,1fr)_minmax(0,2fr)] items-center gap-x-4 gap-y-0.5 sm:grid-cols-[112px_minmax(0,1fr)_minmax(0,1fr)]">
            <span className="t-caption flex min-w-0 items-center gap-2">
              {name && <ClubDots home={name.homeColor} away={name.awayColor} />}
              <span className={`truncate ${i === 0 ? "text-fg" : "text-fg-muted"}`}>{name?.label ?? r.match_id}</span>
            </span>
            <span className="flex items-center gap-3">
              <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-fg/8">
                <span
                  className={`block h-full rounded-full transition-[width] duration-(--t-base) ease-(--ease) ${i === 0 ? "bg-fg" : "bg-fg/35"}`}
                  style={{ width: `${Math.max(2, (r.value / max) * 100)}%` }}
                />
              </span>
              <span className="t-caption tabular w-10 shrink-0 text-right">{r.value.toFixed(2)}</span>
            </span>
            <span className="t-micro col-span-2 truncate text-fg-faint sm:col-span-1">
              {reasons.length ? reasons.join(" · ") : `drama ${r.drama.toFixed(2)}`}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

/** Two small dots in the clubs' colours: the only colour on a Studio row. */
export function ClubDots({ home, away }: { home: string; away: string }) {
  return (
    <span className="flex shrink-0 -space-x-0.5" aria-hidden>
      <i className="block size-2 rounded-full ring-1 ring-bg-elevated" style={{ background: home }} />
      <i className="block size-2 rounded-full ring-1 ring-bg-elevated" style={{ background: away }} />
    </span>
  );
}
