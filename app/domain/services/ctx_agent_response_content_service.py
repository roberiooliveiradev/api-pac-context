from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_CONTENT_PATH = (
    Path(__file__).resolve().parents[2] / "content" / "pt-BR" / "ctx_agent_response.json"
)


@lru_cache(maxsize=1)
def _load_bundle() -> dict[str, Any]:
    with _CONTENT_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return {"interpretations": {}, "operationEmptyHints": {}}
    return payload


class CtxAgentResponseContentService:
    @staticmethod
    def interpretation(key: str, *, record_count: int = 0, branch: str = "") -> str:
        interpretations = _load_bundle().get("interpretations") or {}
        template = str(interpretations.get(key) or "").strip()
        if not template:
            return ""
        return (
            template.replace("{recordCount}", str(record_count)).replace("{branch}", branch)
        )

    @staticmethod
    def operation_empty_hint(operation_id: str) -> str:
        hints = _load_bundle().get("operationEmptyHints") or {}
        return str(hints.get(str(operation_id or "").strip()) or "").strip()
