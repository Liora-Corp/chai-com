#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Tearing down chai.com..."
kubectl delete -f "$SCRIPT_DIR/" --ignore-not-found

echo "Done."
