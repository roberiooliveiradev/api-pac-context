"""Serialização JSON compatível com ChatGPT Actions (sem notação científica em floats)."""

from __future__ import annotations

import json
from typing import Any


class ActionsJSONEncoder(json.JSONEncoder):
    """Evita `2e-05` no payload — validadores da Action costumam rejeitar notação científica."""

    def encode(self, o: Any) -> str:
        return self._encode_value(o)

    def _encode_value(self, o: Any) -> str:
        if o is None:
            return "null"
        if isinstance(o, bool):
            return "true" if o else "false"
        if isinstance(o, int):
            return str(o)
        if isinstance(o, float):
            return self._encode_float(o)
        if isinstance(o, str):
            return json.dumps(o, ensure_ascii=False)
        if isinstance(o, dict):
            if not o:
                return "{}"
            parts = [
                f"{json.dumps(key, ensure_ascii=False)}:{self._encode_value(value)}"
                for key, value in o.items()
            ]
            return "{" + ",".join(parts) + "}"
        if isinstance(o, (list, tuple)):
            if not o:
                return "[]"
            return "[" + ",".join(self._encode_value(item) for item in o) + "]"
        return json.dumps(o, ensure_ascii=False)

    @staticmethod
    def _encode_float(value: float) -> str:
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("Float não finito não é serializável para Actions")
        text = format(value, ".12f").rstrip("0").rstrip(".")
        if not text or text == "-":
            return "0"
        return text


def dumps_actions_safe(payload: Any) -> bytes:
    return ActionsJSONEncoder(ensure_ascii=False, separators=(",", ":")).encode(payload).encode(
        "utf-8"
    )
