# SpanDiff

SpanDiff is a local CLI and coding-agent skill project for comparing API request
traces across code revisions. Its intended findings cover changed operation
counts, new dependencies, errors and qualified timing changes, with sanitized
evidence for every conclusion.

## Current implementation

SD-01 through SD-22 are implemented: Python package, console entry point,
version/help commands, strict YAML repository configuration validation, and a
transactional project-partitioned SQLite evidence schema with bounded owned
storage paths plus default-deny sanitization.
Trace import, structural comparison, execution, reports and the agent skill are
partially implemented; runtime measurement and Docker orchestration remain
planned. No experiment runs when this package is imported or when configuration
is parsed.

## Development setup

Requires Python 3.11 or newer. From this directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\spandiff.exe --version
.\.venv\Scripts\spandiff.exe --help
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The foundation uses standard-library argparse. Configuration parsing uses the
PyYAML safe loader (`>=6.0,<7`), SQLGlot (`>=27.0,<28`) for PostgreSQL shape
normalization, and setuptools are used. Docker is not required for SD-13.

## Layout

`src/spandiff` contains CLI, configuration, orchestration, adapters, collection,
normalization, comparison, evidence, reporting and security packages.
`tests/fixtures`, `examples/fastapi-orders` and `skills/spandiff` reserve the
planned integration boundaries. They do not yet implement runtime behavior.

## Planning documents

The six Word documents in this root are retained project specifications.
`docs/BACKLOG.md` provides the same atomic ticket prompts in developer-friendly
form. `docs/STATUS.md` records actual implementation progress, and
`docs/DECISIONS.md` records implementation choices.

Start next with SD-36 (three-repository pilot), followed by platform packaging
and CI work.
The first milestone is two sanitized trace inputs with evidence-backed
structural findings, not automated execution.

## Safety boundaries

Do not commit credentials, raw traces or experiment artifacts. The current
version does not read trace files, start applications or persist measurements.
Future execution is limited to trusted repositories with synthetic test data.
