#!/usr/bin/env python3
"""Resolve the RUN MODE and decide which quality gates apply — so the whole-site template-residue
gate is enforced when it matters (new/converted sites carry demo residue) and skipped when it
doesn't (daily incremental updates to a site that's already yours and clean).

Three modes:
  from_scratch        — a NEW site was created. It always ships AllinCMS default-template demo
                        content, so residue MUST be cleared. Auto-resolved, no user prompt.
  template_conversion — an EXISTING generic/old-brand site is being converted. Demo/old residue is
                        scattered across it, so the residue gate is required.
  incremental_update  — a DAILY update to a site that is already yours and already clean. No
                        whole-site residue risk, so the residue gate is skipped (new/changed items
                        are still content-quality checked).

Key safety rule: for an EXISTING site the skill cannot tell conversion from daily update, so it MUST
ask the user, and until answered it defaults to conversion (residue gate ON). incremental_update is
NEVER a silent default — only an explicit user declaration (or a confirmed answer) selects it. That
biases every ambiguous case toward scanning, never toward silently shipping leftover template content.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _common import write_json, ensure_output_outside_skill, now_iso

KIND = "allincms_run_mode_decision"
MODES = ("from_scratch", "template_conversion", "incremental_update")

CONFIRMATION_PROMPT = (
    "This is an EXISTING site. Which is it? "
    "(A) a from-template / old-brand CONVERSION — I will scan the WHOLE site and BLOCK on any old "
    "brand / product / category chip / contact residue before launch; or "
    "(B) a DAILY INCREMENTAL update to a site that is already yours and clean — I will SKIP the "
    "whole-site residue scan and only quality-check the new/changed items. "
    "Until you tell me, I treat it as a conversion and keep the residue gate ON."
)


def resolve_run_mode(site_creation_status: str = "", declared_mode: str = "",
                     demo_signal_count: int = 0) -> dict[str, Any]:
    status = (site_creation_status or "").strip()
    declared = (declared_mode or "").strip()
    reasons: list[str] = []
    needs_confirmation = False

    if declared in MODES:
        mode = declared
        reasons.append(f"user-declared mode: {declared}")
    elif status == "created_verified":
        mode = "from_scratch"
        reasons.append("a newly created site always ships AllinCMS default-template demo content; residue must be cleared")
    elif status == "existing_site_selected":
        needs_confirmation = True
        mode = "template_conversion"  # SAFE DEFAULT: unknown existing site treated as conversion until user says daily
        if demo_signal_count > 0:
            reasons.append(f"existing site shows {demo_signal_count} demo/template fingerprint(s) — likely a conversion; CONFIRM with user")
        else:
            reasons.append("existing site: cannot tell conversion from daily update — CONFIRM with user; "
                           "defaulting to conversion (residue gate ON) until told it is incremental")
    else:
        mode = "template_conversion"
        needs_confirmation = True
        reasons.append(f"unknown site-creation status {status!r}; defaulting to conversion (residue gate ON), confirm with user")

    residue_required = mode in ("from_scratch", "template_conversion")
    return {
        "kind": KIND,
        "generatedAt": now_iso(),
        "mode": mode,
        "needsUserConfirmation": needs_confirmation,
        "gates": {
            "template_residue": "required" if residue_required else "skipped",
            "content_quality": "required",  # new or changed content is always quality-checked
        },
        "confirmationPrompt": CONFIRMATION_PROMPT if needs_confirmation else "",
        "rationale": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the AllinCMS run mode and applicable quality gates.")
    parser.add_argument("--site-creation-status", default="",
                        help="created_verified (new site) | existing_site_selected (selected existing site)")
    parser.add_argument("--declared-mode", default="",
                        help=f"Explicit user-declared mode, overrides inference: one of {MODES}")
    parser.add_argument("--demo-signal-count", type=int, default=0,
                        help="How many demo/template fingerprints were detected on a selected existing site")
    parser.add_argument("--output", default="", help="Optional path to write the decision JSON (outside the skill)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    decision = resolve_run_mode(args.site_creation_status, args.declared_mode, args.demo_signal_count)

    if args.output:
        output = ensure_output_outside_skill(Path(args.output).expanduser())
        write_json(output, decision)
        print(f"Wrote run-mode decision: {output}")

    print(f"mode={decision['mode']} needsUserConfirmation={str(decision['needsUserConfirmation']).lower()} "
          f"template_residue={decision['gates']['template_residue']} content_quality={decision['gates']['content_quality']}")
    for reason in decision["rationale"]:
        print(f"  - {reason}")
    if decision["needsUserConfirmation"]:
        print(f"ASK THE USER: {decision['confirmationPrompt']}")
    if args.json:
        print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
