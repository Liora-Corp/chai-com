#!/usr/bin/env python3
"""Print IaC summary markdown for GITHUB_STEP_SUMMARY"""
import json
import os

if not os.path.exists("iac-results.json"):
    print("### IaC (Trivy)")
    print("No results file generated.")
else:
    try:
        with open("iac-results.json") as f:
            data = json.load(f)
        counts = {}
        for result in data.get("Results", []):
            for m in result.get("Misconfigurations", []):
                sev = m.get("Severity", "UNKNOWN")
                counts[sev] = counts.get(sev, 0) + 1
        print("### IaC (Trivy - k8s + Dockerfile)")
        print("| Severity | Count |")
        print("|----------|-------|")
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]:
            if sev in counts:
                print("| " + sev + " | " + str(counts[sev]) + " |")
        if not counts:
            print("| - | No misconfigurations found |")
        print("Download `iac-report.html` from Artifacts.")
    except Exception as e:
        print("### IaC (Trivy)")
        print("Could not parse results: " + str(e))
