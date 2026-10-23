#!/usr/bin/env bash
set -euo pipefail

url="${1:-http://localhost/races/2025/1/standings/30}"
duration="${2:-60s}"
users="${3:-10}"

oha -z "$duration" -c "$users" --no-tui "$url"
