import { t, type Language } from "@/lib/i18n";
import type { MatchStatus } from "@/lib/overlay";

/** A small label on a scrim, so it stays readable on any club surface. */
export function Pill({
  children,
  tone = "scrim",
  className = "",
}: {
  children: React.ReactNode;
  tone?: "scrim" | "neutral" | "solid";
  className?: string;
}) {
  const tones = {
    scrim: "bg-black/25 text-on-card",
    neutral: "bg-fg/8 text-fg",
    solid: "bg-fg text-bg",
  };
  return (
    <span
      className={`t-caption inline-flex h-7 items-center gap-2 rounded-chip px-3 font-semibold ${tones[tone]} ${className}`}
    >
      {children}
    </span>
  );
}

/** LIVE · 24′, HT or FT. The dot pulses only while live. */
export function StatusPill({
  status,
  minute,
  lang,
  tone = "scrim",
}: {
  status: MatchStatus;
  minute: number;
  lang: Language;
  tone?: "scrim" | "neutral";
}) {
  if (status === "live") {
    return (
      <Pill tone={tone}>
        <i className="live-dot block size-2 rounded-full bg-live" aria-hidden />
        <span className="tabular uppercase">
          {t(lang, "live")} · {t(lang, "minute", { n: minute })}
        </span>
      </Pill>
    );
  }
  return <Pill tone={tone}>{t(lang, status === "half_time" ? "halfTime" : "fullTime")}</Pill>;
}
