#!/usr/bin/env python3
"""Audit this AllinCMS skill package for domain leakage and sensitive residue."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
}

DOMAIN_TERMS = [
    "lai" + "faxin",
    "lai" + "fa",
    "\u6765\u53d1\u4fe1",
    "\u641c\u5ba2",
    "\u5ba2\u6237\u5f00\u53d1",
    "\u8054\u7cfb\u4eba",
    "\u90ae\u4ef6\u8425\u9500",
    "\u4e3b\u52a8\u5f00\u53d1",
    "\u7cbe\u51c6\u90ae\u7bb1",
    "\u6f5c\u5ba2",
    "C" + "RM",
    "\u5916\u8d38",
    "web." + "lai" + "faxin.com",
    "lai" + "faxin.com",
    "lai" + "fa.xin",
    "tracking" + "-logs",
    "search" + "-save-records",
    "tag" + "-management",
    "sync" + "-management",
    "i" + "forte",
    "North" + "star",
    "Moving " + "Light",
]

WORKFLOW_TERMS = [
    "lead search",
    "contact export",
    "contact exports",
    "email sending",
    "outreach",
    "prospect",
    "private contact",
    "sales playbook",
]

BLOCKLIST_PATTERNS = {
    "business_domain_leakage": re.compile("|".join(re.escape(term) for term in DOMAIN_TERMS), re.IGNORECASE),
    "non_cms_workflow_leakage": re.compile("|".join(re.escape(term) for term in WORKFLOW_TERMS), re.IGNORECASE),
    "temporary_business_copy": re.compile(r"\b(?:LED(?:\s+Lighting)?|lighting)\b", re.IGNORECASE),
    "email_address": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "mongo_like_content_id": re.compile(r"\b[a-f0-9]{24}\b"),
}

REQUIRED_SEDIMENTATION_MARKERS = {
    "SKILL.md": [
        "Every AllinCMS skill turn must end with a skill sedimentation pass",
        "At the start of each AllinCMS skill turn",
        "The final response must report the sedimentation status",
        "no reusable skill update needed",
    ],
    "references/operational-findings.md": [
        "Problem Recording Contract",
        "Record Template",
        "Per-Turn Skill Sedimentation Discipline",
        "Conversation-Turn Closeout Findings",
        "main roundIssues item",
        "If there is no reusable platform finding",
    ],
}

def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return files


def scan_file(path: Path, root: Path) -> list[str]:
    issues: list[str] = []
    if path.resolve() == Path(__file__).resolve():
        return issues
    if path.name == "test_validate_run_evidence.py":
        return issues
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        issues.append(f"{path.relative_to(root)}: cannot decode as UTF-8")
        return issues

    for lineno, line in enumerate(text.splitlines(), start=1):
        for code, pattern in BLOCKLIST_PATTERNS.items():
            match = pattern.search(line)
            if match:
                snippet = line.strip()[:180]
                issues.append(f"{path.relative_to(root)}:{lineno}: {code}: {snippet}")
    return issues


def check_required_markers(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path, markers in REQUIRED_SEDIMENTATION_MARKERS.items():
        path = root / rel_path
        if not path.exists():
            issues.append(f"{rel_path}: missing required sedimentation file")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"{rel_path}: missing sedimentation marker: {marker}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit skill package hygiene.")
    parser.add_argument("root", nargs="?", default=str(DEFAULT_ROOT), help="Skill root directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"ERROR: root is not a directory: {root}", file=sys.stderr)
        return 2

    issues: list[str] = []
    for path in iter_text_files(root):
        issues.extend(scan_file(path, root))
    issues.extend(check_required_markers(root))
    entrypoint_audit = root / "scripts" / "audit_test_entrypoints.py"
    if entrypoint_audit.exists():
        result = subprocess.run(
            [sys.executable, str(entrypoint_audit), str(root / "scripts")],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            issues.append("test entrypoint audit failed" + (f": {output}" if output else ""))

    if issues:
        print("Skill hygiene audit failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Skill hygiene audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
