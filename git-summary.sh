#!/bin/bash

echo "### Staged Changes ###"
git diff --cached --stat

echo ""
echo "### Unstaged Changes ###"
git diff --stat

echo ""
echo "### Untracked Files ###"
git ls-files --others --exclude-standard
