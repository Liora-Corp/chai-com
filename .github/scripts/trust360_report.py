"""
trust360_report.py
Reads scan.json from the working directory and writes:
  - trust360-report.html  (full styled HTML report)
  - trust360-summary.json (clean JSON for downstream tooling)
"""
import datetime
import html as h
import json
import os
import sys


def load_scan():
    path = os.environ.get("SCAN_JSON", "scan.json")
    with open(path) as f:
        return json.load(f)


def pill(sev, sev_style):
    s = sev_style.get(sev, "background:#888;color:#fff")
    return (
        f'<span style="padding:2px 10px;border-radius:12px;'
        f'font-size:.75rem;font-weight:700;{s}">{sev}</span>'
    )


def count_card(label, n, style):
    return (
        f'<div style="text-align:center;padding:20px;border-radius:8px;{style}">'
        f'<div style="font-size:2.4rem;font-weight:900">{n}</div>'
        f'<div style="font-size:.78rem;margin-top:6px;opacity:.85;'
        f'text-transform:uppercase;letter-spacing:.06em">{label}</div>'
        f"</div>"
    )


def build_html(d):
    fc = d.get("findingCounts", {})
    diff = d.get("diffMeta", {})
    gate = d.get("gate", "UNKNOWN")
    findings = d.get("findings", [])
    files = diff.get("filesChanged", [])

    gate_clr = {"BLOCKED": "#c0392b", "PASS": "#27ae60"}.get(gate, "#7f8c8d")
    sev_style = {
        "CRITICAL": "background:#c0392b;color:#fff",
        "HIGH": "background:#e67e22;color:#fff",
        "MEDIUM": "background:#f1c40f;color:#333",
        "LOW": "background:#3498db;color:#fff",
    }

    finding_rows = "".join(
        "<tr>"
        f"<td><code>{h.escape(fx.get('id',''))}</code></td>"
        f"<td>{pill(fx.get('severity',''), sev_style)}</td>"
        f"<td><code>{h.escape(fx.get('file',''))}:{fx.get('line','')}</code></td>"
        f"<td><strong>{h.escape(fx.get('title',''))}</strong>"
        f"<br><small style='color:#666'>{h.escape(fx.get('detail',''))}</small></td>"
        "</tr>"
        for fx in findings
    )

    files_li = "".join(f"<li><code>{h.escape(f)}</code></li>" for f in files)
    raw_diff = h.escape(diff.get("rawDiff", "(no diff available)"))
    total = sum(fc.values())
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    findings_block = ""
    if findings:
        findings_block = (
            '<div class="card">'
            f"<h2>Findings ({len(findings)})</h2>"
            "<table>"
            "<tr><th>ID</th><th>Severity</th><th>Location</th><th>Detail</th></tr>"
            f"{finding_rows}"
            "</table></div>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Security Gate Review &mdash; {h.escape(d.get('prTitle', ''))}</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:system-ui,sans-serif;background:#f0f2f5;color:#1a1a1a}}
    .banner{{background:{gate_clr};color:#fff;padding:28px 40px}}
    .banner h1{{font-size:1.3rem;font-weight:800;letter-spacing:.02em}}
    .banner .sub{{font-size:.88rem;opacity:.8;margin-top:4px}}
    .gate-pill{{display:inline-block;margin-top:14px;padding:7px 22px;
      border-radius:6px;font-size:1.2rem;font-weight:900;letter-spacing:.1em;
      border:2px solid rgba(255,255,255,.35);background:rgba(0,0,0,.15)}}
    .wrap{{max-width:960px;margin:28px auto;padding:0 20px}}
    .reason{{background:#fff;border-left:5px solid {gate_clr};padding:14px 18px;
      border-radius:0 8px 8px 0;font-size:.9rem;margin-bottom:24px;
      box-shadow:0 1px 4px rgba(0,0,0,.08)}}
    .card{{background:#fff;border-radius:10px;padding:22px 26px;margin-bottom:22px;
      box-shadow:0 1px 4px rgba(0,0,0,.08)}}
    .card h2{{font-size:.95rem;font-weight:700;padding-bottom:10px;margin-bottom:16px;
      border-bottom:1px solid #eee;text-transform:uppercase;letter-spacing:.04em;color:#555}}
    .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
    table{{width:100%;border-collapse:collapse;font-size:.86rem}}
    th{{text-align:left;padding:9px 12px;background:#f7f8fa;border-bottom:2px solid #e4e4e4;
      font-size:.78rem;text-transform:uppercase;letter-spacing:.04em;color:#666}}
    td{{padding:10px 12px;border-bottom:1px solid #f2f2f2;vertical-align:top}}
    tr:last-child td{{border-bottom:none}}
    pre{{background:#16213e;color:#e2e8f0;padding:18px;border-radius:8px;
      font-size:.79rem;overflow-x:auto;white-space:pre;line-height:1.6}}
    ul{{padding-left:20px;line-height:2}}
    .footer{{text-align:center;color:#bbb;font-size:.76rem;padding:32px 0 20px}}
    @media(max-width:580px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
  </style>
</head>
<body>
  <div class="banner">
    <h1>Security Gate Review</h1>
    <p class="sub">
      {h.escape(d.get('prNumber', ''))} &middot;
      {h.escape(d.get('prTitle', ''))} &middot;
      {h.escape(d.get('serviceName', ''))}
    </p>
    <div class="gate-pill">{gate}</div>
  </div>

  <div class="wrap">
    <div class="reason">
      <strong>Gate decision:</strong> {h.escape(d.get('gateReason', ''))}
    </div>

    <div class="card">
      <h2>Finding Counts &nbsp;<span style="font-weight:400;color:#aaa">(total {total})</span></h2>
      <div class="grid">
        {count_card("Critical", fc.get("critical", 0), sev_style["CRITICAL"])}
        {count_card("High",     fc.get("high",     0), sev_style["HIGH"])}
        {count_card("Medium",   fc.get("medium",   0), sev_style["MEDIUM"])}
        {count_card("Low",      fc.get("low",      0), sev_style["LOW"])}
      </div>
    </div>

    {findings_block}

    <div class="card">
      <h2>Pull Request</h2>
      <table>
        <tr><th>Field</th><th>Value</th></tr>
        <tr><td>PR</td>
            <td><a href="{h.escape(diff.get('prLink', '#'))}">{h.escape(d.get('prNumber', ''))}</a></td></tr>
        <tr><td>Title</td><td>{h.escape(d.get('prTitle', ''))}</td></tr>
        <tr><td>Author</td><td><code>{h.escape(d.get('prAuthor', ''))}</code></td></tr>
        <tr><td>Service</td><td><code>{h.escape(d.get('serviceName', ''))}</code></td></tr>
        <tr><td>Branch</td>
            <td><code>{h.escape(d.get('prBranch', ''))}</code>
            &rarr; <code>{h.escape(diff.get('prBaseBranch', ''))}</code></td></tr>
        <tr><td>Diff</td>
            <td>+{diff.get('insertions', 0)} / -{diff.get('deletions', 0)} lines
            across {len(files)} files</td></tr>
        <tr><td>CI Status</td><td><code>{h.escape(d.get('ciStatus', ''))}</code></td></tr>
        <tr><td>Completed</td><td>{h.escape(d.get('completedAt', ''))}</td></tr>
        <tr><td>Scan ID</td><td><code>{h.escape(d.get('scanId', ''))}</code></td></tr>
      </table>
    </div>

    <div class="card">
      <h2>Files Changed ({len(files)})</h2>
      <ul>{files_li}</ul>
    </div>

    <div class="card">
      <h2>Raw Diff</h2>
      <pre>{raw_diff}</pre>
    </div>
  </div>

  <div class="footer">
    Security Gate Review &middot; Scan ID: {h.escape(d.get('scanId', ''))} &middot; {ts}
  </div>
</body>
</html>"""


def build_summary(d):
    diff = d.get("diffMeta", {})
    return {
        "generatedAt": datetime.datetime.utcnow().isoformat() + "Z",
        "scanId": d.get("scanId"),
        "prNumber": d.get("prNumber"),
        "prTitle": d.get("prTitle"),
        "prAuthor": d.get("prAuthor"),
        "prBranch": d.get("prBranch"),
        "serviceName": d.get("serviceName"),
        "gate": d.get("gate"),
        "gateReason": d.get("gateReason"),
        "ciStatus": d.get("ciStatus"),
        "completedAt": d.get("completedAt"),
        "findingCounts": d.get("findingCounts", {}),
        "findings": d.get("findings", []),
        "diffMeta": {
            "filesChanged": diff.get("filesChanged", []),
            "insertions": diff.get("insertions", 0),
            "deletions": diff.get("deletions", 0),
            "prLink": diff.get("prLink", ""),
        },
    }


def write_step_summary(d):
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        return

    fc = d.get("findingCounts", {})
    diff = d.get("diffMeta", {})
    gate = d.get("gate", "UNKNOWN")
    findings = d.get("findings", [])
    files = diff.get("filesChanged", [])
    total = sum(fc.values())

    gate_emoji = {"BLOCKED": "🚫", "PASS": "✅"}.get(gate, "❓")
    sev = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}

    rows = "\n".join(
        f"| `{fx.get('id','')}` | {sev.get(fx.get('severity',''),'⚪')} "
        f"{fx.get('severity','')} | `{fx.get('file','')}:{fx.get('line','')}` "
        f"| {fx.get('title','')} |"
        for fx in findings
    )

    lines = [
        f"## {gate_emoji} Security Gate Review \u2014 {gate}",
        "",
        f"> {d.get('gateReason', '')}",
        "",
        "### Finding Counts",
        "",
        "| Severity | Count |",
        "|----------|------:|",
        f"| 🔴 Critical | **{fc.get('critical', 0)}** |",
        f"| 🟠 High     | **{fc.get('high',     0)}** |",
        f"| 🟡 Medium   | **{fc.get('medium',   0)}** |",
        f"| 🔵 Low      | **{fc.get('low',      0)}** |",
        f"| **Total**   | **{total}** |",
    ]

    if findings:
        lines += [
            "", "### Findings", "",
            "| ID | Severity | Location | Title |",
            "|----|----------|----------|-------|",
            rows,
        ]

    lines += [
        "", "### Pull Request", "",
        "| Field | Value |",
        "|-------|-------|",
        f"| PR | [{d.get('prNumber','')}]({diff.get('prLink','#')}) |",
        f"| Title | {d.get('prTitle','')} |",
        f"| Author | `{d.get('prAuthor','')}` |",
        f"| Service | `{d.get('serviceName','')}` |",
        f"| Branch | `{d.get('prBranch','')}` \u2192 `{diff.get('prBaseBranch','')}` |",
        f"| Diff | +{diff.get('insertions',0)} / -{diff.get('deletions',0)} lines, {len(files)} files |",
        f"| Scan ID | `{d.get('scanId','')}` |",
        f"| Completed | `{d.get('completedAt','')}` |",
        "", "### Files Changed", "",
    ] + [f"- `{f}`" for f in files] + [
        "",
        "---",
        "> **Artifacts:** `trust360-report.html` and `trust360-summary.json` are in the "
        "**Artifacts** section of this run (retained 90 days).",
    ]

    with open(summary_file, "a") as sf:
        sf.write("\n".join(lines) + "\n")


def write_github_output(d):
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return

    fc = d.get("findingCounts", {})
    diff = d.get("diffMeta", {})

    pairs = {
        "scan_id":      d.get("scanId", ""),
        "pr_number":    d.get("prNumber", ""),
        "pr_title":     d.get("prTitle", ""),
        "pr_author":    d.get("prAuthor", ""),
        "pr_branch":    d.get("prBranch", ""),
        "service":      d.get("serviceName", ""),
        "gate":         d.get("gate", "UNKNOWN"),
        "gate_reason":  d.get("gateReason", ""),
        "ci_status":    d.get("ciStatus", ""),
        "completed_at": d.get("completedAt", ""),
        "critical":     str(fc.get("critical", 0)),
        "high":         str(fc.get("high",     0)),
        "medium":       str(fc.get("medium",   0)),
        "low":          str(fc.get("low",      0)),
        "files_changed": str(len(diff.get("filesChanged", []))),
        "insertions":   str(diff.get("insertions", 0)),
        "deletions":    str(diff.get("deletions",  0)),
        "pr_link":      diff.get("prLink", ""),
    }

    with open(output_file, "a") as ef:
        for k, v in pairs.items():
            safe = v.replace("\n", " ").replace("\r", "")
            ef.write(f"{k}={safe}\n")

    print("GITHUB_OUTPUT written:")
    for k, v in pairs.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    d = load_scan()

    html_out = build_html(d)
    with open("trust360-report.html", "w") as f:
        f.write(html_out)
    print(f"trust360-report.html written ({len(html_out):,} bytes)")

    summary = build_summary(d)
    with open("trust360-summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("trust360-summary.json written")

    write_github_output(d)
    write_step_summary(d)
    print("Done.")
