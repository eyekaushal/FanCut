import { Metric } from "@/components/ui/metric";
import { Panel } from "@/components/ui/panel";
import type { Evaluation } from "@/lib/api";

const pct = (v: number) => `${Math.round(v * 100)}%`;

/**
 * The headline measurements, each with how it was measured. Director numbers are
 * computed by the API on this machine; the grounding review is a dated manual record;
 * the Fact Checker tally is what this API process has actually done.
 */
export function TrustMetrics({ evaluation }: { evaluation: Evaluation | null }) {
  const d = evaluation?.director ?? null;
  const g = evaluation?.grounding;
  const measuring = evaluation?.status === "measuring";
  const live = g?.live;
  return (
    <Panel
      title="Measured"
      aside={
        measuring
          ? `Measuring the Director on ${evaluation.progress.total} matchdays… ${evaluation.progress.done}/${evaluation.progress.total}`
          : d
            ? `${d.seeds.length} matchdays · ${d.fans.join(" and ")} · ${d.seconds}s on this machine`
            : evaluation
              ? undefined
              : "Loading…"
      }
    >
      <dl className="grid grid-cols-2 gap-x-6 gap-y-6 md:grid-cols-3 xl:grid-cols-6">
        <Metric
          label="Personal coverage"
          value={d ? `${d.personal_covered}/${d.personal_moments}` : null}
          note="own goals and red cards seen live or replayed"
          met={d ? d.personal_coverage === 1 : null}
        />
        <Metric
          label="Live coverage"
          value={d ? pct(d.live_coverage) : null}
          note={d ? `vs ${pct(d.live_coverage_random)} random · ${pct(d.live_coverage_never_switch)} never switch` : "decisive goals on air, neutral fan"}
          met={d ? d.live_coverage >= 1.4 * d.live_coverage_random : null}
        />
        <Metric
          label="Early cuts"
          value={d ? String(d.early_cuts) : null}
          note={d ? `of ${d.cuts} cuts, dwell 45 s` : "routine cuts inside the dwell"}
          met={d ? d.early_cuts === 0 : null}
        />
        <Metric
          label="Distinctness"
          value={d ? `${pct(d.distinctness_min)}–${pct(d.distinctness_max)}` : null}
          note="two fans on different matches"
          met={d ? d.distinctness_min >= 0.5 : null}
        />
        <Metric
          label="Grounding"
          value={g ? `${g.review.lines - g.review.false_claims}/${g.review.lines}` : null}
          note={g ? `manual review, ${g.review.date} · ${g.review.unsupported_additions} unsupported addition` : undefined}
          met={g ? (g.review.lines - g.review.false_claims) / g.review.lines >= g.review.target : null}
        />
        <Metric
          label="Fact Checker today"
          value={live ? `${live.rejected_drafts} rejected` : null}
          note={live ? `${live.model} model · ${live.template} reference · ${live.drafts} drafts` : undefined}
        />
      </dl>
    </Panel>
  );
}

/** The controls as built, the Director's rules, and what is speaking. */
export function ResponsibleAi({ evaluation }: { evaluation: Evaluation | null }) {
  const s = evaluation?.safety;
  const g = evaluation?.grounding;
  return (
    <Panel title="Responsible AI" aside={s ? (s.model_deployment ? `Narrator on ${s.model_deployment}` : "Deterministic templates speaking · no model configured") : undefined}>
      {s ? (
        <div className="grid gap-8 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
          <ul className="grid gap-5 sm:grid-cols-2">
            {s.controls.map((c) => (
              <li key={c.name}>
                <p className="t-headline">{c.name}</p>
                <p className="t-caption mt-1 text-fg-muted">{c.detail}</p>
              </li>
            ))}
          </ul>
          <div className="space-y-6">
            <div>
              <p className="t-micro mb-2 uppercase text-fg-faint">The Director&rsquo;s rules</p>
              <dl className="t-caption tabular grid grid-cols-[1fr_auto] gap-x-6 gap-y-1">
                <dt className="text-fg-muted">Minimum dwell</dt>
                <dd>{s.director.min_dwell_s} s</dd>
                <dt className="text-fg-muted">Hysteresis to cut</dt>
                <dd>+{Math.round(s.director.hysteresis * 100)}%</dd>
                <dt className="text-fg-muted">Re-ranking every</dt>
                <dd>{s.director.decision_interval_s} s</dd>
                <dt className="text-fg-muted">Alternatives kept</dt>
                <dd>{s.director.alternatives_kept}</dd>
                <dt className="text-fg-muted">Voice</dt>
                <dd>{s.speech ? "Azure AI Speech" : "not configured"}</dd>
              </dl>
            </div>
            {g && (
              <div>
                <p className="t-micro mb-2 uppercase text-fg-faint">Grounding</p>
                <p className="t-caption text-fg-muted">{g.review.method}</p>
                <p className="t-caption mt-1 text-fg-muted">
                  {g.review.lines} lines · {g.review.false_claims} false claims · {g.review.unsupported_additions} unsupported addition · {g.review.date}
                </p>
                <p className="t-caption mt-1 text-fg-muted">{g.automated}</p>
                {g.live.rejections.length > 0 && (
                  <ul className="t-caption mt-3 space-y-1">
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
        <p className="t-callout text-fg-muted">Loading…</p>
      )}
    </Panel>
  );
}
