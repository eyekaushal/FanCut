from fancut.agents.commentary import Commentary, Source
from fancut.agents.fact_checker import Verdict
from fancut.profile import Depth, Language

from .conftest import ScriptedModel
from .test_fact_checker import FACTS, GOOD

REFERENCE = "Replay from Elmhurst Wanderers 2-1 Copperhill City, 71': Callum Brannagh scores."
ACCEPT = Verdict(supported=True, problems=[])
REJECT = Verdict(supported=False, problems=["invented a record"])


async def _narrate(model: ScriptedModel | None) -> object:
    return await Commentary(model).narrate(FACTS, REFERENCE, Language.ENGLISH, Depth.CASUAL)


async def test_without_a_model_the_reference_airs() -> None:
    line = await Commentary(None).narrate(FACTS, REFERENCE, Language.ENGLISH, Depth.CASUAL)
    assert (line.text, line.source, line.drafts) == (REFERENCE, Source.TEMPLATE, 0)


async def test_an_accepted_first_draft_airs() -> None:
    model = ScriptedModel(texts=[GOOD], verdicts=[ACCEPT])
    line = await Commentary(model).narrate(FACTS, REFERENCE, Language.ENGLISH, Depth.CASUAL)
    assert (line.text, line.source, line.drafts) == (GOOD, Source.MODEL, 1)


async def test_a_rejected_draft_is_rewritten_with_feedback() -> None:
    model = ScriptedModel(texts=[GOOD, GOOD], verdicts=[REJECT, ACCEPT])
    line = await Commentary(model).narrate(FACTS, REFERENCE, Language.ENGLISH, Depth.CASUAL)
    assert (line.source, line.drafts, line.rejected) == (Source.MODEL, 2, ["invented a record"])
    assert model.calls == ["Narrator", "FactChecker", "Narrator", "FactChecker"]


async def test_three_rejections_fall_back_to_the_reference() -> None:
    model = ScriptedModel(texts=[GOOD] * 3, verdicts=[REJECT] * 3)
    line = await Commentary(model).narrate(FACTS, REFERENCE, Language.ENGLISH, Depth.CASUAL)
    assert (line.text, line.source, line.drafts) == (REFERENCE, Source.TEMPLATE, 3)
    assert len(line.rejected) == 3


async def test_a_model_outage_never_silences_the_channel() -> None:
    model = ScriptedModel(texts=[])  # the first call raises StopIteration
    line = await Commentary(model).narrate(FACTS, REFERENCE, Language.ENGLISH, Depth.CASUAL)
    assert (line.text, line.source) == (REFERENCE, Source.TEMPLATE)
