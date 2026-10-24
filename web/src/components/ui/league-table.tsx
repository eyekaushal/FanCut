import { clubGradient } from "@/lib/color";
import { t, type Language } from "@/lib/i18n";
import type { TableLine } from "@/lib/overlay";

function signed(n: number): string {
  return n > 0 ? `+${n}` : String(n);
}

function movement(change: number): string {
  if (change === 0) return "–";
  return `${change > 0 ? "▲" : "▼"} ${Math.abs(change)}`;
}

/**
 * The table as it stands. Club colour appears only as a dot on the club's own row;
 * the fan's club is set in bold. `colors` maps team_id to the club's hex.
 */
export function LeagueTable({
  rows,
  lang,
  fanClubId,
  colors,
  limit,
}: {
  rows: TableLine[];
  lang: Language;
  fanClubId?: string | null;
  colors: Record<string, string>;
  limit?: number;
}) {
  const shown = limit ? rows.slice(0, limit) : rows;
  return (
    <table className="tabular w-full t-callout">
      <thead className="t-micro uppercase text-fg-faint">
        <tr>
          <th className="w-7 pb-2 text-left font-semibold">#</th>
          <th className="pb-2 text-left font-semibold">{t(lang, "club")}</th>
          <th className="pb-2 pl-4 text-right font-semibold">{t(lang, "goalDiff")}</th>
          <th className="pb-2 pl-4 text-right font-semibold">{t(lang, "points")}</th>
          <th className="w-14 pb-2 pl-4 text-right font-semibold">
            <span aria-label={t(lang, "change")}>Δ</span>
          </th>
        </tr>
      </thead>
      <tbody>
        {shown.map((row) => {
          const mine = row.team_id === fanClubId;
          return (
            <tr key={row.team_id} className={`border-t border-hairline ${mine ? "font-semibold" : ""}`}>
              <td className="py-2.5 text-fg-muted">{row.position}</td>
              <td className="py-2.5">
                <span className="flex items-center gap-2.5">
                  <i
                    className="block size-2.5 shrink-0 rounded-full"
                    style={{ background: clubGradient(colors[row.team_id] ?? "#888888") }}
                    aria-hidden
                  />
                  <span className="truncate">{row.team}</span>
                </span>
              </td>
              <td className="py-2.5 pl-4 text-right text-fg-muted">{signed(row.goal_difference)}</td>
              <td className="py-2.5 pl-4 text-right">{row.points}</td>
              <td className="py-2.5 pl-4 text-right text-fg-muted">{movement(row.change)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
