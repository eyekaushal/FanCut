import { Button } from "@/components/ui/button";
import { Chip } from "@/components/ui/chip";
import { reasonLabels, t, type Language } from "@/lib/i18n";
import type { RankedMatch } from "@/lib/overlay";

/**
 * Inside a focused match's card: how the Director ranks it against the match it put
 * on air, with the reasons it counted. Every number is the Director's own.
 */
export function FocusCard({
  ranking,
  onAir,
  onAirName,
  lang,
  onRelease,
}: {
  ranking: RankedMatch | null;
  onAir: RankedMatch | null;
  onAirName: string | null;
  lang: Language;
  onRelease: () => void;
}) {
  const isOnAir = ranking && onAir && ranking.match_id === onAir.match_id;
  return (
    <div>
      <div className="t-micro mb-2 uppercase text-on-card-muted">
        {t(lang, "focus")} · {isOnAir ? t(lang, "onAirNow") : t(lang, "whyNotHere")}
      </div>

      {ranking ? (
        <dl className="tabular grid grid-cols-3 gap-4">
          <Stat label={t(lang, "relevance")} value={ranking.value} against={isOnAir ? null : onAir?.value} />
          <Stat label={t(lang, "drama")} value={ranking.drama} against={isOnAir ? null : onAir?.drama} />
          <Stat label={t(lang, "stake")} value={ranking.stake} against={isOnAir ? null : onAir?.stake} />
        </dl>
      ) : (
        <p className="t-body max-w-[46ch]">{t(lang, "notRanked")}</p>
      )}

      {ranking && ranking.reasons.length > 0 && (
        <ul className="mt-4 flex flex-wrap gap-2">
          {reasonLabels(lang, ranking.reasons).map((label) => (
            <Chip key={label}>{label}</Chip>
          ))}
        </ul>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <Button size="small" className="bg-white/14 text-on-card hover:bg-white/20" onClick={onRelease}>
          {t(lang, "backToDirector")}
        </Button>
        {!isOnAir && onAirName && (
          <span className="t-caption text-on-card-muted">
            {t(lang, "directorIsAt")} {onAirName}
          </span>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value, against }: { label: string; value: number; against?: number | null }) {
  return (
    <div>
      <dt className="t-micro uppercase text-on-card-muted">{label}</dt>
      <dd className="t-title2 mt-1">
        {value.toFixed(2)}
        {against !== null && against !== undefined && (
          <span className="t-caption ml-2 text-on-card-muted">vs {against.toFixed(2)}</span>
        )}
      </dd>
    </div>
  );
}
