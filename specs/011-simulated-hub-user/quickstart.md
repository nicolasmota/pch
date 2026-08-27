# Quickstart: Simulated Hub User

**Feature**: `specs/011-simulated-hub-user/`  
Watch a scripted person fill an isolated Hub and then ask it questions. This is not Personal Agency and not the E6 scorecard.

Hub already running locally (`make serve`, loopback). Everyday vault stays untouched.

## 1. See the ticks that will run (no writes)

```bash
uv run pcl-sdk sim dump --persona lived-stretch
```

Expect: a numbered list of owner creates and later searches / situation asks. At least 40 durable creates and 10 queries. No mail, no calendar, no model.

## 2. Watch in the Hub

Open the Hub you already use → **Simulator**. Start `lived-stretch`.

Expect: a timeline that grows while the run is in progress (role, action, result). Click a write → see input and the object. Click a situation ask → see the package’s project and citations.

Or headless (tests / no UI):

```bash
uv run pcl-sdk sim run --persona lived-stretch --delay-ms 0
uv run pcl-sdk sim status
```

Expect: `complete`, `object_count` ≥ 40, `query_count` ≥ 10. Data dir is `~/.pch-sim` (or temp in tests), not `~/.pch`.

## 3. Confirm isolation

Keep using your everyday Hub. After a default sim run, your real memories/projects are unchanged. Opting into the everyday vault requires typing `WRITE_EVERYDAY_VAULT`; a start without that is refused.

## 4. Optional: same path as Cursor

```bash
uv run pcl-sdk sim run --persona lived-stretch --paired-assistant --print-mcp-recipe
```

Expect: query ticks labeled as paired assistant. Recipe printed for *you* to paste into a local MCP config if you want Cursor to talk to this isolated space. The command does not write `.cursor/mcp.json`. The timeline still works if you skip this.

## 5. What not to do

Do not treat the synthetic person as an agent that emails or books travel. Do not replace `pcl-sdk eval run` with this. Do not point a default run at `~/.pch`.
