from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Final

MAX_INPUT_BYTES: Final = 1_000_000
WEEKDAYS: Final = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
MONTHS: Final = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}
MONTH_ALIASES: Final = {
    **MONTHS,
    **{name[:3]: number for name, number in MONTHS.items()},
}
TIMEZONE_ALIASES: Final = {
    "UTC": "UTC",
    "GMT": "UTC",
    "PST": "PST",
    "PDT": "PDT",
    "MST": "MST",
    "MDT": "MDT",
    "CST": "CST",
    "CDT": "CDT",
    "EST": "EST",
    "EDT": "EDT",
    "KST": "KST",
    "JST": "JST",
}

_ISO_DATE = re.compile(r"(?<!\d)(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})(?!\d)")
_MONTH_FIRST = re.compile(
    r"(?P<month>[A-Za-z]{3,9})\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?(?:,|\s)\s*(?P<year>\d{4})",
    re.IGNORECASE,
)
_DAY_FIRST = re.compile(
    r"(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?P<month>[A-Za-z]{3,9})\s+(?P<year>\d{4})",
    re.IGNORECASE,
)
_NUMERIC_DATE = re.compile(r"(?<!\d)(?P<first>\d{1,2})/(?P<second>\d{1,2})/(?P<year>\d{4})(?!\d)")
_TIME = re.compile(
    r"(?<![\d:])(?P<hour>\d{1,2})(?::(?P<minute>[0-5]\d))?\s*(?P<ampm>a\.?m\.?|p\.?m\.?)?(?!\d)",
    re.IGNORECASE,
)
_TIMEZONE_LINE = re.compile(
    r"(?im)^\s*(?:timezone|time zone|tz)\s*:\s*(?P<zone>[A-Za-z][A-Za-z0-9_+./-]*)\s*$"
)
_LOCATION_LINE = re.compile(r"(?im)^\s*location\s*:\s*(?P<location>.+?)\s*$")
_DESCRIPTION_LINE = re.compile(r"(?im)^\s*description\s*:\s*(?P<description>.+?)\s*$")
_ZONE_TOKEN = re.compile(
    r"(?<![A-Za-z])(?P<zone>UTC|GMT|PST|PDT|MST|MDT|CST|CDT|EST|EDT|KST|JST)(?![A-Za-z])",
    re.IGNORECASE,
)


class WhenFoundError(ValueError):
    """Raised when input is unsafe or too ambiguous to turn into one event."""


@dataclass(frozen=True)
class EventDraft:
    """A user-reviewable event candidate produced without network or model calls."""

    title: str
    start: date | datetime
    end: date | datetime | None
    location: str
    description: str
    timezone_name: str | None
    confidence: str
    warnings: tuple[str, ...]
    source: str

    @property
    def all_day(self) -> bool:
        return isinstance(self.start, date) and not isinstance(self.start, datetime)


def parse_text(
    source: str,
    *,
    today: date | None = None,
    title: str | None = None,
    timezone_name: str | None = None,
) -> EventDraft:
    """Parse one text block into one event, failing closed on ambiguity."""

    if not source.strip():
        raise WhenFoundError("input is empty")
    if len(source.encode("utf-8")) > MAX_INPUT_BYTES:
        raise WhenFoundError("input is larger than the 1 MiB safety limit")

    reference_day = today or datetime.now(timezone.utc).astimezone().date()
    date_value, date_spans, date_kind = _find_date(source, reference_day)
    masked = _mask_spans(source, date_spans)
    times = _find_times(masked)
    parsed_timezone = timezone_name or _find_timezone(source)
    location = _find_labeled_value(_LOCATION_LINE, source)
    description = _find_labeled_value(_DESCRIPTION_LINE, source)
    warnings: list[str] = []

    event_title = _clean_title(title or _find_title(source))
    if not event_title:
        event_title = "Untitled event"
        warnings.append("Title not found; review the generated title before importing.")

    if not times:
        start: date | datetime = date_value
        end: date | datetime | None = None
    else:
        start_time, end_time = times[0], times[1] if len(times) > 1 else None
        start = datetime.combine(date_value, start_time)
        end = datetime.combine(date_value, end_time) if end_time else None
        if end is not None and end <= start:
            raise WhenFoundError("end time must be after start time")
        if parsed_timezone is None:
            warnings.append(
                "Timezone not found; the calendar app may interpret this time in its local timezone."
            )

    if len(times) > 2:
        raise WhenFoundError("found more than two times; provide one event at a time")

    if parsed_timezone is not None:
        parsed_timezone = _normalize_timezone(parsed_timezone)

    confidence = _confidence(
        date_kind=date_kind, has_time=bool(times), has_timezone=parsed_timezone is not None
    )
    return EventDraft(
        title=event_title,
        start=start,
        end=end,
        location=location,
        description=description,
        timezone_name=parsed_timezone,
        confidence=confidence,
        warnings=tuple(warnings),
        source=source,
    )


def _find_date(source: str, reference_day: date) -> tuple[date, list[tuple[int, int]], str]:
    numeric = _NUMERIC_DATE.search(source)
    if numeric:
        raise WhenFoundError(
            "ambiguous numeric date found; use YYYY-MM-DD or write the month name explicitly"
        )

    matches: list[tuple[date, tuple[int, int], str]] = []
    for pattern, kind in (
        (_ISO_DATE, "explicit"),
        (_MONTH_FIRST, "explicit"),
        (_DAY_FIRST, "explicit"),
    ):
        for match in pattern.finditer(source):
            try:
                if "month" in match.groupdict() and not match.group("month").isdigit():
                    month = MONTH_ALIASES[match.group("month").lower()]
                else:
                    month = int(match.group("month"))
                value = date(int(match.group("year")), month, int(match.group("day")))
            except (KeyError, TypeError, ValueError) as exc:
                raise WhenFoundError("date is invalid") from exc
            matches.append((value, match.span(), kind))

    if matches:
        unique = {value for value, _, _ in matches}
        if len(unique) > 1:
            raise WhenFoundError("found multiple different dates; provide one event at a time")
        first_value = matches[0][0]
        return (
            first_value,
            [span for value, span, _ in matches if value == first_value],
            matches[0][2],
        )

    relative = re.search(r"\b(today|tomorrow)\b", source, re.IGNORECASE)
    if relative:
        offset = 1 if relative.group(1).lower() == "tomorrow" else 0
        return reference_day + timedelta(days=offset), [relative.span()], "relative"

    weekday = re.search(
        r"\b(?:(next)\s+)?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
        source,
        re.IGNORECASE,
    )
    if weekday:
        target = WEEKDAYS[weekday.group(2).lower()]
        days_ahead = (target - reference_day.weekday()) % 7
        if weekday.group(1) or days_ahead == 0:
            days_ahead = days_ahead or 7
        return reference_day + timedelta(days=days_ahead), [weekday.span()], "relative"

    raise WhenFoundError(
        "no date found; use YYYY-MM-DD, a written month, today, tomorrow, or a weekday"
    )


def _find_times(source: str) -> list[time]:
    values: list[time] = []
    for match in _TIME.finditer(source):
        has_colon = match.group("minute") is not None
        ampm = match.group("ampm")
        if not has_colon and ampm is None:
            continue
        hour = int(match.group("hour"))
        minute = int(match.group("minute") or 0)
        if ampm:
            if not 1 <= hour <= 12:
                raise WhenFoundError("12-hour time must use an hour from 1 to 12")
            normalized = ampm.replace(".", "").lower()
            if normalized == "pm" and hour != 12:
                hour += 12
            if normalized == "am" and hour == 12:
                hour = 0
        elif not 0 <= hour <= 23:
            raise WhenFoundError("24-hour time must use an hour from 0 to 23")
        values.append(time(hour, minute))
    return values


def _find_timezone(source: str) -> str | None:
    line = _TIMEZONE_LINE.search(source)
    if line:
        return line.group("zone")
    token = _ZONE_TOKEN.search(source)
    return token.group("zone") if token else None


def _normalize_timezone(value: str) -> str:
    stripped = value.strip()
    alias = TIMEZONE_ALIASES.get(stripped.upper())
    if alias:
        return alias
    if re.fullmatch(r"[A-Za-z]+/[A-Za-z0-9_+.-]+(?:/[A-Za-z0-9_+.-]+)?", stripped):
        return stripped
    raise WhenFoundError(
        "timezone must be UTC, a supported abbreviation, or an IANA name like America/Vancouver"
    )


def _find_title(source: str) -> str:
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or re.match(
            r"^(?:location|description|timezone|time zone|tz)\s*:", line, re.IGNORECASE
        ):
            continue
        if _ISO_DATE.search(line) or _MONTH_FIRST.search(line) or _DAY_FIRST.search(line):
            continue
        if _NUMERIC_DATE.search(line) or re.search(
            r"\b(?:today|tomorrow|next\s+\w+)\b", line, re.IGNORECASE
        ):
            continue
        if _find_times(line):
            continue
        return line
    return ""


def _find_labeled_value(pattern: re.Pattern[str], source: str) -> str:
    match = pattern.search(source)
    return _clean_title(match.group(1) if match else "")


def _clean_title(value: str) -> str:
    return " ".join(value.replace("\r", " ").replace("\n", " ").split())


def _mask_spans(source: str, spans: list[tuple[int, int]]) -> str:
    chars = list(source)
    for start, end in spans:
        for index in range(start, end):
            if chars[index] not in "\r\n":
                chars[index] = " "
    return "".join(chars)


def _confidence(*, date_kind: str, has_time: bool, has_timezone: bool) -> str:
    if date_kind == "explicit" and (not has_time or has_timezone):
        return "high"
    if date_kind == "explicit":
        return "medium"
    return "medium" if not has_time or has_timezone else "low"
