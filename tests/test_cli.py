from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SAMPLE = """Design review
September 18, 2026
09:30 AM - 10:45 AM
Location: Vancouver Library
Timezone: America/Vancouver
Description: Bring the draft plan
"""


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "whenfound.cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_preview_shows_reviewable_event_without_writing_a_file() -> None:
    result = run_cli("preview", "--text", SAMPLE, "--today", "2026-09-14")

    assert result.returncode == 0
    assert "Design review" in result.stdout
    assert "2026-09-18 09:30" in result.stdout
    assert "2026-09-18 10:45" in result.stdout
    assert "America/Vancouver" in result.stdout
    assert "No file written" in result.stdout


def test_export_writes_ics_only_when_explicitly_requested(tmp_path: Path) -> None:
    target = tmp_path / "design-review.ics"
    result = run_cli(
        "export",
        "--text",
        SAMPLE,
        "--today",
        "2026-09-14",
        "--output",
        str(target),
    )

    assert result.returncode == 0
    calendar = target.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in calendar
    assert "SUMMARY:Design review" in calendar
    assert "DTSTART;TZID=America/Vancouver:20260918T093000" in calendar
    assert "DTEND;TZID=America/Vancouver:20260918T104500" in calendar
    assert "LOCATION:Vancouver Library" in calendar
    assert "Bring the draft plan" in calendar


def test_export_refuses_to_overwrite_without_force(tmp_path: Path) -> None:
    target = tmp_path / "event.ics"
    first = run_cli("export", "--text", SAMPLE, "--output", str(target))
    original = target.read_text(encoding="utf-8")
    second = run_cli("export", "--text", SAMPLE, "--output", str(target))

    assert first.returncode == 0
    assert second.returncode == 2
    assert "already exists" in second.stderr
    assert target.read_text(encoding="utf-8") == original


def test_ambiguous_numeric_date_fails_closed() -> None:
    result = run_cli(
        "preview",
        "--text",
        "Budget call\n03/04/2026 at 9:00 AM",
    )

    assert result.returncode == 2
    assert "ambiguous" in result.stderr.lower()


def test_missing_timezone_is_visible_as_a_warning() -> None:
    result = run_cli(
        "preview",
        "--text",
        "Dentist\n2026-09-18 at 9:00 AM",
    )

    assert result.returncode == 0
    assert "timezone not found" in result.stdout.lower()


def test_oversized_file_is_rejected_before_utf8_decoding(tmp_path: Path) -> None:
    source = tmp_path / "too-large.txt"
    source.write_bytes(b"A" * 1_000_001 + b"\xff")

    result = run_cli("preview", str(source))

    assert result.returncode == 2
    assert "1 MiB" in result.stderr


def test_ics_escapes_text_that_could_change_calendar_fields(tmp_path: Path) -> None:
    target = tmp_path / "escaped.ics"
    result = run_cli(
        "export",
        "--text",
        "Launch, v1; final\n2026-09-18",
        "--output",
        str(target),
    )

    assert result.returncode == 0
    calendar = target.read_text(encoding="utf-8")
    assert "SUMMARY:Launch\\, v1\\; final" in calendar
    assert "\nSUMMARY:Launch, v1; final\n" not in calendar
