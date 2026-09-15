from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta, timezone

from .core import EventDraft

FIXED_OFFSETS = {
    "UTC": timedelta(0),
    "PST": timedelta(hours=-8),
    "PDT": timedelta(hours=-7),
    "MST": timedelta(hours=-7),
    "MDT": timedelta(hours=-6),
    "CST": timedelta(hours=-6),
    "CDT": timedelta(hours=-5),
    "EST": timedelta(hours=-5),
    "EDT": timedelta(hours=-4),
    "KST": timedelta(hours=9),
    "JST": timedelta(hours=9),
}


def render_ics(
    event: EventDraft,
    *,
    uid: str | None = None,
    dtstamp: datetime | None = None,
) -> str:
    """Render a single RFC 5545-compatible event with visible provenance fields."""

    event_uid = uid or _event_uid(event)
    stamp = dtstamp or datetime.now(timezone.utc)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    stamp_utc = stamp.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//WhenFound//Reviewable event//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{escape_text(event_uid)}",
        f"DTSTAMP:{stamp_utc}",
    ]
    lines.append(_date_line("DTSTART", event.start, event.timezone_name, event.all_day))
    if event.end is not None:
        lines.append(_date_line("DTEND", event.end, event.timezone_name, event.all_day))
    lines.append(f"SUMMARY:{escape_text(event.title)}")
    if event.location:
        lines.append(f"LOCATION:{escape_text(event.location)}")
    if event.description:
        lines.append(f"DESCRIPTION:{escape_text(event.description)}")
    lines.append(f"X-WHENFOUND-CONFIDENCE:{escape_text(event.confidence)}")
    for warning in event.warnings:
        lines.append(f"X-WHENFOUND-WARNING:{escape_text(warning)}")
    lines.extend(["END:VEVENT", "END:VCALENDAR"])
    return "\r\n".join(fold_line(line) for line in lines) + "\r\n"


def escape_text(value: str) -> str:
    """Escape iCalendar TEXT characters without allowing new properties."""

    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\r", "\\n")
        .replace("\n", "\\n")
    )


def fold_line(line: str, limit: int = 75) -> str:
    """Fold a content line at UTF-8 octet boundaries."""

    encoded = line.encode("utf-8")
    if len(encoded) <= limit:
        return line
    pieces: list[str] = []
    remaining = encoded
    first = True
    while remaining:
        available = limit if first else limit - 1
        cut = _safe_cut(remaining, available)
        pieces.append(remaining[:cut].decode("utf-8"))
        remaining = remaining[cut:]
        first = False
    return "\r\n ".join(pieces)


def _safe_cut(value: bytes, limit: int) -> int:
    cut = min(len(value), limit)
    while cut > 0:
        try:
            value[:cut].decode("utf-8")
            return cut
        except UnicodeDecodeError:
            cut -= 1
    raise ValueError("unable to fold UTF-8 content line")


def _date_line(name: str, value: date | datetime, zone: str | None, all_day: bool) -> str:
    if all_day:
        assert isinstance(value, date) and not isinstance(value, datetime)
        if name == "DTEND":
            value = value + timedelta(days=1)
        return f"{name};VALUE=DATE:{value.strftime('%Y%m%d')}"

    assert isinstance(value, datetime)
    if zone in FIXED_OFFSETS:
        aware = value.replace(tzinfo=timezone(FIXED_OFFSETS[zone]))
        return f"{name}:{aware.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    local = value.strftime("%Y%m%dT%H%M%S")
    return f"{name};TZID={zone}:{local}" if zone else f"{name}:{local}"


def _event_uid(event: EventDraft) -> str:
    start = event.start.isoformat()
    material = f"{event.title}\x1f{start}\x1f{event.location}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return f"{digest}@whenfound.local"
