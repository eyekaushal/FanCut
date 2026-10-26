import { Metric } from "@/components/ui/metric";
import { Panel } from "@/components/ui/panel";
import type { Evaluation } from "@/lib/api";
import { t, type Language } from "@/lib/i18n";

const pct = (v: number) => `${Math.round(v * 100)}%`;

/**
 * The headline measurements, each with how it was measured. Director numbers are
 * computed by the API on this machine; the grounding review is a dated manual record;
 * the Fact Checker tally is what this API process has actually done.
 */
export function TrustMetrics({ evaluation, lang }: { evaluation: Evaluation | null; lang: Language }) {
  const d = evaluation?.director ?? null;
  const g = evaluation?.grounding;
  const measuring = evaluation?.status === "measuring";
  const live = g?.live;
  const redteam = g?.redteam ?? evaluation?.recorded.redteam?.rules ?? null;
  const judge = evaluation?.recorded.redteam?.judge ?? null;
  const foundry = evaluation?.recorded.foundry ?? null;
  return (
    <Panel
      title={t(lang, "measured")}
      aside={
        measuring
          ? t(lang, "measuring", { n: evaluation.progress.total, done: evaluation.progress.done })
          : d
            ? t(lang, "measuredOn", { n: d.seeds.length, fans: d.fans.join(` ${t(lang, "and")} `), s: d.seconds })
            : evaluation
              ? undefined
              : t(lang, "loading")
      }
    >
      <dl className="grid grid-cols-2 gap-x-6 gap-y-6 md:grid-cols-3 xl:grid-cols-5">
        <Metric
          lang={lang}
          label={t(lang, "personalCoverage")}
          value={d ? `${d.personal_covered}/${d.personal_moments}` : null}
          note={t(lang, "personalCoverageNote")}
          met={d ? d.personal_coverage === 1 : null}
        />
        <Metric
          lang={lang}
          label={t(lang, "liveCoverage")}
          value={d ? pct(d.live_coverage) : null}
          note={
            d
              ? t(lang, "liveCoverageNote", { random: pct(d.live_coverage_random), never: pct(d.live_coverage_never_switch) })
              : t(lang, "liveCoverageHint")
          }
          met={d ? d.live_coverage >= 1.4 * d.live_coverage_random : null}
        />
        <Metric
          lang={lang}
          label={t(lang, "earlyCuts")}
          value={d ? String(d.early_cuts) : null}
          note={d ? t(lang, "earlyCutsNote", { n: d.cuts, s: 45 }) : t(lang, "earlyCutsHint")}
          met={d ? d.early_cuts === 0 : null}
        />
        <Metric
          lang={lang}
          label={t(lang, "distinctness")}
          value={d ? `${pct(d.distinctness_min)}–${pct(d.distinctness_max)}` : null}
          note={t(lang, "distinctnessNote")}
          met={d ? d.distinctness_min >= 0.5 : null}
        />
        <Metric
          lang={lang}
          label={t(lang, "grounding")}
          value={g ? `${g.review.lines - g.review.false_claims}/${g.review.lines}` : null}
          note={g ? t(lang, "groundingNote", { date: g.review.date, n: g.review.unsupported_additions }) : undefined}
          met={g ? (g.review.lines - g.review.false_claims) / g.review.lines >= g.review.target : null}
        />
        <Metric
          lang={lang}
          label={t(lang, "redTeamRules")}
          value={redteam ? `${redteam.caught}/${redteam.rule_detectable}` : null}
          note={redteam ? t(lang, "redTeamRulesNote", { f: redteam.false_rejects, j: redteam.judge_only }) : t(lang, "redTeamRulesHint")}
          met={redteam ? redteam.caught === redteam.rule_detectable && redteam.false_rejects === 0 : null}
        />
        <Metric
          lang={lang}
          label={t(lang, "redTeamJudge")}
          value={judge ? `${judge.caught}/${judge.caught + judge.missed}` : evaluation ? t(lang, "pending") : null}
          note={judge ? t(lang, "redTeamJudgeNote", { f: judge.false_rejects, model: judge.model }) : t(lang, "needsModelRun")}
          met={judge ? judge.missed === 0 : undefined}
        />
        <Metric
          lang={lang}
          label={t(lang, "foundryGroundedness")}
          value={foundry ? `${foundry.metrics.groundedness?.toFixed(1) ?? "—"}/5` : evaluation ? t(lang, "pending") : null}
          note={
            foundry
              ? t(lang, "foundryNote", {
                  n: foundry.scored,
                  p: pct(foundry.pass_rates.groundedness ?? 0),
                  model: foundry.evaluator_model,
                })
              : t(lang, "foundryHint")
          }
          met={foundry ? (foundry.pass_rates.groundedness ?? 0) >= 0.98 : undefined}
        />
        <Metric
          lang={lang}
          label={t(lang, "factCheckerToday")}
          value={live ? t(lang, "rejectedN", { n: live.rejected_drafts }) : null}
          note={live ? t(lang, "factCheckerNote", { m: live.model, t: live.template, d: live.drafts }) : undefined}
        />
      </dl>
    </Panel>
  );
}

/**
 * The controls as built, the Director's rules, and what is speaking. The control texts
 * and the review method are the API's own words, in English.
 */
export function ResponsibleAi({ evaluation, lang }: { evaluation: Evaluation | null; lang: Language }) {
  const s = evaluation?.safety;
  const g = evaluation?.grounding;
  const foundry = evaluation?.recorded.foundry ?? null;
  return (
    <Panel
      title={t(lang, "responsibleAi")}
      aside={s ? (s.model_deployment ? t(lang, "narratorOn", { model: s.model_deployment }) : t(lang, "templatesSpeaking")) : undefined}
    >
      {s ? (
        <div className="grid gap-8 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
          <ul className="grid gap-5 sm:grid-cols-2" lang="en">
            {s.controls.map((c) => (
              <li key={c.name}>
                <p className="t-headline">{c.name}</p>
                <p className="t-caption mt-1 text-fg-muted">{c.detail}</p>
              </li>
            ))}
          </ul>
          <div className="space-y-6">
            <div>
              <p className="t-micro mb-2 uppercase text-fg-faint">{t(lang, "directorsRules")}</p>
              <dl className="t-caption tabular grid grid-cols-[1fr_auto] gap-x-6 gap-y-1">
                <dt className="text-fg-muted">{t(lang, "minDwell")}</dt>
                <dd>{s.director.min_dwell_s} s</dd>
                <dt className="text-fg-muted">{t(lang, "hysteresis")}</dt>
                <dd>+{Math.round(s.director.hysteresis * 100)}%</dd>
                <dt className="text-fg-muted">{t(lang, "rerankEvery")}</dt>
                <dd>{s.director.decision_interval_s} s</dd>
                <dt className="text-fg-muted">{t(lang, "alternativesKept")}</dt>
                <dd>{s.director.alternatives_kept}</dd>
                <dt className="text-fg-muted">{t(lang, "voice")}</dt>
                <dd>{s.speech ? "Azure AI Speech" : t(lang, "notConfigured")}</dd>
              </dl>
            </div>
            {g && (
              <div>
                <p className="t-micro mb-2 uppercase text-fg-faint">{t(lang, "grounding")}</p>
                <p className="t-caption text-fg-muted" lang="en">
                  {g.review.method}
                </p>
                <p className="t-caption mt-1 text-fg-muted">
                  {t(lang, "groundingLines", {
                    n: g.review.lines,
                    f: g.review.false_claims,
                    u: g.review.unsupported_additions,
                    date: g.review.date,
                  })}
                </p>
                {foundry ? (
                  <p className="t-caption mt-1 text-fg-muted">
                    {t(lang, "foundryOn", { n: foundry.scored, date: foundry.generated_at.slice(0, 10) })}{" "}
                    {Object.entries(foundry.metrics)
                      .map(([k, v]) => `${k.replace("_", " ")} ${v.toFixed(2)}`)
                      .join(" · ")}
                    {foundry.safety_run ? "" : ` · ${t(lang, "safetyNotRun")}`}
                  </p>
                ) : (
                  <p className="t-caption mt-1 text-fg-muted" lang="en">
                    {g.automated}
                  </p>
                )}
                {g.live.rejections.length > 0 && (
                  <ul className="t-caption mt-3 space-y-1" lang="en">
                    {g.live.rejections.map((r) => (
                      <li key={r.problem} className="flex justify-between gap-4">
                        <span className="min-w-0 truncate text-fg-muted">{r.problem}</span>
                        <span className="tabular shrink-0">{r.count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </div>
      ) : (
        <p className="t-callout text-fg-muted">{t(lang, "loading")}</p>
      )}
    </Panel>
  );
}
