#!/usr/bin/env python3
"""Write a GitHub Step Summary block from an oasis-pub-check JSON report.

Reads pubcheck-report.json (produced with --json) and pubcheck-report.txt
(the human-readable ordered findings list, produced by the same tool without
--json) for one matrix package, and appends a summary section to
$GITHUB_STEP_SUMMARY so a TC member opening the run page sees the actual
findings without opening raw logs.

Env vars (set by the workflow step):
  PKG_NAME    human-readable package label, e.g. "ACAL core v1.0 csd02"
  PKG_TARGET  the target path/zip that was checked
  REPORT_JSON path to the --json report file
  REPORT_TXT  path to the plain-text report file
"""
import json
import os
import sys

pkg_name = os.environ.get("PKG_NAME", "package")
pkg_target = os.environ.get("PKG_TARGET", "")
report_json_path = os.environ.get("REPORT_JSON", "pubcheck-report.json")
report_txt_path = os.environ.get("REPORT_TXT", "pubcheck-report.txt")
summary_path = os.environ["GITHUB_STEP_SUMMARY"]

with open(report_json_path) as f:
    report = json.load(f)

findings = report.get("findings", [])
blockers = sum(1 for x in findings if x.get("severity") == "BLOCKER")
warnings = sum(1 for x in findings if x.get("severity") == "WARN")
infos = sum(1 for x in findings if x.get("severity") == "INFO")
verdict = "NOT PUBLISHABLE" if blockers else "PUBLISHABLE"

try:
    with open(report_txt_path) as f:
        txt_body = f.read().rstrip("\n")
except FileNotFoundError:
    txt_body = "(no text report produced)"

with open(summary_path, "a") as s:
    s.write(f"## pub-check: {pkg_name}\n\n")
    s.write(f"Target: `{pkg_target}`\n\n")
    s.write(
        f"**{blockers} blocker(s), {warnings} warning(s), {infos} info "
        f"-> {verdict}**\n\n"
    )
    s.write("<details>\n<summary>Full findings list (ordered)</summary>\n\n")
    s.write("```\n")
    s.write(txt_body)
    s.write("\n```\n\n")
    s.write("</details>\n\n")
    s.write(
        f"Full reports: `pubcheck-report-{os.environ.get('PKG_ID', pkg_name)}` "
        "artifact (this run's Artifacts section).\n\n"
    )
    s.write("---\n\n")

print(f"{pkg_name}: {blockers} blocker(s), {warnings} warning(s) -> {verdict}")
sys.exit(0)
