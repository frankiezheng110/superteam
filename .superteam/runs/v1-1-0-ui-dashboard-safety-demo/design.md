# Design

Approved direction: build the admin dashboard as a two-zone surface.

## Core Decisions

- left zone shows usage metrics, health counters, and recent cache activity
- right zone contains maintenance actions with stronger warnings and confirmation affordances
- destructive controls use a distinct visual treatment informed by `design-system.md`
- the cache reset endpoint stays behind an explicit operator confirmation flow

## Risks

- the action panel could feel too prominent if danger styling is overused
- the maintenance flow must remain testable without hitting production infrastructure

## Approval

- Status: approved
- Approved by: orchestrator
- Approval basis: clear boundary between informative UI and guarded action UI
