# Workflow Presets / Routers

**Location**: `sage.libs.agentic.workflows`

This module holds concrete workflow presets and routers that compose the core interfaces from `workflow/`.

Guidelines:
- Treat these as registered presets (examples/routers), not core interfaces.
- Keep dependencies light and L3-safe.
- Consider externalizing heavy presets to `isage-agentic`.
