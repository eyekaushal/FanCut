from fancut.agents.profile_compiler import ProfileCompiler, ProfileDraft, readback, resolve
from fancut.profile import Depth, Language
from fancut.sim.clubs import TEAMS

from .conftest import ScriptedModel

STAR = {t.id: t.star_player_id for t in TEAMS.values()}


def test_names_resolve_even_with_typos_and_the_captain_joins_the_squad() -> None:
    draft = ProfileDraft(
        club="Kingsmere",
        players=["Ronan Mehtta"],
        fantasy_players=["Pierre Delacroix"],
        captain="Theo Ashworth",
        language="hinglish",
        depth="analyst",
    )
    compiled = resolve(draft, "…")
    profile = compiled.profile
    assert profile.club_id == "kingsmere"
    assert profile.player_ids == (STAR["kingsmere"],)
    assert set(profile.fantasy_squad) == {STAR["oakbridge"], STAR["ashvale"]}
    assert profile.captain_id == STAR["ashvale"]
    assert (profile.language, profile.depth) == (Language.HINGLISH, Depth.ANALYST)
    assert compiled.questions == []


def test_unknown_names_become_questions_not_guesses() -> None:
    compiled = resolve(ProfileDraft(club="Real Madrid", players=["Zlatan"]), "…")
    assert compiled.profile.club_id is None
    assert compiled.profile.player_ids == ()
    assert len(compiled.questions) == 2


def test_language_falls_back_to_the_script_the_fan_wrote_in() -> None:
    assert resolve(ProfileDraft(), "मैं फ़ैन हूँ").profile.language is Language.HINDI
    assert resolve(ProfileDraft(), "I am a fan").profile.language is Language.ENGLISH


def test_readback_speaks_the_fans_language() -> None:
    profile = resolve(ProfileDraft(club="Thornwick United", language="hi"), "…").profile
    assert readback(profile).startswith("आप Thornwick United के फ़ैन हैं।")


async def test_the_compiler_uses_the_model_when_there_is_one() -> None:
    model = ScriptedModel(verdicts=[ProfileDraft(club="Harbourside Rangers", language="en")])
    compiled = await ProfileCompiler(model).compile("Harbourside fan")
    assert compiled.profile.club_id == "harbourside"
    assert model.calls == ["ProfileCompiler"]


async def test_offline_the_compiler_still_finds_full_names() -> None:
    compiled = await ProfileCompiler(None).compile("Copperhill City fan, I follow Yusuf Okafor")
    assert compiled.profile.club_id == "copperhill"
    assert compiled.profile.player_ids == (STAR["copperhill"],)
