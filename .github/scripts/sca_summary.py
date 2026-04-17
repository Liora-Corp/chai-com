#!/usr/bin/env python3
"""Print SCA summary markdown for GITHUB_STEP_SUMMARY"""
import json

try:
    with open("npm-audit.json") as f:
        d = json.load(f)
    v = d.get("metadata", {}).get("vulnerabilities", {})
    print("### SCA (npm audit + Trivy)")
    print("| Severity | Count |")
    print("|----------|-------|")
    for k, n in v.items():
        print("| " + k + " | " + str(n) + " |")
    print("Download `sca-report.html` from Artifacts.")
except Exception as e:
    print("### SCA (npm audit + Trivy)")
    print("Could not parse results: " + str(e))
