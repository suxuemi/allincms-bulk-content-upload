---
name: allincms-bulk-content-upload
description: AllinCMS / LAICMS backend site setup and content upload operator for creating or inspecting sites, turning user PDFs/DOCX/spreadsheets/websites/briefs into a source-backed wiki and confirmed site content package, configuring site info/domains/themes/routes/forms, and uploading posts, products, media, themes, routes, and page-like content after live inspection. Use when Codex must distill source files into publish-ready single-page/product/post/site-info drafts, get user confirmation, inspect a logged-in workspace.laicms.com site, map the current content-type fields, capture one real save request, build a content-type-specific payload template, validate a manifest, upload sample content, batch upload or publish entries, and verify backend/frontend persistence. Do not use for non-CMS browser workflows, external SaaS operations, private data exports, or assuming posts and products share identical payload schemas.
---

# AllinCMS Bulk Content Upload

## Operating Rule

**JSON-first split rule (read this before choosing an operation mode).** After live inspection + one real save capture, prefer JSON/Server-Action replay over UI simulation — UI simulation wastes time and tokens. The layers split cleanly:

- **Content — categories, products, posts → default to JSON.** All three save via a Next Server Action (POST current route + `next-action` header + JSON-array body) that a late-injected `window.fetch` interceptor CAN capture. Capture once per deployment, then batch-replay serially with retry. Taxonomy first: create categories, get each `categoryId`, then reference them as an ID array in products/posts. Body-bearing entities (product/post `content`) MUST go through JSON as a Slate node array — the UI edit form does not bind the Slate editor, so a UI save wipes the body. Contract, action table, publish semantics (`mode:'publish'`), `next-action` per-deployment drift, and the 503/Mongo-transaction serial-retry rule live in `references/server-action-save-api.md`.
- **Theme design — JSON-replayable, but capture via CDP, not late `fetch`.** Theme page design-save is also a Server Action (`POST .../design`, body carries the whole-page `pageDocument`), but Next captured its `fetch` at bundle init so a late `window.fetch` patch cannot see it — capture it via CDP Network (or a pre-init hook / scoped Jotai atom), then edit `pageDocument` block props and replay the whole page. Until captured, the reliable fallback is the designer half-auto method (React value-setter batch-fill + Save/Publish; images via the media modal URL tab) in `server-action-save-api.md` §7. Never write "theme cannot be JSON" — it can; the constraint is the capture method.
- **Genuinely UI-only:** creating a site, default-theme bootstrap when the frontend is 404/blank, and local-image → CDN media upload. These have no JSON path and stay browser-driven behind the normal gates.
- Move between backend routes with click-based SPA soft-navigation; `navigate`/hard-reload drops the Clerk session. Set fields with `form_input`/value-setter, never keystroke `type` (drops characters) and never editor typing/`execCommand` for Slate bodies.

Treat posts and products as similar workflows with different schemas. Never reuse a post payload for products, pages, or media until the current site and content type have been inspected and one real save request has been captured.

Bulk upload is supported only after the live gates pass. The skill can turn source files into draft products/posts manifests, bind them to a created or selected site, capture the current save schema, prepare a one-item sample runbook, and then prepare a batch upload/publish runbook. It must not perform live batch upload from source files, source-site packages, exported draft manifests, or `schemaVerified: false` manifests. Before any batch run, require all of these for the exact site and content type: `validate_manifest.py --require-schema-verified` passes, the manifest was upgraded with validated save-capture evidence, one real manifest sample slug passed backend and frontend verification, the batch authorization record exists, and `check_pre_mutation_gate.py --action batch_upload` passes. Treat source-derived categories and tags as a separate taxonomy plan: confirm them with the user, then capture/create/map current-site category/tag schemas before relying on them in products, posts, or homepage modules.

Follow the official AllinCMS tutorial flow before improvising UI exploration. When building a site from scratch, use the docs order as the default path: create site, open the frontend once, reuse or edit default template content if present, fix theme/homepage first if the frontend is 404 or blank, then prepare product categories, products, posts, homepage modules, extra pages, domains/settings, and launch checks. Use browser probing and JSON/Server Action capture to verify or accelerate that documented flow, not to replace it with ad hoc blank-theme experimentation. If the user explicitly says to follow `https://www.allincms.com/docs`, refresh the relevant docs pages first and treat the refreshed tutorial order as the current operating route.

The official tutorial defines the first-launch target as a small complete website, not a full catalog: 2-3 product categories, at least 2 products per category, 3 basic posts, homepage Header/Banner/category/product/news/footer modules, default pages edited before duplicates, and visitor-style frontend QA. Stop and fix the current tutorial gate before moving forward: a public 404/blank blocks content expansion; missing categories/products/posts block homepage module completion; backend save/publish blocks are incomplete until public list/detail click-through works.

This skill touches shared remote state. Default to read-only inspection until the user has explicitly authorized creating a site, clicking content create buttons that create drafts, creating a probe item, saving sample content, publishing, deleting, uploading media, or batch uploading.

For a user-designated temporary/test site, a current-session policy such as "operate directly on this test site" may remove repeated user prompts, but it does not remove action records. Before each remote mutation, still bind the operation to an exact site key, target URL, action, target identifier, expected result, verification plan, and cleanup or stop boundary. If a helper gate only supports probe names and the current action is legitimate demo-site content creation, record the gate coverage gap, keep the browser action narrowly scoped, and verify backend plus frontend state before continuing.

**Run-scoped authorization (one grant covers the in-scope content build, no re-prompting).** When the user wants a hands-off build, capture ONE run-scoped authorization at the content-intent confirmation point (after they reviewed the prepared package) with `scripts/run_authorization.py` — it binds to a single `siteKey` + the confirmed package hash and allowlists only the repetitive content-build actions (taxonomy, product/post create/save/publish, batch, media upload, theme content build). Then run each in-scope mutation's gate with `check_pre_mutation_gate.py --run-authorization <grant> --target <url>`: it derives the per-action authorization so the user is not re-prompted, but STILL runs every other gate check (preflight, schema, sample, evidence, freshness) and STILL records each action. Hard carve-outs ALWAYS require a fresh explicit `--authorization` even under a run-scoped grant — creating a NEW site, delete/cleanup/unpublish, outward-facing settings (domains, tracking, forms/webhooks, site-settings saves), any site other than the authorized one, and any action not on the allowlist (unknown/future actions default to carve-out). A gate FAILURE (bad schema, empty Slate body, placeholder) still stops regardless of the grant. The grant EXPIRES (`expiresAt`, default 8h TTL, `--ttl-hours` to change) — past its TTL it stops auto-covering and you must re-grant, so a grant from an earlier session never silently keeps authorizing. Never fabricate PII/contact/price — those are user-supplied, never auto. Grant at content-review time, not as a blank check before content exists.

Keep this skill about LAICMS / AllinCMS site-building operations only. Do not store external-product SOPs, site-specific business copy, private export workflows, account-specific operations, or other non-CMS material in the skill. When live evidence comes from a real site, record only neutral field names, route shapes, DOM symptoms, and redacted snippets needed to prove the platform behavior.

For verification or exploration work, parallel agents may be used when the tasks are independent and read-only, such as checking frontend routes, inspecting backend visible fields, auditing skill references, or reviewing captured evidence. When the user asks to "逐个验证", "核验", "探索接口", or "对抗检查", consider parallel read-only agents first if the targets can be split cleanly. The main agent remains the controller: assign each subagent a scoped question, exact URLs or files, allowed read-only actions, forbidden mutations, and required evidence format; then reconcile findings before making a claim or moving to the next stage. Do not give subagents permission to save, publish, delete, upload, create drafts, replay requests, or operate the same mutable browser state. Remote mutations stay single-stage and controller-run after the normal authorization and pre-mutation gates.

Use the in-app browser first for LAICMS work when it is available. Fall back to Chrome when the in-app browser cannot be controlled reliably, including zero-size viewports, missing controllable tabs, repeated claim failures, route load failures, or suspected login-state drift. Chrome fallback is not mutation readiness by itself: first prove authentication by loading `/sites` or the exact target module route in Chrome, then bind the current site key and target URL before any save, publish, upload, delete, or create action.

Every AllinCMS skill turn must end with a skill sedimentation pass before the final response. This includes browser operation, local simulation, helper-script changes, request analysis, planning, discussion, and validation-only rounds. Actively check whether the turn exposed reusable platform findings, interface changes, failure modes, field risks, validation gaps, command drift, or safer operation order. Record encountered reusable problems in this skill package before the final response. If the turn reveals no reusable finding, explicitly note "no reusable skill update needed" in the final response after checking. Do not record temporary site business copy, private account data, raw IDs, cookies, tokens, or one-off content.

If the current user instruction explicitly forbids file edits or asks for read-only review only, do not mutate this skill package just to satisfy sedimentation. Report reusable findings in the final answer as `read-only deferred sedimentation`, then record them in the skill at the first later turn where edits are allowed before continuing mutable work.

At the start of each AllinCMS skill turn, choose the closeout path you will need: run-evidence closeout when current browser/rehearsal evidence exists, or maintenance closeout for planning, discussion, request analysis, documentation, helper-script, or validation-only work. Keep a running `roundIssues` note of reusable problems, command drift, validation gaps, browser surprises, and explicit no-change observations as they appear; do not wait until the final response to decide whether the turn produced a skill update. Before the final response, either update this skill package and run closeout with `--sedimentation updated`, or run closeout with `--sedimentation none --note "no reusable skill update needed after checking"`. Every closeout command must include at least one `--round-issue` item. The final response must report the sedimentation status (`updated` or `none`) and the main `roundIssues` item so the user can see whether the skill was improved this turn.

When resuming after interruption, summary handoff, or context compaction, first check whether the previous AllinCMS skill turn already ran `scripts/check_round_closeout.py` for its latest sedimentation change. If not, run the missing maintenance or run-evidence closeout before continuing to the next browser stage or helper change. Do not let a resumed turn skip closeout because the underlying finding was already written.

## Required Reading

Read only the references needed for the current task:

- `references/field-mapping.md`: use only for UI-probing a content type's field names on first inspection or after a backend version change. It is probe input for building the JSON payload template, not the authoring path — the field contract itself lives in `field-contract.md` + `server-action-save-api.md`, and authoring goes through JSON replay.
- `references/field-contract.md`: use before accepting a manifest schema or payload template; explains each common field, risk, and verification method.
- `references/source-files-to-site-package.md`: use when the user provides files, URLs, catalogs, PDFs, spreadsheets, or briefs and wants Codex to extract, build a local wiki layer, generate pages/products/posts/site-info/forms/media/navigation drafts, ask for confirmation, then create or update an AllinCMS site.
- `references/source-material-norms.md`: read FIRST when turning raw product/article material (a PDF page, a website blurb, a spreadsheet blob) into source-wiki records. It is the visitor-first upstream norm — organized by the visitor's product-page and article decision journey (relevance → fit → differentiate → trust → act) — that says what each product/article's source data must supply and why, plus the acceptance checklist (a conforming record vs a messy blob) and the input-hygiene rules (one product per record, specs structured not prose, strip unverifiable marketing, every claim traceable to a sourceRef, gaps flagged never fabricated). It is the "why these fields serve the visitor" rationale above the intake checklist / content floors / validators.
- `references/site-content-and-aesthetics-spec.md`: use before authoring a new site's content and before theme/beautification. It is the upstream standard for what information a complete site needs (brand/logo, SEO, navigation, taxonomy, products, articles, pages, forms, media, trust), the per-type content floors, the Professional Copy Standard, and the aesthetics rules — especially image/media quality (clean consistent crops, one aspect ratio, hosted URLs) and typography/color/layout consistency. Run its Information Intake Checklist and Aesthetics Gate; it feeds `official-docs-alignment.md` (modules) and `launch-acceptance.md` (final QA). For per-product/article source-material norms, `source-material-norms.md` is the upstream rationale.
- `references/e2e-simulation.md`: use when simulating the full workflow from site creation through content upload while updating this skill.
- `references/official-docs-alignment.md`: use before from-scratch site builds, broad feature walkthroughs, homepage/module work, launch QA, or deciding whether JSON/Server Action submission should replace UI operation. It is the official-docs-first route map for categories, products, posts, homepage modules, new pages, settings, mobile checks, and launch checks.
- `references/site-creation.md`: use before creating a site, simulating site creation, or doing first-site setup checks. It includes official-docs alignment for first opening the frontend, default-template reuse, default-theme creation only when needed, and setup-module order.
- `references/create-flows.md`: use before clicking content, route, theme, form, or media create/upload actions.
- `references/mutation-safety.md`: use before any remote mutation, including site creation, draft creation, save, publish, upload, delete, or cleanup. Also use it before delegating read-only verification or exploration to parallel agents so the dispatch boundary and evidence format are explicit.
- `references/request-capture.md`: use before saving a probe item or replaying requests.
- `references/server-action-save-api.md`: use before a JSON/Server Action content batch. It records the neutral request shape (POST current route + `next-action` header + JSON-array body; `text/x-component` flight response), the per-entity action table (category create only; product/post create/update/publish/delete), field contracts (Slate node arrays for `content`, ID arrays for categories/tags, `{name,alt,type,source:'url',url}` media; product uses `name`+`specifications`, post uses `title`+`excerpt`), publish semantics (update action + `mode:'publish'`, not `isDraft:false`), `next-action` per-deployment drift (re-capture each run), the 503 / MongoDB transaction-conflict serial-retry rule, and §7's two theme scopes (design-save is JSON-replayable via CDP capture; React-setter designer method is the fallback). No real siteId/action-id/copy — those stay in the run folder's contract + registry.
- `references/interface-inventory.md`: use when comparing module interfaces and deciding whether JSON/Server Action replay is safer or faster than UI operation.
- `references/operational-findings.md`: use at the end of each AllinCMS skill turn to capture reusable problems found during browser operation, local simulation, request analysis, planning, discussion, or helper validation. For fast practical passes across many backend pages, first keep a per-module fast-pass ledger with action, return, evidence, blocker, and next step, then compress reusable findings into this file plus `create-flows.md`, `interface-inventory.md`, or `batch-verification.md`. Follow its problem-recording contract, record template, and final-response gate.
- `references/batch-verification.md`: use before sample upload, batch upload, publish, cleanup, or final QA.
- `references/launch-acceptance.md`: use before claiming a from-scratch site-build or launch is complete. It defines the top-level acceptance checklist across site creation, setup, module capture, beautification/theme/routes, content upload, media/forms/settings, final frontend QA, cleanup, and sedimentation.
- `references/live-verification-mysite01.md`: one browser-verified example from 2026-06-29; use only as orientation, not as a cross-site schema.
- Full helper-script index (169 scripts, one line each) lives in `references/script-index.md` — consult it for "which script does what"; each script also has `--help`. The Workflow steps below invoke the ones you run by hand with full commands. Gates you must not skip: `check_pre_mutation_gate.py` (before every remote mutation); `validate_manifest.py --require-schema-verified` + `validate_slate_content_shape.py` + `check_next_action_freshness.py` (before a content batch); `validate_theme_page_document.py` (theme JSON replay body); `audit_skill_hygiene.py` + `check_round_closeout.py` (turn closeout).

## Workflow

**Run-folder convention (stated once; the command blocks below reuse it).** All artifacts go in one run folder OUTSIDE the skill package, e.g. `/tmp/allincms-run/` (subfolders like `confirmed-artifacts/`, `refined-source-apply/`, `created-site-schema-capture/`). The `/tmp/allincms-run/...` paths in the examples below are that convention filled in — substitute your own run folder; each command shows its distinctive flags and the paths just follow this layout.

**Authorization invariant (stated once; do not re-derive per step).** Every prepare/apply/build/validate helper below is local-only, non-authorizing scaffolding — see Invariants INV-2 (authorization never carries to the next action/type/site) and INV-3 (a read-only load/preflight is recovery, not authorization) in `references/operational-findings.md`. Each remote mutation (create site, save, publish, upload, delete, batch) still needs its own action-time authorization + `check_pre_mutation_gate.py`; the steps below assume this everywhere and only call it out where a specific gate name or ordering matters.

1. Confirm whether this run starts from user source files, site creation, or an existing site.
   If the user gives PDFs, DOCX files, spreadsheets, websites, images, or briefs for a new site, do not jump straight to `/sites` or content upload. First read `references/source-files-to-site-package.md`, create a run folder outside this skill package, build a source inventory with `build_source_inventory.py`, extract raw source material, build and validate `allincms_source_wiki`, generate source-input requirements, build `allincms_source_site_package`, validate it, and get user confirmation of the package. Treat this source package as a content contract, not an AllinCMS payload template.
   Read the live tab list (`openTabs()`/`tabs.list()`) as the current URL authority; chat-provided "Current URL" can be stale after switches/redirects/resumes. Browser-control recovery detail lives in `references/mutation-safety.md` — the short rule: a tab missing from `openTabs()` but present in `tabs.list()`/`tabs.selected()`, a `0x0` viewport, or a single `/sign-in` redirect from a stale/wrong-site deep link is a control-surface issue, NOT a LAICMS state/login failure; recover (bind the listed tab, or open a fresh tab), and prove auth by loading `/sites` or the target module route in the same tab before any mutation. Only ask the user to re-login if the target module still redirects to `/sign-in` after recovery.
   After claiming a live tab, compare its backend/frontend state to any local queue/summary/handoff/gap-audit you plan to reuse. If the live tab proves the next queued mutation already happened (e.g. an existing probe edit page while the queue still says `create_*_probe`), stop using that queue and regenerate the next action from fresh evidence — do not create duplicate probes or replay stale mutation stages.
   If a from-scratch rehearsal ledger advances to `create_site_submit` after a real existing-site refresh, stop before mutation and choose explicitly: either branch to an existing-site continuation ledger, or request exact create-site authorization for a new site. Do not create another temporary site just because the static rehearsal ledger says the next stage is create-site.
   For broad verification/exploration tasks, decide whether the work can be split across read-only agents. Keep one controller-owned browser mutation path; use parallel agents only for independent read-only URLs, local files, or evidence reviews, and merge their evidence before reporting status.
2. If creating a site, inspect `/sites`, open the create-site dialog, and confirm required fields. Submit the create action only after explicit action-time authorization recorded with action, target workspace, fields, and cleanup/rollback expectation.
3. After site creation or site selection, first open the public frontend from the site card or `https://{siteKey}.web.allincms.com`. If it renders a normal template page, do not create another theme; continue by editing/replacing default content. If it is 404 or blank, inspect backend theme/homepage state before content upload.
4. Confirm site identity: `siteKey`, backend URL, frontend base URL, dashboard counts, login state, and visible module routes.
5. Inspect first-site setup pages without saving: `site-info`, `domains`, `themes`, `routes`, and `forms`. For a new empty/404 site, inspect themes before trying to design pages; if a theme exists with pages, edit it. If no theme or zero pages exist, create a `默认` preset theme, not a blank theme, unless the user explicitly asks for a blank theme or the operator has a captured pageDocument path.
6. Follow the official first-build order before beautification: product categories, products, posts, homepage modules, optional extra pages, site settings/domains/forms/media, launch checks. Content comes before homepage modules because homepage product/category/news blocks depend on real backend content. If the public frontend is normal after creation, do not create another theme; if it is 404 or blank, fix theme preset, theme enablement, homepage selection, page enablement, and route binding before expanding content.
7. Confirm target content type: usually `posts`, `products`, or `media`. Page-like content may live under `themes` and `routes`; do not assume `/pages` exists.
8. Open the backend list page and inspect visible columns without modifying data.
9. Open one existing edit page and map the actual editable fields.
10. Create or select a safe probe item only after explicit authorization. On verified LAICMS behavior, some `创建` buttons immediately create an `Untitled ...` draft before showing fields.
   For products, a verified create flow may immediately create an `Untitled Product` draft and navigate to `/{siteKey}/products/{contentId}/update`. Do not promise that the probe name is set during the create-only stage; renaming it to `Codex Probe - Delete Me` requires a separate save/request-capture authorization.
11. Trigger one real save and capture the request URL, method, headers, payload, IDs, content-block (Slate node) shape, and publish behavior. This capture is to build the JSON replay, not to rely on the UI save persisting the body: for body-bearing entities (products/posts) the UI edit form does NOT bind the Slate editor, so a UI form save wipes `content` (see the JSON-first split rule at the top and `validate_slate_content_shape.py`). Capture the shape, then submit the body as a Slate node array via JSON replay; re-read `content` to confirm it persisted.
12. Build a payload template for this exact site and content type. JSON/Server Action replay may be used as an acceleration path for themes, pages, routes, posts, products, or forms only after fresh request capture, action-specific authorization, and backend/frontend persistence proof. UI submission remains the fallback when the browser auth context cannot safely replay requests — but never for Slate content bodies, which a UI form save wipes; those must go through JSON.
    Before choosing JSON replay, apply `references/official-docs-alignment.md`: the replayed action must belong to the current official-docs step, not merely be a captured nearby API. Capturing `create blank theme`, `create page`, `save product`, or `publish post` proves only that exact action, not the rest of the tutorial flow.
    For homepage work, keep the docs distinction clear: `Category Showcase`, `Featured Product List`, and `Recommended Products` are homepage/catalog modules; `Full Product List (Filtered)` is a product-list page block. Do not use a list-page block as proof that the homepage product module is configured.
13. For theme/page launch work, verify each state separately: page saved, page published, page enabled, route bound, theme active, frontend HTTP status, and frontend DOM content. Do not treat active theme or a success toast as proof that public pages render.
14. During browser operation, record field-input gaps as soon as they appear. If a page, field, editor, media control, form setting, route, domain, tracking setting, navigation item, or public QA result shows that future users must provide source material or confirmation, append one row to a local ledger outside this skill package:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/record_source_input_gap.py \
     --output /tmp/allincms-source-input-gap-ledger.json \
     --site-key current-site-key \
     --content-type products \
     --field "specifications" \
     --target "products.specifications" \
     --classification "recommended,source-derived,blocked-until-schema-captured" \
     --source-hint "PDF/catalog table with wattage, lumen, voltage, dimensions, certifications" \
     --generation-rule "Generate structured spec rows only after current-site spec row schema is captured." \
     --current-evidence blocked \
     --decision-needed needs-schema-capture \
     --evidence-pointer /tmp/current-run-redacted-evidence.json
   ```

   Keep the ledger in `/tmp` or another run-evidence path. Do not write ledgers into `skills/allincms-bulk-content-upload/`, and do not store business copy, source text, personal data, raw IDs, cookies, or request headers in the ledger.
   Append rows to the same ledger serially. Parallel read-only agents may discover field gaps independently, but the controller must either write one row at a time with `record_source_input_gap.py` or collect per-agent ledgers and merge them later. Do not run multiple `record_source_input_gap.py` writers against the same JSON file concurrently.
   Each discovered field must answer four questions for later PDF/catalog/brief generation: who supplies it (`source-derived`, `user-confirmed`, or both), how to generate it, what current evidence proves the backend shape, and what blocks upload if it is missing. If any answer is unknown, record the field as blocked or needing user confirmation instead of leaving it implicit.
   Separate source-derived fields from user-confirmed fields. Product names, summaries, body copy, specs, applications, image alt text, menu labels, and draft page copy can usually be derived from PDFs, catalogs, websites, spreadsheets, or briefs after schema capture. Domains, notification emails, tracking IDs/snippets, legal company names, public contact channels, route visibility, final sitemap, CTA destinations, pricing, inventory, and unsupported certification claims require user confirmation unless the source explicitly provides them and the user has accepted that source as authoritative.
   If later browser proof supersedes an earlier gap, do not edit or delete the old ledger row. Generate resolved-gap evidence for exactly the superseded field, then record any newly exposed missing field as a separate gap:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/make_resolved_source_input_gaps.py \
     --site-key current-site-key \
     --gap-ledger /tmp/allincms-source-input-gap-ledger.json \
     --resolved-gap "fieldLabel=posts.post-detail-route|proof=/tmp/redacted-post-detail-recheck.json|note=Bounded frontend recheck rendered the new post detail route; body and cover remain separate unresolved fields." \
     --output /tmp/allincms-resolved-source-input-gaps.json
   ```

   Before feeding a ledger into source extraction, validate it:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/record_source_input_gap.py \
     --validate-only \
     --output /tmp/allincms-source-input-gap-ledger.json \
     --site-key current-site-key
   ```

15. Before extracting PDFs, catalogs, websites, spreadsheets, or briefs into a manifest, generate a source-input requirements record for the current site and content types. Use it together with the operation-time gap ledger to identify which fields the source can fill, which fields need user confirmation, and which fields are blocked until a real schema capture exists:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/make_source_input_requirements.py \
     --site-key current-site-key \
     --content-types products,posts,forms,media,themes/pages,site-info,routes,domains,tracking,navigation \
     --gap-ledger /tmp/allincms-source-input-gap-ledger.json \
     --resolved-gap-evidence /tmp/allincms-resolved-source-input-gaps.json \
     --save-capture-evidence /tmp/allincms-products-save-capture-evidence.json \
     --media-evidence /tmp/allincms-media-evidence.json \
     --output /tmp/allincms-source-input-requirements.json
   ```

   Keep the generated file as run evidence. Do not copy business copy, source text, source documents, private communication details, or concrete media URLs into the skill package.
   For a user-supplied PDF/catalog/website/spreadsheet, use the requirements record plus `operationGaps.entries` as the extraction contract: generate only fields marked source-derived with adequate schema evidence; ask for or defer fields marked user-confirmed; keep fields with `blocked-until-schema-captured` out of live upload unless the user records an explicit omission/no-body/no-image/custom-domain/tracking acceptance rule. If an operation gap names a field not present in the static requirement list, treat the operation gap as current-browser evidence that the field needs extraction, confirmation, schema capture, or explicit omission.
16. If the run started from user source files, build and validate the source inventory and source wiki before making the local source-site package:

   For the default path, use the local-only orchestrator first:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_source_site_package.py \
     /tmp/allincms-run/source-files \
     --recursive \
     --output-dir /tmp/allincms-run \
     --site-name "Draft site name" \
     --site-description "Draft source-backed positioning" \
     --industry "target industry"
   ```

   If the summary reports `packageStatus: review_ready`, show the generated review packet to the user for content-intent confirmation. If it reports `needs_source_wiki_refinement` because pages are thin while products/posts/site plan are usable, rerun the rehearsal with `--auto-draft-refined-source-wiki` to generate a local refined wiki draft and apply it in the same run:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/run_source_file_rehearsal.py \
     /tmp/allincms-run/source-files \
     --recursive \
     --output-dir /tmp/allincms-run/source-rehearsal \
     --site-name "Draft site name" \
     --site-description "Draft source-backed positioning" \
     --industry "target industry" \
     --auto-draft-refined-source-wiki
   ```

   This fast path is still local-only. It should reach `waiting_for_user_content_confirmation` only when package and review validation pass. If the source declares `contentGoals.media` but supplies no concrete images, auto-draft may add page/product/post `mediaNeeds` with `source=user_confirmation_or_public_url_required`; treat those as reviewable media requirements, not image URLs or upload proof. If it remains blocked, refine `source-wiki.json` manually from extracted source material into publication-ready pages/products/posts/site-info/navigation/media/contact/taxonomy policy, then apply the refined wiki before asking for confirmation:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/apply_refined_source_wiki.py \
     --source-wiki /tmp/allincms-run/source-wiki.refined.json \
     --inventory /tmp/allincms-run/source-index.json \
     --requirements /tmp/allincms-run/source-input-requirements.json \
     --output-dir /tmp/allincms-run/refined-source-apply
   ```

   Use the generated `source-package-review-packet.refined.json` only if `reviewReady=true`. Do not ask for confirmation or create a site from a placeholder package. A refined wiki is bound to the current refinement brief's `outputRefinedSourceWiki`; if you change `--output-dir`, regenerate the refined wiki or use `--auto-draft-refined-source-wiki` again instead of reusing an older refined file from another run folder.

   Use the individual commands below when debugging or when the source-wiki refinement needs manual control:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/build_source_inventory.py \
     /tmp/allincms-run/source-files \
     --recursive \
     --output /tmp/allincms-run/source-index.json
   python3 skills/allincms-bulk-content-upload/scripts/extract_source_materials.py \
     --inventory /tmp/allincms-run/source-index.json \
     --output-dir /tmp/allincms-run/raw-extraction \
     --site-name "draft site name for extraction summary"
   python3 skills/allincms-bulk-content-upload/scripts/build_source_wiki.py \
     --inventory /tmp/allincms-run/source-index.json \
     --extraction-summary /tmp/allincms-run/raw-extraction/summary.json \
     --output /tmp/allincms-run/source-wiki.json
   python3 skills/allincms-bulk-content-upload/scripts/validate_source_wiki.py \
     --inventory /tmp/allincms-run/source-index.json \
     /tmp/allincms-run/source-wiki.json
   ```

   Then build and validate the local source-site package before making upload manifests:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/build_source_site_package.py \
     --source-wiki /tmp/allincms-run/source-wiki.json \
     --requirements /tmp/allincms-run/source-input-requirements.json \
     --output /tmp/allincms-run/source-site-package.json
   python3 skills/allincms-bulk-content-upload/scripts/validate_source_site_package.py \
     --require-complete-package \
     --require-publication-ready \
     /tmp/allincms-run/source-site-package.json
   ```

   Use structural validation without `--require-publication-ready` only for local rehearsals or early extraction diagnostics. Before asking the user to confirm a package, the publication-ready gate must pass: no `Draft Product` / `Draft Article` placeholders, no `requires review` / `requires source extraction` wording, no unresolved replacement notes, and no page/product/post copy that is too thin to publish. The package may contain publish-ready draft copy, but it must still keep `confirmationGate.required: true`, remote actions blocked, and product/post manifests at `schemaVerified: false` until current-site request capture. Do not upload from the source package directly.
17. Before asking for confirmation, create and validate a local review packet:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/make_source_package_review_packet.py \
     --package /tmp/allincms-run/source-site-package.json \
     --output /tmp/allincms-run/source-package-review-packet.json
   python3 skills/allincms-bulk-content-upload/scripts/validate_source_package_review_packet.py \
     /tmp/allincms-run/source-package-review-packet.json \
     --package /tmp/allincms-run/source-site-package.json
   ```

   Show or summarize this packet for the user instead of pasting long source copy. It is local review evidence only; it does not authorize creating a site, saving, uploading, publishing, routing, media, domains, or tracking.
18. After the user confirms the source-site package from the review packet, prepare the local execution bundle:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_confirmed_site_execution.py \
     --package /tmp/allincms-run/source-site-package.json \
     --review-packet /tmp/allincms-run/source-package-review-packet.json \
     --user-confirmation-text "paste current user confirmation text here" \
     --output-dir /tmp/allincms-run/execution \
     --target-mode new_site
   ```

   This writes a confirmation record, confirmed execution plan, exported draft artifacts, and source execution status. If `--create-preflight /tmp/allincms-create-site-preflight.json` is also provided, it prepares a create-site handoff with authorization placeholders. It still does not create a site, save, upload, publish, route, or bind domains; action-specific mutation gates remain required.

   Use the individual commands below when debugging or when you need to rebuild one artifact:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/make_source_package_confirmation.py \
     --package /tmp/allincms-run/source-site-package.json \
     --review-packet /tmp/allincms-run/source-package-review-packet.json \
     --user-confirmation-text "paste current user confirmation text here" \
     --output /tmp/allincms-run/confirmation-record.json
   python3 skills/allincms-bulk-content-upload/scripts/validate_source_package_confirmation.py \
     /tmp/allincms-run/confirmation-record.json \
     --package /tmp/allincms-run/source-site-package.json \
     --review-packet /tmp/allincms-run/source-package-review-packet.json
   python3 skills/allincms-bulk-content-upload/scripts/build_confirmed_site_execution_plan.py \
     --package /tmp/allincms-run/source-site-package.json \
     --confirmation /tmp/allincms-run/confirmation-record.json \
     --target-mode new_site \
     --output /tmp/allincms-run/confirmed-site-execution-plan.json
   python3 skills/allincms-bulk-content-upload/scripts/export_confirmed_site_artifacts.py \
     --package /tmp/allincms-run/source-site-package.json \
     --confirmation /tmp/allincms-run/confirmation-record.json \
     --execution-plan /tmp/allincms-run/confirmed-site-execution-plan.json \
     --output-dir /tmp/allincms-run/confirmed-artifacts
   ```

   This confirms content intent only. It does not authorize create-site, save, publish, route binding, media upload, domain binding, tracking, or batch upload. Continue to use action-specific mutation authorization records and pre-mutation gates.
   After a site is created or selected and setup pages have been inspected, the next main orchestrator can prepare the page/site-info browser handoff from the exported plans. Use the standalone command only when continuing an existing site or debugging that one stage:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_pages_site_info_execution.py \
     --pages-plan /tmp/allincms-run/execution/confirmed-artifacts/pages-plan.json \
     --site-info-plan /tmp/allincms-run/execution/confirmed-artifacts/site-info-plan.json \
     --preflight /tmp/allincms-run/created-site-evidence.json \
     --output-dir /tmp/allincms-run/pages-site-info
   ```

   This handoff is local-only. It does not save site-info, create pages, save design, publish, enable, bind routes, or prove frontend rendering. Use it to choose one action at a time, replace any `{themeId}` or `{pageId}` placeholder with current browser evidence, then request action-time authorization and run the matching pre-mutation gate.
   After taxonomy is confirmed and before relying on categories/tags in upload manifests or homepage category modules, prepare taxonomy execution:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_taxonomy_execution.py \
     --taxonomy-plan /tmp/allincms-run/execution/confirmed-artifacts/taxonomy-plan.json \
     --preflight /tmp/allincms-run/created-site-evidence.json \
     --output-dir /tmp/allincms-run/taxonomy
   ```

   This handoff is local-only. It does not create categories, tags, or mappings. Execute one term action at a time only after current UI/request schema is captured, action-time authorization exists, and the generated pre-mutation gate passes. If an evidence bundle exists, fill `taxonomy-execution-evidence.filled.json`, run its validation command, then run its apply command instead of hand-writing taxonomy evidence from memory. Apply completed taxonomy proof with `apply_taxonomy_execution.py` before batch upload depends on taxonomy. When a manifest contains `categories`, `tags`, or `categoryIds`, pass the resulting validation report into upload readiness and batch preparation with `--taxonomy-validation`; otherwise those helpers must block the run.
19. If the plan targets a new site, refresh `/sites`, build create-site preflight evidence, then prepare the confirmed create-site handoff:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/build_confirmed_create_site_handoff.py \
     --package /tmp/allincms-run/source-site-package.json \
     --review-packet /tmp/allincms-run/source-package-review-packet.json \
     --confirmation /tmp/allincms-run/confirmation-record.json \
     --execution-plan /tmp/allincms-run/confirmed-site-execution-plan.json \
     --preflight /tmp/allincms-create-site-preflight.json \
     --authorization-output /tmp/allincms-authorization-create-site.json \
     --output /tmp/allincms-create-site-handoff.json
   ```

   The handoff is not user authorization and does not create a site. It exists to bind the confirmed package's `siteName` and `siteDescription` to the current create-site preflight, preserve the authorization placeholder, and forbid uploads/publish/theme/domain work in the same mutation.
20. After the new site is created, bind the created `siteKey` and `frontendBaseUrl` into exported draft manifests, and prepare pages/site-info, taxonomy, and content schema-capture handoffs:

   Prefer the created-site schema-capture preparation orchestrator:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_created_site_schema_capture.py \
     --artifact-readiness /tmp/allincms-run/execution/confirmed-artifacts/artifact-readiness.json \
     --created-site-evidence /tmp/allincms-run/created-site-evidence.json \
     --package /tmp/allincms-run/source-site-package.json \
     --review-packet /tmp/allincms-run/source-package-review-packet.json \
     --confirmation /tmp/allincms-run/execution/confirmation-record.json \
     --execution-plan /tmp/allincms-run/execution/confirmed-site-execution-plan.json \
     --output-dir /tmp/allincms-run/created-site-schema-capture
   ```

   This writes bound manifests, created-site artifact binding, pages/site-info browser handoff and evidence bundle, taxonomy execution handoff and evidence bundle, schema-capture handoff, schema-capture progress, and refreshed source execution status. Follow the summary's `nextAction`; source status may correctly stop at pages/site-info execution or taxonomy execution before schema probes. Do not hand-edit site keys, schema flags, taxonomy state, or page/site-info action targets.

   If the created site's frontend is 404/blank and the themes page has no usable theme/pages, prepare and run the default-theme bootstrap before relying on page/site-info or content upload stages:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_default_theme_bootstrap.py \
     --preflight /tmp/allincms-run/created-site-evidence.json \
     --output /tmp/allincms-run/default-theme-bootstrap-runbook.json
   ```

   Execute `create_theme` and `activate_theme` as two separately authorized browser mutations, then validate the redacted evidence:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/validate_default_theme_bootstrap_evidence.py \
     /tmp/allincms-run/default-theme-bootstrap-evidence.json \
     --runbook /tmp/allincms-run/default-theme-bootstrap-runbook.json \
     --output /tmp/allincms-run/default-theme-bootstrap-validation.json
   ```

   Then apply the validated foundation proof back into the created-site evidence and rerun the next preparation step from the refreshed evidence:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/apply_default_theme_bootstrap.py \
     --created-site-evidence /tmp/allincms-run/created-site-evidence.json \
     --runbook /tmp/allincms-run/default-theme-bootstrap-runbook.json \
     --bootstrap-evidence /tmp/allincms-run/default-theme-bootstrap-evidence.json \
     --output-dir /tmp/allincms-run/default-theme-bootstrap-applied \
     --fail-on-invalid
   ```

   A valid bootstrap only proves the default theme foundation is usable and public paths are non-empty. It does not replace source-confirmed page copy, site-info save, taxonomy, product/post schema capture, sample upload, batch upload, forms/media/settings, or launch acceptance. Use `created-site-evidence.after-default-theme-bootstrap.json` as the next `--created-site-evidence` input; do not continue from the stale pre-bootstrap evidence after the public site was blank.

   If the package, confirmation, execution plan, and artifact readiness paths are available, let the same helper immediately rebuild the local post-create preparation from the refreshed evidence:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/apply_default_theme_bootstrap.py \
     --created-site-evidence /tmp/allincms-run/created-site-evidence.json \
     --runbook /tmp/allincms-run/default-theme-bootstrap-runbook.json \
     --bootstrap-evidence /tmp/allincms-run/default-theme-bootstrap-evidence.json \
     --output-dir /tmp/allincms-run/default-theme-bootstrap-applied \
     --prepare-created-site-schema-capture \
     --artifact-readiness /tmp/allincms-run/execution/confirmed-artifacts/artifact-readiness.json \
     --package /tmp/allincms-run/source-site-package.json \
     --confirmation /tmp/allincms-run/execution/confirmation-record.json \
     --execution-plan /tmp/allincms-run/execution/confirmed-site-execution-plan.json \
     --fail-on-invalid
   ```

   After this chained path, follow `artifacts.sourceNextStageHandoff` from the apply summary instead of manually rerunning stale handoffs.

   If a source execution status is already blocked at `pages_site_info_handoff`, `taxonomy_execution_handoff`, or another post-create boundary, regenerate the next-stage handoff with the bootstrap artifacts so it emits `apply_default_theme_bootstrap.py` before later preparation:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_source_next_stage.py \
     --status /tmp/allincms-run/source-execution-status.json \
     --created-site-evidence /tmp/allincms-run/created-site-evidence.json \
     --default-theme-bootstrap-runbook /tmp/allincms-run/default-theme-bootstrap-runbook.json \
     --default-theme-bootstrap-evidence /tmp/allincms-run/default-theme-bootstrap-evidence.json \
     --output /tmp/allincms-run/source-next-stage-handoff.after-default-theme-bootstrap.json \
     --output-dir /tmp/allincms-run/next-stage
   ```

   After authorized pages/site-info browser actions run and redacted execution evidence is captured, validate and apply that evidence before continuing:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/apply_pages_site_info_execution.py \
     --package /tmp/allincms-run/source-site-package.json \
     --confirmation /tmp/allincms-run/execution/confirmation-record.json \
     --execution-plan /tmp/allincms-run/execution/confirmed-site-execution-plan.json \
     --artifact-readiness /tmp/allincms-run/execution/confirmed-artifacts/artifact-readiness.json \
     --create-site-handoff /tmp/allincms-run/execution/confirmed-create-site-handoff.json \
     --created-site-binding /tmp/allincms-run/created-site-schema-capture/created-site-artifact-binding.json \
     --pages-site-info-handoff /tmp/allincms-run/created-site-schema-capture/pages-site-info/pages-site-info-browser-handoff.json \
     --pages-site-info-evidence /tmp/allincms-run/pages-site-info-execution-evidence.json \
     --taxonomy-handoff /tmp/allincms-run/created-site-schema-capture/taxonomy/taxonomy-execution-handoff.json \
     --schema-capture-handoff /tmp/allincms-run/created-site-schema-capture/schema-capture-handoff.json \
     --output-dir /tmp/allincms-run/pages-site-info-applied
   ```

   Follow the refreshed `source-execution-status.after-pages-site-info.json`; a valid pages/site-info stage does not skip taxonomy, schema, sample, batch, launch, or cleanup gates.

   After authorized taxonomy create/map actions run and redacted taxonomy evidence is captured, validate and apply it before schema or batch work. Prefer the generated `taxonomy/taxonomy-evidence-bundle/evidence-bundle.json`: fill its `taxonomy-execution-evidence.filled.json`, then run the bundle's validation and apply commands. The direct apply command is:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/apply_taxonomy_execution.py \
     --package /tmp/allincms-run/source-site-package.json \
     --confirmation /tmp/allincms-run/execution/confirmation-record.json \
     --execution-plan /tmp/allincms-run/execution/confirmed-site-execution-plan.json \
     --artifact-readiness /tmp/allincms-run/execution/confirmed-artifacts/artifact-readiness.json \
     --create-site-handoff /tmp/allincms-run/execution/confirmed-create-site-handoff.json \
     --created-site-binding /tmp/allincms-run/created-site-schema-capture/created-site-artifact-binding.json \
     --pages-site-info-handoff /tmp/allincms-run/created-site-schema-capture/pages-site-info/pages-site-info-browser-handoff.json \
     --pages-site-info-validation /tmp/allincms-run/pages-site-info-applied/pages-site-info-execution-validation.json \
     --taxonomy-handoff /tmp/allincms-run/created-site-schema-capture/taxonomy/taxonomy-execution-handoff.json \
     --taxonomy-evidence /tmp/allincms-run/taxonomy-execution-evidence.json \
     --schema-capture-handoff /tmp/allincms-run/created-site-schema-capture/schema-capture-handoff.json \
     --output-dir /tmp/allincms-run/taxonomy-applied
   ```

   Feed the resulting `taxonomy-execution-validation.json` into manifest readiness, schema/sample status, and batch preparation whenever products/posts carry taxonomy fields.

   Use the individual binding command only when debugging:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/bind_created_site_to_artifacts.py \
     --artifact-readiness /tmp/allincms-run/confirmed-artifacts/artifact-readiness.json \
     --created-site-evidence /tmp/allincms-run/created-site-evidence.json \
     --output-dir /tmp/allincms-run/created-site-bound-artifacts \
     --output /tmp/allincms-run/created-site-artifact-binding.json
   ```

   This step is local-only. It must keep `schemaVerified: false`; products and posts still need separate save-request capture, schema binding, sample upload, and frontend verification. If you run this debug command, point its `--output` at the same path the downstream apply/schema-capture step reads as `--created-site-binding` (the orchestrator writes `created-site-artifact-binding.json` under its `--output-dir`); otherwise the later apply step will not find the binding.
21. Build a schema-capture handoff for the bound draft manifests:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/build_schema_capture_handoff.py \
     --created-site-binding /tmp/allincms-run/created-site-artifact-binding.json \
     --created-site-evidence /tmp/allincms-run/created-site-evidence.json \
     --output-dir /tmp/allincms-run/schema-capture \
     --output /tmp/allincms-run/schema-capture-handoff.json
   ```

   The handoff is local preparation only. It does not create probes, save, publish, upload, or authorize browser mutations. If it reports `needs_readonly_content_preflight` for posts or products, first inspect that content type's list/edit fields and regenerate evidence before preparing create-probe authorization. Do not let products field proof stand in for posts, or posts proof stand in for products.

   When a read-only refresh evidence file exists for the missing content type, merge it into the created-site evidence and rebuild the handoff:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/merge_content_type_preflight.py \
     --created-evidence /tmp/allincms-run/created-site-evidence.json \
     --refresh-evidence /tmp/allincms-run/posts-readonly-evidence.json \
     --content-type posts \
     --output /tmp/allincms-run/created-site-evidence.posts-preflight.json
   python3 skills/allincms-bulk-content-upload/scripts/build_schema_capture_handoff.py \
     --created-site-binding /tmp/allincms-run/created-site-artifact-binding.json \
     --created-site-evidence /tmp/allincms-run/created-site-evidence.posts-preflight.json \
     --output-dir /tmp/allincms-run/schema-capture \
     --output /tmp/allincms-run/schema-capture-handoff.json
   ```

   The refresh evidence must be same-site `existing_site_selected` evidence and must list the current site key in `existingSiteKeysBeforeCreate`; otherwise the merge must fail.

   As schema-capture artifacts accumulate, refresh the per-content-type progress queue instead of inferring readiness from the newest file:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/summarize_schema_capture_progress.py \
     --schema-capture-handoff /tmp/allincms-run/schema-capture-handoff.json \
     --create-evidence products=/tmp/allincms-run/schema-capture/products-create-evidence.json \
     --save-handoff products=/tmp/allincms-run/schema-capture/products-save-handoff.json \
     --save-runbook products=/tmp/allincms-run/schema-capture/products-save-runbook.json \
     --save-capture products=/tmp/allincms-run/schema-capture/products-save-capture-evidence.json \
     --base-run-evidence products=/tmp/allincms-run/schema-capture/products-after-save-capture.json \
     --schema-manifest products=/tmp/allincms-run/products-schema-verified-manifest.json \
     --output /tmp/allincms-run/schema-capture-progress.json
   ```

   Treat `results[].status` as the current boundary for each content type. `schema_manifest_ready` means the next step is one manifest sample runbook, not batch upload.

   After one authorized create-probe stage has produced redacted create evidence and a concrete edit URL, prepare the save-capture handoff/runbook locally:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_schema_save_capture.py \
     --schema-capture-handoff /tmp/allincms-run/schema-capture-handoff.json \
     --content-type products \
     --create-evidence /tmp/allincms-run/schema-capture/products-create-evidence.json \
     --output-dir /tmp/allincms-run/schema-capture/products-save-prep
   ```

   This writes a save handoff, save runbook, and refreshed schema-capture progress. It does not save the probe. Request `save_probe` action-time authorization and run the pre-mutation gate before executing the runbook.
22. Normalize posts/products source content into a manifest JSON. If the run used `export_confirmed_site_artifacts.py`, start from the bound manifest paths in `/tmp/allincms-run/created-site-bound-artifacts/` after new-site creation, or from `/tmp/allincms-run/confirmed-artifacts/products-draft-manifest.json` and `/tmp/allincms-run/confirmed-artifacts/posts-draft-manifest.json` only when an existing site key was already passed at export time. For media, themes, routes, or forms, use the exported plan JSON only as source-confirmed planning; first capture the real request and build a dedicated validator before JSON replay.
23. Run local posts/products manifest validation before upload:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/validate_manifest.py path/to/manifest.json
   ```

   Use draft manifest validation while source content is being normalized. Before any live upload or replay, run the stricter schema gate:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/validate_manifest.py \
     --require-schema-verified path/to/manifest.json
   ```

   This requires `schemaVerified: true`, a captured `fieldMapping`, and a `payloadTemplate` from the current site's real save request.

   Do not hand-edit `schemaVerified`, `fieldMapping`, or `payloadTemplate`. After validating one save-capture evidence file for the exact site/content type, bind it into the draft manifest:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/apply_save_capture_to_manifest.py \
     --manifest /tmp/allincms-run/confirmed-artifacts/products-draft-manifest.json \
     --save-capture-evidence /tmp/allincms-products-save-capture-evidence.json \
     --base-run-evidence /tmp/allincms-products-run-evidence-after-save-capture.json \
     --output /tmp/allincms-run/products-schema-verified-manifest.json
   python3 skills/allincms-bulk-content-upload/scripts/validate_manifest.py \
     --require-schema-verified \
     /tmp/allincms-run/products-schema-verified-manifest.json
   ```

   Repeat separately for posts. A schema-verified manifest still only proves local schema binding; sample upload/publish and backend/frontend verification remain required before batch upload.

   Prefer the combined local preparation when save-capture evidence already exists:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_schema_manifest_sample.py \
     --manifest /tmp/allincms-run/created-site-bound-artifacts/products-draft-manifest.bound-created-site.json \
     --save-capture-evidence /tmp/allincms-run/schema-capture/products-save-capture-evidence.json \
     --base-run-evidence /tmp/allincms-run/schema-capture/products-after-save-capture.json \
     --schema-capture-handoff /tmp/allincms-run/schema-capture-handoff.json \
     --package /tmp/allincms-run/source-site-package.json \
     --confirmation /tmp/allincms-run/execution/confirmation-record.json \
     --execution-plan /tmp/allincms-run/execution/confirmed-site-execution-plan.json \
     --artifact-readiness /tmp/allincms-run/execution/confirmed-artifacts/artifact-readiness.json \
     --create-site-handoff /tmp/allincms-run/execution/confirmed-create-site-handoff.json \
     --created-site-binding /tmp/allincms-run/created-site-schema-capture/created-site-artifact-binding.json \
     --pages-site-info-handoff /tmp/allincms-run/created-site-schema-capture/pages-site-info/pages-site-info-browser-handoff.json \
     --pages-site-info-validation /tmp/allincms-run/pages-site-info-applied/pages-site-info-execution-validation.json \
     --taxonomy-validation /tmp/allincms-run/taxonomy-applied/taxonomy-execution-validation.json \
     --output-dir /tmp/allincms-run/schema-capture/products-schema-manifest-sample
   ```

   This creates the schema-verified manifest, upload readiness report, sample runbook, sample evidence bundle, refreshed schema-capture progress, and, when source-status inputs are supplied, `source-execution-status.after-schema-manifest.json`. It does not upload or publish the sample; request sample action-time authorization and pass the sample gate before browser execution. Follow the refreshed source status instead of assuming sample upload is next; pages/site-info, taxonomy, or schema-capture blockers can still be earlier.

   When products and posts are prepared in separate schema-capture passes, preserve the readiness already generated for the previous content type. Pass each prior readiness file with `--existing-upload-readiness` when preparing the next schema manifest. Later apply helpers and launch acceptance accept repeated `--upload-readiness` flags; pass every products/posts readiness file so `sourceExecutionStatus.contentTypeCoverage.uploadReadiness` proves both content types instead of only the most recent one.

   When more than one posts/products manifest exists, summarize readiness explicitly before upload planning:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/make_manifest_upload_readiness.py \
     /tmp/products-manifest.json /tmp/posts-manifest.json \
     --output /tmp/allincms-upload-readiness-report.json
   ```

   `overallStatus: blocked` is expected until every manifest passes the schema gate for its own content type.

24. Upload one sample item first.
   For source-generated schema-verified manifests, prepare and validate this stage explicitly:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/build_manifest_sample_upload_runbook.py \
     --manifest /tmp/allincms-run/products-schema-verified-manifest.json \
     --target https://workspace.laicms.com/current-site-key/products \
     --authorization-output /tmp/allincms-authorization-products-sample.json \
     --output /tmp/allincms-products-sample-runbook.json
   python3 skills/allincms-bulk-content-upload/scripts/validate_manifest_sample_upload_evidence.py \
     /tmp/allincms-products-sample-evidence.json \
     --manifest /tmp/allincms-run/products-schema-verified-manifest.json \
     --output /tmp/allincms-products-sample-validation.json
   python3 skills/allincms-bulk-content-upload/scripts/apply_manifest_sample_upload.py \
     --manifest /tmp/allincms-run/products-schema-verified-manifest.json \
     --sample-evidence /tmp/allincms-products-sample-evidence.json \
     --package /tmp/allincms-run/source-site-package.json \
     --confirmation /tmp/allincms-run/execution/confirmation-record.json \
     --execution-plan /tmp/allincms-run/execution/confirmed-site-execution-plan.json \
     --artifact-readiness /tmp/allincms-run/execution/confirmed-artifacts/artifact-readiness.json \
     --create-site-handoff /tmp/allincms-run/execution/confirmed-create-site-handoff.json \
     --created-site-binding /tmp/allincms-run/created-site-schema-capture/created-site-artifact-binding.json \
     --pages-site-info-handoff /tmp/allincms-run/created-site-schema-capture/pages-site-info/pages-site-info-browser-handoff.json \
     --pages-site-info-validation /tmp/allincms-run/pages-site-info-applied/pages-site-info-execution-validation.json \
     --taxonomy-validation /tmp/allincms-run/taxonomy-applied/taxonomy-execution-validation.json \
     --schema-capture-handoff /tmp/allincms-run/created-site-schema-capture/schema-capture-handoff.json \
     --upload-readiness /tmp/allincms-run/schema-capture/products-schema-manifest-sample/products-upload-readiness.json \
     --output-dir /tmp/allincms-run/manifest-sample-applied
   ```

   The runbook is local preparation only. It restricts the browser mutation to one `sampleSlug`; it must not process the rest of the manifest, clean probes, or touch themes/routes/settings. The evidence must prove save, publish, backend state, frontend detail, body, media or accepted no-media note, and no blocking issues.
   If a sample evidence bundle exists, fill `manifest-sample-evidence.filled.json`, run its validation command, then run its apply command instead of hand-writing sample evidence from memory.
   Use `apply_manifest_sample_upload.py` after browser evidence is captured so the source execution dashboard advances explicitly to `batch_upload`; do not treat a standalone validation report as the whole source-stage transition.
25. Verify backend persisted state and frontend route.
26. Clean probe/test items only after explicit cleanup authorization.
27. Batch upload with progress tracking and duplicate-slug handling.
   Prefer the local batch preparation orchestrator. It validates the same sample evidence against the schema-verified manifest, seeds the progress log, and builds the non-executable batch runbook plus fillable evidence bundle:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_batch_upload_publish.py \
     --run-evidence /tmp/allincms-run-evidence-after-save-capture.json \
     --manifest /tmp/allincms-run/products-schema-verified-manifest.json \
     --sample-evidence /tmp/allincms-products-sample-evidence.json \
     --output-dir /tmp/allincms-run/batch-products \
     --target https://workspace.laicms.com/current-site-key/products \
     --authorization-output /tmp/allincms-authorization-products-batch.json
   ```

   Then request action-time batch authorization, create the authorization record from the runbook template, and run the pre-mutation gate. The runbook's `preMutationGateCommand` must include the same sample evidence. Fill the bundle's `batch-upload-publish-evidence.filled.json`, final-audit command, validation command, and apply command after the real browser batch run instead of hand-writing batch evidence from memory:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/check_pre_mutation_gate.py \
     --action batch_upload \
     --preflight /tmp/allincms-run-evidence-after-save-capture.json \
     --authorization /tmp/allincms-authorization-products-batch.json \
     --sample-evidence /tmp/allincms-products-sample-evidence.json
   ```
   After the authorized batch browser run, apply the redacted batch evidence back into source execution status. If the generated batch evidence bundle was used, prefer routing through `prepare_source_next_stage.py --batch-evidence-bundle /tmp/.../evidence-bundle.json`; it derives the filled evidence, manifest, base run evidence, and `final-audit-report.redacted.json` paths before emitting `apply_batch_upload_publish.py`.

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/apply_batch_upload_publish.py \
     --batch-evidence /tmp/allincms-batch-upload-evidence.json \
     --manifest /tmp/allincms-run/products-schema-verified-manifest.json \
     --base-run-evidence /tmp/allincms-run-evidence-after-save-capture.json \
     --frontend-audit-report /tmp/allincms-final-audit-report.json \
     --package /tmp/allincms-run/source-site-package.json \
     --confirmation /tmp/allincms-run/execution/confirmation-record.json \
     --execution-plan /tmp/allincms-run/execution/confirmed-site-execution-plan.json \
     --artifact-readiness /tmp/allincms-run/execution/confirmed-artifacts/artifact-readiness.json \
     --create-site-handoff /tmp/allincms-run/execution/confirmed-create-site-handoff.json \
     --created-site-binding /tmp/allincms-run/created-site-schema-capture/created-site-artifact-binding.json \
     --pages-site-info-handoff /tmp/allincms-run/created-site-schema-capture/pages-site-info/pages-site-info-browser-handoff.json \
     --pages-site-info-validation /tmp/allincms-run/pages-site-info-applied/pages-site-info-execution-validation.json \
     --schema-capture-handoff /tmp/allincms-run/created-site-schema-capture/schema-capture-handoff.json \
     --upload-readiness /tmp/allincms-run/schema-capture/products-schema-manifest-sample/products-upload-readiness.json \
     --sample-evidence /tmp/allincms-products-sample-evidence.json \
     --output-dir /tmp/allincms-run/batch-applied
   ```

   Use the refreshed `source-execution-status.after-batch-upload.json` before moving to launch acceptance; a standalone batch validation report does not by itself update the source-stage boundary.
28. Publish only after backend and frontend sample verification passes.
29. Bulk verify frontend links, covers, descriptions, body content, status, and broken entries.
30. Before claiming a site-build run is launch-complete, apply `references/launch-acceptance.md`. A complete from-scratch launch requires created-site proof, setup inspection, module capture, theme/page/route launch readiness, static audit, content save/sample proof, schema-verified batch upload, in-scope media/forms/settings proof or explicit deferral, final frontend audit, cleanup, and sedimentation. Local rehearsal success alone is not launch completion.
   Run the executable launch gate when the required artifacts exist:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/validate_launch_acceptance.py \
     --require-created-site \
     --run-evidence /tmp/allincms-run-evidence.json \
     --module-coverage /tmp/allincms-module-coverage.json \
     --upload-readiness /tmp/allincms-upload-readiness-report.json \
     --batch-evidence /tmp/allincms-batch-upload-evidence.json \
     --batch-validation /tmp/allincms-batch-upload-validation.json \
     --forms-media-settings /tmp/allincms-forms-media-settings.json \
     --final-frontend-audit /tmp/allincms-final-frontend-audit-stage-result.json \
     --cleanup-evidence /tmp/allincms-probe-cleanup-evidence.json \
     --round-closeout /tmp/allincms-round-closeout.json
   ```

   If only local rehearsal/stage coverage exists, expect this gate to fail and report the remaining live proof instead of claiming launch completion.
   For source-file driven runs, apply the launch validation back into the source execution dashboard instead of hand-wiring the final status:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/apply_launch_acceptance.py \
     --require-created-site \
     --run-evidence /tmp/allincms-run-evidence.json \
     --module-coverage /tmp/allincms-module-coverage.json \
     --upload-readiness /tmp/allincms-upload-readiness-report.json \
     --batch-evidence /tmp/allincms-batch-upload-evidence.json \
     --batch-validation /tmp/allincms-batch-upload-validation.json \
     --forms-media-settings /tmp/allincms-forms-media-settings.json \
     --final-frontend-audit /tmp/allincms-final-frontend-audit-stage-result.json \
     --cleanup-evidence /tmp/allincms-probe-cleanup-evidence.json \
     --auto-final-closeout \
     --final-closeout-sedimentation updated \
     --final-closeout-sedimentation-note "Recorded final source-run launch proof." \
     --package /tmp/allincms-run/source-site-package.json \
     --confirmation /tmp/allincms-run/execution/confirmation-record.json \
     --execution-plan /tmp/allincms-run/execution/confirmed-site-execution-plan.json \
     --artifact-readiness /tmp/allincms-run/execution/confirmed-artifacts/artifact-readiness.json \
     --create-site-handoff /tmp/allincms-run/execution/confirmed-create-site-handoff.json \
     --created-site-binding /tmp/allincms-run/created-site-schema-capture/created-site-artifact-binding.json \
     --pages-site-info-handoff /tmp/allincms-run/created-site-schema-capture/pages-site-info/pages-site-info-browser-handoff.json \
     --pages-site-info-validation /tmp/allincms-run/pages-site-info-applied/pages-site-info-execution-validation.json \
     --schema-capture-handoff /tmp/allincms-run/created-site-schema-capture/schema-capture-handoff.json \
     --sample-evidence /tmp/allincms-products-sample-evidence.json \
     --output-dir /tmp/allincms-run/launch-acceptance-applied
   ```

   Use the refreshed `source-execution-status.after-launch-acceptance.json`; a standalone launch validation report proves the launch gate result but does not by itself update the source-stage dashboard.
   For source-file driven runs, the lower-level dashboard command remains useful for diagnostics:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/summarize_source_execution_status.py \
     --package /tmp/allincms-run/source-site-package.json \
     --review-packet /tmp/allincms-run/source-package-review-packet.json \
     --confirmation /tmp/allincms-run/confirmation-record.json \
     --execution-plan /tmp/allincms-run/confirmed-site-execution-plan.json \
     --artifact-readiness /tmp/allincms-run/confirmed-artifacts/artifact-readiness.json \
     --create-site-handoff /tmp/allincms-run/confirmed-create-site-handoff.json \
     --pages-site-info-handoff /tmp/allincms-run/pages-site-info/pages-site-info-browser-handoff.json \
     --created-site-binding /tmp/allincms-run/created-site-artifact-binding.json \
     --schema-capture-handoff /tmp/allincms-run/schema-capture-handoff.json \
     --upload-readiness /tmp/allincms-run/upload-readiness.json \
     --sample-evidence /tmp/allincms-products-sample-evidence.json \
     --batch-validation /tmp/allincms-batch-upload-validation.json \
     --launch-acceptance /tmp/allincms-launch-acceptance.json \
     --output /tmp/allincms-source-execution-status.json
   ```

   Treat `currentStage` as the next work boundary. Do not claim the full source-file-to-site goal is done unless this status is `complete` and launch acceptance also passes.
   Key source execution orchestrators now write a `sourceNextStageHandoff` artifact next to the refreshed status. Prefer that artifact from the summary before running any later helper or browser action. If a status was produced by a lower-level diagnostic command without the handoff, prepare one next-stage handoff instead of hand-writing the next command:

   ```bash
   python3 skills/allincms-bulk-content-upload/scripts/prepare_source_next_stage.py \
     --status /tmp/allincms-source-execution-status.json \
     --output /tmp/allincms-source-next-stage-handoff.json \
     --output-dir /tmp/allincms-next-stage
   ```

   If `currentStage=created_site_binding` and the browser proof exists only as a filled created-site evidence bundle, pass `--created-site-evidence-bundle` and `--filled-created-site-evidence-template`; the handoff should emit `apply_created_site_evidence_bundle.py --prepare-created-site-schema-capture` instead of asking you to hand-copy fields into `make_created_site_evidence.py`. If `currentStage=sample_upload` and the browser proof exists in a manifest sample evidence bundle, pass `--sample-evidence-bundle`; the handoff should derive the filled evidence path and manifest before emitting `apply_manifest_sample_upload.py`. If the handoff emits any `localCommand`, inspect placeholders and run it only after the named evidence exists. If it reports `browserWorkRequired=true`, perform the browser work through the stage-specific authorization, pre-mutation gate, and evidence validator. Regenerate source status and use the newly emitted `sourceNextStageHandoff` after each completed, partial, or blocked stage.
31. Run the sedimentation pass now (the what/when contract is stated once in the Operating Rule above): record reusable findings in `references/operational-findings.md` + any affected reference, or explicitly note none after checking; if the user forbade edits, report as `read-only deferred sedimentation` instead.
32. Run the closeout gate before the final response — `scripts/check_round_closeout.py` against the run-summary JSON (commands under "Closeout" below); for a maintenance/planning/validation-only turn with no run-evidence, build a maintenance summary first with `scripts/make_round_maintenance_summary.py`. Report `--sedimentation updated|none` + the main `--round-issue`.
33. Run skill hygiene checks after any skill edit.
34. Leave the frontend list page open for the user.

For frontend rendering QA, run with redaction when the output will be stored as evidence:

```bash
python3 skills/allincms-bulk-content-upload/scripts/audit_frontend_rendering.py \
  --json --redact \
  --timeout 8 --max-bytes 2000000 \
  https://example.web.allincms.com/posts/example-slug
```

After changing this skill package, run:

```bash
PYTHONPYCACHEPREFIX=/tmp/allincms-pycache python3 -m py_compile \
  skills/allincms-bulk-content-upload/scripts/*.py
python3 skills/allincms-bulk-content-upload/scripts/audit_skill_hygiene.py
python3 /Users/tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/allincms-bulk-content-upload
```

Use `PYTHONPYCACHEPREFIX=/tmp/allincms-pycache` for `py_compile` in restricted sandboxes so Python does not try to write bytecode under `~/Library/Caches`.

Before claiming an end-to-end simulation is complete, run:

```bash
python3 skills/allincms-bulk-content-upload/scripts/validate_run_evidence.py path/to/run-evidence.json
python3 skills/allincms-bulk-content-upload/scripts/summarize_run_status.py path/to/run-evidence.json
```

Only claim completion when the summary says `valid: true`, `complete: true`, and `completionGaps: []`. A valid file with `complete: false` is phase evidence, not an achieved site-build/content-upload run.

Before a final response for a browser, rehearsal, or run-evidence round, save the run summary and run closeout:

```bash
python3 skills/allincms-bulk-content-upload/scripts/summarize_run_status.py \
  path/to/run-evidence.json \
  --output /tmp/allincms-run-summary.json
python3 skills/allincms-bulk-content-upload/scripts/check_round_closeout.py \
  --summary /tmp/allincms-run-summary.json \
  --sedimentation updated \
  --note "Recorded reusable platform finding in operational-findings.md." \
  --round-issue "Captured a reusable platform finding and recorded it in the skill."
```

Use `--sedimentation none --note "no reusable skill update needed after checking"` only when the turn changed no skill files and revealed no reusable platform finding or problem after an explicit check. Still pass a `--round-issue` item such as `--round-issue "Checked the turn and found no reusable skill update needed."`

When the run summary emits `nextActionDetails`, prepare the next authorization package from the summary instead of hand-writing JSON:

```bash
python3 skills/allincms-bulk-content-upload/scripts/prepare_next_action_authorization.py \
  /tmp/allincms-run-summary.json \
  --action create_product_probe \
  --preflight /tmp/allincms-existing-site-readonly-evidence.json \
  --expect-missing-authorization-failure \
  --output /tmp/allincms-next-action-authorization-package.json
```

The output is a preparation artifact only. It must keep `preparedOnly: true`, `isUserAuthorization: false`, and an authorization-source placeholder in the command template. Do not run the authorization-record command or mutate LAICMS until the current user provides matching action-time authorization text.

For browser-stage authorization packages, the command must retain `--authorization-source '<paste current user authorization text here>'` even when the package also includes a suggested Chinese authorization sentence. The suggested sentence is for the user to approve or edit; it is not a usable authorization source until the current user provides it in the conversation. Always validate the package with `validate_browser_stage_authorization_package.py` before treating it as ready to request authorization.

For direct capture-plan authorization packages generated by `prepare_capture_authorization.py`, apply the same placeholder rule. `authorizationRecordCommand` must retain `--authorization-source '<paste current user authorization text here>'`; `suggestedAuthorizationText` must remain only user-facing guidance. Validate each package with `validate_capture_authorization_package.py` before asking for action-time authorization, and reject any package whose command already embeds helper-generated text such as `授权 Codex`.

For a `module_interface_capture` browser-stage package, bind the validator to the current packet, preflight, and capture plan:

```bash
python3 skills/allincms-bulk-content-upload/scripts/validate_browser_stage_authorization_package.py \
  /tmp/allincms-browser-stage-authorization-package.json \
  --packet-json /tmp/allincms-next-browser-stage-packet.json \
  --preflight /tmp/allincms-existing-site-readonly-evidence.json \
  --capture-plan /tmp/allincms-real-site-module-capture-plan.json
```

This prevents a valid-looking single-action package from drifting away from the current module/action plan. Passing this validator still means "safe to ask the user for action-time authorization", not "safe to run".

Before asking the user to authorize the next real browser action, wrap the validated pieces into one handoff:

```bash
python3 skills/allincms-bulk-content-upload/scripts/make_next_browser_action_handoff.py \
  --package /tmp/allincms-browser-stage-authorization-package.json \
  --packet-json /tmp/allincms-next-browser-stage-packet.json \
  --preflight /tmp/allincms-existing-site-readonly-evidence.json \
  --capture-plan /tmp/allincms-real-site-module-capture-plan.json \
  --output /tmp/allincms-next-browser-action-handoff.json
python3 skills/allincms-bulk-content-upload/scripts/validate_next_browser_action_handoff.py \
  /tmp/allincms-next-browser-action-handoff.json
```

Use the handoff to present the exact target, action, stop condition, required proof, suggested authorization text, authorization-record command, and pre-mutation gate. The handoff is still preparation only; it does not grant permission to run commands or operate the browser.
In the handoff JSON, the stop condition field is `stopAfter`. Do not invent `stopCondition` or treat a missing `stopCondition` key as missing proof; read `stopAfter`, `suggestedAuthorizationText`, and `authorizationRecordCommand --expected-result` together.
Before asking the user for action-time authorization, write a readiness report so stale read-only evidence blocks the request early:

```bash
python3 skills/allincms-bulk-content-upload/scripts/make_handoff_readiness.py \
  /tmp/allincms-next-browser-action-handoff.json \
  --output /tmp/allincms-next-browser-action-readiness.json \
  --fail-on-blocked
```

Only ask for authorization when the report says `status: ready_to_request_authorization`. If it says `blocked_refresh_readonly_evidence`, refresh read-only evidence and rebuild the handoff first.

After generating a real-site module capture plan, create the full local checklist with:

```bash
python3 skills/allincms-bulk-content-upload/scripts/prepare_all_capture_authorizations.py \
  /tmp/allincms-real-site-module-capture-plan.json \
  --preflight /tmp/allincms-existing-site-readonly-evidence.json \
  --output-dir /tmp/allincms-capture-authorization-packages \
  --summary-output /tmp/allincms-capture-authorization-packages/summary.json
python3 skills/allincms-bulk-content-upload/scripts/validate_all_capture_authorizations.py \
  /tmp/allincms-capture-authorization-packages/summary.json \
  --plan-json /tmp/allincms-real-site-module-capture-plan.json
```

Use the resulting `summary.json` to choose exactly one next action. A valid package set means every action has a safe preparation record; it does not grant permission to run any command and does not prove JSON replay readiness. Continue to use `prepare_browser_stage_authorization.py` for the single selected browser-stage packet before asking for action-time authorization.
The package-set summary uses `count` and `items`, not `packageCount` or `packages`. Inspect `items[].module`, `items[].action`, `items[].authorizationAction`, `items[].gateSupported`, and `items[].package` when selecting the next action.

For a documentation-only, helper-script, request-analysis, or validation-only round with no current run-evidence file, create a maintenance summary and run the same closeout gate:

```bash
python3 skills/allincms-bulk-content-upload/scripts/make_round_maintenance_summary.py \
  --output /tmp/allincms-maintenance-summary.json \
  --sedimentation updated \
  --note "Recorded reusable closeout finding in operational-findings.md." \
  --changed-files "skills/allincms-bulk-content-upload/SKILL.md,skills/allincms-bulk-content-upload/references/operational-findings.md" \
  --round-issue "Closeout wording allowed reusable issues to remain only in chat."
python3 skills/allincms-bulk-content-upload/scripts/check_round_closeout.py \
  --summary /tmp/allincms-maintenance-summary.json \
  --sedimentation updated \
  --note "Recorded reusable closeout finding in operational-findings.md." \
  --changed-files "skills/allincms-bulk-content-upload/SKILL.md,skills/allincms-bulk-content-upload/references/operational-findings.md" \
  --round-issue "Closeout wording allowed reusable issues to remain only in chat."
```

Do not use a maintenance summary to claim site creation, launch, upload, publish, cleanup, or frontend persistence.

After creating a site and auditing static frontend routes plus backend launch state, keep the proof in one evidence file when possible by passing generated frontend and launch evidence into `make_created_site_evidence.py`:

```bash
python3 skills/allincms-bulk-content-upload/scripts/make_created_site_evidence.py \
  --preflight /tmp/allincms-create-site-preflight.json \
  --created-site-key new-site-key \
  --content-type products \
  --list-columns "媒体,名称,Slug,描述,排序,状态,分类,标签,创建时间" \
  --edit-fields "name input,slug input,description textarea,body editor,publish" \
  --site-card-evidence "site list shows new-site-key card" \
  --backend-evidence "dashboard opens at https://workspace.laicms.com/new-site-key/dashboard" \
  --frontend-evidence "frontend opens at https://new-site-key.web.allincms.com" \
  --site-info-evidence "site-info inspected" \
  --domains-evidence "domains inspected" \
  --themes-evidence "themes inspected" \
  --routes-evidence "routes inspected" \
  --forms-evidence "forms inspected" \
  --tracking-evidence "tracking inspected" \
  --module-routes "/new-site-key/dashboard,/new-site-key/products,/new-site-key/posts,/new-site-key/media,/new-site-key/themes,/new-site-key/routes,/new-site-key/forms,/new-site-key/site-info,/new-site-key/tracking,/new-site-key/domains" \
  --submitted-fields name,description \
  --authorization-source "current user explicitly authorizes create site at https://workspace.laicms.com/sites for new-site-key" \
  --frontend-rendering-evidence /tmp/allincms-frontend-rendering-evidence.json \
  --launch-readiness-evidence /tmp/allincms-launch-readiness-evidence.json \
  --output /tmp/allincms-created-site-evidence.json
```

When the user asked to start from site creation, use the stricter summary gate:

```bash
python3 skills/allincms-bulk-content-upload/scripts/summarize_run_status.py \
  --require-created-site path/to/run-evidence.json
```

This rejects an existing-site run as proof of a from-scratch build.

For a one-command local-only full dry run that does not touch LAICMS, run:

```bash
python3 skills/allincms-bulk-content-upload/scripts/run_full_rehearsal.py \
  --existing-site-keys old-site-a,old-site-b \
  --site-key-evidence "old-site-a from backend url route https://workspace.laicms.com/old-site-a/dashboard;old-site-b from backend url route https://workspace.laicms.com/old-site-b/dashboard" \
  --output-dir /tmp/allincms-full-rehearsal
```

This orchestrates the create-site dry run, module interface planning dry run, probe lifecycle dry run, manifest/schema-gate rehearsal, full output validation, next-stage handoff generation, handoff safety validation, launch proof planning, browser execution planning, execution ledger generation, next-stage packet generation, simulated first-stage result application, and plan/ledger/packet/result validation. It writes `full-e2e/`, `next-capture-handoff/handoff.json`, `launch-plan.json`, `browser-execution-plan.json`, `browser-execution-ledger.json`, `next-browser-stage-packet.json`, stage-result and ledger artifacts through static audit, content-probe creation, save-request capture, and `rehearsal-summary.json`. It proves local helper compatibility and evidence-state modeling, not remote LAICMS persistence.

After a stage result is applied, generate a fresh packet from the updated ledger before continuing. The first post-refresh packet should normally be `create_site_submit`, target `https://workspace.laicms.com/sites`, require authorization, and use the `/sites` target directly because no `{realSiteKey}` exists before site creation.

Use `ledger.nextStageId` as the authoritative next-stage pointer after applying a browser stage result. Do not infer readiness by filtering `stages` for `status == "ready"`; some ledgers intentionally expose the ready stage through `nextStageId` and derived counts while stage entries remain dependency records. Build the next packet from the ledger instead of hand-picking stages.

Stage results must include auditable redacted evidence pointers, not free text such as `done`, `ok`, or `verified`. Use pointers like `local://redacted-scan.json`, `/tmp/allincms-run/stage-result.json`, `./run-evidence/stage.json`, or a redacted backend/frontend URL. Proof labels explain what was checked; evidence pointers identify where the proof can be inspected.

Packet `ledgerUpdate.commandTemplate` must be tied to the actual generated ledger, packet, stage-result, and updated-ledger paths for the current run. Do not copy an older packet whose command still points at another `/tmp/allincms-full-rehearsal...` directory. If a packet was built without paths and contains `{ledgerPath}`, `{packetPath}`, `{stageResultPath}`, or `{updatedLedgerPath}`, replace those placeholders with the current run files before applying a stage result.

When applying a browser stage result or regenerating a packet, use the exact `ledgerUpdate.commandTemplate`, `operatorHandoff.ledgerApplyCommand`, or the helper's `--help` output. Do not infer CLI flags from nearby scripts. In particular, `apply_browser_stage_result.py` does not provide a `--json` flag, and `build_browser_stage_packet.py` takes the ledger JSON as a positional argument.

Each packet carries `remoteMutationExpectation`: `must`, `may`, or `must_not`. When a completed packet says `must`, the stage result must set `browserStageMutatedRemote: true`. For `must_not` stages such as read-only refresh, setup inspection, static audits, manifest gates, and final QA, the result must keep it false. For `may` stages, record true only if the authorized browser action actually changed remote state.

Before running the browser stage, create a local evidence bundle from the packet so proof is captured as files instead of staying in chat:

```bash
python3 skills/allincms-bulk-content-upload/scripts/prepare_browser_stage_evidence_bundle.py \
  --packet-json /tmp/allincms-full-rehearsal/next-browser-stage-packet.json \
  --output-dir /tmp/allincms-stage-proof
```

The bundle is scaffolding only. It does not authorize browser actions and does not prove persistence. Fill it with redacted browser, network, backend, and frontend proof, then use those pointers when creating the stage result.

Validate the bundle before using it for a real browser stage or ledger apply:

```bash
python3 skills/allincms-bulk-content-upload/scripts/validate_browser_stage_evidence_bundle.py \
  /tmp/allincms-stage-proof \
  --packet-json /tmp/allincms-full-rehearsal/next-browser-stage-packet.json
```

Before executing an authorization-required browser packet, prepare the local authorization package when supported:

```bash
python3 skills/allincms-bulk-content-upload/scripts/prepare_browser_stage_authorization.py \
  /tmp/allincms-full-rehearsal/next-browser-stage-packet-after-first-stage.json \
  --preflight /tmp/allincms-create-site-preflight.json \
  --authorization-output /tmp/allincms-authorization-create-site.json
```

The package only creates command templates and suggested wording. It is not user authorization. If `gateSupported` is false, stop and extend the helper/gate before mutating that stage.

Validate the prepared package against the current packet and preflight before asking the user to authorize or before running the generated commands:

```bash
python3 skills/allincms-bulk-content-upload/scripts/validate_browser_stage_authorization_package.py \
  /tmp/allincms-browser-stage-authorization-package.json \
  --packet-json /tmp/allincms-full-rehearsal/next-browser-stage-packet-after-first-stage.json \
  --preflight /tmp/allincms-create-site-preflight.json
```

This validation must pass with the authorization-source placeholder still present. Only after the user provides fresh action-time authorization should `make_authorization_record.py` write the authorization JSON and `check_pre_mutation_gate.py` unlock the real browser mutation.

If the next step is queue/gap-audit planning, convert the validated browser-stage authorization package into readiness with a helper instead of hand-writing JSON:

```bash
python3 skills/allincms-bulk-content-upload/scripts/make_browser_stage_authorization_readiness.py \
  /tmp/allincms-browser-stage-authorization-package.json \
  --packet-json /tmp/allincms-full-rehearsal/next-browser-stage-packet-after-setup-pages.json \
  --preflight /tmp/allincms-created-site-evidence.json \
  --capture-plan /tmp/allincms-full-rehearsal/full-e2e/03-module-interface-plan/module-capture-plan.json \
  --output /tmp/allincms-browser-stage-authorization-readiness.json
```

Use the generated readiness as `make_browser_stage_queue.py --readiness`. If it reports `blocked_refresh_readonly_evidence`, refresh read-only evidence and rebuild the package before asking for authorization.

For `module_interface_capture`, pass the current capture plan and, after the first captured module/action, the current coverage file so the helper selects only the next missing `module:action`:

```bash
python3 skills/allincms-bulk-content-upload/scripts/prepare_browser_stage_authorization.py \
  /tmp/allincms-full-rehearsal/next-browser-stage-packet-after-setup-pages.json \
  --preflight /tmp/allincms-created-site-evidence.json \
  --authorization-output /tmp/allincms-authorization-module-capture.json \
  --capture-plan /tmp/allincms-full-rehearsal/full-e2e/03-module-interface-plan/module-capture-plan.json \
  --coverage /tmp/allincms-full-rehearsal/module-capture-coverage-after-one-stage.json
```

If `commandsSuppressed` is true, the packet came from a simulated target and must be rebuilt from real browser evidence before LAICMS mutation. Do not use `--allow-command-output` except for local helper tests.

If a module-capture authorization package for a real browser run still contains `{realSiteKey}` in `target` or `suggestedAuthorizationText`, treat it as a template-only handoff. Stop before clicking create/save controls, rebuild the capture plan or authorization package from current real-site evidence, and require the package to target the concrete current backend route before any action-time authorization can be recorded.

For `theme_page_route_launch`, never ask for or prepare permission for the aggregate stage. Prepare one launch sub-action at a time from real browser evidence:

```bash
python3 skills/allincms-bulk-content-upload/scripts/prepare_browser_stage_authorization.py \
  /tmp/allincms-full-rehearsal/next-browser-stage-packet-after-module-capture.json \
  --preflight /tmp/allincms-created-site-evidence.json \
  --authorization-output /tmp/allincms-authorization-save-design.json \
  --launch-action save_design \
  --launch-target https://workspace.laicms.com/{realSiteKey}/themes/{themeId}/{pageId}/design \
  --launch-target-identifier "{themeId}/{pageId} design"
```

Replace placeholders with the exact current backend URL and identifiers observed in the browser before mutating. Supported launch actions are `create_theme_page`, `save_design`, `publish_design`, `enable_theme_page`, `set_homepage`, `create_route`, and `bind_route`. If the target still contains placeholders, the helper suppresses copyable mutation commands; use the output as a template only.

For content probe lifecycle browser packets, prepare one content action at a time. `--content-type` is required because a templated packet cannot prove whether the current module is posts, products, or forms:

```bash
python3 skills/allincms-bulk-content-upload/scripts/prepare_browser_stage_authorization.py \
  /tmp/allincms-full-rehearsal/next-browser-stage-packet-after-static-audit.json \
  --preflight /tmp/allincms-created-site-evidence.json \
  --authorization-output /tmp/allincms-authorization-product-probe.json \
  --content-type products \
  --content-target https://workspace.laicms.com/{realSiteKey}/products \
  --content-target-identifier "Codex Probe - Delete Me product draft"
```

Use the same helper for later packets by changing the packet path and exact target: `save_request_capture` and `publish_sample_verify` normally target the proven edit URL, while `cleanup_probes` may target the list URL or edit URL depending on the cleanup action captured. If the target still contains `{realSiteKey}`, `{contentId}`, or another placeholder, the helper suppresses copyable commands and the output is only a template. Do not treat probe creation authorization as permission to save, publish, batch upload, or cleanup.

For `batch_upload_publish`, prepare one batch action only after the current site/content type has passed manifest schema gate and sample verification:

```bash
python3 skills/allincms-bulk-content-upload/scripts/prepare_browser_stage_authorization.py \
  /tmp/allincms-full-rehearsal/next-browser-stage-packet-after-manifest-gate.json \
  --preflight /tmp/allincms-created-site-evidence.json \
  --authorization-output /tmp/allincms-authorization-batch-upload.json \
  --content-type products \
  --content-target https://workspace.laicms.com/{realSiteKey}/products \
  --content-target-identifier "products manifest batch"
```

The batch gate requires schema gate pass, sample verification, progress log, and frontend detail audit fields. It currently supports posts/products content batches only. Do not fold forms, media uploads, site settings, route changes, or cleanup into the batch authorization.

Before the real browser batch stage, build and inspect the runbook:

```bash
python3 skills/allincms-bulk-content-upload/scripts/build_batch_upload_publish_runbook.py \
  --run-evidence /tmp/allincms-run-evidence-after-publish-sample.json \
  --manifest /tmp/allincms-schema-verified-manifest.json \
  --target https://workspace.laicms.com/{realSiteKey}/products \
  --target-identifier "products manifest batch" \
  --authorization-output /tmp/allincms-authorization-batch-upload.json \
  --output /tmp/allincms-batch-upload-runbook.json
```

After the browser batch run, validate the redacted evidence before using it to unlock forms/settings or final audit:

```bash
python3 skills/allincms-bulk-content-upload/scripts/validate_batch_upload_publish_evidence.py \
  /tmp/allincms-batch-upload-evidence.json \
  --manifest /tmp/allincms-schema-verified-manifest.json \
  --base-run-evidence /tmp/allincms-run-evidence-after-publish-sample.json \
  --frontend-audit-report /tmp/allincms-final-audit-report.json \
  --output /tmp/allincms-batch-upload-validation.json
```

The evidence must prove one progress entry per manifest slug, `saveStatus: ok`, `publishStatus: ok`, backend/frontend verification, cover/media verification, body verification, and an empty frontend detail audit issue list. HTTP 200 without DOM/rich-text/image proof is not enough.

For `forms_media_settings`, never ask for or prepare permission for the aggregate stage. Prepare one settings, media, form, domain, tracking, or theme setup sub-action at a time from real browser evidence:

```bash
python3 skills/allincms-bulk-content-upload/scripts/prepare_browser_stage_authorization.py \
  /tmp/allincms-full-rehearsal/next-browser-stage-packet-after-batch-upload.json \
  --preflight /tmp/allincms-created-site-evidence.json \
  --authorization-output /tmp/allincms-authorization-save-site-settings.json \
  --settings-action save_site_settings \
  --settings-target https://workspace.laicms.com/{realSiteKey}/site-info \
  --settings-target-identifier "site-info settings"
```

Replace placeholders with the exact current backend URL and identifier observed in the browser before mutating. Supported gated settings actions are `save_site_settings`, `create_theme`, `create_form`, `add_domain`, and `add_tracking_tag`. `upload_media` is UI-first: it requires a media-specific preflight and gate, a generated or user-approved non-private file, upload request capture, backend media row proof, public URL proof, and cleanup/rollback proof before any replay or batch media upload is considered. If the selected browser surface cannot set files, record a simulated click path only and do not claim upload success.

When a non-module stage is applied as `partial`, the ledger should normally expose no `nextStageId`. Do not rebuild from the whole plan or mark the stage complete out of band. If the missing proof is later captured, explicitly rebuild the packet for that same partial stage with `scripts/build_browser_stage_packet.py --stage-id <partial-stage-id>`. A recovery packet must have `recovery: true`, allow only same-stage recovery actions, and may be used only to apply a completed, partial, or blocked result for that same stage. Later stages become available only after the recovered stage is applied as completed.

After `create_site_submit` is completed and its proof is applied, the next packet should normally be `setup_pages_inspection`. This is read-only and must inspect site-info, domains, themes, routes, and forms before any theme, page, route, product, post, media, form, or settings mutation.

After `setup_pages_inspection` is completed and applied, the next packet should normally be `module_interface_capture`. This stage requires explicit authorization and should capture exactly one module/action interface before stopping. A single capture should usually be applied as a `partial` result unless the current run has an explicit coverage rule proving the whole interface-capture stage is complete. Also update `module-capture-coverage-after-one-stage.json` or the current run's coverage file with `scripts/update_module_capture_coverage.py` so the next missing module/action is explicit. Then sync coverage into the browser ledger; if coverage is incomplete, regenerate the next packet and continue with `module_interface_capture` for the named missing `module:action`. Only complete coverage may mark aggregate `module_interface_capture` completed and unlock `theme_page_route_launch`. Partial module capture must not unlock theme/page launch, forms/media/settings mutation, or batch upload. Do not treat setup-page visibility or one captured request as proof that JSON replay is safe for the site.

Before executing any capture-plan stage generated from module scanning, validate the whole capture plan gate coverage. `run_full_rehearsal.py` now writes `capture-plan-gate-coverage.json`, and `validate_full_rehearsal.py` recomputes and cross-checks it. For direct capture-plan work outside a full rehearsal, run:

```bash
python3 skills/allincms-bulk-content-upload/scripts/validate_capture_plan_gate_coverage.py \
  /tmp/allincms-full-rehearsal/full-e2e/03-module-interface-plan/module-capture-plan.json
```

If this fails, stop and extend `make_authorization_record.py`, `prepare_capture_authorization.py`, or `check_pre_mutation_gate.py` before touching the browser. `upload_media` is the only intentionally ungated capture action in the current helper set; it is still authorization-required and UI-first until multipart/storage behavior is captured.

After a specific action has been captured and a single authorized sample replay has been verified, write a redacted action replay contract and validate it before using JSON/Server Action replay for speed:

```bash
python3 skills/allincms-bulk-content-upload/scripts/validate_action_replay_contract.py \
  /tmp/allincms-action-replay-contract.json
```

The contract is per action, not per module. It must include current `siteKey`, exact `requestUrl`, method, redacted required header names, payload keys/shape, required id field names, authorization action, backend persistence proof, public frontend proof when applicable, and cleanup/rollback plan. Do not store cookie/header values, raw `next-action` IDs, raw router state, or raw payloads. Passing this contract validator proves only that this one action is locally replay-ready; it does not authorize replay, batch upload, neighboring actions, or future sessions.

When every captured module/action stage has a matching valid contract, aggregate them into coverage:

```bash
python3 skills/allincms-bulk-content-upload/scripts/apply_action_replay_contracts.py \
  --coverage /tmp/allincms-module-capture-coverage.json \
  --contract /tmp/allincms-products-create-replay-contract.json \
  --contract /tmp/allincms-posts-create-replay-contract.json \
  --output /tmp/allincms-module-capture-coverage-replay-ready.json
```

This may set `actionReplayContractsVerified: true` and `jsonReplayReady: true` only for the listed contracts. It is still local evidence, not action-time user authorization. Use it to decide whether JSON acceleration is technically ready; then request a fresh action-specific authorization before replaying anything.

Before reporting a full rehearsal artifact, validate the top-level summary too. A fresh `run_full_rehearsal.py` run writes `browser-runbook-summary.json` automatically and `validate_full_rehearsal.py` cross-checks it against the first ledger packet:

```bash
python3 skills/allincms-bulk-content-upload/scripts/validate_full_rehearsal.py \
  /tmp/allincms-full-rehearsal/rehearsal-summary.json
python3 skills/allincms-bulk-content-upload/scripts/validate_browser_runbook_summary.py \
  /tmp/allincms-full-rehearsal/browser-runbook-summary.json
```

Do not read `rehearsal-summary.json` or `browser-runbook-summary.json` as run-evidence summaries. They do not expose `valid`, `complete`, or `completionGaps`. Rehearsal success is proven by the two validators above and by safety blocks such as `fullE2EValidation.ok`, `handoffSafety.ok`, `browserExecutionPlanSafety.ok`, `browserExecutionLedgerSafety.ok`, and `nextBrowserActionHandoffSafety.ok`. Use `summarize_run_status.py` only on run-evidence JSON.

Inspect the generated real-browser runbook summary before acting on the rehearsal:

```bash
cat /tmp/allincms-full-rehearsal/browser-runbook-summary.json
```

Use this summary to decide the next real browser step, not the long artifact list. When it says commands are suppressed or the source rehearsal is invalid, refresh real browser evidence or fix the rehearsal before any LAICMS mutation. The first real step after a local-only from-scratch rehearsal should normally be a read-only `/sites` refresh and create-dialog open/close proof, not a mutation. For an external or older rehearsal summary that lacks the integrated artifact, generate it manually with `scripts/make_browser_runbook_summary.py`.

If `browser-runbook-summary.json` is copied, edited, transferred, or reused after context compaction, re-run `validate_browser_runbook_summary.py` before relying on `operatorHandoff` or `requiredLocalArtifacts`. A valid `rehearsal-summary.json` does not prove a standalone runbook file is still aligned after it leaves the original generation step.

In the standalone `browser-runbook-summary.json` file, read the next browser step from `nextRealBrowserStep.stageId`. In `rehearsal-summary.json`, `browserRunbookSummary.nextStageId` is only a compact embedded summary. Do not expect the standalone runbook file to expose a top-level `nextStageId`.

In `browser-runbook-summary.json`, use `operatorHandoff` as the compact execution checklist for the next stage. It must include:

```text
packetPath
ledgerPath
evidenceBundleDir
evidenceManifestPath
nextBrowserActionHandoffPath
browserStageModuleCaptureAuthorizationPackagePath
stageResultTemplatePath
bundleStageResultDraftPath
ledgerExpectedStageResultPath
ledgerApplyCommand
authorizationPreparation
requiredProof
stopAfter
nextActionMode
```

Do not assume the bundle draft result path is the same file that the ledger apply command expects. Fill evidence in the bundle, then write or copy the final stage result to `ledgerExpectedStageResultPath` before running `ledgerApplyCommand`. The handoff is not authorization and is not remote proof.

When the rehearsal has already generated `next-browser-action-handoff.json`, the standalone `browser-runbook-summary.json` must surface it through `operatorHandoff.nextBrowserActionHandoffPath` and `requiredLocalArtifacts.nextBrowserActionHandoff`. Use that artifact for authorization-preparation review before asking the user for an action-time browser mutation. If the runbook omits it, regenerate or validate the full rehearsal before continuing.

After complete module capture coverage unlocks `theme_page_route_launch`, a partial theme/page/route launch result must keep `nextStageId` empty and must not unlock `static_frontend_audit`, content probe creation, upload, or forms/media/settings mutation. Only a completed launch result that records active theme, published pages, enabled pages, bound routes, frontend HTTP ok, and frontend DOM verified may unlock `static_frontend_audit`. The packet after complete theme launch should be verification mode and should not require mutation authorization.

After `static_frontend_audit` starts, partial static audit proof must keep `nextStageId` empty and must not unlock `content_probe_create`, save request capture, or upload. Only a completed static audit result with expected status map, redacted frontend audit, and `frontendRendering` evidence may unlock `content_probe_create`. The content-probe packet requires fresh mutation authorization.

After `content_probe_create` starts, partial probe proof must keep `nextStageId` empty and must not unlock `save_request_capture`, publish, or upload. Authorization text plus probe naming proof is not enough; the completed result must include backend draft proof such as a redacted list row or edit URL. Only completed content-probe proof may unlock `save_request_capture`, and that next packet still requires fresh mutation authorization before saving or capturing a request.

After `save_request_capture` starts, partial request proof must keep `nextStageId` empty and must not unlock `publish_sample_verify`, `manifest_schema_gate`, or upload. A URL, method, headers, or payload shape alone is not enough. Only completed save-request proof with request URL, method, required headers, payload template, field mapping, and backend persistence proof may unlock the downstream sample-publish and manifest-schema gates. The next packet should normally be `publish_sample_verify` because it appears first in the staged plan, while `manifest_schema_gate` may also become ready after the same completed capture.

After `publish_sample_verify` starts, partial sample proof must keep `publish_sample_verify` partial and must not unlock `batch_upload_publish`, forms/media/settings, cleanup, or final audit. Because `manifest_schema_gate` may already be ready after a completed save-request capture, a partial sample result may leave the next packet at the local manifest gate; do not mistake that for upload permission. Only completed sample proof with backend published status, frontend detail 200, title/name, cover/media, and structured body may let the run continue toward the manifest schema gate and, after that gate passes, batch upload.

After `manifest_schema_gate` starts, partial manifest proof must keep `manifest_schema_gate` partial and must not unlock `batch_upload_publish`. Generic manifest validation alone is not enough. Only completed manifest proof with both generic validation and `--require-schema-verified` validation passing for the current site/content type may unlock batch upload, and the resulting `batch_upload_publish` packet requires fresh mutation authorization.

After `batch_upload_publish` starts, partial batch proof must keep `batch_upload_publish` partial and must not unlock forms/media/settings, final frontend audit, or cleanup. A progress log or some verified detail pages is not enough. Only completed batch proof with schema gate pass, sample verification pass, progress log, duplicate-slug handling where applicable, and frontend detail audit for every uploaded route may unlock `forms_media_settings`, which still requires fresh mutation authorization.

After `forms_media_settings` starts, partial settings/media/forms proof must keep `forms_media_settings` partial and must not unlock final frontend audit or cleanup. A captured settings request plus backend state is not enough when the setting has a public or integration-facing effect. Only completed proof with action-specific request capture, backend persisted proof, and public or integration effect proof where applicable may unlock `final_frontend_audit`. The next packet should be verification mode and should not require mutation authorization.

Before `final_frontend_audit`, generate the URL/status files from the schema-verified manifest and, when available, the batch progress log. Do not hand-maintain the final detail URL list:

```bash
python3 skills/allincms-bulk-content-upload/scripts/make_final_frontend_audit_inputs.py \
  --manifest /tmp/allincms-schema-verified-manifest.json \
  --progress-log /tmp/allincms-batch-progress.json \
  --require-schema-verified \
  --require-progress-complete \
  --static-paths /,/products,/about-us,/contact-us \
  --urls-output /tmp/allincms-final-audit-urls.txt \
  --statuses-output /tmp/allincms-final-expected-statuses.json \
  --summary-output /tmp/allincms-final-audit-inputs-summary.json
```

The generated URL file may contain concrete slugs because it is a runtime audit input. Keep those files in temporary run evidence, not in this skill package. Convert the redacted audit output with `make_frontend_rendering_evidence.py` before copying route proof into run evidence.

Then convert the redacted final audit report into the browser stage result before applying the execution ledger:

```bash
python3 skills/allincms-bulk-content-upload/scripts/make_final_frontend_audit_stage_result.py \
  --packet-json /tmp/allincms-full-rehearsal/next-browser-stage-packet-after-forms-media-settings-complete.json \
  --audit-report-json /tmp/allincms-final-audit-report.json \
  --audit-inputs-summary-json /tmp/allincms-final-audit-inputs-summary.json \
  --expected-statuses-json /tmp/allincms-final-expected-statuses.json \
  --evidence-pointers /tmp/allincms-final-audit-report.json,/tmp/allincms-final-audit-inputs-summary.json \
  --output /tmp/allincms-final-frontend-audit-stage-result.json
```

Apply the generated result with `scripts/apply_browser_stage_result.py`. Do not hand-write `final_frontend_audit` proof; if the helper outputs `partial`, keep cleanup locked until the missing expected route coverage, HTTP, DOM/rich-text, image, or broken-entry proof is fixed and the same stage is recovered.

After `final_frontend_audit` starts, partial audit proof must keep `final_frontend_audit` partial and must not unlock cleanup. HTTP 200, DOM/rich-text proof, or image checks alone are not enough if any expected route, media, description, body, status, or broken-entry check is unresolved. Only completed proof with HTTP status report, DOM/rich-text report, image report, and an empty broken-entry list may unlock `cleanup_probes`, which requires fresh cleanup authorization.

After `cleanup_probes` starts, partial cleanup proof must keep `cleanup_probes` partial and must not claim the run is closed. Cleanup authorization and candidate list alone are not enough. Only completed proof with cleanup authorization, candidate list, backend cleanup proof, and frontend non-public proof may mark cleanup completed. Even then, local rehearsal cleanup proof is not remote LAICMS cleanup proof.

For a local-only create-site chain dry run by itself, run:

```bash
python3 skills/allincms-bulk-content-upload/scripts/simulate_site_creation_chain.py \
  --existing-site-keys old-site-a,old-site-b \
  --site-key-evidence "old-site-a from backend url route https://workspace.laicms.com/old-site-a/dashboard;old-site-b from backend url route https://workspace.laicms.com/old-site-b/dashboard" \
  --include-simulated-static-launch \
  --output-dir /tmp/allincms-site-creation-simulation
```

This dry run proves the local evidence chain and validators, not that a site was created.
It writes `create-site-preflight.json`, `create-site-authorization.json`, `created-site-evidence.json`, `run-summary.json`, and `round-closeout.json`.
With `--include-simulated-static-launch`, the dry run also adds simulated `frontendRendering` and `launchReadiness` blocks for static routes so the summary can exercise the launch-ready-but-upload-incomplete state.

After a created-site or existing-site evidence file is available, run a local-only content probe lifecycle dry run before the real browser probe:

```bash
python3 skills/allincms-bulk-content-upload/scripts/simulate_probe_lifecycle.py \
  --base /tmp/allincms-site-creation-simulation/created-site-evidence.json \
  --require-created-site \
  --output-dir /tmp/allincms-probe-lifecycle-simulation
```

This writes staged authorization and evidence files for create probe, save/request capture, publish/sample verification, cleanup, plus `run-summary.json` and `round-closeout.json`. It proves the local probe evidence chain and gates, not that remote content was created, saved, published, or deleted.

Before submitting a create-site form, generate and validate preflight evidence:

```bash
python3 skills/allincms-bulk-content-upload/scripts/make_create_preflight_evidence.py \
  --existing-site-keys old-site-a,old-site-b \
  --site-key-evidence "old-site-a from backend url route https://workspace.laicms.com/old-site-a/dashboard;old-site-b from backend url route https://workspace.laicms.com/old-site-b/dashboard" \
  --observed-create-fields "button: 创建站点;dialog title: 创建站点;input name: name, placeholder: 站点名称;textarea name: description, placeholder: 站点简介;submit button: 创建;close button: Close" \
  --dialog-closed-verified \
  --output /tmp/allincms-create-site-preflight.json
python3 skills/allincms-bulk-content-upload/scripts/validate_run_evidence.py \
  /tmp/allincms-create-site-preflight.json
```

If the workspace site list is verified empty, use `--no-existing-sites` instead of `--existing-site-keys`.
Add `--empty-site-list-evidence "verified empty /sites list"` in that case.

The preflight helper writes `generatedAt`. Treat the file as short-lived; regenerate it after refreshing `/sites` and the create dialog if more than 30 minutes pass.

Before any remote mutation, generate an action-specific authorization record. Generic instructions such as "continue", "go ahead", or "逐个验证" are not enough unless a current-session test-site policy is paired with a record that names the exact action and target:

```bash
python3 skills/allincms-bulk-content-upload/scripts/make_authorization_record.py \
  --action create_site \
  --target https://workspace.laicms.com/sites \
  --target-type site \
  --target-identifier pending-new-site \
  --fields-or-files name,description \
  --expected-result "new site card, backend dashboard, and default frontend open" \
  --verification-plan "verify site card, backend dashboard, frontend base URL, and module routes" \
  --cleanup-plan "no automatic deletion; stop before content upload" \
  --authorization-source "current user explicitly authorizes creating a site at https://workspace.laicms.com/sites with name and description" \
  --output /tmp/allincms-authorization-create-site.json
```

Validate any existing authorization record before using it:

```bash
python3 skills/allincms-bulk-content-upload/scripts/make_authorization_record.py \
  --validate-only /tmp/allincms-authorization-create-site.json
```

Immediately before submitting the create-site form, run the final gate:

```bash
python3 skills/allincms-bulk-content-upload/scripts/check_pre_mutation_gate.py \
  --action create_site \
  --preflight /tmp/allincms-create-site-preflight.json \
  --authorization /tmp/allincms-authorization-create-site.json
```

The final gate requires both JSON files to have recent `generatedAt` timestamps and defaults to a 30 minute maximum age. Regenerate stale preflight or authorization records instead of editing timestamps by hand.

## Browser Paths

Backend paths commonly look like:

```text
https://workspace.laicms.com/sites
https://workspace.laicms.com/{siteKey}/posts
https://workspace.laicms.com/{siteKey}/products
https://workspace.laicms.com/{siteKey}/media
https://workspace.laicms.com/{siteKey}/themes
https://workspace.laicms.com/{siteKey}/routes
https://workspace.laicms.com/{siteKey}/site-info
https://workspace.laicms.com/{siteKey}/domains
https://workspace.laicms.com/{siteKey}/forms
```

Frontend paths usually look like:

```text
https://{siteKey}.web.allincms.com/posts
https://{siteKey}.web.allincms.com/products
```

Verify the actual routes for the current site. Do not assume `/posts/{slug}` or `/products/{slug}` until a real frontend page or route pattern is confirmed.

On one verified site (`mysite01`, checked 2026-06-29), backend `/pages` returned 404; page routes were represented through `themes` and `routes`.

## Probe Rules

Safe probe titles must include a clear cleanup prefix:

```text
Codex Probe - Delete Me
```

Prefer an existing test draft or a user-approved temporary item. Do not probe with real business titles. After verification, delete or unpublish probe content and confirm the frontend probe URL returns 404 or is inaccessible.

## Payload Rules

The authoritative per-type field contract is `references/server-action-save-api.md` §3 (measured, not hypothesized):
- **Posts**: `title`, `slug`, `excerpt`, `coverImage`, `content` (Slate node array), categories, tags, `postId`, `mode`.
- **Products**: `name`, `slug`, `description`, `media` (`{name,alt,type,source:'url',url}`), `content` (Slate node array), `specifications` (`[{key,value}]`), categories, tags, `productId`, `mode`.

Do NOT carry `title`/`specs`/`coverImage` into a product payload — products use `name`/`specifications`/`media`; that old assumption breaks fields (会挂字段). Any other field (`variants`, `price`, `sku`, `gallery`, `inventory`) is a per-site hypothesis to confirm against the captured save request, which remains the source of truth for anything not in §3.

Browser-verified example: on `mysite01` the product edit form used `name` for product name, `description` for product description, and separate media areas labeled `主图/视频` and `图片/视频列表`. Do not generalize that to all sites without inspecting the current form.

Do not upload raw Markdown syntax as plain editor text. Browser verification on `mysite01` showed that literal `**bold**` and backtick code remained visible when stored as text in the Slate editor, while true `<strong>` and `<table>` nodes rendered correctly on another product page. Convert Markdown into the editor's supported structured content blocks and marks before upload.

## Anti-Confusion Checklist

Before batch upload, answer these explicitly:

- Is the content type definitely `posts`, `products`, `media`, `themes`, `routes`, or a verified page-like model?
- Did I inspect the current backend fields instead of relying on memory?
- Did I capture the current save request for this exact content type?
- Did HTTP success actually persist data in the backend?
- Did the frontend page render the saved content?
- Did bold, code, links, lists, and tables render as structured HTML instead of raw Markdown characters?
- Do images use public URLs instead of local paths?
- Does `coverImage` or `media` require `source`, `type`, `url`, `name`, or `alt`?
- Does a product require specs, price, gallery, variants, inventory, or SKU?
- Did one sample pass before batch upload?
- Did I clean probe content?
- Did I verify every uploaded frontend link, cover, description, and status?

## Stop Conditions

Stop and report before continuing if:

- Neither a current exact user instruction nor a current-session test-site policy plus exact action record authorizes creating, editing, publishing, deleting, or batch uploading content.
- Neither a current exact user instruction nor a current-session test-site policy plus exact action record authorizes submitting the create-site form or saving site settings.
- Neither a current exact user instruction nor a current-session test-site policy plus exact action record authorizes clicking a content-type `创建` button that may create an empty draft.
- Neither a current exact user instruction nor a current-session test-site policy plus exact action record authorizes opening a media upload flow or selecting/uploading files.
- Neither a current exact user instruction nor a current-session test-site policy plus exact action record authorizes deleting or unpublishing accidental drafts/probes.
- Login is expired or the workspace redirects to sign-in.
- The create-site form fields, resulting siteKey, or default frontend domain cannot be confirmed.
- List/edit fields differ materially from the expected model.
- The save request cannot be captured or interpreted.
- A replayed request returns success but backend or frontend data does not change.
- Probe cleanup fails.
- The manifest validator reports errors.
- Frontend verification finds missing pages, broken images, duplicate slugs, or wrong content type routes.
