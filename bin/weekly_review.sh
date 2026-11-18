#!/usr/bin/env bash
# weekly_review.sh — run every Sunday (or any quiet hour). Collects evidence,
# forces four questions, writes one worklog entry so growth compounds instead
# of drifting.
set -uo pipefail
ROOT="${OPENROOT:-$HOME/openroot}"; cd "$ROOT"

echo "=========== OPENROOT WEEKLY REVIEW $(date +%F) ==========="
echo "-- system deltas --"
bash bin/health_sweep.sh quick | grep -E 'usage|entries|tip age|mesh sync'
echo "-- worklog volume (last 7d) --"
grep -c '"ts"' worklog/$(date +%Y).jsonl 2>/dev/null || echo 0
echo "-- wins logged --"
grep '"type": "win"' worklog/$(date +%Y).jsonl 2>/dev/null | tail -5 || echo "(none — name at least one)"
echo "-- risks logged --"
grep '"type": "risk"' worklog/$(date +%Y).jsonl 2>/dev/null | tail -5 || echo "(none — name at least one)"

echo ""
echo "ANSWER THESE FOUR, then log them:"
echo "  1. WIN    — what did the system gain this week?"
echo "  2. RISK   — what almost broke, or will break if ignored?"
echo "  3. PRUNE  — what should be deleted/archived to buy back capacity?"
echo "  4. NEXT   — the ONE capability to add next week (write it as a script name)."
echo ""
read -r -p "One-line win:   " w;  [ -n "$w" ] && bash bin/worklog.sh win "week: $w"
read -r -p "One-line risk:  " r;  [ -n "$r" ] && bash bin/worklog.sh risk "week: $r"
read -r -p "Next cap:       " n;  [ -n "$n" ] && bash bin/worklog.sh add "next-week-target: $n"
echo "=========== review sealed — R=1, c=0 ==========="
