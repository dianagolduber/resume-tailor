#!/bin/bash
# Job search tools — resume tailor + application tracker
#
# Tailor a resume:
#   ./run.sh tailor --url "https://..."
#   ./run.sh tailor --url "https://..." --company "Stripe" --role "PMM"
#   ./run.sh tailor --jd job.txt --company "Stripe" --role "PMM"
#
# Track applications:
#   ./run.sh tracker list
#   ./run.sh tracker list --status "Interview"
#   ./run.sh tracker update 3 --status "Phone Screen" --notes "Call Thu 2pm"
#   ./run.sh tracker show 3
#   ./run.sh tracker stats
#
# Open output folder:
#   ./run.sh open

cd "$(dirname "$0")"
source venv/bin/activate

COMMAND="${1:-tailor}"
shift

case "$COMMAND" in
  tailor)   python tailor.py "$@" ;;
  tracker)  python tracker.py "$@" ;;
  open)     mkdir -p output && open output ;;
  *)        echo "Usage: ./run.sh [tailor|tracker|open] [options]"; exit 1 ;;
esac
