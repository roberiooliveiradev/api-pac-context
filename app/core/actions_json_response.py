from __future__ import annotations

from typing import Any

from starlette.responses import Response

from app.core.json_encoding import dumps_actions_safe


class ActionsJSONResponse(Response):
    media_type = "application/json"

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            content=dumps_actions_safe(content),
            status_code=status_code,
            headers=headers,
        )
