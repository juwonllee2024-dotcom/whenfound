# Founder note — 2026-09-15

## Today’s problem

People repeatedly receive an event as text in an email, chat, support ticket, school notice, or community post. The event is visible, but moving it into a calendar means retyping title, date, time, timezone, and location. That retyping step is small, frequent, and easy to get wrong.

## What is confirmed

- Google Calendar documents a “Create an event” flow from a Gmail message, then asks the user to confirm the event details. [Google Calendar Help](https://support.google.com/calendar/answer/13469141?hl=en-au)
- A Google Calendar community thread records users saying that the flow often copies only the event name and leaves date, time, and location for manual entry. [Google Calendar Community](https://support.google.com/calendar/thread/8689157/how-to-manually-add-a-calendar-event-from-gmail-email-non-travel-meeting-origin?hl=en)
- Open-source `timesense` demonstrates that deterministic, zero-dependency natural-language event parsing and `.ics` export are technically feasible. [timesense](https://github.com/kruatech/timesense)
- GitHub’s current trending page shows continued interest in local/open-source tools and agent workflows, but trending is a discovery signal, not proof of demand for this product. [GitHub Trending](https://github.com/trending)

## Four independent innovation questions

### 1. WhenFound — selected

- Pain: a date in text must be retyped into a calendar.
- Gap: provider integrations start after the event reaches one inbox; they do not offer a portable, provider-neutral boundary for any copied text.
- Innovation hypothesis: a “review first, standard file second” flow can remove retyping while keeping the user in control.
- Different one thing: it refuses ambiguous dates and exposes missing timezone instead of silently guessing.
- 7-day experiment: give ten people who copy events from email/chat a real message; measure five successful exports and three repeat uses without a tutorial.
- Score (0–5): pain 5, novelty 4, buildability 5, organic shareability 4, open-source fit 5. Total 23/25.

### 2. PasteUnwrap — rejected

- Pain: terminal and AI output can paste with hard wraps, padding, and control artifacts.
- Gap: rendered output and clipboard output can disagree; a current Claude Code issue groups 42 copy/paste reports. [Claude Code issue #81472](https://github.com/anthropics/claude-code/issues/81472)
- Innovation hypothesis: a local before/after repair with explicit copy would help.
- Different one thing: prove every transformation before copying.
- 7-day experiment: test ten terminal users on five captured outputs.
- Score: pain 5, novelty 2, buildability 5, organic shareability 4, open-source fit 4. Total 20/25.
- Rejection: overlaps this portfolio’s LinePatch and several current terminal-cleaner tools, including `unwrap-terminal-text` and `clipaste`. The pain is real, but this candidate is not a sufficiently new repository for today.

### 3. TabMemory — rejected

- Pain: closing research tabs loses the reason they mattered.
- Gap: bookmarks save URLs, not intent or a recoverable work state.
- Innovation hypothesis: a local “save with intent, restore when needed” session file could reduce tab hoarding.
- Different one thing: human-readable, versionable session records rather than an opaque cloud workspace.
- 7-day experiment: ask ten researchers to recover one past task from a saved session.
- Score: pain 4, novelty 2, buildability 4, organic shareability 3, open-source fit 3. Total 16/25.
- Rejection: crowded by Tab Stash, TabMark, PageStow, and multiple projects in this portfolio; discovery and context storage are already heavily represented.

### 4. DropSort — rejected

- Pain: Downloads folders accumulate files that users fear moving or deleting.
- Gap: safe preview and undo matter more than automatic classification.
- Innovation hypothesis: a local plan that groups moves and leaves a reversible receipt can make cleanup trustworthy.
- Different one thing: no-delete, deterministic move plans.
- 7-day experiment: measure whether ten users accept a preview for one messy folder.
- Score: pain 4, novelty 2, buildability 4, organic shareability 3, open-source fit 4. Total 17/25.
- Rejection: overlaps CopyHomes and the current open-source `filo`/`folder-elf`/`FolderSorter` space. The feature is useful, but not a fresh wedge here.

## Selected business wedge

- First user: developer, student, researcher, support operator, or community member moving event details between apps.
- First ten users: people in open-source communities, local-first productivity forums, and calendar/workflow groups; ask for one real message test, not a star.
- Smallest offer: paste or point WhenFound at one event-shaped text block, review it, export `.ics`.
- Free-first cost: zero required service cost; Python standard library only. GitHub Actions is used for public verification.
- Revenue hypothesis: keep the parser free and open; only test paid team templates or support after repeat use is proven. No revenue is claimed.
- Main risks: date-language coverage, user distrust of generated events, and the existence of provider-native flows. The next experiment must test repeated use, not add integrations.

## Decision

Build WhenFound as a new repository. Existing repositories receive no new feature in this run. The product is not guaranteed to go viral or reach 100,000 stars; its evidence-backed chance is the combination of a universal import boundary, a visible artifact, no account requirement, and a conservative trust model.
