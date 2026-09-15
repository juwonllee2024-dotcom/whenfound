from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

from .core import MAX_INPUT_BYTES, EventDraft, WhenFoundError, parse_text
from .ics import render_ics


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        source = _read_source(args.source, args.text)
        event = parse_text(
            source,
            today=_parse_today(args.today),
            title=args.title,
            timezone_name=args.timezone,
        )
        if args.command == "preview":
            print(_preview(event))
            return 0
        _export(event, Path(args.output), force=args.force)
        print(f"Wrote {args.output}")
        return 0
    except (WhenFoundError, OSError, UnicodeError) as exc:
        print(f"whenfound: {exc}", file=sys.stderr)
        return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="whenfound",
        description="Turn one date hidden in text into a reviewable calendar file without guessing.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("preview", "export"):
        subparser = subparsers.add_parser(command, help=f"{command} one event")
        subparser.add_argument("source", nargs="?", help="UTF-8 text file, or - for stdin")
        subparser.add_argument("--text", help="Use literal text instead of a file")
        subparser.add_argument(
            "--today", default=None, help="Reference date for relative phrases (YYYY-MM-DD)"
        )
        subparser.add_argument("--title", help="Explicit event title")
        subparser.add_argument("--timezone", help="Explicit timezone, such as America/Vancouver")
        if command == "preview":
            subparser.set_defaults(command="preview")
        else:
            subparser.add_argument("--output", required=True, help="Destination .ics path")
            subparser.add_argument(
                "--force", action="store_true", help="Allow replacing an existing output"
            )
            subparser.set_defaults(command="export")
    return parser


def _read_source(source_path: str | None, literal: str | None) -> str:
    if source_path and literal is not None:
        raise WhenFoundError("choose a file or --text, not both")
    if literal is not None:
        return literal
    if source_path in (None, "-"):
        value = sys.stdin.read(MAX_INPUT_BYTES + 1)
        if len(value.encode("utf-8")) > MAX_INPUT_BYTES:
            raise WhenFoundError("input is larger than the 1 MiB safety limit")
        return value
    path = Path(source_path)
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise WhenFoundError("input is larger than the 1 MiB safety limit")
    return path.read_text(encoding="utf-8")


def _parse_today(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise WhenFoundError("--today must use YYYY-MM-DD") from exc


def _preview(event: EventDraft) -> str:
    lines = [
        "WHENFOUND: REVIEW BEFORE IMPORT",
        f"Title: {event.title}",
        f"Start: {_display_value(event.start)}",
        f"End: {_display_value(event.end) if event.end is not None else '(not specified)'}",
        f"Timezone: {event.timezone_name or '(not found; local calendar timezone may be used)'}",
        f"Location: {event.location or '(not specified)'}",
        f"Confidence: {event.confidence}",
    ]
    for warning in event.warnings:
        lines.append(f"Warning: {warning}")
    lines.append("No file written. Run `whenfound export ... --output event.ics` to create it.")
    return "\n".join(lines)


def _display_value(value: date | datetime | None) -> str:
    if value is None:
        return "(not specified)"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return f"{value.isoformat()} (all day)"


def _export(event: EventDraft, destination: Path, *, force: bool) -> None:
    if destination.exists() and not force:
        raise WhenFoundError(f"output already exists: {destination}; pass --force to replace it")
    if not destination.parent.exists():
        raise WhenFoundError(f"output directory does not exist: {destination.parent}")
    mode = "w" if force else "x"
    with destination.open(mode, encoding="utf-8", newline="") as handle:
        handle.write(render_ics(event))


if __name__ == "__main__":
    raise SystemExit(main())
