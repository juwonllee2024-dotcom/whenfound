"""WhenFound: turn one event hidden in text into a reviewable calendar file."""

from .core import EventDraft, WhenFoundError, parse_text
from .ics import render_ics

__all__ = ["EventDraft", "WhenFoundError", "parse_text", "render_ics"]
__version__ = "0.1.0"
