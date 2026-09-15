# Verification record

Recorded: 2026-09-15

## TDD evidence

1. Wrote six CLI behavior tests before implementation.
2. Ran the suite first: 6 failed because `whenfound.cli` did not exist (`ModuleNotFoundError`).
3. Implemented the smallest parser, preview, exporter, and iCalendar renderer needed by those tests.
4. Added a regression test proving an oversized file is rejected before UTF-8 decoding.
5. Ran the focused regression first: it failed with the old pre-read behavior, then passed after the input boundary fix.
6. Ran the suite again: 7 passed.

## Real input run

Input: [`examples/appointment.txt`](../examples/appointment.txt)

```console
whenfound preview examples/appointment.txt
```

Observed result:

```text
WHENFOUND: REVIEW BEFORE IMPORT
Title: Design review
Start: 2026-09-18 09:30
End: 2026-09-18 10:45
Timezone: America/Vancouver
Location: Vancouver Library
Confidence: high
No file written. Run `whenfound export ... --output event.ics` to create it.
```

Explicit export:

```console
whenfound export examples/appointment.txt --output design-review.ics
```

Observed result: `Wrote design-review.ics`; output contained `BEGIN:VCALENDAR`, the reviewed summary, `DTSTART;TZID=America/Vancouver:20260918T093000`, `DTEND;TZID=America/Vancouver:20260918T104500`, location, description, and provenance warning fields where applicable. The installed-wheel smoke export was also written to `smoke-output.ics` and hashed as `5c65514c34ddb5f04516e2d99b984612d9f617e54efa8321f42f71dbcd780113`.

## Local checks

| Check | Result |
| --- | --- |
| Unit/integration tests | 7 passed |
| Ruff lint | pass: `All checks passed!` |
| Ruff format | pass: 11 files already formatted |
| Mypy strict | pass: no issues in 5 source files |
| Build wheel/sdist | pass: wheel and sdist created; wheel SHA-256 `e5e2b7a816c7bd04324ff08a6bc877194dacfb1f414ddbf5276b0f08f93539cb`; sdist SHA-256 `add1ec24e7a7499462fb7716a5e26594bef86a2c99eb2de1740119e24ed61d1d` |
| Package smoke test | pass: isolated wheel install, preview, and export |
| Dependency audit | pass for built artifact path; global environment audit separately found unrelated `httpcore2`/`httpx2` advisories and unpublished local packages |
| Security scan | pass: Codex Security scan `40d62cad-b0cb-4602-9f46-da99172874bf`; 16/16 surfaces reviewed; 0 reportable findings; Daybreak access unavailable, and the current tree was manually re-reviewed after the final file-size guard |
| Git diff check | pending until final verification |
| GitHub Actions | pending until push |
| Release | pending until CI is green |

This record is updated only after each command is run fresh.
