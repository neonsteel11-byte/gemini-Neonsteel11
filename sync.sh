#!/bin/bash
git add -A
git commit -m "sync" --allow-empty-message -q 2>/dev/null
for i in 1 2 3 4 5; do
  git pull --rebase origin main && git push && echo "SYNCED OK" && exit 0
  echo "retry $i/5..."
  sleep 3
done
echo "FAILED after 5 retries"
