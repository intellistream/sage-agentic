# ADR 0001: Remove L5/L4 bindings from `sage-agentic` L3 generators

## Status

Accepted

## Context

Issue `intellistream/sage-agentic#10` requires `sage-agentic` to remain an L3 algorithm repository.
Direct imports from L5 (`sage-cli`) or hard-coded L4 operator paths (`sage.middleware.*`) in this repo
break the layer boundary.

## Decision

- Remove direct `sage-cli` imports from `LLMWorkflowGenerator`.
- Require an application-layer injected `plan_generator` callable.
- Replace hard-coded `sage.middleware.*` stage class paths in rule-based plans with `sage.libs.rag.*` class paths.
- Keep fail-fast behavior when required application-layer dependencies are not injected.

## Consequences

- `sage-agentic` stays runtime/service-neutral at L3.
- Application layers own concrete planner wiring and deployment-specific dependencies.
- No alias/re-export/fallback layer is introduced.
