# Next Thin Slices

## Purpose
Maintain a phase-agnostic, execution-first queue of immediate slices.

Use this as the active implementation plan when roadmap phase ordering may change.

Active detailed plan:
- `ops/phase-5-thin-slices.md`
- `ops/versioning-automation-thin-slices.md` (queued)

Completed prior track:
- `ops/done/phase-4-1-thin-slices.md`
- `ops/done/phase-4-2-thin-slices.md`

## Status
- Phase 4.1 / Slice 0 - OpenAI-Compatible Adapter Contract and Env Spec: done
- Phase 4.1 / Slice 1 - Adapter Skeleton and Config Validation: done
- Phase 4.1 / Slice 2 - Request/Response Path: done
- Phase 4.1 / Slice 3 - Registry and CLI Integration: done
- Phase 4.1 / Slice 4 - Error Handling and Diagnostics: done
- Phase 4.1 / Slice 5 - Docs and Consumer Usage: done
- Phase 4.1 / Slice 6 - Regression and Contract Gates: done
- Phase 4.1 / Slice 7 - Exit Validation and Handoff: done
- Phase 4.2 / Slice 0 - Contract Decision and Guardrails: done
- Phase 4.2 / Slice 1 - Opt-In Fallback Path in OpenAI-Compat: done
- Phase 4.2 / Slice 2 - Error Handling, Timeout, and Secret Safety for Fallback: done
- Phase 4.2 / Slice 3 - Dedicated Ollama Adapter Skeleton: done
- Phase 4.2 / Slice 4 - Registry/CLI Integration for Ollama: done
- Phase 4.2 / Slice 5 - Docs and Consumer Usage: done
- Phase 4.2 / Slice 6 - Exit Validation and Queue Handoff: done
- Next / Phase 5 Slice 1 - GitHub App Skeleton: queued
- Next / Versioning Automation Slice 0 - Policy and Human-in-Loop Baseline: done
- Next / Versioning Automation Slice 1 - Release Automation Skeleton: done
- Next / Versioning Automation Slice 2 - Label and Policy Enforcement: done
- Next / Versioning Automation Slice 3 - Tag and Release Asset Publishing: queued

## Next Actions
1. Phase 4.1 is complete; reference `ops/done/phase-4-1-exit-validation.md` for handoff details.
2. Phase 4.2 is complete; reference `ops/done/phase-4-2-exit-validation.md` for handoff details.
3. Start Phase 5 Slice 1 from `ops/phase-5-thin-slices.md`.
4. Start Versioning Automation Slice 3 from `ops/versioning-automation-thin-slices.md`.

## Mapping Notes
- `ops/ROADMAP.md` remains the strategic phase plan.
- `ops/done/phase-4-2-thin-slices.md` is the completed execution-level extension for local/self-hosted adapter compatibility.
- `ops/phase-5-thin-slices.md` remains phase-specific draft/detail.
- `ops/versioning-automation-thin-slices.md` is a cross-cutting execution plan for release/version automation.
- This file is the active execution queue and may pull slices from different phases.
