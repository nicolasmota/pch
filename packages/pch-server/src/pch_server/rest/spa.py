from __future__ import annotations

from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles
from starlette.types import Scope


class SpaStaticFiles(StaticFiles):
    """Serve the React app for UI paths; never swallow /v1 or /health."""

    async def get_response(self, path: str, scope: Scope):
        if path == "health" or path == "v1" or path.startswith("v1/"):
            raise HTTPException(status_code=404)
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code == 404 and self.html:
                return await super().get_response("index.html", scope)
            raise
