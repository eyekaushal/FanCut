import { Panel } from "@/components/ui/panel";
import { t, type Language } from "@/lib/i18n";
import type { FantasyData } from "@/lib/overlay";

/** The fan's fantasy squad and points, as the API scores them (captain already doubled). */
export function FantasyPanel({ fantasy, lang }: { fantasy: FantasyData | null; lang: Language }) {
  const players = fantasy ? [...fantasy.players].sort((a, b) => b.points - a.points) : [];
  return (
    <Panel
      title={t(lang, "fantasyPts")}
      aside={fantasy ? <span className="t-title2 tabular text-fg">{fantasy.total}</span> : undefined}
    >
      {players.length === 0 ? (
        <p className="t-callout text-fg-muted">—</p>
      ) : (
        <ul className="tabular t-callout">
          {players.map((p) => (
            <li key={p.name} className="flex items-center justify-between border-t border-hairline py-2">
              <span className="flex items-center gap-2">
                {p.name}
                {p.captain && (
                  <span className="t-micro rounded-chip bg-fg/8 px-1.5 py-0.5 uppercase text-fg-muted">
                    {t(lang, "captain")}
                  </span>
                )}
              </span>
              <span className={p.points > 0 ? "" : "text-fg-muted"}>{p.points}</span>
            </li>
          ))}
        </ul>
      )}
    </Panel>
  );
}
