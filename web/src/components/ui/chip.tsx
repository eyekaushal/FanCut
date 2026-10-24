import { stakesLabel, t, type Language } from "@/lib/i18n";
import type { CutFacts } from "@/lib/overlay";

export function Chip({
  children,
  tone = "card",
}: {
  children: React.ReactNode;
  tone?: "card" | "page";
}) {
  const tones = { card: "bg-white/14 text-on-card", page: "bg-fg/8 text-fg" };
  return (
    <li className={`t-caption inline-flex h-7 items-center rounded-chip px-3 ${tones[tone]}`}>
      {children}
    </li>
  );
}

/**
 * The reasons behind a cut, as chips, drawn only from the facts the API attached to it.
 * Names stay in Latin script in every language.
 */
export function factChips(facts: CutFacts, lang: Language): string[] {
  const chips: string[] = [];
  if (facts.fan_club_is_playing_in_this_match) chips.push(t(lang, "yourClub"));
  if (facts.fan_club_table_rival_in_this_match) {
    chips.push(`${t(lang, "rival")} · ${facts.fan_club_table_rival_in_this_match}`);
  }
  chips.push(stakesLabel(lang, facts.match_stakes));
  for (const player of facts.players_the_fan_follows_on_pitch) {
    chips.push(`${player} · ${t(lang, "followed")}`);
  }
  if (facts.fan_fantasy_captain_on_pitch) {
    chips.push(`${facts.fan_fantasy_captain_on_pitch} · ${t(lang, "captain")}`);
  }
  for (const player of facts.fan_fantasy_players_on_pitch) {
    if (player !== facts.fan_fantasy_captain_on_pitch) chips.push(`${player} · ${t(lang, "fantasy")}`);
  }
  return chips;
}

export function FactChips({
  facts,
  lang,
  tone = "card",
}: {
  facts: CutFacts;
  lang: Language;
  tone?: "card" | "page";
}) {
  return (
    <ul className="flex flex-wrap gap-2">
      {factChips(facts, lang).map((chip) => (
        <Chip key={chip} tone={tone}>
          {chip}
        </Chip>
      ))}
    </ul>
  );
}
