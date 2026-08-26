from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from pcl_core.errors import PclError


def problem(code: str, detail: str, status: int) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": f"https://pch.local/errors/{code}",
            "title": code,
            "status": status,
            "detail": detail,
        },
        media_type="application/problem+json",
    )


async def pcl_error_handler(_request: Request, exc: PclError) -> JSONResponse:
    return problem(exc.code, exc.detail, exc.status)
