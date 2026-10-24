import { Chip } from "@/components/ui/chip";
import { Panel } from "@/components/ui/panel";
import { fontClass, ordinal, t, type Language } from "@/lib/i18n";
import type { Recap } from "@/lib/api";

/**
 * The fan's matchday in a few sentences, from the API's recap. The numbers under the
 * text are the fact sheet the Narrator was held to; nothing here is computed in the UI.
 */
export function RecapCard({ recap, lang }: { recap: Recap; lang: Language }) {
  const f = recap.facts;
  const stats: { label: string; value: string }[] = [];
  if (f.fan_club && f.fan_club_goals !== null && f.fan_club_opponent_goals !== null) {
    stats.push({ label: f.fan_club, value: `${f.fan_club_goals}–${f.fan_club_opponent_goals}` });
  }
  if (f.fan_club_position_now !== null) {
    stats.push({ label: t(lang, "tableLabel"), value: ordinal(lang, f.fan_club_position_now) });
  }
  stats.push({ label: t(lang, "cutsLabel"), value: String(f.cuts) });
  stats.push({ label: t(lang, "matchesLabel"), value: String(f.matches_shown) });
  if (f.fantasy_total !== null) stats.push({ label: t(lang, "fantasyPts"), value: String(f.fantasy_total) });

  return (
    <Panel title={t(lang, "yourMatchday")} aside={recap.source === "model" ? "Narrator" : t(lang, "referenceLine")}>
      <p lang={lang === "hi" ? "hi" : undefined} className={`t-title2 max-w-[40ch] font-medium ${fontClass(lang)}`}>
        {recap.text}
      </p>
      <dl className="tabular mt-6 grid grid-cols-2 gap-4 sm:grid-cols-5">
        {stats.map((s) => (
          <div key={s.label}>
            <dt className="t-micro truncate uppercase text-fg-faint">{s.label}</dt>
            <dd className="t-title1 mt-1">{s.value}</dd>
          </div>
        ))}
      </dl>
      {f.moments_shown.length > 0 && (
        <ul className="mt-6 flex flex-wrap gap-2">
          {f.moments_shown.map((m) => (
            <Chip key={`${m.minute}-${m.player}`} tone="page">
              {m.minute}′ · {m.player} · {m.player_team}
            </Chip>
          ))}
        </ul>
      )}
      <p className="t-caption mt-6 text-fg-muted">
        {t(lang, "mostDramatic")}: {f.most_dramatic_home_team} {f.most_dramatic_home_goals}–{f.most_dramatic_away_goals}{" "}
        {f.most_dramatic_away_team}
        {f.most_dramatic_excitement_out_of_10 !== null && ` · ${f.most_dramatic_excitement_out_of_10}/10`}
      </p>
    </Panel>
  );
}
