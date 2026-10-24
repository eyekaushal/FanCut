/**
 * Interface strings in the three languages the channel speaks. Club and player names
 * are never translated: they stay in Latin script, as the narration does.
 */

export type Language = "en" | "hi" | "hinglish";

export const LANGUAGES: { id: Language; label: string }[] = [
  { id: "en", label: "English" },
  { id: "hi", label: "हिंदी" },
  { id: "hinglish", label: "Hinglish" },
];

// prettier-ignore
const STRINGS = {
  live:        { en: "Live",          hi: "लाइव",            hinglish: "Live" },
  halfTime:    { en: "HT",            hi: "हाफ़ टाइम",        hinglish: "HT" },
  fullTime:    { en: "FT",            hi: "फ़ुल टाइम",        hinglish: "FT" },
  onAir:       { en: "On air",        hi: "ऑन एयर",          hinglish: "On air" },
  replay:      { en: "Replay",        hi: "रीप्ले",           hinglish: "Replay" },
  home:        { en: "Home",          hi: "होम",             hinglish: "Home" },
  away:        { en: "Away",          hi: "अवे",             hinglish: "Away" },
  yourClub:    { en: "Your club",     hi: "आपका क्लब",        hinglish: "Aapka club" },
  rival:       { en: "Table rival",   hi: "तालिका प्रतिद्वंद्वी", hinglish: "Table rival" },
  followed:    { en: "You follow",    hi: "आप फ़ॉलो करते हैं",  hinglish: "Aap follow karte ho" },
  fantasy:     { en: "Fantasy",       hi: "फ़ैंटेसी",          hinglish: "Fantasy" },
  captain:     { en: "Captain",       hi: "कप्तान",           hinglish: "Captain" },
  onThePitch:  { en: "on the pitch",  hi: "मैदान पर",         hinglish: "maidan par" },
  titleRace:   { en: "Title race",    hi: "ख़िताब की दौड़",     hinglish: "Title race" },
  topFour:     { en: "Top four",      hi: "टॉप फ़ोर",          hinglish: "Top four" },
  relegation:  { en: "Relegation",    hi: "रेलीगेशन",          hinglish: "Relegation" },
  derby:       { en: "Derby",         hi: "डर्बी",            hinglish: "Derby" },
  midTable:    { en: "Mid-table",     hi: "मिड-टेबल",         hinglish: "Mid-table" },
  asItStands:  { en: "As it stands",  hi: "अभी की स्थिति",     hinglish: "Abhi ki table" },
  liveTable:   { en: "Live table",    hi: "लाइव तालिका",       hinglish: "Live table" },
  played:      { en: "played",        hi: "खेले",             hinglish: "khele" },
  club:        { en: "Club",          hi: "क्लब",             hinglish: "Club" },
  points:      { en: "Pts",           hi: "अंक",              hinglish: "Pts" },
  goalDiff:    { en: "GD",            hi: "गोल अंतर",          hinglish: "GD" },
  change:      { en: "Change",        hi: "बदलाव",            hinglish: "Change" },
  minute:      { en: "{n}′",          hi: "{n}′",             hinglish: "{n}′" },
  position:    { en: "{n} in the table", hi: "तालिका में {n}", hinglish: "Table mein {n}" },
  whyThisCut:  { en: "Why this match", hi: "यह मैच क्यों",     hinglish: "Yeh match kyun" },
  narrating:   { en: "Narrator writing…", hi: "कमेंटरी लिखी जा रही है…", hinglish: "Narrator likh raha hai…" },
  allMatches:  { en: "All matches",   hi: "सभी मैच",          hinglish: "Sabhi match" },
  fantasyPts:  { en: "Fantasy points", hi: "फ़ैंटेसी अंक",      hinglish: "Fantasy points" },
  language:    { en: "Language",      hi: "भाषा",             hinglish: "Bhasha" },
} satisfies Record<string, Record<Language, string>>;

export type StringKey = keyof typeof STRINGS;

/** The string for `key` in `lang`, with `{n}`-style slots filled from `vars`. */
export function t(lang: Language, key: StringKey, vars?: Record<string, string | number>): string {
  let text: string = STRINGS[key][lang];
  for (const [name, value] of Object.entries(vars ?? {})) {
    text = text.replace(`{${name}}`, String(value));
  }
  return text;
}

const STAKES_KEY = {
  title_race: "titleRace",
  top_four: "topFour",
  relegation: "relegation",
  derby: "derby",
  mid_table: "midTable",
} as const satisfies Record<string, StringKey>;

export type Stakes = keyof typeof STAKES_KEY;

export function stakesLabel(lang: Language, stakes: Stakes): string {
  return t(lang, STAKES_KEY[stakes]);
}

/** Ordinals are language-specific: 2nd / 2रा / 2nd. */
export function ordinal(lang: Language, n: number): string {
  if (lang === "hi") return `${n}${n === 1 ? "ला" : n === 2 ? "रा" : n === 3 ? "रा" : "वाँ"}`;
  const mod100 = n % 100;
  const suffix =
    mod100 >= 11 && mod100 <= 13 ? "th" : (["th", "st", "nd", "rd"][n % 10] ?? "th");
  return `${n}${suffix}`;
}

/** Hindi (Devanagari) wants its own font; the other two are Latin. */
export function fontClass(lang: Language): string {
  return lang === "hi" ? "font-devanagari" : "";
}
