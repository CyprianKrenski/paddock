#!/usr/bin/env bash
set -euo pipefail

hub_user="${1:?usage: build-push.sh <dockerhub-user> <tag>}"
tag="${2:?usage: build-push.sh <dockerhub-user> <tag>}"

for service in catalogue analysis web; do
  docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --build-arg "SERVICE=${service}" \
    --tag "${hub_user}/paddock-${service}:${tag}" \
    --push \
    .
done
