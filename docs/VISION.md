# Personal Context

> **Your agent can change. Your context shouldn't.**

You tell one agent you are planning a ten-day trip for two, Amsterdam or London. You open a different agent — different product, different model — and say only: continue planning the trip. It already knows the goal, the people, the candidates. You drop London. Every agent you have authorized sees Amsterdam as the live one.

That is not how personal AI works today. Each ChatGPT, Claude, Gemini, Cursor, or OpenClaw keeps its own shard of you. The shards disagree. You cannot take them with you. The industry calls that a memory problem and reaches for better retrieval. It is a **ownership** problem: the representation of the person is trapped inside the runtime.

It is also a **situation** problem. Remembering that you once mentioned Amsterdam is not the same as knowing you are in the middle of planning a trip, with a budget, two travelers, and London already rejected. Memory is what happened. Context is what matters now.

People already live in several agents. MCP exists. Memory is still locked per runtime. That is why this is due.

The thing that should exist is a **context layer** the person owns: a portable record of who they are and what they are doing, plus the smallest sufficient slice for the task at hand. Not a chatbot. Not a model. Not a vector database. Agents read it under a grant. None of them own it.

Product memory (ChatGPT, Claude) dies when you leave the product. App memory (Mem0, Zep, most “layers”) is embeddings for one application. OpenClaw is an agent; it should plug into a layer like this, not pretend to be one.

A Hub already runs on your machine — encrypted, local, loopback, MCP, grants, Calendar and Gmail as plugins. You can store, search, and propose. What it cannot do yet is assemble that trip package for a stranger agent.

The missing piece is not “more memory.” It is a pass that, given a purpose, returns only what that agent is allowed to know for that situation: the live goal, the current state, the constraints, the citations — and an explicit note of what was withheld. Agents should not have to guess what to search. That engine is next. Inferring your patterns and acting for you come after it is trustworthy. Not before.

```bash
make install
make serve
```

Pair Cursor in Connections, paste the recipe into MCP settings, grant a project. Data stays in `~/.pch`. You get a private vault and scoped retrieval today. The trip handoff is the proof the engine has to pass.

How that work is sequenced: [ROADMAP.md](ROADMAP.md).
