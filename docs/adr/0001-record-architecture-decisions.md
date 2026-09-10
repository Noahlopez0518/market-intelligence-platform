# 1. Record architecture decisions

## Status

Accepted

## Context

The project charter (`project-charter.md`) names the tech stack and rationale, but individual design decisions (schema choices, ingestion strategy, anomaly-detection method selection, etc.) need their own record as they're made, per the charter's Definition of Done ("architecture diagram and ADRs explaining every design choice").

## Decision

Use lightweight ADRs (Architecture Decision Records) in `docs/adr/`, one file per decision, numbered sequentially. Format follows Michael Nygard's template: Status, Context, Decision, Consequences.

## Consequences

Every non-trivial architectural choice made during Phases 1–7 gets its own ADR before or alongside the code that implements it.
