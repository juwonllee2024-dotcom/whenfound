# Contributing

Thanks for improving WhenFound.

## Ground rules

- Keep the core local, deterministic, and dependency-free.
- Do not add automatic calendar writes, background clipboard watchers, network calls, or hidden telemetry.
- Every behavior change needs a focused test. Follow the red-green-refactor cycle.
- Keep ambiguous input visible or rejected. Do not silently guess.
- Never commit private messages, calendar data, credentials, or generated build artifacts.

## Development

```console
python -m pip install -e ".[dev]"
python -m pytest -q
ruff check .
ruff format --check .
mypy
python -m build
pip-audit --local
```

Use a fresh branch for changes. Explain the user pain, the smallest behavior change, and the verification result in the pull request. Add a fixture when a new date or time shape is supported.

## Pull requests

Keep pull requests small. Include:

1. the problem and intended user;
2. the observable behavior changed;
3. tests, including an ambiguity or failure case when relevant;
4. privacy and security impact;
5. documentation and changelog updates.
