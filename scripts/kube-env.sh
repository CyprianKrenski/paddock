#!/usr/bin/env bash

paddock_kubeconfig="${HOME}/.kube/paddock"

if [ ! -f "${paddock_kubeconfig}" ]; then
  kubectl config view --minify --flatten --context docker-desktop > "${paddock_kubeconfig}"
  chmod 600 "${paddock_kubeconfig}"
fi

export KUBECONFIG="${paddock_kubeconfig}"
kubectl config set-context --current --namespace paddock > /dev/null
