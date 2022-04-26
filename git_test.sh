#!/bin/bash
git add -u && \
git commit --amend --no-edit && \
git switch test && \
git reset --hard HEAD~1 && \
git merge dev && \
git push -f && \
git switch dev

