#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pre-flight: verify cluster connectivity
if ! kubectl cluster-info &>/dev/null; then
  echo "ERROR: Cannot reach the Kubernetes cluster."
  echo ""
  echo "If using access keys, export credentials first:"
  echo "  export AWS_ACCESS_KEY_ID=<key>"
  echo "  export AWS_SECRET_ACCESS_KEY=<secret>"
  echo "  export AWS_DEFAULT_REGION=<region>"
  echo "  aws eks update-kubeconfig --region <region> --name <cluster>"
  exit 1
fi

echo "Deploying chai.com..."
kubectl apply -f "$SCRIPT_DIR/"

echo "Waiting for rollout..."
kubectl rollout status deployment/chai-com

echo ""
echo "chai.com is ready."
echo ""
echo "Waiting for external IP/hostname from LoadBalancer..."

EXTERNAL=""
for i in $(seq 1 30); do
  EXTERNAL=$(kubectl get svc chai-com -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
  if [ -z "$EXTERNAL" ]; then
    EXTERNAL=$(kubectl get svc chai-com -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
  fi
  if [ -n "$EXTERNAL" ]; then
    break
  fi
  printf "."
  sleep 5
done
echo ""

if [ -n "$EXTERNAL" ]; then
  echo "Access: http://${EXTERNAL}"
else
  echo "LoadBalancer IP/hostname not yet assigned."
  echo "Check status with: kubectl get svc chai-com"
fi
