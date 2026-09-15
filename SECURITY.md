# Security policy

## Boundary

WhenFound is a local parser and `.ics` writer. It reads UTF-8 text that a user explicitly gives it and writes one explicitly chosen output path. It does not read a clipboard, connect to a calendar account, make network requests, start subprocesses, execute source text, or run in the background.

Input is untrusted data. The parser rejects empty or oversized input, refuses ambiguous dates, limits one event to two times, validates timezone syntax, and escapes iCalendar text fields. Export refuses to overwrite an existing path unless `--force` is explicit.

WhenFound is not a sandbox. Do not pass secrets to third-party processes or import an event you have not reviewed.

## Reporting a vulnerability

Do not open a public issue for a security-sensitive report. Use GitHub’s private vulnerability reporting for this repository when available. Include:

- affected version and operating system;
- the exact command and a minimal non-sensitive input;
- expected and observed behavior;
- whether the issue can write outside the chosen output path, add iCalendar fields, or cause network/process activity.

Do not include passwords, access tokens, private calendar data, or real personal information. We will acknowledge a report when practical and publish a fix or mitigation when verified.

## Supported versions

Only the latest public release receives security fixes. The project is alpha software; review generated calendar files before importing them.
