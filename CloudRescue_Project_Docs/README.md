# CloudRescue — Project Documentation

CloudRescue is an academic cloud-resilience simulation and research evaluation platform developed at IIIT Dharwad. It implements and experimentally evaluates an autonomic resilience technique selected from the assigned survey paper (*On Resilience in Cloud Computing: A Survey of Techniques across the Cloud Domain*, Welsh & Benkhelifa, ACM Computing Surveys 2020).

---

## Documentation map

| File | Purpose | Current Status |
|---|---|---|
| [`PRD.md`](file:///home/andesindica/Downloads/CloudRescue-Research/CloudRescue_Project_Docs/PRD.md) | Product goals, scope, functional/non-functional requirements, and 10 standardized metrics | **Version 1.3 — Approved** |
| [`RESEARCH_NOTES.md`](file:///home/andesindica/Downloads/CloudRescue-Research/CloudRescue_Project_Docs/RESEARCH_NOTES.md) | Paper review, evidence extraction, citations, and mapping of Klein et al. [60, 61] | **Complete — Approved** |
| [`EXPERIMENT_PLAN.md`](file:///home/andesindica/Downloads/CloudRescue-Research/CloudRescue_Project_Docs/EXPERIMENT_PLAN.md) | Research questions, hypotheses, experimental variables, 3-way ablation design, metric formulas, and statistical testing | **Complete — Approved** |
| [`ARCHITECTURE.md`](file:///home/andesindica/Downloads/CloudRescue-Research/CloudRescue_Project_Docs/ARCHITECTURE.md) | Software architecture, discrete-event simulation components, velocity PI controller math, BALB scoring function, multi-stream PRNG architecture, and repository structure | **Complete — Approved** |
| [`DECISIONS.md`](file:///home/andesindica/Downloads/CloudRescue-Research/CloudRescue_Project_Docs/DECISIONS.md) | Architecture Decision Records (ADRs) logging decisions DEC-001 through DEC-009 | **Current — Approved** |
| [`DESIGN.md`](file:///home/andesindica/Downloads/CloudRescue-Research/CloudRescue_Project_Docs/DESIGN.md) | Visual design system (Variant A — Brutalist Swiss Monograph) and 7-screen UI direction | **Approved** |
| [`AGENTS.md`](file:///home/andesindica/Downloads/CloudRescue-Research/CloudRescue_Project_Docs/AGENTS.md) | Rules of engagement, safety constraints, and research integrity instructions for AI coding assistants | **Active** |

---

## Current project status

- **Selected Research Technique:** **Brownout-based self-adaptive graceful degradation with brownout-aware load balancing** (DEC-005).
- **Implementation Scope:** Brownout velocity PI feedback controller + brownout-aware load balancer across a cluster of simulated cloud worker instances (DEC-006, DEC-009).
- **Standardized Baseline:** Join-Shortest-Queue (JSQ) load balancing standardized for `CFG-A` (Baseline) and `CFG-B` (Brownout Only); Brownout-Aware Load Balancing (BALB) reserved strictly for `CFG-C` (Full CloudRescue) (DEC-008).
- **Multi-Stream Reproducibility:** Pre-sampled request tuples across five isolated random sub-streams to guarantee 100% matched arrivals, service demands, and failure events across configurations under the same master seed (DEC-008).
- **Experimental Design:** Three-way ablation comparison (Baseline vs. Brownout-Only vs. Full CloudRescue) across 4 stress scenarios using matched random seeds and paired statistical tests ($N=30$ runs, 360 executions total) (DEC-007).
- **Simulation Engine:** Python 3.10+ / SimPy (discrete-event simulation).
- **Simulator Implementation:** Ready to begin upon user approval (no code written yet).
- **Frontend Implementation:** Not started (awaits verified simulation outputs per `DESIGN.md`).
- **Experiments Executed:** None yet (methodology pre-registered).
- **Results Recorded:** None (no fabricated or mock data).

---

## Important integrity rule

CloudRescue adheres to strict research integrity:
- Do not invent experimental results, citations, paper claims, author details, publication metadata, statistical significance, or performance improvements.
- Keep source-derived statements traceably linked to the assigned survey (`research/assigned-paper.pdf`) and primary cited literature.
- Distinguish the survey authors' discussion from our proposed discrete-event simulation model. The composite scoring function used by CloudRescue is explicitly a CloudRescue design synthesizing principles from Klein et al. [61].
- Every reported metric must derive strictly from executed simulation runs with saved configurations, random seeds, and raw event traces.

---

## Project workflow & roadmap

1. [x] Add assigned research paper to `research/assigned-paper.pdf`.
2. [x] Complete comprehensive literature review and evidence extraction (`RESEARCH_NOTES.md`).
3. [x] Officially approve resilience technique and implementation scope (`DECISIONS.md`).
4. [x] Finalize simulation requirements and metric formulas (`PRD.md`).
5. [x] Finalize experimental methodology, variables, and statistical plan (`EXPERIMENT_PLAN.md`).
6. [x] Finalize simulation architecture, controller equations, and module layout (`ARCHITECTURE.md`).
7. [ ] **Next Step:** User approval to implement the Python discrete-event simulation engine and automated test suite.
8. [ ] Execute 3-way ablation experiments and record raw event data.
9. [ ] Run statistical tests and generate publication-quality figures.
10. [ ] Build the editorial research UI around verified outputs (`DESIGN.md`).
11. [ ] Draft the academic technical report based on verified experimental findings.
