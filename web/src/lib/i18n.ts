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
  goal:        { en: "Goal",          hi: "गोल",             hinglish: "Goal" },
  redCard:     { en: "Red card",      hi: "रेड कार्ड",         hinglish: "Red card" },
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
  // Studio and Trust (the producer's screen follows the channel's language; names and
  // the API's raw records stay as they are).
  studio:      { en: "Studio",        hi: "स्टूडियो",          hinglish: "Studio" },
  fansChannel: { en: "{name}'s channel", hi: "{name} का चैनल", hinglish: "{name} ka channel" },
  fan:         { en: "Fan",           hi: "फ़ैन",             hinglish: "Fan" },
  openChannel: { en: "Open the channel", hi: "चैनल खोलें",     hinglish: "Channel kholo" },
  apiUnreachable: { en: "Could not reach the API at the configured address.", hi: "तय पते पर API तक नहीं पहुँच सके।", hinglish: "Configured address par API tak nahi pahunch paaye." },
  tryAgain:    { en: "Try again",     hi: "फिर कोशिश करें",     hinglish: "Phir try karo" },
  reconnecting: { en: "Reconnecting…", hi: "फिर जोड़ रहे हैं…",  hinglish: "Reconnect ho raha hai…" },
  connecting:  { en: "Connecting…",   hi: "जोड़ रहे हैं…",      hinglish: "Connect ho raha hai…" },
  directorsNotes: { en: "Director's notes", hi: "डायरेक्टर के नोट्स", hinglish: "Director ke notes" },
  loading:     { en: "Loading…",      hi: "लोड हो रहा है…",     hinglish: "Load ho raha hai…" },
  measured:    { en: "Measured",      hi: "मापा गया",          hinglish: "Measured" },
  measuring:   { en: "Measuring the Director on {n} matchdays… {done}/{n}", hi: "डायरेक्टर को {n} मैचडे पर माप रहे हैं… {done}/{n}", hinglish: "Director ko {n} matchdays par naap rahe hain… {done}/{n}" },
  measuredOn:  { en: "{n} matchdays · {fans} · {s}s on this machine", hi: "{n} मैचडे · {fans} · इस मशीन पर {s} सेकंड", hinglish: "{n} matchdays · {fans} · is machine par {s}s" },
  and:         { en: "and",           hi: "और",              hinglish: "aur" },
  personalCoverage: { en: "Personal coverage", hi: "निजी कवरेज", hinglish: "Personal coverage" },
  personalCoverageNote: { en: "own goals and red cards seen live or replayed", hi: "अपने गोल और रेड कार्ड, लाइव या रीप्ले में देखे", hinglish: "apne goals aur red cards, live ya replay mein dekhe" },
  liveCoverage: { en: "Live coverage", hi: "लाइव कवरेज",       hinglish: "Live coverage" },
  liveCoverageNote: { en: "vs {random} random · {never} never switch", hi: "{random} रैंडम · {never} कभी न बदलने के मुकाबले", hinglish: "vs {random} random · {never} kabhi na badle" },
  liveCoverageHint: { en: "decisive goals on air, neutral fan", hi: "निर्णायक गोल ऑन एयर, न्यूट्रल फ़ैन", hinglish: "decisive goals on air, neutral fan" },
  earlyCuts:   { en: "Early cuts",    hi: "जल्दी कट",          hinglish: "Early cuts" },
  earlyCutsNote: { en: "of {n} cuts, dwell {s} s", hi: "{n} कट में से, ठहराव {s} सेकंड", hinglish: "{n} cuts mein se, dwell {s} s" },
  earlyCutsHint: { en: "routine cuts inside the dwell", hi: "ठहराव के भीतर सामान्य कट", hinglish: "dwell ke andar routine cuts" },
  distinctness: { en: "Distinctness", hi: "भिन्नता",           hinglish: "Distinctness" },
  distinctnessNote: { en: "two fans on different matches", hi: "दो फ़ैन अलग-अलग मैचों पर", hinglish: "do fans alag-alag matches par" },
  grounding:   { en: "Grounding",     hi: "तथ्य-आधार",         hinglish: "Grounding" },
  groundingNote: { en: "manual review, {date} · {n} unsupported addition", hi: "मैनुअल समीक्षा, {date} · {n} असमर्थित जोड़", hinglish: "manual review, {date} · {n} unsupported addition" },
  redTeamRules: { en: "Red team · rules", hi: "रेड टीम · नियम", hinglish: "Red team · rules" },
  redTeamRulesNote: { en: "{f} false rejects · {j} left to the judge", hi: "{f} गलत अस्वीकृति · {j} जज के लिए बाकी", hinglish: "{f} false rejects · {j} judge ke liye baaki" },
  redTeamRulesHint: { en: "wrong lines the code rules catch", hi: "गलत पंक्तियाँ जो कोड के नियम पकड़ते हैं", hinglish: "galat lines jo code rules pakadte hain" },
  redTeamJudge: { en: "Red team · judge", hi: "रेड टीम · जज",  hinglish: "Red team · judge" },
  redTeamJudgeNote: { en: "{f} false rejects · {model}", hi: "{f} गलत अस्वीकृति · {model}", hinglish: "{f} false rejects · {model}" },
  needsModelRun: { en: "needs a model run", hi: "मॉडल रन चाहिए", hinglish: "model run chahiye" },
  pending:     { en: "pending",       hi: "बाकी",             hinglish: "pending" },
  foundryGroundedness: { en: "Foundry groundedness", hi: "Foundry तथ्य-आधार", hinglish: "Foundry groundedness" },
  foundryNote: { en: "{n} lines · pass {p} · {model}", hi: "{n} पंक्तियाँ · पास {p} · {model}", hinglish: "{n} lines · pass {p} · {model}" },
  foundryHint: { en: "Foundry evaluators, needs a model run", hi: "Foundry मूल्यांकन, मॉडल रन चाहिए", hinglish: "Foundry evaluators, model run chahiye" },
  factCheckerToday: { en: "Fact Checker today", hi: "आज का फ़ैक्ट चेकर", hinglish: "Aaj ka Fact Checker" },
  rejectedN:   { en: "{n} rejected",  hi: "{n} अस्वीकृत",       hinglish: "{n} reject" },
  factCheckerNote: { en: "{m} model · {t} reference · {d} drafts", hi: "{m} मॉडल · {t} संदर्भ · {d} ड्राफ़्ट", hinglish: "{m} model · {t} reference · {d} drafts" },
  met:         { en: "met",           hi: "पूरा",             hinglish: "met" },
  missed:      { en: "missed",        hi: "चूका",             hinglish: "missed" },
  responsibleAi: { en: "Responsible AI", hi: "ज़िम्मेदार AI",   hinglish: "Responsible AI" },
  narratorOn:  { en: "Narrator on {model}", hi: "नैरेटर {model} पर", hinglish: "Narrator {model} par" },
  templatesSpeaking: { en: "Deterministic templates speaking · no model configured", hi: "तय टेम्पलेट बोल रहे हैं · कोई मॉडल सेट नहीं", hinglish: "Deterministic templates bol rahe hain · koi model set nahi" },
  directorsRules: { en: "The Director's rules", hi: "डायरेक्टर के नियम", hinglish: "Director ke rules" },
  minDwell:    { en: "Minimum dwell", hi: "न्यूनतम ठहराव",      hinglish: "Minimum dwell" },
  hysteresis:  { en: "Hysteresis to cut", hi: "कट के लिए हिस्टैरिसिस", hinglish: "Cut ke liye hysteresis" },
  rerankEvery: { en: "Re-ranking every", hi: "री-रैंकिंग हर",   hinglish: "Re-ranking har" },
  alternativesKept: { en: "Alternatives kept", hi: "रखे गए विकल्प", hinglish: "Alternatives rakhe" },
  notConfigured: { en: "not configured", hi: "सेट नहीं",       hinglish: "set nahi" },
  groundingLines: { en: "{n} lines · {f} false claims · {u} unsupported addition · {date}", hi: "{n} पंक्तियाँ · {f} झूठे दावे · {u} असमर्थित जोड़ · {date}", hinglish: "{n} lines · {f} false claims · {u} unsupported addition · {date}" },
  foundryOn:   { en: "Foundry evaluators on {n} Narrator lines ({date}):", hi: "{n} नैरेटर पंक्तियों पर Foundry मूल्यांकन ({date}):", hinglish: "{n} Narrator lines par Foundry evaluators ({date}):" },
  safetyNotRun: { en: "content safety not run", hi: "कंटेंट सेफ़्टी नहीं चली", hinglish: "content safety nahi chali" },
  decisionLog: { en: "Decision log",  hi: "निर्णय लॉग",         hinglish: "Decision log" },
  decisionsAside: { en: "{n} decisions · {m} by the Narrator", hi: "{n} निर्णय · {m} नैरेटर के", hinglish: "{n} decisions · {m} Narrator ke" },
  waitingFirst: { en: "Waiting for the first decision…", hi: "पहले निर्णय का इंतज़ार…", hinglish: "Pehle decision ka intezaar…" },
  triggerStart: { en: "kick-off",     hi: "किक-ऑफ़",           hinglish: "kick-off" },
  triggerRelevance: { en: "more relevant", hi: "ज़्यादा अहम",   hinglish: "zyada relevant" },
  triggerMustShow: { en: "must-show moment", hi: "ज़रूर दिखाने वाला पल", hinglish: "must-show moment" },
  triggerOffAir: { en: "match went off air", hi: "मैच ऑफ़ एयर हुआ", hinglish: "match off air hua" },
  triggerMoment: { en: "moment in the match on screen", hi: "स्क्रीन पर चल रहे मैच का पल", hinglish: "screen par chal rahe match ka pal" },
  kindOpen:    { en: "open",          hi: "ओपन",              hinglish: "open" },
  kindCut:     { en: "cut",           hi: "कट",               hinglish: "cut" },
  overNext:    { en: "+{n} over the next match", hi: "अगले मैच से +{n} आगे", hinglish: "agle match se +{n} aage" },
  belowTop:    { en: "−{n} below the top match", hi: "शीर्ष मैच से −{n} पीछे", hinglish: "top match se −{n} peeche" },
  reference:   { en: "Reference",     hi: "संदर्भ",            hinglish: "Reference" },
  narratorDrafts: { en: "Narrator · {n} drafts", hi: "नैरेटर · {n} ड्राफ़्ट", hinglish: "Narrator · {n} drafts" },
  narratorDraft: { en: "Narrator · 1 draft", hi: "नैरेटर · 1 ड्राफ़्ट", hinglish: "Narrator · 1 draft" },
  onAirReference: { en: "On air: the reference line", hi: "ऑन एयर: संदर्भ पंक्ति", hinglish: "On air: reference line" },
  afterRejected: { en: ", after {n} rejected drafts", hi: ", {n} अस्वीकृत ड्राफ़्ट के बाद", hinglish: ", {n} rejected drafts ke baad" },
  factCheckerRejected: { en: "Fact Checker rejected:", hi: "फ़ैक्ट चेकर ने अस्वीकार किया:", hinglish: "Fact Checker ne reject kiya:" },
  rankingNow:  { en: "The ranking at this moment", hi: "इस पल की रैंकिंग", hinglish: "Is pal ki ranking" },
  factSheet:   { en: "The fact sheet the Narrator was held to", hi: "वह फ़ैक्ट शीट जिस पर नैरेटर को रखा गया", hinglish: "Woh fact sheet jis par Narrator ko rakha gaya" },
  overlayInspector: { en: "Overlay inspector", hi: "ओवरले इंस्पेक्टर", hinglish: "Overlay inspector" },
  eventsKept:  { en: "overlay.v1 · {n} events kept", hi: "overlay.v1 · {n} इवेंट रखे", hinglish: "overlay.v1 · {n} events rakhe" },
  eventTypes:  { en: "Event types",   hi: "इवेंट प्रकार",        hinglish: "Event types" },
  all:         { en: "All",           hi: "सभी",              hinglish: "Sab" },
  pause:       { en: "Pause",         hi: "रोकें",             hinglish: "Pause" },
  resume:      { en: "Resume",        hi: "जारी रखें",          hinglish: "Resume" },
  nothingYet:  { en: "Nothing yet.",  hi: "अभी कुछ नहीं।",       hinglish: "Abhi kuch nahi." },
  copyJson:    { en: "Copy JSON",     hi: "JSON कॉपी करें",      hinglish: "JSON copy karo" },
  copied:      { en: "Copied",        hi: "कॉपी हुआ",           hinglish: "Copy hua" },
  sumFullTime: { en: "full time everywhere", hi: "हर जगह फ़ुल टाइम", hinglish: "har jagah full time" },
  sumReleased: { en: "released",      hi: "छोड़ा",             hinglish: "release" },
  sumLocked:   { en: "locked to {m}", hi: "{m} पर लॉक",         hinglish: "{m} par lock" },
  sumOnPitch:  { en: "{n} on the pitch · {m}", hi: "{n} मैदान पर · {m}", hinglish: "{n} maidan par · {m}" },
  sumMatches:  { en: "{n} matches · on air {m}", hi: "{n} मैच · ऑन एयर {m}", hinglish: "{n} matches · on air {m}" },
  sumTable:    { en: "{n} rows · 1st {s}", hi: "{n} पंक्तियाँ · पहला {s}", hinglish: "{n} rows · 1st {s}" },
  sumFantasy:  { en: "{n} points · {p} players", hi: "{n} अंक · {p} खिलाड़ी", hinglish: "{n} points · {p} players" },
} satisfies Record<string, Record<Language, string>>;

export type StringKey = keyof typeof STRINGS;

/** The string for `key` in `lang`, with `{n}`-style slots filled from `vars`. */
export function t(lang: Language, key: StringKey, vars?: Record<string, string | number>): string {
  let text: string = STRINGS[key][lang];
  for (const [name, value] of Object.entries(vars ?? {})) {
    text = text.replaceAll(`{${name}}`, String(value));
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
