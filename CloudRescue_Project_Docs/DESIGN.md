# CloudRescue — Design System & UI Direction

**Approved direction:** Variant A — Brutalist Swiss Monograph  
**Status:** Design direction selected; exact Stitch screens remain the visual source of truth.

## 1. Design intent

CloudRescue should feel like a serious research instrument presented through a premium editorial publication—not a generic cloud SaaS dashboard and not a fictional mission-control interface.

The visual language should communicate precision, evidence, restraint and technical credibility. Every chart, number and status must correspond to real application data or be explicitly labelled as a placeholder.

## 2. Visual principles

1. **Editorial, not template-driven:** Use strong typographic hierarchy, deliberate whitespace and asymmetric layouts.
2. **Minimal, not empty:** Remove decoration that does not clarify content or hierarchy.
3. **Evidence-led:** Give experimental results and methodology visual priority.
4. **Technical precision:** Use monospaced typography for identifiers, timestamps, parameter values and compact metadata.
5. **Consistent, not repetitive:** Maintain shared tokens and components while varying page composition to suit each task.
6. **Accessible:** Maintain readable contrast, visible focus states, keyboard access and non-colour status cues.

## 3. Colour palette

| Token | Value | Intended use |
|---|---|---|
| `paper` | `#F3F0E8` | Main page background |
| `ink` | `#171717` | Primary text and strong surfaces |
| `electric-blue` | `#2457E8` | Primary action, selected state, key accent |
| `hairline` | `#D3D0C8` | Dividers, borders and table rules |
| `muted-ink` | `#686760` | Secondary text |
| `surface` | `#FAF9F5` | Raised content surface |

Use colour sparingly. Do not use electric blue for every button, icon and chart series. Status must not rely on colour alone. Additional semantic colours may be introduced only when they have a clear meaning and pass contrast checks.

## 4. Typography

### Display
**Instrument Serif**
- Use for selective large editorial headlines and section openers.
- Do not use for dense UI labels, data tables or long technical paragraphs.

### Interface and body
**Geist Sans**
- Use for navigation, controls, body copy, labels, tables and general interface text.

### Technical
**IBM Plex Mono**
- Use for experiment IDs, parameter values, timestamps, code-like labels and compact technical metadata.
- Do not set all body text in monospace.

Use a restrained type scale. Prioritize hierarchy through size, weight, spacing and alignment rather than excessive font styles.

## 5. Layout and composition

- Use a clear grid with generous margins and deliberate alignment.
- Allow selected pages to use asymmetric columns and editorial side notes.
- Prefer hairline dividers and typographic grouping over excessive rounded cards.
- Avoid large gradients, glassmorphism, glowing borders, excessive shadows and decorative 3D effects.
- Avoid repeating a uniform 3-column card layout across all seven screens.
- Keep dense experiment tables legible and scannable.
- Use responsive layouts for desktop and smaller screens.

## 6. Component guidance

### Navigation
Use restrained navigation with clear active states. Keep project identity and current experiment context visible without crowding the page.

### Buttons
- Primary: ink or electric blue with accessible contrast.
- Secondary: quiet outline or text action.
- Destructive: explicit warning treatment and confirmation where needed.
- Labels should describe the action: `Run experiment`, `Export CSV`, `Compare runs`.

### Forms
Group configuration fields by purpose. Include units, valid ranges, defaults and concise helper text. Show validation close to the relevant field.

### Tables
Use strong column labels, subtle row separators, aligned numeric values and explicit units. Avoid unexplained abbreviations.

### Charts
Every chart must include:
- Descriptive title.
- Metric and unit.
- Axis labels and readable ticks.
- Legend when multiple series exist.
- Experiment/configuration identity.
- Clear indication of missing or incomplete data.

Never render fabricated values as live results.

### Status
Use text labels such as `Queued`, `Running`, `Completed`, `Failed` and `Demo data`. Do not rely on colour alone.

## 7. Seven-screen experience map

These are intended screen roles; map them to the supplied Stitch screens after inspecting the actual designs.

1. **Overview / cover:** Project identity, research question, current project status and recent verified runs.
2. **Failure & workload configuration:** Configure workload, failure scenario, duration, seed and comparison setup.
3. **Simulation lab:** Run controls, progress, event timeline and execution logs.
4. **Benchmark comparison:** Side-by-side baseline and resilient configuration results.
5. **Experimental analytics:** Time series, distributions and aggregate metrics from actual runs.
6. **Research methodology:** Technique description, assumptions, variables, metric definitions and protocol.
7. **Report / publication preview:** Exportable findings, methodology and limitations. Publication metadata must be real or omitted.

## 8. Content and data integrity in UI

- Label all mock content clearly as `DEMO` or `PLACEHOLDER`.
- Do not show invented researcher names, DOI, ISSN, publication status, checksums or institutional endorsements.
- Do not show example percentages, p-values, recovery times or request throughput as measured results.
- Empty states should explain how to generate real data.
- Failed runs should remain visibly failed; never turn missing values into zero without an explicit definition.

## 9. Motion

Motion should be purposeful and restrained:
- Use short transitions for navigation, state changes and feedback.
- Use progress indicators only when tied to actual execution state.
- Avoid decorative perpetual animations and simulated activity.
- Respect reduced-motion preferences.

## 10. Accessibility and responsive behaviour

- Use semantic headings and controls.
- Ensure keyboard navigation and visible focus.
- Provide labels and descriptions for form fields.
- Provide text summaries or tabular alternatives for important charts.
- Check contrast and do not communicate state through colour alone.
- Ensure tables and charts remain usable on narrow screens.

## 11. Design implementation gate

Before implementing the frontend:
1. Inspect the seven actual Stitch screens or exported images.
2. Record the intended route and content for each screen.
3. Identify reusable components and differences between screens.
4. Confirm font availability and licensing/hosting approach.
5. Confirm responsive behaviour.
6. Get user approval before replacing the supplied design direction.
