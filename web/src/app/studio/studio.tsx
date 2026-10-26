"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { ConnectionPill } from "@/app/channel/channel";
import { DecisionLog } from "@/components/ui/decision-log";
import { OverlayInspector } from "@/components/ui/overlay-inspector";
import { Panel } from "@/components/ui/panel";
import type { MatchNames } from "@/components/ui/relevance-bars";
import { Segmented } from "@/components/ui/segmented";
import { ResponsibleAi, TrustMetrics } from "@/components/ui/trust-panel";
import { api, type AuditTrail, type Contract, type Evaluation, type Matchday } from "@/lib/api";
import { narrationSummary } from "@/lib/audit";
import { fontClass, t } from "@/lib/i18n";
import { useFanChannel } from "@/lib/use-fan-channel";
import type { Connection } from "@/lib/use-channel";

const DEFAULT_SPEED = 30;
const AUDIT_EVERY_MS = 3000;
const FANS = [
  { id: "arjun", label: "Arjun" },
  { id: "maya", label: "Maya" },
];

/**
 * Studio and Trust: one fan's channel as a producer or an auditor sees it. The decision
 * log is the API's audit trail; the inspector is the raw overlay.v1 stream; the
 * measurements are the API's own. The screen follows the channel's language; names, the
 * contract's words and the API's raw records (JSON, rejection reasons) stay as sent.
 */
export function Studio() {
  const params = useSearchParams();
  const router = useRouter();
  const profileId = params.get("profile") ?? "arjun";
  const speed = Number(params.get("speed")) || DEFAULT_SPEED;
  const channel = useFanChannel(profileId, params.get("lang"), speed);
  const { profile, matchday, channelId, state, connection, log, lang, error } = channel;
  const audit = useAudit(channelId, connection);
  const evaluation = useEvaluation(connection);
  const contract = useContract();
  const names = useMemo(() => matchNames(matchday), [matchday]);
  const summary = audit ? narrationSummary(audit.decisions) : null;

  const switchFan = (id: string) => {
    const q = new URLSearchParams(params);
    q.set("profile", id);
    q.delete("lang");
    router.replace(`/studio?${q}`);
  };

  return (
    <main
      lang={lang === "hi" ? "hi" : undefined}
      className={`mx-auto w-full max-w-[1400px] px-(--gutter) pb-16 sm:px-(--gutter-wide) ${fontClass(lang)}`}
    >
      <header className="flex flex-wrap items-center justify-between gap-4 py-5">
        <div className="flex flex-wrap items-center gap-3">
          <Link href="/" className="t-headline">
            FanCut
          </Link>
          <span className="t-caption text-fg-muted">{t(lang, "studio")}</span>
          {profile && (
            <span className="t-caption text-fg-muted">
              · {t(lang, "fansChannel", { name: profile.name })} · {lang}
            </span>
          )}
          <ConnectionPill connection={connection} ended={state.ended} lang={lang} />
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Segmented value={FANS.some((f) => f.id === profileId) ? profileId : "arjun"} options={FANS} onChange={switchFan} label={t(lang, "fan")} />
          <Link href={`/channel?profile=${profileId}`} className="pressable t-caption inline-flex h-9 items-center rounded-control bg-fg/8 px-4 font-semibold text-fg">
            {t(lang, "openChannel")}
          </Link>
        </div>
      </header>

      {error && (
        <Panel className="mb-6">
          <p className="t-body">{t(lang, "apiUnreachable")}</p>
          <p className="t-caption mt-1 text-fg-muted">{error}</p>
        </Panel>
      )}

      <div className="space-y-5">
        <TrustMetrics evaluation={evaluation} lang={lang} />

        <div className="grid gap-5 xl:grid-cols-[minmax(0,3fr)_minmax(360px,2fr)]">
          <Panel
            title={t(lang, "decisionLog")}
            aside={
              audit ? (
                <>
                  {t(lang, "decisionsAside", { n: audit.decisions.length, m: summary?.model ?? 0 })} ·{" "}
                  <a href={api.auditUrl(audit.channel_id)} target="_blank" rel="noreferrer" className="text-fg underline-offset-2 hover:underline">
                    audit.v1 JSON
                  </a>
                </>
              ) : undefined
            }
          >
            <DecisionLog entries={audit?.decisions ?? []} names={names} lang={lang} />
          </Panel>

          <Panel title={t(lang, "overlayInspector")} aside={t(lang, "eventsKept", { n: log.length })} className="xl:sticky xl:top-5 xl:self-start">
            <OverlayInspector log={log} contract={contract} lang={lang} />
          </Panel>
        </div>

        <ResponsibleAi evaluation={evaluation} lang={lang} />
      </div>
    </main>
  );
}

/** The audit trail, refreshed while the channel is live and once more when it ends. */
function useAudit(channelId: string | null, connection: Connection): AuditTrail | null {
  const [audit, setAudit] = useState<AuditTrail | null>(null);
  useEffect(() => {
    if (!channelId) return;
    let cancelled = false;
    const load = () =>
      api
        .audit(channelId)
        .then((a) => !cancelled && setAudit(a))
        .catch(() => undefined);
    void load();
    if (connection !== "live") return () => void (cancelled = true);
    const timer = setInterval(load, AUDIT_EVERY_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [channelId, connection]);
  return audit;
}

/** Measurements: polled quickly while the Director is being measured, slowly while live. */
function useEvaluation(connection: Connection): Evaluation | null {
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const measuring = evaluation?.status === "measuring";
  useEffect(() => {
    let cancelled = false;
    const load = () =>
      api
        .evaluation()
        .then((e) => !cancelled && setEvaluation(e))
        .catch(() => undefined);
    void load();
    const every = measuring ? 1500 : connection === "live" ? 6000 : 0;
    if (!every) return () => void (cancelled = true);
    const timer = setInterval(load, every);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [measuring, connection]);
  return evaluation;
}

function useContract(): Contract | null {
  const [contract, setContract] = useState<Contract | null>(null);
  useEffect(() => {
    let cancelled = false;
    api
      .contract()
      .then((c) => !cancelled && setContract(c))
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);
  return contract;
}

function matchNames(matchday: Matchday | null): MatchNames {
  const names: MatchNames = {};
  for (const f of matchday?.fixtures ?? []) {
    names[f.match_id] = { label: `${f.home.short}–${f.away.short}`, homeColor: f.home.color, awayColor: f.away.color };
  }
  return names;
}
