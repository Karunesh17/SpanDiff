"""Accessible static CSS trace waterfall rendering."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from collections.abc import Sequence


class WaterfallError(ValueError):
    """Raised for invalid or unbounded waterfall observations."""


@dataclass(frozen=True)
class WaterfallSpan:
    span_id: str
    name: str
    start_ns: int
    end_ns: int
    kind: str = "operation"
    background: bool = False


def render_waterfall(spans: Sequence[WaterfallSpan], *, observation_start_ns: int | None = None,
                     observation_end_ns: int | None = None) -> str:
    """Render CSS bars plus an ordered text fallback; durations are never summed."""
    if not spans:
        return '<section aria-labelledby="waterfall-title"><h2 id="waterfall-title">Trace waterfall</h2><p>No spans recorded.</p></section>'
    start = min(span.start_ns for span in spans) if observation_start_ns is None else observation_start_ns
    end = max(span.end_ns for span in spans) if observation_end_ns is None else observation_end_ns
    if end <= start:
        raise WaterfallError("observation bounds: end must be greater than start")
    for span in spans:
        if span.end_ns < span.start_ns or span.start_ns < start or span.end_ns > end:
            raise WaterfallError(f"span {span.span_id}: outside observation bounds")
    width = end - start
    rows: list[str] = []
    text_rows: list[str] = []
    for index, span in enumerate(spans):
        left = (span.start_ns - start) * 100 / width
        bar_width = max(0.25, (span.end_ns - span.start_ns) * 100 / width)
        label = f"{span.name} ({span.kind}{', background' if span.background else ''})"
        rows.append(
            f'<div class="wf-row"><span class="wf-label">{escape(label, quote=True)}</span>'
            f'<span class="wf-track"><span class="wf-bar wf-{"background" if span.background else "foreground"}" '
            f'style="left:{left:.4f}%;width:{bar_width:.4f}%" title="{escape(label, quote=True)}; '
            f'{span.end_ns - span.start_ns} ns">{escape(span.name, quote=True)}</span></span></div>'
        )
        text_rows.append(
            f'<li>{escape(span.name, quote=True)} — {span.end_ns - span.start_ns} ns; '
            f'{escape(span.kind, quote=True)}{"; background" if span.background else ""}</li>'
        )
    return f'''<section aria-labelledby="waterfall-title"><h2 id="waterfall-title">Trace waterfall</h2>
<style>.wf-row{{display:flex;gap:.5rem;margin:.35rem 0;align-items:center}}.wf-label{{width:14rem;overflow-wrap:anywhere}}.wf-track{{position:relative;min-height:1.5rem;flex:1;background:#edf0f2;border:1px solid #c7d0d9}}.wf-bar{{position:absolute;top:.15rem;bottom:.15rem;overflow:hidden;padding:0 .2rem;box-sizing:border-box;white-space:nowrap}}.wf-foreground{{background:#6baed6;color:#102a43}}.wf-background{{background:#f6c85f;color:#3d2b00}}</style>
<p>Observation: {end - start} ns; bars show position and individual duration, not a sum.</p>
<div aria-label="Visual trace waterfall">{"".join(rows)}</div>
<h3>Ordered span text</h3><ol>{"".join(text_rows)}</ol></section>'''
