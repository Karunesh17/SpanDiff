"""Shared result serialization and offline reports. Implementation pending its backlog ticket."""
from .result import ResultV1, ResultValidationError, result_from_dict, result_from_json
from .verdict import Verdict, VerdictError, evaluate_verdict
from .html import render_html, render_html_json
from .waterfall import WaterfallError, WaterfallSpan, render_waterfall

__all__ = ["ResultV1", "ResultValidationError", "result_from_dict", "result_from_json",
           "Verdict", "VerdictError", "evaluate_verdict"]
__all__ += ["render_html", "render_html_json"]
__all__ += ["WaterfallError", "WaterfallSpan", "render_waterfall"]
