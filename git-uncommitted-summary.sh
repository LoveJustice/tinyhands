#!/bin/bash

echo "=== Git Uncommitted Work Summary ==="

# Staged Changes
staged=$(git diff --cached --name-only)
if [ -n "$staged" ]; then
  echo "Staged Changes:"
  echo "$staged"
  echo ""
fi

# Unstaged Changes
unstaged=$(git diff --name-only)
if [ -n "$unstaged" ]; then
  echo "Unstaged Changes:"
  echo "$unstaged"
  echo ""
fi

# Untracked Files
untracked=$(git ls-files --others --exclude-standard)
if [ -n "$untracked" ]; then
  echo "Untracked Files:"
  echo "$untracked"
  echo ""
fi
