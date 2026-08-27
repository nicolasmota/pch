# Quickstart: Assistant Capture Guidance

**Feature**: `specs/012-assistant-capture-guidance/`  
Pair once at **user** MCP. A second window of the same assistant can request the situation package. Stating two facts creates **proposals**, not live memories. This is not Personal Agency and not the Simulator.

Hub already running locally (`make serve` or `make desktop`), loopback.

## 1. Pair and copy the new recipe

Connections → pair Cursor (or Hermes / OpenClaw) → Generate recipe.

Expect: instructions tell you to add the server in the **assistant’s user/runtime settings** (Cursor: Settings → MCP on this machine), not “only paste into this repo’s `.cursor/mcp.json`.” A **runtime rule** block is visible and copyable. The Hub does not create files in `~/.cursor` for you.

Reload MCP. Health check must pass (`/health`).

## 2. Other window

Open a **different local folder** in the same assistant. Ask only: continue planning the trip / what should I do next that depends on my context.

Expect: the assistant requests the situation package (purpose set). If the everyday vault is empty, it says so — it does not invent Amsterdam as your life.

## 3. Two durable facts

Still in that window, state two real facts you want remembered (or, in tests, the fixture lines).

Expect: Review Queue shows **two proposals**. Memories list does not treat them as live until you Accept.

## 4. This repository

A coding session whose only job is implementing the Hub still MUST NOT dump spec/plan chatter into the vault. `AGENTS.md` still says the coding agent is not a Hub client. Override only if **you** say this chat is personal.

## 5. What not to do

Do not paste the recipe only into `pcl/.cursor/mcp.json` and expect other projects to capture. Do not ask the Hub to tail chat logs. Do not seed `~/.pch` from Simulator `lived-stretch` unless you explicitly confirm everyday write. Do not treat Gmail/Calendar import as “extract my trip.”
