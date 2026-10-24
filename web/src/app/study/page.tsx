import type { Metadata } from "next";

import { MatchSurface } from "@/components/match-surface";
import { clubGradient } from "@/lib/color";
import { STAKES_LABEL, cut, fanClubId, scoreboard, table, type ScoreLine } from "@/lib/study-data";

export const metadata: Metadata = { title: "Visual study · FanCut" };

// Every match shares the clock, so a card only speaks up when its status differs.
const STATUS_LABEL = { live: "", half_time: "HT", full_time: "FT" } as const;

export default function Study() {
  const onAir = scoreboard.find((m) => m.on_air) ?? scoreboard[0];
  return (
    <main className="mx-auto w-full max-w-[1120px] px-4 py-8 sm:px-6 sm:py-12">
      <header className="mb-6 flex items-baseline justify-between">
        <p className="caption text-[13px] font-medium text-fg-muted">Visual study</p>
        <p className="caption tabular text-[13px] text-fg-faint">Arjun&rsquo;s channel · 24&prime;</p>
      </header>

      <OnAirCard match={onAir} />

      <section aria-label="All matches" className="mt-5">
        <ul className="-mx-4 flex snap-x gap-3 overflow-x-auto px-4 pb-2 sm:-mx-6 sm:px-6">
          {scoreboard.map((m) => (
            <StripCard key={m.match_id} match={m} />
          ))}
        </ul>
      </section>

      <div className="mt-8 grid gap-5 lg:grid-cols-[3fr_2fr]">
        <Table />
        <Specimen />
      </div>
    </main>
  );
}

function OnAirCard({ match }: { match: ScoreLine }) {
  const facts = cut.facts;
  const chips = [
    "Your club",
    STAKES_LABEL[match.stakes],
    ...facts.players_the_fan_follows_on_pitch.map((p) => `${p} on the pitch`),
    ...facts.fan_fantasy_players_on_pitch.map((p) => `${p} · fantasy`),
  ];
  return (
    <article
      className="grain rounded-[var(--radius-card)] p-6 text-on-card sm:p-8"
    >
      <MatchSurface home={match.home_color} away={match.away_color} seed={1} />
      <div className="flex items-center justify-between">
        <span className="caption flex items-center gap-2 rounded-[var(--radius-chip)] bg-black/25 px-3 py-1.5 text-[13px] font-semibold">
          <i className="live-dot block size-2 rounded-full bg-live" aria-hidden />
          <span className="tabular">LIVE · {match.minute}&prime;</span>
        </span>
        <span className="caption text-[13px] font-medium uppercase text-on-card-muted">
          {STAKES_LABEL[match.stakes]}
        </span>
      </div>

      <div className="mt-10 grid grid-cols-[1fr_auto_1fr] items-center gap-4 sm:mt-12 sm:gap-8">
        <div className="min-w-0">
          <TeamName full={match.home} short={match.home_short} />
          <p className="caption mt-1 text-[13px] text-on-card-muted">
            Home · {ordinal(facts.fan_club_position_now)} in the table
          </p>
        </div>
        <p className="display tabular text-[clamp(64px,11vw,120px)] font-semibold">
          {match.home_goals}
          <span className="mx-2 opacity-45 sm:mx-4">–</span>
          {match.away_goals}
        </p>
        <div className="min-w-0 text-right">
          <TeamName full={match.away} short={match.away_short} />
          <p className="caption mt-1 text-[13px] text-on-card-muted">Away</p>
        </div>
      </div>

      <div className="mt-10 border-t border-white/15 pt-5 sm:mt-12">
        <p lang="hi" className="font-devanagari max-w-[46ch] text-[19px] leading-[1.55]">
          {cut.text}
        </p>
        <ul className="mt-4 flex flex-wrap gap-2">
          {chips.map((chip) => (
            <li
              key={chip}
              className="caption rounded-[var(--radius-chip)] bg-white/14 px-3 py-1 text-[13px] font-medium"
            >
              {chip}
            </li>
          ))}
        </ul>
      </div>
    </article>
  );
}

/** Full name where there is room; the club's three-letter code where there is not. */
function TeamName({ full, short }: { full: string; short: string }) {
  return (
    <p className="title text-[26px] font-semibold sm:text-[28px]">
      <span className="sm:hidden" aria-label={full}>
        {short}
      </span>
      <span className="hidden sm:inline">{full}</span>
    </p>
  );
}

function StripRow({ short, goals, mine }: { short: string; goals: number; mine: boolean }) {
  return (
    <div className="flex items-center justify-between text-[17px] font-semibold">
      <span className="flex items-center gap-1.5">
        {mine && <i className="block size-1.5 rounded-full bg-white" aria-label="your club" />}
        {short}
      </span>
      <span className="tabular">{goals}</span>
    </div>
  );
}

function StripCard({ match }: { match: ScoreLine }) {
  return (
    <li
      className={`grain pressable w-[156px] shrink-0 snap-start rounded-2xl p-3.5 text-on-card ${
        match.on_air ? "ring-2 ring-white ring-offset-2 ring-offset-bg" : ""
      }`}
    >
      <MatchSurface home={match.home_color} away={match.away_color} size="small" />
      <div className="caption h-4 text-[12px] font-semibold">
        {match.on_air ? "ON AIR" : <span className="text-on-card-muted">{STATUS_LABEL[match.status]}</span>}
      </div>
      <div className="mt-2.5 space-y-1">
        <StripRow short={match.home_short} goals={match.home_goals} mine={isFanClub(match.home)} />
        <StripRow short={match.away_short} goals={match.away_goals} mine={isFanClub(match.away)} />
      </div>
    </li>
  );
}

function Table() {
  return (
    <section
      aria-label="League table"
      className="rounded-[var(--radius-card)] border border-hairline bg-bg-elevated p-5 sm:p-6"
    >
      <div className="flex items-baseline justify-between">
        <h2 className="title text-[20px] font-semibold">As it stands</h2>
        <p className="caption text-[13px] text-fg-muted">Live table · 34 played</p>
      </div>
      <table className="tabular mt-4 w-full text-[15px]">
        <thead className="caption text-[12px] font-medium text-fg-faint">
          <tr>
            <th className="w-7 pb-2 text-left font-medium">#</th>
            <th className="pb-2 text-left font-medium">Club</th>
            <th className="pb-2 pl-4 text-right font-medium">GD</th>
            <th className="pb-2 pl-4 text-right font-medium">Pts</th>
            <th className="w-14 pb-2 pl-4 text-right font-medium">Δ</th>
          </tr>
        </thead>
        <tbody>
          {table.map((row) => {
            const mine = row.team_id === fanClubId;
            const club = scoreboard.flatMap((m) => [
              [m.home_short, m.home_color],
              [m.away_short, m.away_color],
            ]);
            const color = club.find(([s]) => s === row.short)?.[1] ?? "#888888";
            return (
              <tr key={row.team_id} className={`border-t border-hairline ${mine ? "font-semibold" : ""}`}>
                <td className="py-2.5 text-fg-muted">{row.position}</td>
                <td className="py-2.5">
                  <span className="flex items-center gap-2.5">
                    <i
                      className="block size-2.5 rounded-full"
                      style={{ background: clubGradient(color) }}
                      aria-hidden
                    />
                    {row.team}
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
    </section>
  );
}

function Specimen() {
  return (
    <section
      aria-label="Type"
      className="rounded-[var(--radius-card)] border border-hairline bg-bg-elevated p-5 sm:p-6"
    >
      <p className="display text-[clamp(34px,4vw,44px)] font-semibold">
        Ten matches.
        <br />
        One channel. Yours.
      </p>
      <p className="mt-5 max-w-[36ch] text-[17px] leading-[1.5] text-fg-muted">
        FanCut watches every match at once, cuts to the one that matters to you, and says why.
      </p>
      <p lang="hi" className="font-devanagari mt-3 max-w-[36ch] text-[17px] leading-[1.6] text-fg-muted">
        हर मैच पर नज़र, कट सिर्फ़ उस मैच पर जो आपके लिए मायने रखता है।
      </p>
      <p className="tabular mt-5 text-[15px] text-fg-faint">90+4&prime; · 2–1 · 58 pts · +29 GD · 1.85</p>
    </section>
  );
}

function isFanClub(name: string): boolean {
  return name.toLowerCase().startsWith(fanClubId);
}

function ordinal(n: number): string {
  const suffix = ["th", "st", "nd", "rd"][n % 100 > 10 && n % 100 < 14 ? 0 : Math.min(n % 10, 4) % 4] ?? "th";
  return `${n}${suffix}`;
}

function signed(n: number): string {
  return n > 0 ? `+${n}` : String(n);
}

function movement(change: number): string {
  if (change === 0) return "–";
  return `${change > 0 ? "▲" : "▼"} ${Math.abs(change)}`;
}
