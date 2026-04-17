#!/usr/bin/env python3
"""Convert semgrep-results.json to sast-report.html"""
import json
import html
import os

try:
    with open("semgrep-results.json") as f:
        data = json.load(f)
except Exception as e:
    data = {"results": [], "errors": [{"message": str(e)}]}

findings = data.get("results", [])
errors   = data.get("errors", [])

rows = ""
for r in findings:
    sev   = r.get("extra", {}).get("severity", "INFO")
    color = {"ERROR": "#f8d7da", "WARNING": "#fff3cd", "INFO": "#d1ecf1"}.get(sev, "#f8f9fa")
    rows += (
        '<tr style="background:' + color + '">'
        "<td>" + html.escape(r.get("check_id", "")) + "</td>"
        "<td>" + html.escape(sev) + "</td>"
        "<td>" + html.escape(r.get("path", "")) + ":" + str(r.get("start", {}).get("line", "")) + "</td>"
        "<td>" + html.escape(r.get("extra", {}).get("message", "")) + "</td>"
        "</tr>"
    )

no_findings = '<tr><td colspan="4">No findings</td></tr>'

report = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SAST Report - Semgrep</title>
  <style>
    body { font-family: sans-serif; margin: 2rem; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: .5rem; text-align: left; }
    th { background: #343a40; color: #fff; }
  </style>
</head>
<body>
  <h1>SAST Report - Semgrep</h1>
  <p>Findings: <strong>""" + str(len(findings)) + """</strong> &nbsp;|&nbsp; Errors: <strong>""" + str(len(errors)) + """</strong></p>
  <table>
    <tr><th>Rule</th><th>Severity</th><th>Location</th><th>Message</th></tr>
    """ + (rows if rows else no_findings) + """
  </table>
</body>
</html>"""

with open("sast-report.html", "w") as f:
    f.write(report)

print("SAST: " + str(len(findings)) + " finding(s)")
