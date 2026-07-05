# allincms-bulk-content-upload

An AI **skill** (agent operating contract) for building and populating [AllinCMS / LAICMS](https://www.allincms.com) sites: turn a user's source material — PDFs, DOCX, spreadsheets, websites, a written brief — into a source-backed wiki and a confirmed content package, then create or select a site, inspect its live schema, and upload/publish products, posts, media, themes, routes, and pages — verifying backend and frontend state at every step.

This repository is the **single source** for that skill. Claude Code, Codex, and other AI tools load the same contract; this README and the thin `AGENTS.md` / `CLAUDE.md` entry files point every tool at it rather than copying it.

> **The authoritative contract is [`SKILL.md`](SKILL.md).** Everything here is a map to it. If this README and `SKILL.md` ever disagree, `SKILL.md` wins.

## What it does

- **Source → package.** Distill user source files into a local source-backed wiki, then a publish-ready draft package: single-page/product/post/site-info drafts, plus a media / form / navigation / category plan. Nothing is fabricated — PII, contact details, and prices are user-supplied only.
- **Confirm, then build.** The user reviews the prepared package once. Only then does the skill touch the live site.
- **JSON-first execution.** After one live save-capture, replay via the Next Server Action instead of simulating the UI: content (categories/products/posts) as JSON batches, theme design captured via CDP, with site-creation and local-image→CDN media upload as the genuinely UI-only steps.
- **Verify everything.** Every create/save/publish is checked against live backend re-read and public frontend state — not against the producer's own summary.

## Safety model (non-negotiable)

This skill touches shared remote state, so safety is enforced in code (`scripts/check_pre_mutation_gate.py`), not just prose:

- **Read-only by default.** No site is mutated until the user explicitly authorizes it.
- **A gate before every remote mutation.** Each create/save/publish/upload/delete/batch action must pass the pre-mutation gate (preflight freshness, schema verification, sample proof, evidence, action record) — a gate failure stops the run.
- **Run-scoped authorization, with hard carve-outs.** One upfront grant can auto-cover the repetitive in-scope content build (no re-prompting), but it **expires** (default 8h TTL) and never covers carve-outs: creating a new site, delete/cleanup/unpublish, outward-facing settings (domains, tracking, forms), or any other site — those always require a fresh explicit authorization. See [`references/mutation-safety.md`](references/mutation-safety.md).
- **No business data at rest.** Real site keys, cookies, tokens, credentials, contact lists, and PII never live in this repo — only neutral field names, route shapes, and redacted evidence needed to prove platform behavior.

## Using it from different AI tools

The skill is discovered through `SKILL.md`. The recommended layout keeps one real copy and links it into each tool:

```bash
# 1. Clone this repo as the single source
git clone <repo-url> "$HOME/skills/allincms-bulk-content-upload"

# 2. Link it into each tool's skill folder (symlink = one source, no drift)
mkdir -p "$HOME/.codex/skills" "$HOME/.claude/skills"
ln -s "$HOME/skills/allincms-bulk-content-upload" "$HOME/.codex/skills/allincms-bulk-content-upload"
ln -s "$HOME/skills/allincms-bulk-content-upload" "$HOME/.claude/skills/allincms-bulk-content-upload"
```

| Tool | How it loads | Entry file |
|---|---|---|
| **Claude Code** | Skill tool, invoked as `allincms-bulk-content-upload` | `SKILL.md` (+ `CLAUDE.md` if the repo is opened as a project) |
| **Codex** | `~/.codex/skills/` symlink | `SKILL.md` (+ `AGENTS.md` if the repo is opened as a project) |
| **Other agents** (Cursor, Gemini CLI, …) | Read `AGENTS.md` at repo root | `AGENTS.md` → `SKILL.md` |
| **OpenAI-style interface** | `agents/openai.yaml` card | `agents/openai.yaml` → `SKILL.md` |

`AGENTS.md` and `CLAUDE.md` matter mainly when this repo is opened **as a project**; when it is loaded **as a skill**, the loader reads `SKILL.md` directly. Both paths converge on the same contract.

If symlinks are unavailable, copy the whole directory into the tool's skill folder — but then keep exactly one long-lived copy authoritative and re-sync the others from this repo.

## Repository layout

| Path | What lives there |
|---|---|
| [`SKILL.md`](SKILL.md) | The authoritative operating contract: operating rule, required reading, workflow, browser paths, probe/payload rules, stop conditions |
| [`AGENTS.md`](AGENTS.md) | Thin agent entry (generic `agents.md` standard) → points at `SKILL.md` |
| [`CLAUDE.md`](CLAUDE.md) | Thin Claude Code entry → points at `AGENTS.md` + `SKILL.md` |
| `references/` | Deep contracts: Server-Action save API, mutation safety, field mapping, request capture, launch acceptance, and more |
| `scripts/` | Enforcement + helpers: the pre-mutation gate, authorization builders, manifest/evidence validators, simulators, and their `test_*.py` |
| `agents/` | Per-tool interface cards (`openai.yaml`) |
| `_archive/` | Retired build logs kept for recovery, out of the active contract |

## Repository safety

This repo is GitHub-maintained and reusable across devices. Keep it generic and clean:

- **Do** include the operating contract, references, helper scripts, tests, and install instructions.
- **Do not** include customer data, secrets, production credentials, real site keys, cookies/tokens, contact lists, or account-specific business copy. Placeholder site keys in tests are neutral (e.g. `mysite01`), never real.
