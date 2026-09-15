# WhenFound

## Don’t retype the date hiding in a message.

WhenFound turns one copied email, chat message, or note into a **reviewable `.ics` calendar file** — locally, with no account, no cloud, and no silent guesses.

```text
paste text  →  inspect the event  →  explicitly export .ics  →  import into any calendar
```

It exists for the small but repeated moment when a date is clear enough to notice, yet annoying enough to type again. WhenFound shows the title, date, time, timezone, location, confidence, and warnings before it writes anything.

## The 20-second demo

```console
$ whenfound preview examples/appointment.txt
WHENFOUND: REVIEW BEFORE IMPORT
Title: Design review
Start: 2026-09-18 09:30
End: 2026-09-18 10:45
Timezone: America/Vancouver
Location: Vancouver Library
Confidence: high
No file written. Run `whenfound export ... --output event.ics` to create it.

$ whenfound export examples/appointment.txt --output design-review.ics
Wrote design-review.ics
```

The generated file opens in Google Calendar, Apple Calendar, Outlook, and other iCalendar clients.

## Install

Requires Python 3.10 or newer.

```console
python -m pip install whenfound
```

Or install the public source checkout:

```console
git clone https://github.com/juwonllee2024-dotcom/whenfound.git
cd whenfound
python -m pip install -e .
```

## Use

Preview a text file. Preview never writes a file:

```console
whenfound preview message.txt
```

Use literal text when the message is already in your clipboard or shell:

```console
whenfound preview --text "Dentist\n2026-09-18 at 9:00 AM"
```

Use stdin:

```console
type message.txt | whenfound preview -
```

Export only after reviewing the preview:

```console
whenfound export message.txt --output event.ics
```

Relative phrases use today’s date. Pin it for a reproducible result:

```console
whenfound preview --text "Call\ntomorrow at 9 AM" --today 2026-09-14
```

When a time has no timezone, WhenFound leaves it as a floating local time and warns you. It refuses ambiguous numeric dates such as `03/04/2026` and messages containing multiple different dates instead of choosing silently.

## Input format

The first ordinary line becomes the title. These labeled lines are optional:

```text
Design review
September 18, 2026
09:30 AM - 10:45 AM
Location: Vancouver Library
Timezone: America/Vancouver
Description: Bring the draft plan
```

Supported dates: `YYYY-MM-DD`, written month names, `today`, `tomorrow`, and weekdays such as `next Tuesday`.

Supported times: `9 AM`, `09:30`, and a two-time range. One event is accepted per input. A second different date, an ambiguous slash date, or more than two times fails closed.

## What makes it different

Calendar integrations usually start inside one provider. WhenFound starts at the boundary where the information actually arrives: a text block in an email, chat, issue, or note. It produces a standard file rather than taking control of a calendar account.

The product promise is narrow:

- local deterministic parsing; no AI model and no network request;
- visible preview before export;
- no calendar API, account login, automatic invite, or background watcher;
- explicit output path and no overwrite unless `--force` is supplied;
- iCalendar text escaping and UTF-8 line folding;
- warnings when timezone or title is incomplete.

WhenFound is a parser and exporter, not a promise that a date in the source is correct. Review the event before importing it.

## First-user experiment

First users are people who move events from email, chat, support tickets, school notices, and community posts into a calendar. The seven-day test is to give the CLI to ten such users and observe whether five can turn a real message into an `.ics` file without a tutorial, then whether three use it again.

Revenue is only a hypothesis: keep the local core free and open; consider paid team templates or support only if repeat use proves that the import boundary saves meaningful time. No revenue or adoption is promised.

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

The complete recorded verification is in [`docs/verification.md`](docs/verification.md). Product research and the first experiment are in [`docs/research/2026-09-15-founder-note.md`](docs/research/2026-09-15-founder-note.md).

## Safety and privacy

WhenFound reads only text you explicitly pass to the command and writes only the output path you explicitly choose. It makes no network requests, starts no subprocesses, watches no clipboard, and never changes a calendar. The parser caps input at 1 MiB and escapes calendar fields so source text cannot add new iCalendar properties. See [`SECURITY.md`](SECURITY.md).

## Roadmap

- browser “send to WhenFound” action that still requires a click and shows the same preview;
- more locale-aware written dates with an explicit locale flag;
- a local verifier for imported `.ics` files;
- no inbox or calendar account integration until the core boundary is proven.

## Contributing

Small, test-backed changes welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) first.

## License

MIT. See [`LICENSE`](LICENSE).
