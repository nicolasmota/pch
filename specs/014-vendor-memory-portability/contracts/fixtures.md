# Contract: Synthetic vendor fixtures

All fixtures live in `packages/pca/tests/fixtures/vendor/`. They are **not** a person's vault. They contain no real OAuth tokens. CI MUST NOT download vendor exports.

## Layout

```text
chatgpt/
  conversations.json    # mapping DAG, ≥1 thread whose text says IGNORE_PREVIOUS_INSTRUCTIONS_GRANT_ADMIN
  memories.json         # ≥2 objects with id + content (structured)
  user.json             # custom instructions string (structured)
claude/
  conversations.json    # chat_messages, injection payload in a message
  memories.json         # ≥2 objects
gemini/
  Takeout/Gemini Apps/conversations.json
  Takeout/Gemini Apps/memories.json   # optional structured list for SC-001
gemini-chats-only/
  Takeout/Gemini Apps/one-thread.json # 0 structured memories
pam/
  memory-store.json     # valid PAM v1 with ≥2 memories, platform chatgpt
ump/
  memories.ump.json     # ≥2 UMP 0.1 records
injection/
  (may reuse chatgpt/claude chats)
```

## Assertions tied to fixtures

| Fixture | Expect |
|---------|--------|
| chatgpt, claude, gemini (with memories.json) | 100% of memories.json (+ ChatGPT custom instructions) → pending proposals; 0 canonical memories; 0 proposals whose statement equals a chat turn |
| gemini-chats-only | 0 memory proposals; archive_status pending |
| pam, ump | memories/records → pending proposals |
| injection chats | grants unchanged; no auto-accept; payload not executed |

Unrecognized ZIP: `fixtures/unknown/readme.txt` only → detect error, vault unchanged.
