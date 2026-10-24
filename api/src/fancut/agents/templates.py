"""Deterministic narration in English, Hindi (Devanagari) and Hinglish.

Used when no language model is available, and as the fallback when the Fact Checker
rejects every model draft. Player and club names stay in Latin script in all three
languages, as Indian sports apps commonly write them, which also lets code verify them.
"""

from fancut.agents.facts import CutFacts
from fancut.agents.recap import RecapFacts
from fancut.profile import Language

EN, HI, HINGLISH = Language.ENGLISH, Language.HINDI, Language.HINGLISH

_OPENERS = {
    "open": {EN: "We start at {match}: {why}.", HI: "हम {match} से शुरू करते हैं: {why}।",
             HINGLISH: "Shuruaat {match} se: {why}."},
    "cut": {EN: "Cutting to {match}, {minute}': {why}.", HI: "अब {match} पर, {minute}': {why}।",
            HINGLISH: "Ab chalte hain {match} par, {minute}': {why}."},
    "replay": {EN: "Replay from {match}, {minute}': {why}.", HI: "{match} से रीप्ले, {minute}': {why}।",
               HINGLISH: "{match} se replay, {minute}': {why}."},
}  # fmt: skip

_WHY = {
    "goal": {EN: "{player} scores for {team}", HI: "{team} के लिए {player} का गोल",
             HINGLISH: "{player} ka goal, {team} ke liye"},
    "red_card": {EN: "red card for {player} of {team}", HI: "{team} के {player} को रेड कार्ड",
                 HINGLISH: "{team} ke {player} ko red card"},
    "your_club": {EN: "your club {club} is playing", HI: "आपका क्लब {club} खेल रहा है",
                  HINGLISH: "aapka club {club} khel raha hai"},
    "followed": {EN: "{player}, whom you follow, is on the pitch", HI: "आप जिन्हें फ़ॉलो करते हैं, वे {player} मैदान पर हैं",
                 HINGLISH: "aap jinhe follow karte ho, woh {player} maidan par hain"},
    "captain": {EN: "your fantasy captain {player} is playing",
                HI: "आपके फ़ैंटेसी कप्तान {player} खेल रहे हैं",
                HINGLISH: "aapke fantasy captain {player} khel rahe hain"},
    "fantasy": {EN: "your fantasy player {player} is in this match",
                HI: "आपके फ़ैंटेसी खिलाड़ी {player} इस मैच में हैं",
                HINGLISH: "aapke fantasy player {player} is match mein hain"},
    "rival": {EN: "{club} are a table rival of your club {mine}",
              HI: "{club} तालिका में आपके क्लब {mine} के प्रतिद्वंद्वी हैं",
              HINGLISH: "{club} table mein aapke club {mine} ke rival hain"},
    "title_race": {EN: "it's a title-race game", HI: "यह ख़िताब की दौड़ का मैच है",
                   HINGLISH: "yeh title race ka match hai"},
    "relegation": {EN: "it's a relegation fight", HI: "यह रेलीगेशन की लड़ाई है",
                   HINGLISH: "yeh relegation ki ladai hai"},
    "top_four": {EN: "it's a top-four race", HI: "यह टॉप-फ़ोर की दौड़ है",
                 HINGLISH: "yeh top-four ki race hai"},
    "heating_up": {EN: "the game is heating up", HI: "मैच गरमा रहा है",
                   HINGLISH: "match garma raha hai"},
}  # fmt: skip

_ANALYST = {
    EN: " Suspense {s}/10, pressure {p}/10.",
    HI: " सस्पेंस {s}/10, दबाव {p}/10।",
    HINGLISH: " Suspense {s}/10, pressure {p}/10.",
}
_TABLE = {
    EN: " As it stands, your club {club} is in position {pos} (it started the day {start}).",
    HI: " इस समय आपका क्लब {club} तालिका में {pos} नंबर पर है (दिन की शुरुआत {start} पर)।",
    HINGLISH: " Abhi aapka club {club} table mein {pos} number par hai (din ki shuruaat {start} par).",
}


def match_label(facts: CutFacts) -> str:
    return f"{facts.home_team} {facts.home_goals}-{facts.away_goals} {facts.away_team}"


def narrate_cut(facts: CutFacts, language: Language) -> str:
    text = _OPENERS[facts.kind][language].format(
        match=match_label(facts), minute=facts.minute, why=_reason(facts, language)
    )
    if facts.suspense_out_of_10 is not None and facts.pressure_out_of_10 is not None:
        text += _ANALYST[language].format(s=facts.suspense_out_of_10, p=facts.pressure_out_of_10)
    now, start = facts.fan_club_position_now, facts.fan_club_position_at_kickoff
    if facts.fan_club and now is not None and now != start:
        text += _TABLE[language].format(club=facts.fan_club, pos=now, start=start)
    return text


def _reason(facts: CutFacts, language: Language) -> str:
    """The single most personal reason, in a fixed order of priority."""
    if facts.moment is not None:
        return _WHY[facts.moment.type][language].format(
            player=facts.moment.player, team=facts.moment.player_team
        )
    if facts.fan_club_is_playing_in_this_match and facts.fan_club:
        return _WHY["your_club"][language].format(club=facts.fan_club)
    if facts.players_the_fan_follows_on_pitch:
        player = facts.players_the_fan_follows_on_pitch[0]
        return _WHY["followed"][language].format(player=player)
    if facts.fan_fantasy_captain_on_pitch:
        return _WHY["captain"][language].format(player=facts.fan_fantasy_captain_on_pitch)
    if facts.fan_fantasy_players_on_pitch:
        return _WHY["fantasy"][language].format(player=facts.fan_fantasy_players_on_pitch[0])
    if facts.fan_club_table_rival_in_this_match and facts.fan_club:
        return _WHY["rival"][language].format(
            club=facts.fan_club_table_rival_in_this_match, mine=facts.fan_club
        )
    if facts.match_stakes in _WHY:
        return _WHY[facts.match_stakes][language]
    return _WHY["heating_up"][language]


# -- the recap ---------------------------------------------------------------------

_RECAP_CLUB = {
    EN: "Your club {club} finished {mine}-{theirs} against {opp} and ends the day {pos} in the table (it started {start}).",
    HI: "आपका क्लब {club} {opp} के ख़िलाफ़ {mine}-{theirs} पर रहा और दिन के अंत में तालिका में {pos} नंबर पर है (शुरुआत {start} पर)।",
    HINGLISH: "Aapka club {club} {opp} ke khilaaf {mine}-{theirs} par raha aur din ke ant mein table mein {pos} number par hai (shuruaat {start} par).",
}  # fmt: skip
_RECAP_NEUTRAL = {
    EN: "The most dramatic match of the day was {home} {h}-{a} {away}.",
    HI: "दिन का सबसे नाटकीय मैच {home} {h}-{a} {away} रहा।",
    HINGLISH: "Din ka sabse dramatic match {home} {h}-{a} {away} raha.",
}  # fmt: skip
_RECAP_ANALYST = {
    EN: " Its excitement rated {x}/10.",
    HI: " इसका रोमांच {x}/10 रहा।",
    HINGLISH: " Iska excitement {x}/10 raha.",
}
_RECAP_CHANNEL = {
    EN: " Your channel cut {cuts} times across {matches} matches and replayed {replays} moments.",
    HI: " आपके चैनल ने {matches} मैचों में {cuts} बार कट किया और {replays} पल रीप्ले किए।",
    HINGLISH: " Aapke channel ne {matches} matches mein {cuts} baar cut kiya aur {replays} pal replay kiye.",
}  # fmt: skip
_RECAP_FANTASY = {
    EN: " Your fantasy squad scored {total} points; {best} led with {pts}.",
    HI: " आपकी फ़ैंटेसी टीम ने {total} अंक बनाए; {best} ने {pts} के साथ सबसे ज़्यादा।",
    HINGLISH: " Aapki fantasy team ne {total} points banaye; {best} ne {pts} ke saath sabse zyada.",
}  # fmt: skip


def narrate_recap(facts: RecapFacts, language: Language) -> str:
    """The reference recap: correct, plain, and every number from the fact sheet."""
    if facts.fan_club:
        text = _RECAP_CLUB[language].format(
            club=facts.fan_club,
            opp=facts.fan_club_opponent,
            mine=facts.fan_club_goals,
            theirs=facts.fan_club_opponent_goals,
            pos=facts.fan_club_position_now,
            start=facts.fan_club_position_at_kickoff,
        )
    else:
        text = _RECAP_NEUTRAL[language].format(
            home=facts.most_dramatic_home_team,
            away=facts.most_dramatic_away_team,
            h=facts.most_dramatic_home_goals,
            a=facts.most_dramatic_away_goals,
        )
        if facts.most_dramatic_excitement_out_of_10 is not None:
            text += _RECAP_ANALYST[language].format(x=facts.most_dramatic_excitement_out_of_10)
    text += _RECAP_CHANNEL[language].format(
        cuts=facts.cuts, matches=facts.matches_shown, replays=facts.replays
    )
    if facts.fantasy_total is not None:
        text += _RECAP_FANTASY[language].format(
            total=facts.fantasy_total, best=facts.fantasy_best_player, pts=facts.fantasy_best_points
        )
    return text
