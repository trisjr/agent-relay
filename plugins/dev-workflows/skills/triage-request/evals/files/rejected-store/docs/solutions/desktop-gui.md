---
title: No desktop or web GUI for linkcheck
type: decision
area: ui
tags: [rejected-request, gui, scope]
created: 2026-06-02
last_seen: 2026-09-20
occurrences: 2
---

## Context
Two users asked for a graphical front end to browse broken links instead of reading terminal output.

## Options considered
- Bundle a desktop app: friendlier, but triples the release surface (signing, installers, three platforms).
- Serve a local web page: lighter, still a second UI to keep in step with every flag.
- Stay terminal-only and keep the output easy to pipe into other tools.

## Lesson
Stay terminal-only. The tool is meant for CI and editors; anything visual is better built by a consumer on top of the machine-readable output.

## Apply
Decline GUI and dashboard requests; point to `linkcheck scan --format json` for building one outside the project.

## Source
Feature requests in June and September 2026.
