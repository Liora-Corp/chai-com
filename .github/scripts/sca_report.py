#!/usr/bin/env python3
"""Convert npm-audit.json to sca-report.html"""
import json
import html as h

try:
    with open("npm-audit.json") as f:
        audit = json.load(f)
except Exception as e:
    audit = {"vulnerabilities": {}, "metadata": {"vulnerabilities": {}}, "_error": str(e)}

vulns = audit.get("vulnerabilities", {})
rows  = ""
for name, info in vulns.items():
    sev   = info.get("severity", "").upper()
    color = {
        "CRITICAL": "#f8d7da",
        "HIGH":     "#f8d7da",
        "MODERATE": "#fff3cd",
        "LOW":      "#d1ecf1",
    }.get(sev, "#f8f9fa")
    via = ", ".join(
        str(v.get("source", v)) if isinstance(v, dict) else str(v)
        for v in info.get("via", [])
    )
    rows += (
        '<tr style="background:' + color + '">'
        "<td>" + h.escape(name) + "</td>"
        "<td>" + h.escape(sev) + "</td>"
        "<td>" + h.escape(info.get("range", "")) + "</td>"
        "<td>" + h.escape(str(info.get("fixAvailable", ""))) + "</td>"
        '<td style="font-size:.8em">' + h.escape(via[:120]) + "</td>"
        "</tr>"
    )

total = audit.get("metadata", {}).get("vulnerabilities", {})
summary_parts = [k + ": <strong>" + str(v) + "</strong>" for k, v in total.items() if v]
summary_line  = " | ".join(summary_parts) if summary_parts else "No vulnerabilities found"

no_vulns = '<tr><td colspan="5">No vulnerabilities</td></tr>'

report = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SCA Report - npm audit</title>
  <style>
    body { font-family: sans-serif; margin: 2rem; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: .5rem; text-align: left; word-break: break-word; }
    th { background: #343a40; color: #fff; }
  </style>
</head>
<body>
  <h1>SCA Report - npm audit</h1>
  <p>""" + summary_line + """</p>
  <table>
    <tr><th>Package</th><th>Severity</th><th>Range</th><th>Fix Available</th><th>Via</th></tr>
    """ + (rows if rows else no_vulns) + """
  </table>
  <hr>
  <p>See also <code>trivy-sca-report.html</code> artifact for Trivy analysis.</p>
</body>
</html>"""

with open("sca-report.html", "w") as f:
    f.write(report)

counts = audit.get("metadata", {}).get("vulnerabilities", {})
print("SCA:", counts)
