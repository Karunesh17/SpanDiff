"""Self-contained offline HTML report rendering."""

from __future__ import annotations

from html import escape
import json
import re

from .result import ResultV1, result_from_json


_STYLE = """
:root { color-scheme: light; font-family: system-ui, sans-serif; line-height: 1.45; }
body { margin: 0 auto; max-width: 72rem; padding: 2rem; color: #17202a; background: #fff; }
header, section { border: 1px solid #c7d0d9; border-radius: .5rem; margin: 0 0 1rem; padding: 1rem; }
h1, h2 { margin-top: 0; } .state { font-weight: 700; padding: .25rem .5rem; border-radius: .25rem; }
.state-incomplete, .state-cleanup { background: #fff2cc; border: 1px solid #9a6700; }
.state-complete { background: #dff6dd; border: 1px solid #216e39; }
dt { font-weight: 700; } dd { margin: 0 0 .5rem; overflow-wrap: anywhere; }
table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #c7d0d9; padding: .5rem; text-align: left; vertical-align: top; }
*:focus-visible { outline: 3px solid #005fcc; outline-offset: 2px; }
@media (max-width: 42rem) { body { padding: .75rem; } table { display: block; overflow-x: auto; } }
@media print { body { max-width: none; padding: 0; color: #000; background: #fff; } header, section { break-inside: avoid; border-color: #000; } a { color: #000; text-decoration: underline; } }
""".strip()


def _text(value: object) -> str:
    return escape(str(value), quote=True)


def _anchor(value: object, prefix: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.:-]+", "-", str(value)).strip("-") or "unknown"
    return f"{prefix}-{safe}"


def render_html(result: ResultV1) -> str:
    """Render a report with inline CSS and escaped data only."""
    coverage = result.coverage
    state_class = "state-complete" if result.result_state == "complete" else "state-incomplete"
    variants = "".join(f"<li>{_text(variant)}</li>" for variant in result.variants) or "<li>None recorded</li>"
    coverage_rows = "".join(
        f"<tr><th scope=\"row\">{_text(key)}</th><td>{_text(value)}</td></tr>"
        for key, value in sorted(coverage.items())
    ) or "<tr><td colspan=\"2\">No coverage data recorded</td></tr>"
    finding_rows = "".join(
        "<tr><td><a href=\"#" + _anchor(finding.get("finding_id"), "finding") + "\">"
        + _text(finding.get("finding_id", "unknown")) + "</a></td><td>"
        + _text(finding.get("rule_id", finding.get("summary", "Unspecified finding")))
        + "</td><td>" + _text(finding.get("uncertainty", "Uncertainty not recorded")) + "</td></tr>"
        for finding in result.findings
    ) or "<tr><td colspan=\"3\">No findings recorded</td></tr>"
    finding_details = "".join(
        "<article id=\"" + _anchor(finding.get("finding_id"), "finding") + "\"><h3>"
        + _text(finding.get("finding_id", "unknown")) + "</h3><dl><dt>Rule</dt><dd>"
        + _text(finding.get("rule_id", "Unspecified")) + "</dd><dt>Uncertainty</dt><dd>"
        + _text(finding.get("uncertainty", "Uncertainty not recorded")) + "</dd><dt>Source location</dt><dd>"
        + _text(finding.get("source_location", "Not recorded")) + "</dd></dl><p>Linked samples:</p>"
        + ("<ul>" + "".join("<li><a href=\"#" + _anchor(sample, "sample") + "\">" + _text(sample) + "</a></li>" for sample in finding.get("sample_ids", ())) + "</ul>"
           if finding.get("sample_ids") else "<p>No linked samples recorded.</p>")
        + "</article>"
        for finding in result.findings
    ) or "<p>No finding details recorded.</p>"
    sample_ids = sorted({sample for finding in result.findings for sample in finding.get("sample_ids", ())})
    sample_details = "".join(
        f"<p id=\"{_anchor(sample, 'sample')}\"><strong>Sample:</strong> {_text(sample)} — source span detail is not recorded in this result.</p>"
        for sample in sample_ids
    ) or "<p>No sample evidence recorded.</p>"
    cleanup_class = "state-complete" if result.cleanup_state in {"clean", "not_applicable"} else "state-cleanup"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SpanDiff report — {_text(result.experiment_id)}</title><style>{_STYLE}</style></head>
<body><header><h1>SpanDiff comparison report</h1>
<p><strong>Experiment:</strong> {_text(result.experiment_id)}</p>
<p>Result state: <span class="state {state_class}">{_text(result.result_state)}</span></p>
<p>Cleanup state: <span class="state {cleanup_class}">{_text(result.cleanup_state)}</span></p></header>
<main><section><h2>Variants</h2><ul>{variants}</ul></section>
<section><h2>Coverage summary</h2><table><thead><tr><th scope="col">Field</th><th scope="col">Value</th></tr></thead><tbody>{coverage_rows}</tbody></table></section>
<section><h2>Findings</h2><table><thead><tr><th scope="col">Evidence ID</th><th scope="col">Rule</th><th scope="col">Uncertainty</th></tr></thead><tbody>{finding_rows}</tbody></table>{finding_details}</section>
<section><h2>Sample evidence</h2>{sample_details}</section>
<section><h2>Provenance</h2><pre>{_text(json.dumps(dict(result.provenance), sort_keys=True, ensure_ascii=False, indent=2))}</pre></section></main>
</body></html>"""


def render_html_json(text: str) -> str:
    """Validate ResultV1 JSON before rendering it."""
    return render_html(result_from_json(text))
