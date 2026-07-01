import re

from app.core.json_encoding import ActionsJSONEncoder, dumps_actions_safe

_SCI_NOTATION = re.compile(r"\d+e[+-]?\d+", re.I)


def test_encoder_avoids_scientific_notation_for_small_floats():
    payload = {"standard_time_hours_piece": 0.00002, "setup_hours": 0.08}
    raw = dumps_actions_safe(payload).decode()
    assert _SCI_NOTATION.search(raw) is None
    assert "0.00002" in raw
    assert "0.08" in raw


def test_encoder_preserves_nested_lists():
    payload = {"items": [{"value": 2e-05}]}
    raw = dumps_actions_safe(payload).decode()
    assert "2e-05" not in raw
    assert "0.00002" in raw


def test_encoder_roundtrip_structure():
    text = ActionsJSONEncoder().encode({"page": 1, "total": 18, "ratio": 0.0012})
    assert '"page":1' in text
    assert _SCI_NOTATION.search(text) is None
