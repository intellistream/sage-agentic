# ADR 0003: Remove Implicit Agentic Entry Points

## Status

Accepted

## Context

Issue `intellistream/sage-agentic#11` requires removing implicit entry points and keeping API boundaries explicit.

Observed boundary problems:

- top-level package exposed `interfaces` as an extra entry path while `interface` is the canonical API layer,
- workflow registry accepted alias names (`baseline`, `parallelization`) in addition to canonical keys,
- bots package used wildcard imports, creating implicit symbol export behavior.

## Decision

1. Keep a single canonical interface entry path: `sage_libs.sage_agentic.interface`.
2. Remove old `sage_libs.sage_agentic.interfaces` package.
3. Keep only canonical workflow optimizer registry keys:
   - `noop`
   - `greedy`
   - `parallel`
4. Replace wildcard exports in `agents.bots` with explicit imports and explicit `__all__`.

## Consequences

- API surface is explicit and easier to audit.
- Callers must use canonical import/registry paths directly.
- No alias/indirect/fallback layer remains for these entry points.
