# AGENTS.md — allincms-bulk-content-upload

Generic entry point for any AI agent that reads `AGENTS.md` (Codex, Cursor, Gemini CLI, and other `agents.md`-aware tools). This file is intentionally thin: it does not restate the contract, it routes you to it.

## Read this before acting

**The operating contract is [`SKILL.md`](SKILL.md). Read it before touching AllinCMS.** It defines the JSON-first execution split, the required reading, the full workflow, browser paths, probe/payload rules, and stop conditions. Do not infer behavior from this file — this file only exists to send you there. Deep contracts are under `references/`; enforcement and helpers are under `scripts/`.

## Non-negotiable safety gates (full text in `SKILL.md` + `references/mutation-safety.md`)

*Summary only. `SKILL.md` and `references/mutation-safety.md` are authoritative on the exact TTL and carve-out list — do not treat these bullets as the source of truth or edit them in place of the contract.*

- **Read-only until authorized.** Default to inspection. Do not create a site, click content-create buttons, save, publish, upload, delete, or batch until the user explicitly authorizes it.
- **Gate every remote mutation.** Each mutation must pass `scripts/check_pre_mutation_gate.py` (preflight freshness, schema verified, sample proof, evidence, action record). A gate failure stops the run — do not work around it.
- **Run-scoped authorization is not a blank check.** One grant may auto-cover the repetitive in-scope content build, but it expires (default 8h) and never covers carve-outs: new-site creation, delete/cleanup/unpublish, outward-facing settings (domains/tracking/forms), or any site other than the authorized one. Carve-outs always need a fresh explicit authorization.
- **Never fabricate.** PII, contact details, prices, certifications, reviews, and addresses are user-supplied only. Never invent them to fill a template.
- **No business data at rest.** Do not write real site keys, cookies, tokens, credentials, or contact data into this repo. Record only neutral field names, route shapes, and redacted evidence.
- **Single controller for mutations.** Parallel agents may run only independent read-only checks. Remote mutations stay single-stage and controller-run behind the gates above.

## Scope

LAICMS / AllinCMS site-building only. Do not add external-product SOPs, site-specific business copy, private export workflows, or account-specific operations to this skill.
