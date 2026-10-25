"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Chip } from "@/components/ui/chip";
import { DragDemo } from "@/components/ui/drag-demo";
import { FpsMeter } from "@/components/ui/fps-meter";
import { LanguageSwitch } from "@/components/ui/language-switch";
import { LeagueTable } from "@/components/ui/league-table";
import { CompactMatchCard, MatchCard } from "@/components/ui/match-card";
import { Panel } from "@/components/ui/panel";
import { Pill, StatusPill } from "@/components/ui/pill";
import { ReasonCard } from "@/components/ui/reason-card";
import { ScoreStrip } from "@/components/ui/score-strip";
import { palette, type as typeScale } from "@/design/tokens";
import { cut, fan, narration, replay, scoreboard, table } from "@/lib/demo-data";
import { t, type Language } from "@/lib/i18n";

function Section({ title, note, children }: { title: string; note?: string; children: React.ReactNode }) {
  return (
    <section className="border-t border-hairline py-10">
      <div className="mb-6 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="t-title1">{title}</h2>
        {note && <p className="t-callout max-w-[60ch] text-fg-muted">{note}</p>}
      </div>
      {children}
    </section>
  );
}

export default function Design() {
  const [lang, setLang] = useState<Language>("hi");
  const [narrated, setNarrated] = useState(true);
  const [selected, setSelected] = useState("md34-09");
  const onAir = scoreboard.find((m) => m.on_air)!;
  const halfTime = { ...scoreboard[1], status: "half_time" as const, minute: 45 };
  const fullTime = { ...scoreboard[4], status: "full_time" as const, minute: 94 };

  return (
    <main className="mx-auto w-full max-w-(--page) px-(--gutter) pb-24 sm:px-(--gutter-wide)">
      <FpsMeter />

      <header className="flex flex-wrap items-end justify-between gap-4 py-10">
        <div>
          <p className="t-caption text-fg-muted">FanCut · design system</p>
          <h1 className="t-display mt-2">
            Ten matches.
            <br />
            One channel. Yours.
          </h1>
        </div>
        <LanguageSwitch value={lang} onChange={setLang} />
      </header>

      <Section title="The match on air" note="Both clubs on one silk surface. The reason card lives inside it, so why you are here is never more than a glance away.">
        <MatchCard match={onAir} lang={lang} fanClub={fan.club} fanClubPosition={2} seed={1}>
          <ReasonCard cut={cut(lang)} narration={narrated && lang === "en" ? narration : null} lang={lang} />
        </MatchCard>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <Button size="small" onClick={() => setNarrated((v) => !v)}>
            {narrated ? "Show the reference line" : "Show the Narrator's line"}
          </Button>
          <p className="t-caption text-fg-muted">
            The reference line shows the instant the Director cuts; the Narrator&rsquo;s line replaces it when the Fact
            Checker passes it (English sample).
          </p>
        </div>
      </Section>

      <Section title="All matches" note="The whole matchday in one row. The match on air is ringed and kept in view; a dot marks your club.">
        <ScoreStrip matches={scoreboard} lang={lang} fanClub={fan.club} selected={selected} onSelect={setSelected} />
        <div className="mt-6 flex flex-wrap gap-3">
          <CompactMatchCard match={halfTime} lang={lang} fanClub={fan.club} />
          <CompactMatchCard match={fullTime} lang={lang} fanClub={fan.club} />
          <CompactMatchCard match={{ ...scoreboard[7], on_air: true }} lang={lang} selected />
        </div>
      </Section>

      <Section title="A replay" note="A must-show moment the fan did not see live. The reason card names the moment and the player; the chips say why it mattered to this fan.">
        <MatchCard match={scoreboard[2]} lang={lang} fanClub={fan.club} seed={3}>
          <ReasonCard cut={replay(lang)} lang={lang} />
        </MatchCard>
      </Section>

      <div className="grid gap-5 lg:grid-cols-[3fr_2fr]">
        <Section title={t(lang, "asItStands")} note="Numbers are tabular; club colour appears only as a dot on the club's own row.">
          <Panel title={t(lang, "asItStands")} aside={`${t(lang, "liveTable")} · 34 ${t(lang, "played")}`}>
            <LeagueTable rows={table} lang={lang} fanClubId={fan.clubId} />
          </Panel>
        </Section>

        <Section title="Pills, chips, buttons">
          <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-3 rounded-panel bg-fg/70 p-4">
              <StatusPill status="live" minute={24} lang={lang} />
              <StatusPill status="half_time" minute={45} lang={lang} />
              <StatusPill status="full_time" minute={94} lang={lang} />
              <Pill>{t(lang, "onAir")}</Pill>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <StatusPill status="live" minute={24} lang={lang} tone="neutral" />
              <Pill tone="neutral">{t(lang, "replay")}</Pill>
              <Pill tone="solid">{t(lang, "onAir")}</Pill>
            </div>
            <ul className="flex flex-wrap gap-2">
              <Chip tone="page">{t(lang, "yourClub")}</Chip>
              <Chip tone="page">{t(lang, "titleRace")}</Chip>
              <Chip tone="page">Rohan Mehta · {t(lang, "followed")}</Chip>
            </ul>
            <div className="flex flex-wrap items-center gap-3">
              <Button variant="primary">Start my channel</Button>
              <Button>Director&rsquo;s notes</Button>
              <Button variant="quiet">Skip</Button>
              <Button variant="primary" disabled>
                Disabled
              </Button>
              <Button size="small" variant="primary">
                Small
              </Button>
              <Button size="small">Small</Button>
            </div>
          </div>
        </Section>
      </div>

      <Section title="Motion" note="Springs, critically damped by default. Bounce is earned by momentum: only a flick gets it. Drag the card, throw it, grab it mid-flight.">
        <DragDemo />
        <dl className="t-caption mt-4 grid grid-cols-2 gap-x-6 gap-y-1 text-fg-muted sm:grid-cols-4">
          <dt>settle</dt>
          <dd className="tabular">bounce 0 · 350 ms</dd>
          <dt>snap</dt>
          <dd className="tabular">bounce 0 · 220 ms</dd>
          <dt>throw</dt>
          <dd className="tabular">bounce 0.2 · 400 ms</dd>
          <dt>stage</dt>
          <dd className="tabular">bounce 0 · 550 ms</dd>
        </dl>
      </Section>

      <Section title="Type" note="One family, Inter, with optical sizing; Noto Sans Devanagari for Hindi. Tracking tightens as size grows; names stay Latin in every language.">
        <div className="space-y-4">
          {Object.entries(typeScale).map(([name, style]) => (
            <div key={name} className="grid grid-cols-[88px_1fr] items-baseline gap-4 border-t border-hairline pt-3">
              <dl className="t-micro uppercase text-fg-faint">
                <dt>{name}</dt>
                <dd className="tabular normal-case">{style.size.replace("clamp", "").slice(0, 18)}</dd>
              </dl>
              <p className={`t-${name} ${name === "score" ? "tabular" : ""} truncate`}>
                {name === "score" ? "2–1" : "Kingsmere City · आपका क्लब"}
              </p>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Colour" note="Surfaces are neutral; the only colour on the page belongs to a club. Every pair here passes WCAG AA in CI.">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
          {Object.entries(palette.light).map(([name]) => (
            <div key={name} className="rounded-control border border-hairline p-3">
              <div
                className="h-10 rounded-[8px] border border-hairline"
                style={{ background: `var(--${name.replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`)})` }}
              />
              <p className="t-micro mt-2 uppercase text-fg-muted">{name}</p>
            </div>
          ))}
        </div>
      </Section>
    </main>
  );
}
