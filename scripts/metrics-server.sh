#!/usr/bin/env bash
set -euo pipefail

version="v0.9.0"

kubectl apply -f "https://github.com/kubernetes-sigs/metrics-server/releases/download/${version}/components.yaml"
if ! kubectl -n kube-system get deployment metrics-server -o jsonpath='{.spec.template.spec.containers[0].args}' | grep -q kubelet-insecure-tls; then
  kubectl -n kube-system patch deployment metrics-server --type=json \
    -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
fi
kubectl -n kube-system rollout status deployment/metrics-server
