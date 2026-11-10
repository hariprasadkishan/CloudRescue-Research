# AGENTS.md — Instructions for AI Coding Agents

These instructions apply to Antigravity and any other AI coding agent working in this repository.

## 1. Project identity

This repository is the IIIT Dharwad academic project **CloudRescue**, a cloud-resilience simulator and research evaluation platform.

CloudRescue is NOT a cloud backup dashboard, backup manager, disaster-recovery SaaS product, or production cloud-control plane.

Read `README.md`, `PRD.md`, `DESIGN.md`, `ARCHITECTURE.md`, `EXPERIMENT_PLAN.md` and `RESEARCH_NOTES.md` before making changes relevant to them.

## 2. Absolute safety rules

- Work only inside the project directory explicitly opened and confirmed by the user.
- Never search the user's whole filesystem, browser history, trash, home directory or unrelated repositories to locate project files.
- Never clone a repository unless the user explicitly supplies and approves its exact URL and destination.
- Never create, publish, push or deploy a GitHub repository without explicit user approval.
- Never delete, overwrite, move or mass-rename files without explicit approval.
- Never modify files outside the confirmed project directory.
- Before destructive or broad changes, explain the plan and wait for approval.
- Do not run commands with broad destructive effects, such as recursive deletion, filesystem-wide cleanup or unreviewed reset commands.
- Do not expose secrets. Never print API keys, tokens, passwords or `.env` contents.
- Do not add telemetry, external services or cloud integrations without approval.

## 3. Work protocol

For each task:

1. State the task and intended files.
2. Inspect only relevant files inside the confirmed repository.
3. Summarize the current state and any assumptions.
4. Propose a small implementation plan.
5. Wait for approval when the task changes architecture, scope, dependencies, data formats or research methodology.
6. Make the smallest coherent change.
7. Run relevant tests or checks.
8. Report exact files changed, commands run, test outcomes and known limitations.

Do not claim a command or test succeeded unless it was actually executed and its output inspected.

## 4. Research integrity

- The assigned survey paper is the primary source for selecting and describing the resilience technique.
- Do not invent paper content, quotations, citations, page numbers or claims.
- If the paper is unavailable, ask the user to provide it. Do not pretend it was reviewed.
- Keep source-derived statements separate from design decisions and engineering assumptions.
- Do not fabricate experiment runs, CSVs, graphs, metrics, p-values, confidence intervals, performance improvements or conclusions.
- Mock data must be clearly labelled `DEMO` or `PLACEHOLDER` and must never be mixed with measured data.
- Every result must be traceable to raw output and a recorded configuration.
- Report negative, inconclusive and failed experiments honestly.
- Do not claim statistical significance unless an appropriate test was actually run and its assumptions are discussed.

## 5. Engineering rules

- Keep simulation logic independent of frontend presentation.
- Keep metric calculations in testable functions with documented definitions and units.
- Validate user-provided experiment configurations.
- Record random seeds and all parameters needed to reproduce a run.
- Use explicit types and clear names where practical.
- Avoid unnecessary abstractions and dependencies.
- Do not silently change experiment semantics while refactoring.
- Add or update tests for behaviour changes.
- Preserve raw experiment outputs; do not overwrite prior runs.

## 6. Frontend and design rules

Follow `DESIGN.md`. The approved visual direction is **Variant A — Brutalist Swiss Monograph**:
- Instrument Serif for selective editorial display typography.
- Geist Sans for interface and body text.
- IBM Plex Mono for technical labels and values.
- Warm paper, ink black and electric blue.
- Editorial hierarchy, asymmetric composition and varied page layouts.

Do not replace this direction with a generic dark dashboard or generic AI-generated SaaS template. Do not use the same card grid on every screen. Avoid decorative charts, fake telemetry and invented statistics.

Use the seven Stitch screens as the visual source of truth once the user provides their project link or exported assets. Do not invent a Stitch project ID or claim to have inspected screens you cannot access.

## 7. Dependency and command discipline

- Do not install packages until the user approves the proposed stack and dependency list.
- Explain commands before running them when they create files, install packages, start servers or change system state.
- Do not run package installation at the home-directory level.
- Do not start background servers without telling the user how to stop them.
- Do not commit, push or deploy without explicit approval.

## 8. Definition of done

A task is complete only when:
- The requested change is implemented in the correct repository.
- Relevant checks have been run, or the reason they could not be run is stated.
- Changed files and results are reported accurately.
- Documentation is updated when behaviour, architecture, metrics or workflows change.
