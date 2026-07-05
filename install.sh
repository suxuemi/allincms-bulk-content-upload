#!/usr/bin/env bash
# Install this skill for local AI tools by symlinking THIS repo into each tool's
# skill folder (~/.codex/skills, ~/.claude/skills). Run it from inside the clone:
#
#   ./install.sh                 # link into both codex and claude
#   ./install.sh codex           # only codex
#   ./install.sh claude --force  # only claude; repoint an existing symlink
#
# Idempotent: re-running is safe. It NEVER deletes a real file or directory —
# it only creates symlinks, and --force only ever replaces an existing SYMLINK.
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

FORCE=0
ROOTS=()
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    codex)   ROOTS+=("$HOME/.codex/skills") ;;
    claude)  ROOTS+=("$HOME/.claude/skills") ;;
    -h|--help)
      echo "Usage: ./install.sh [codex] [claude] [--force]"
      echo "  No tool arg installs for both codex and claude."
      echo "  --force repoints an existing SYMLINK (never touches a real directory)."
      exit 0 ;;
    *) echo "unknown arg: $arg (see --help)" >&2; exit 2 ;;
  esac
done
if [ "${#ROOTS[@]}" -eq 0 ]; then
  ROOTS=("$HOME/.codex/skills" "$HOME/.claude/skills")
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
