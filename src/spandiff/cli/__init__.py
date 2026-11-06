"""Public command entry point. Importing the CLI never starts an experiment."""

import argparse
from pathlib import Path
import sys
from collections.abc import Sequence
from uuid import uuid4

from spandiff import __version__
from spandiff.collection import ImportValidationError, import_otlp_json
from spandiff.reporting import ResultV1
from spandiff.orchestration import run_doctor


class CliParser(argparse.ArgumentParser):
    """Use the project contract for invalid command-line input."""

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(3, f"{self.prog}: error: {message}\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Parse commands and return the documented process exit status."""
    parser = CliParser(
        prog="spandiff",
        description="Compare API request traces across code revisions.",
        epilog="Development foundation: comparison is not implemented yet.",
    )
    parser.add_argument("--version", action="version", version=f"SpanDiff {__version__}")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("version", help="Show the installed SpanDiff version.")
    import_parser = commands.add_parser("import", help="Import a baseline and candidate OTLP JSON pair.")
    import_parser.add_argument("--baseline", required=True, help="Baseline OTLP JSON path.")
    import_parser.add_argument("--candidate", required=True, help="Candidate OTLP JSON path.")
    import_parser.add_argument("--output", help="Optional ResultV1 JSON output path.")
    doctor_parser = commands.add_parser("doctor", help="Check configured prerequisites without starting services.")
    doctor_parser.add_argument("--config", required=True, help="Repository configuration YAML path.")
    doctor_parser.add_argument("--repo-root", help="Repository root used for relative checks.")
    args = parser.parse_args(argv)
    if args.command == "version":
        print(f"SpanDiff {__version__}")
    elif args.command == "import":
        return _import_pair(args.baseline, args.candidate, args.output)
    elif args.command == "doctor":
        try:
            report = run_doctor(args.config, repo_root=args.repo_root)
        except Exception as exc:
            print(f"spandiff: doctor failed: {exc}", file=sys.stderr)
            return 3
        for check in report.checks:
            print(f"{'ok' if check.ok else 'missing'} {check.name}: {check.detail}")
        return 0 if report.ok else 4
    else:
        parser.print_help()
    return 0


def _import_pair(baseline_path: str, candidate_path: str, output_path: str | None) -> int:
    try:
        baseline = import_otlp_json(Path(baseline_path).read_text(encoding="utf-8"))
        candidate = import_otlp_json(Path(candidate_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ImportValidationError) as exc:
        print(f"spandiff: import failed: {exc}", file=sys.stderr)
        return 3
    # Imported OTLP alone has no request denominator, so it cannot support a
    # comparable per-request verdict yet.
    complete = False
    result = ResultV1(
        experiment_id=f"import-{uuid4().hex}",
        result_state="complete" if complete else "incomplete",
        variants=("baseline", "candidate"),
        coverage={"complete": complete, "baseline_spans": len(baseline.spans), "candidate_spans": len(candidate.spans), "request_denominator": None},
        findings=(),
        provenance={"mode": "import", "baseline": str(Path(baseline_path)), "candidate": str(Path(candidate_path))},
        cleanup_state="not_applicable",
    )
    text = result.to_json() + "\n"
    try:
        if output_path:
            Path(output_path).write_text(text, encoding="utf-8")
        else:
            print(text, end="")
    except OSError as exc:
        print(f"spandiff: cannot write result: {exc}", file=sys.stderr)
        return 4
    return 0 if complete else 2
