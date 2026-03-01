#!/usr/bin/env bash
# Deploy docker-deploy/ to HF Spaces via git subtree.
# Usage:
#   bash scripts/deploy-hf.sh          # normal push
#   bash scripts/deploy-hf.sh --force  # force push (overwrite HF history)
set -euo pipefail

HF_REMOTE="hf"
HF_REPO="https://huggingface.co/spaces/Hesusgc/evaluador-curricular-upaep"
SUBTREE_PREFIX="docker-deploy"
BRANCH="main"
FORCE=false

if [[ "${1:-}" == "--force" ]]; then
  FORCE=true
fi

# ── Ensure we're at repo root ────────────────────────────────────────
cd "$(git rev-parse --show-toplevel)"

# ── Add HF remote if missing ─────────────────────────────────────────
if ! git remote get-url "$HF_REMOTE" &>/dev/null; then
  echo "Adding remote '$HF_REMOTE' -> $HF_REPO"
  git remote add "$HF_REMOTE" "$HF_REPO"
fi

# ── Show what will be deployed ────────────────────────────────────────
LAST_COMMIT=$(git log --oneline -1)
echo ""
echo "Deploying to HF Spaces:"
echo "  Remote:  $HF_REPO"
echo "  Subtree: $SUBTREE_PREFIX/"
echo "  Commit:  $LAST_COMMIT"
echo "  Force:   $FORCE"
echo ""

# ── Push subtree ──────────────────────────────────────────────────────
if $FORCE; then
  echo "Force pushing $SUBTREE_PREFIX/ -> $HF_REMOTE/$BRANCH ..."
  # Split subtree into a temp branch, force push, then clean up
  TEMP_BRANCH="hf-deploy-tmp-$$"
  git subtree split --prefix="$SUBTREE_PREFIX" -b "$TEMP_BRANCH"
  git push "$HF_REMOTE" "$TEMP_BRANCH:$BRANCH" --force
  git branch -D "$TEMP_BRANCH"
else
  echo "Pushing $SUBTREE_PREFIX/ -> $HF_REMOTE/$BRANCH ..."
  git subtree push --prefix="$SUBTREE_PREFIX" "$HF_REMOTE" "$BRANCH"
fi

echo ""
echo "Done! Space will rebuild at:"
echo "  https://huggingface.co/spaces/Hesusgc/evaluador-curricular-upaep"
