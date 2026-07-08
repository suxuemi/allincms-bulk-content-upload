#!/usr/bin/env bash
# Install this skill for local AI tools by symlinking THIS repo into each tool's
# skills folder. Works with any tool that discovers the SKILL.md format from a
# skills directory (Claude Code, Codex, WorkBuddy, …).
#
#   ./install.sh                       # auto-detect installed tools and link into each
#   ./install.sh codex                 # only Codex
#   ./install.sh claude workbuddy      # pick specific tools
#   ./install.sh --dir=/path/to/skills # any other tool's skills dir (unknown / self-managed)
#   ./install.sh claude --force        # repoint an existing symlink
#
# Idempotent. NEVER deletes a real file or directory — it only creates symlinks,
# and --force only ever replaces an existing SYMLINK.
#
# NOTE: tools that don't use the SKILL.md-in-a-skills-dir format (e.g. plugin-based
# ones) won't discover it this way. For those, just point the AI at this repo's
# SKILL.md directly as its operating contract — no install needed.
set -euo pipefail

SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# This must be the real skill repo. Derive the skill name from SKILL.md so the
# link name always matches the contract's declared name.
if [ ! -f "$SOURCE/SKILL.md" ]; then
  echo "ERROR: $SOURCE/SKILL.md not found — run install.sh from inside the cloned repo." >&2
  exit 1
fi
NAME="$(awk -F': *' '/^name:/{gsub(/["'\'' ]/,"",$2); print $2; exit}' "$SOURCE/SKILL.md")"
NAME="${NAME:-$(basename "$SOURCE")}"

# Known SKILL.md-format tools -> their skills directory.
tool_dir() {
  case "$1" in
    codex)     echo "$HOME/.codex/skills" ;;
    claude)    echo "$HOME/.claude/skills" ;;
    workbuddy) echo "$HOME/.workbuddy/skills" ;;
    *) return 1 ;;
  esac
}
KNOWN_TOOLS="codex claude workbuddy"

FORCE=0
ROOTS=()
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --dir=*) p="${arg#--dir=}"; p="${p/#\~/$HOME}"; ROOTS+=("$p") ;;
    /*)      ROOTS+=("$arg") ;;                       # an absolute skills-dir path
    codex|claude|workbuddy) ROOTS+=("$(tool_dir "$arg")") ;;
    -h|--help)
      echo "Usage: ./install.sh [codex] [claude] [workbuddy] [--dir=/path/to/skills] [--force]"
      echo "  No tool arg: auto-detect installed tools (~/.codex, ~/.claude, ~/.workbuddy) and link into each."
      echo "  --dir=<path>: link into any other tool's skills directory (unknown / self-managed tools)."
      echo "  --force: repoint an existing SYMLINK (never touches a real file or directory)."
      exit 0 ;;
    *) echo "unknown arg: $arg (see --help)" >&2; exit 2 ;;
  esac
done

# Default: auto-detect — install only for tools whose home dir actually exists,
# so we never scatter link dirs for tools you don't have.
if [ "${#ROOTS[@]}" -eq 0 ]; then
  for t in $KNOWN_TOOLS; do
    d="$(tool_dir "$t")"
    [ -d "$(dirname "$d")" ] && ROOTS+=("$d")
  done
fi
if [ "${#ROOTS[@]}" -eq 0 ]; then
  echo "No known tool detected (~/.codex, ~/.claude, ~/.workbuddy). Use --dir=<path> to target one explicitly." >&2
  exit 1
fi

link_one() {
  local root="$1" link="$1/$NAME"
  mkdir -p "$root"
  if [ -L "$link" ]; then
    local cur; cur="$(readlink "$link")"
    if [ "$cur" = "$SOURCE" ]; then
      echo "  = $link already links here"
      return 0
    fi
    if [ "$FORCE" -eq 1 ]; then
      rm "$link"                       # removes only the symlink, not its target
      ln -s "$SOURCE" "$link"
      echo "  ~ $link repointed (was -> $cur)"
      return 0
    fi
    echo "  ! $link is a symlink to $cur — re-run with --force to repoint" >&2
    return 1
  fi
  if [ -e "$link" ]; then
    echo "  x $link exists as a REAL file/dir — refusing to touch it; move it aside first" >&2
    return 1
  fi
  ln -s "$SOURCE" "$link"
  echo "  + $link -> $SOURCE"
}

echo "Installing skill '$NAME' from $SOURCE"
rc=0
for root in "${ROOTS[@]}"; do link_one "$root" || rc=1; done

echo "Verifying:"
for root in "${ROOTS[@]}"; do
  if head -1 "$root/$NAME/SKILL.md" >/dev/null 2>&1; then
    echo "  ok $root/$NAME/SKILL.md reachable"
  else
    echo "  FAIL $root/$NAME/SKILL.md not reachable" >&2; rc=1
  fi
done

if [ "$rc" -ne 0 ]; then
  echo "Done with warnings — see messages above." >&2
else
  echo "Done. Restart the tool if it only discovers skills at startup."
fi
exit "$rc"
