# ADR 0002: Wave B3 boundary regression and migration contract

## Status

Accepted

## Context

Issue `intellistream/sage-agentic#12` requires QA/Docs closure after Wave B2 boundary cleanup.
Wave B2 removed cross-layer bindings and implicit wiring paths. Wave B3 must lock these constraints
with regression tests and migration instructions.

## Decision

- Add boundary contract tests to prevent reintroducing:
  - direct imports from `sage.cli` in L3 generators,
  - hard-coded `sage.middleware.*` stage paths in rule-based plans,
  - implicit model construction in `BaseAgent`.
- Add migration documentation with direct before/after replacements.
- Keep hard-removal policy: no alias layer, no fallback layer.

## Consequences

- Boundary constraints are executable and continuously testable.
- Application layer owns runtime planner/model wiring explicitly.
- Downstream callers get a single migration path without dual API behavior.
