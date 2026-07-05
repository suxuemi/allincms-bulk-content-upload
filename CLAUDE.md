# CLAUDE.md — allincms-bulk-content-upload

Entry point for Claude Code. This file is intentionally minimal — it routes you to the shared contract so there is nothing here to drift out of sync.

- **Operating contract:** [`SKILL.md`](SKILL.md) — read it before touching AllinCMS. It is the single authoritative source for the JSON-first execution split, required reading, full workflow, and stop conditions.
- **Agent operating rules + safety gates:** [`AGENTS.md`](AGENTS.md) — the read-only-by-default rule, the pre-mutation gate, run-scoped authorization with hard carve-outs, no-fabrication, and no-business-data-at-rest rules apply to Claude exactly as written there. They are not restated here to avoid two versions.

When loaded as a skill, invoke it as `allincms-bulk-content-upload` via the Skill tool. When this repo is opened as a project, treat `AGENTS.md` as the authority for how to work in it.
