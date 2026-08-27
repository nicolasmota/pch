from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pcl_core.errors import PclError
from pcl_core.service import Hub

from pcl_server.mcp.server import ToolHub
from pcl_server.plugins.migrate import migrate_connectors
from pcl_server.rest.auth import current_actor, get_hub
from pcl_server.rest.errors import pcl_error_handler
from pcl_server.rest.idempotency import IdempotencyMiddleware
from pcl_server.rest.routers import (
    actions,
    briefs,
    connections,
    connectors,
    events,
    marketplace,
    memories,
    operational,
    plugins,
    portability,
    projects,
    proposals,
    relations,
    search,
    setup,
    state,
    versions,
)
from pcl_server.rest.spa import SpaStaticFiles
from pcl_server.sync.scheduler import scheduler_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = asyncio.Event()
    task = asyncio.create_task(scheduler_loop(app.state.hub, stop))
    try:
        yield
    finally:
        stop.set()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


def create_app(hub: Hub | None = None, data_dir: Path | None = None) -> FastAPI:
    hub = hub or Hub(data_dir or Path.home() / ".pch", plain=True)
    try:
        migrate_connectors(hub)
    except Exception:
        pass
    app = FastAPI(title="Personal Context Layer", version="0.1.0", lifespan=lifespan)
    app.state.hub = hub
    app.state.mcp = ToolHub(hub)
    app.add_exception_handler(PclError, pcl_error_handler)
    app.add_middleware(IdempotencyMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for router in (
        setup.router,
        search.router,
        briefs.router,
        connections.router,
        connectors.router,
        plugins.router,
        marketplace.router,
        proposals.router,
        state.router,
        actions.router,
        events.router,
        portability.router,
        versions.router,
        memories.router,
        projects.router,
        operational.router,
        relations.router,
    ):
        app.include_router(router, prefix="/v1")

    @app.post("/v1/mcp/tools/{name}")
    def mcp_tool(
        name: str,
        body: dict | None = None,
        hub_dep: Hub = Depends(get_hub),
        actor: tuple[str, bool] = Depends(current_actor),
    ) -> dict:
        ident, is_owner = actor
        return app.state.mcp.call(name, "owner" if is_owner else ident, **(body or {}))

    @app.get("/v1/mcp/resources")
    def mcp_resource(
        uri: str,
        actor: tuple[str, bool] = Depends(current_actor),
    ) -> dict:
        ident, is_owner = actor
        data = app.state.mcp.resource(uri, "owner" if is_owner else ident)
        return {"uri": uri, "contents": data}

    @app.get("/health")
    def health() -> dict:
        return {"ok": True}

    static = Path(__file__).parent.parent / "static"
    if static.exists():
        app.mount("/", SpaStaticFiles(directory=str(static), html=True), name="ui")
    return app


def dev_app() -> FastAPI:
    data_dir = Path(os.environ.get("PCH_DATA_DIR") or (Path.home() / ".pch"))
    plain = os.environ.get("PCH_PLAIN_SQLITE") == "1"
    return create_app(Hub(data_dir, plain=plain))
