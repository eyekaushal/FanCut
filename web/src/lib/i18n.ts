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
  focus:       { en: "Focus",         hi: "फ़ोकस",            hinglish: "Focus" },
  focusOn:     { en: "Focus on this match", hi: "इस मैच पर फ़ोकस", hinglish: "Is match par focus" },
  backToDirector: { en: "Back to the Director", hi: "डायरेक्टर के पास वापस", hinglish: "Director ke paas wapas" },
  directorIsAt: { en: "The Director is at", hi: "डायरेक्टर अभी यहाँ है:", hinglish: "Director abhi yahan hai:" },
  follow:      { en: "Follow",        hi: "वहाँ चलें",         hinglish: "Wahan chalein" },
  whyNotHere:  { en: "Why the Director isn't here", hi: "डायरेक्टर यहाँ क्यों नहीं", hinglish: "Director yahan kyun nahi" },
  relevance:   { en: "Relevance to you", hi: "आपके लिए अहमियत", hinglish: "Aapke liye relevance" },
  drama:       { en: "Drama",         hi: "ड्रामा",           hinglish: "Drama" },
  stake:       { en: "Your stake",    hi: "आपका दांव",         hinglish: "Aapka stake" },
  onAirNow:    { en: "on air now",    hi: "अभी ऑन एयर",        hinglish: "abhi on air" },
  notRanked:   { en: "Not among the Director's top picks right now.", hi: "अभी डायरेक्टर की शीर्ष पसंद में नहीं।", hinglish: "Abhi Director ki top picks mein nahi." },
  reasonRival: { en: "table rival",   hi: "तालिका प्रतिद्वंद्वी", hinglish: "table rival" },
  reasonFollowed: { en: "{n} you follow", hi: "{n} जिन्हें आप फ़ॉलो करते हैं", hinglish: "{n} jo aap follow karte ho" },
  reasonFantasy: { en: "{n} in your fantasy team", hi: "{n} आपकी फ़ैंटेसी टीम में", hinglish: "{n} aapki fantasy team mein" },
  reasonCaptain: { en: "your captain", hi: "आपके कप्तान",      hinglish: "aapke captain" },
  yourMatchday: { en: "Your matchday", hi: "आपका मैचडे",       hinglish: "Aapka matchday" },
  referenceLine: { en: "Reference line", hi: "संदर्भ पंक्ति",   hinglish: "Reference line" },
  cutsLabel:   { en: "Cuts",          hi: "कट",               hinglish: "Cuts" },
  matchesLabel: { en: "Matches shown", hi: "दिखाए गए मैच",     hinglish: "Matches dikhaye" },
  mostDramatic: { en: "Most dramatic match", hi: "सबसे नाटकीय मैच", hinglish: "Sabse dramatic match" },
  tableLabel:  { en: "Table",         hi: "तालिका",           hinglish: "Table" },
  voice:       { en: "Voice",         hi: "आवाज़",            hinglish: "Awaaz" },
  matchdayOver: { en: "Full time everywhere. Your recap is ready.", hi: "हर जगह फ़ुल टाइम। आपका रीकैप तैयार है।", hinglish: "Har jagah full time. Aapka recap taiyaar hai." },
  playerCam:   { en: "Player cam",    hi: "प्लेयर कैम",         hinglish: "Player cam" },
  everyone:    { en: "Everyone",      hi: "सभी",              hinglish: "Sab" },
  distance:    { en: "Carried",       hi: "दौड़",              hinglish: "Carried" },
  topSpeed:    { en: "Top speed",     hi: "टॉप स्पीड",          hinglish: "Top speed" },
  bursts:      { en: "Bursts",        hi: "बर्स्ट",            hinglish: "Bursts" },
  passes:      { en: "Passes",        hi: "पास",              hinglish: "Passes" },
  passDifficulty: { en: "Pass difficulty", hi: "पास कठिनाई",    hinglish: "Pass difficulty" },
  fastestPass: { en: "Fastest pass",  hi: "सबसे तेज़ पास",       hinglish: "Fastest pass" },
  shots:       { en: "Shots · xG",    hi: "शॉट · xG",          hinglish: "Shots · xG" },
  fastestShot: { en: "Fastest shot",  hi: "सबसे तेज़ शॉट",       hinglish: "Fastest shot" },
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

/**
 * The Director's machine-readable reasons ("your_club", "rival:oakbridge",
 * "fantasy_player:ash-09", "stakes:title_race", "half_time") as short labels. Player
 * reasons are counted rather than named, since the ids are not names.
 */
export function reasonLabels(lang: Language, reasons: string[]): string[] {
  const labels: string[] = [];
  const count = (prefix: string) => reasons.filter((r) => r.startsWith(prefix)).length;
  if (reasons.includes("your_club")) labels.push(t(lang, "yourClub"));
  if (count("rival:")) labels.push(t(lang, "reasonRival"));
  const followed = count("followed_player:");
  if (followed) labels.push(t(lang, "reasonFollowed", { n: followed }));
  if (count("captain:")) labels.push(t(lang, "reasonCaptain"));
  const fantasy = count("fantasy_player:");
  if (fantasy) labels.push(t(lang, "reasonFantasy", { n: fantasy }));
  for (const r of reasons) {
    if (r.startsWith("stakes:")) labels.push(stakesLabel(lang, r.slice(7) as Stakes));
    if (r === "half_time") labels.push(t(lang, "halfTime"));
    if (r === "full_time") labels.push(t(lang, "fullTime"));
  }
  return labels;
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
