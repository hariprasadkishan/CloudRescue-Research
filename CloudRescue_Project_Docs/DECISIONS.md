# CloudRescue — Decision Log

Record important research, architecture, implementation and design decisions. Add new entries at the top.

## Decision record template

### DEC-XXX — Short title
- **Date:** YYYY-MM-DD
- **Status:** Proposed / Accepted / Rejected / Superseded
- **Context:** What decision is needed and why?
- **Options considered:** What alternatives were considered?
- **Decision:** What was selected?
- **Rationale:** Why was it selected?
- **Consequences:** What changes or trade-offs follow?
- **Evidence:** Paper section, experiment, requirement or other supporting source.

---

## Current recorded decisions

### DEC-010 — Nominal-Referenced Post-Restoration Recovery Criterion
- **Date:** 2026-10-31
- **Status:** Accepted
- **Context:** The provisional post-restoration recovery criterion ($T_{\text{restore}}$) in DEC-009 and EXPERIMENT_PLAN.md required operational cluster dimmer to achieve $\bar{\theta} \ge 0.95$ alongside rolling $p_{95} \le 80\text{ ms}$. In an M/M/1 queueing environment under nominal load ($\lambda = 80\text{ req/s}$), full fidelity ($\theta = 1.0$) yields theoretical $p_{95} \approx 600\text{ ms}$. To maintain $r_{\text{target}} \le 80\text{ ms}$, the feedback controller stabilizes at steady-state dimmer $\theta_{\text{nom}}^* \in [0.05, 0.25]$. Consequently, requiring absolute $\theta \ge 0.95$ is physically unachievable in nominal equilibrium and produced 100% right-censoring across all runs.
- **Options considered:**
  - *Option 1 (Absolute Threshold):* Retain $\bar{\theta} \ge 0.95$. (Rejected: mathematically incompatible with steady-state load under $80\text{ ms}$ setpoint).
  - *Option 2 (Arbitrary Fixed Constant):* Lower threshold to fixed $\theta \ge 0.10$. (Rejected: ad-hoc and configuration/seed dependent).
  - *Option 3 (Nominal-Referenced Relative Restoration):* Establish a ground-truth steady-state baseline $\theta_{\text{nom}}^*(c, s, w)$ for each configuration, seed, and worker from the matched nominal stationary run. Require restored workers to recover to $\ge 95\%$ of their nominal reference ($\theta_w(t) \ge 0.95 \cdot \theta_{\text{nom}}^*(w)$) with $p_{95} \le 80\text{ ms}$ for $t_{\text{stable}} = 3.0\text{ s}$.
- **Decision:** Adopt Option 3:
  1. For each configuration $c$, seed $s$, and worker $w$, compute reference $\theta_{\text{nom}}^*(c, s, w)$ as the mean post-warmup dimmer ($t \in [100\text{ s}, 1000\text{ s}]$) from the corresponding nominal run.
  2. For crash failure scenarios (`server_failure`, `compound_stress`), require the restored workers ($w \in \{1, 2\}$) to satisfy $\theta_w(t) \ge 0.95 \cdot \theta_{\text{nom}}^*(w)$.
  3. Require rolling 95th-percentile response latency $\hat{r}_{95}(t) \le r_{\text{target}}$ ($80\text{ ms}$).
  4. Both conditions must hold continuously for $t_{\text{stable}} = 3.0\text{ s}$.
  5. Preserve right-censoring at $(T_{\text{sim}} - t_{\text{shock\_end}}) = 550\text{ s}$ with `recovered = False` when conditions are not satisfied before simulation end.
- **Rationale:** Grounding restoration in the empirical nominal steady state reflects genuine autonomic recovery: returning to the exact healthy operational baseline for that specific seed and worker without violating latency SLAs.
- **Consequences:** Updated `simulator/cloudrescue/monitoring/recovery_analyzer.py`, `tests/test_recovery_analyzer.py`, and results analysis.
- **Evidence:** Klein et al. (2014) [60, 61]; M/M/1 queueing theory; empirical 360-run nominal telemetry.

### DEC-009 — Velocity-form PI controller anti-windup, insufficient-data handling, and recovery censoring
- **Date:** 2026-10-31
- **Status:** Accepted
- **Context:** Mathematical rigor is required for: (1) consistent velocity-form PI control without phantom integral state accumulators, (2) handling intervals with insufficient latency samples without introducing derivative kicks or integrator drift, (3) separating queue depth and CPU utilization in load balancing, and (4) formally defining recovery observation windows and right-censoring.
- **Options considered:**
  - *PI Controller Formulation:* Positional form with separate integral accumulator vs. Velocity form with output clamping intrinsic anti-windup.
  - *Insufficient Data in Window:* Set error to zero and continue velocity math vs. Skip complete PI update, hold $\theta$, and reset derivative state upon resumption.
  - *Recovery Measurement:* Arbitrary penalty values for unrecovered runs vs. Right-censored survival analysis with distinct adaptation and restoration phases.
- **Decision:**
  1. Adopt the **discrete velocity-form PI controller with intrinsic output clamping**:
     $$\Delta \theta_i(t) = K_p (e_i(t) - e_i(t - \Delta t_{\text{ctrl}})) + K_i \cdot e_i(t) \cdot \Delta t_{\text{ctrl}}$$
     $$\theta_i(t) = \text{clamp}(\theta_i(t - \Delta t_{\text{ctrl}}) + \Delta \theta_i(t), \theta_{\text{min}}, \theta_{\text{max}})$$
     Because the next update is computed directly from the clamped output $\theta_i(t)$, no hidden integral accumulation exists beyond the physical boundary $[0.0, 1.0]$.
  2. When fewer than $N_{\text{min\_ctrl}} = 5$ requests complete in an interval, **skip the complete PI calculation and hold $\theta$ constant**. When measurements resume, re-initialize $e_{\text{prev}} \leftarrow e_{\text{current}}$ to eliminate artificial derivative kicks.
  3. Formally distinguish **Adaptation Recovery Time ($T_{\text{adapt}}$)** during active stress from **Post-Restoration Recovery Time ($T_{\text{restore}}$)** following repair. Use a rolling window of $W_{\text{rec}} = 10.0\text{ s}$ requiring at least $N_{\text{rec\_min}} = 20$ completed requests for valid p95 estimation. Mark unrecovered runs as right-censored.
  4. Retain both queue depth ($q_i$, forward-looking buffer backlog) and CPU utilization ($U_i$, cumulative mean operational utilization up to decision timestamp) in the load-balancer scoring function, and calibrate weights empirically via sensitivity experiments.
- **Rationale:** Eliminates mathematical contradictions, prevents controller destabilization during low-traffic intervals, and establishes rigorous, publication-grade statistical survival standards.
- **Consequences:** All metric calculators, controller processes, and experimental plans must implement these exact definitions.
- **Evidence:** Klein et al. (2014) [60, 61]; discrete control theory; PRD FR-01, FR-06, FR-07.

### DEC-008 — Standardized baseline load balancer and independent random stream architecture
- **Date:** 2026-10-31
- **Status:** Accepted
- **Context:** Methodological precision is required for: (1) establishing a single standardized conventional load balancer for baseline comparisons, and (2) guaranteeing that random request attributes remain synchronized across configurations despite differences in optional execution.
- **Options considered:**
  - *Load Balancer Options:* Round Robin vs. Random vs. Join-Shortest-Queue (JSQ).
  - *Random Number Generation Options:* Single shared PRNG stream vs. Pre-generated request tuples with isolated sub-streams.
- **Decision:**
  1. Standardize on **Join-Shortest-Queue (JSQ)** as the single conventional load balancing policy for both `CFG-A` (Baseline) and `CFG-B` (Brownout Only). Reserve **Brownout-Aware Load Balancing (BALB)** strictly for `CFG-C` (Full CloudRescue).
  2. Implement an **isolated multi-stream PRNG architecture** where each request entity is pre-assigned its arrival timestamp, mandatory service time, optional service time, and optional execution random draw from independent streams.
- **Rationale:** Round Robin allows idle workers while queues form on busy workers, confounding latency measurements. JSQ represents the strongest standard load-balancing baseline. Pre-generating request attributes with isolated streams ensures that when `CFG-B` or `CFG-C` bypasses an optional computation, the random number sequence for future arrivals and service times remains 100% identical to `CFG-A`.
- **Consequences:** The simulation engine enforces single-variable ablation: `CFG-A` vs. `CFG-B` isolates the Brownout Controller under JSQ; `CFG-B` vs. `CFG-C` isolates Brownout-Aware Load Balancing on top of the Brownout Controller.
- **Evidence:** Klein et al. (2014) [61]; PRD FR-05, FR-06; reproducibility guidelines.

### DEC-007 — Three-way experiment comparison selected
- **Date:** 2026-10-30
- **Status:** Accepted
- **Context:** An experimental design is needed to determine the independent and combined effects of the brownout controller and the brownout-aware load balancer under equivalent workloads and failure schedules.
- **Options considered:**
  - Option 1: Two-way comparison (Baseline vs. Full CloudRescue).
  - Option 2: Three-way ablation comparison (Baseline vs. Brownout Controller Alone vs. Full CloudRescue with Brownout Controller + Brownout-Aware Load Balancing).
  - Option 3: Multi-factor grid varying all sub-mechanisms simultaneously.
- **Decision:** Adopt Option 2: a three-way ablation experiment comparing:
  1. *Configuration A (Baseline)*: No brownout ($\theta = 1.0$), conventional Join-Shortest-Queue (JSQ) load balancing.
  2. *Configuration B (Brownout Only)*: Adaptive brownout feedback controller ($\theta_i(t)$), conventional Join-Shortest-Queue (JSQ) load balancing.
  3. *Configuration C (Full CloudRescue)*: Adaptive brownout feedback controller ($\theta_i(t)$), brownout-aware load balancing (BALB).
- **Rationale:** A three-way ablation cleanly isolates whether the brownout-aware load balancing mechanism contributes measurable resilience advantages beyond the local feedback controller alone, addressing an explicit finding in Klein et al. [61] regarding controller-balancer interactions.
- **Consequences:** The simulation engine and runner must support running all three modes under identical pseudorandom seeds, workloads, and failure schedules.
- **Evidence:** Welsh & Benkhelifa (2020), Section 2.3, p. 59:15; Klein et al. (2014) [61].

### DEC-006 — Brownout controller and brownout-aware load balancing selected as implementation scope
- **Date:** 2026-10-30
- **Status:** Accepted
- **Context:** The implementation scope for the brownout resilience technique must be formally bounded for a Python discrete-event simulation.
- **Options considered:**
  - Option 1: Brownout controller only on a single worker instance (as in Klein et al. [60]).
  - Option 2: Brownout controller combined with brownout-aware load balancing across multiple worker instances (as in Klein et al. [61]).
  - Option 3: Full autonomous cloud deployment with auto-scaling, container migration, and brownout.
- **Decision:** Adopt Option 2: Brownout feedback controller + brownout-aware load balancing across a cluster of simulated cloud worker instances. Note: The multi-attribute scoring function ($Score_i = \alpha \theta_i - \beta \frac{q_i}{Q_{\text{max}}} - \gamma U_i$) is a CloudRescue design that synthesizes the principles of Klein et al. [61] rather than an exact reproduction of their Rubis benchmark heuristic.
- **Rationale:** Option 1 is constrained by single-replica limitations noted by Welsh & Benkhelifa (Table 5, p. 59:13). Option 3 introduces excessive complexity (e.g., VM provisioning delays) that distracts from the core resilience mechanism. Option 2 provides a realistic, multi-node service architecture while remaining tractable and testable in a discrete-event simulation.
- **Consequences:** The simulator must model: (a) discrete worker instances with mandatory and optional execution stages, (b) individual worker queues, (c) periodic feedback controllers adjusting dimmer $\theta_i$, and (d) a central load balancer that routes incoming requests based on queue lengths, utilization, and dimmer state.
- **Evidence:** Welsh & Benkhelifa (2020), Section 2.3, p. 59:15; Table 5, p. 59:13; Klein et al. (2014) [60, 61].

### DEC-005 — Brownout resilience technique selected
- **Date:** 2026-10-30
- **Status:** Accepted
- **Context:** The primary research technique must be traceably selected from the assigned survey paper (*On Resilience in Cloud Computing*, Welsh & Benkhelifa, ACM CSUR 2020).
- **Options considered:**
  - Option 1: Brownout-based self-adaptive graceful degradation (Klein et al. [60, 61], Section 2.3, p. 59:15).
  - Option 2: Resilient task scheduling and VM allocation placement (Cartlidge & Sriram [25], Section 2.3, pp. 59:13–14).
  - Option 3: Component quality ranking and failure-aware orchestration (FTCloud, Zheng et al. [132], Section 2.3, p. 59:16).
  - Option 4: Memory snapshotting and VM replication (Remus, Cully et al. [34], Jhawar & Piuri [54], Section 2.2.2, p. 59:9).
- **Decision:** Select Option 1: **Brownout-based self-adaptive graceful degradation with brownout-aware load balancing**.
- **Rationale:** Welsh and Benkhelifa repeatedly emphasize that traditional cloud resilience relies on costly, over-provisioned redundancy (Section 3.1, p. 59:24; Section 4, p. 59:30). Brownout introduces an autonomic self-adaptation paradigm that preserves service availability and response latency during unexpected traffic surges and node failures by dynamically shedding optional computations rather than relying on idle replica over-provisioning. It is highly tractable in a discrete-event simulation (SimPy), produces rich time-series dynamics, and supports rigorous, paired statistical evaluation.
- **Consequences:** Project documentation (`PRD.md`, `EXPERIMENT_PLAN.md`, `RESEARCH_NOTES.md`, `ARCHITECTURE.md`, `README.md`) must be updated to align with the Brownout paradigm.
- **Evidence:** Welsh & Benkhelifa (2020), Section 2.3, p. 59:15; Table 5, p. 59:13; Table 9, p. 59:25; Klein et al. [60, 61].

### DEC-004 — Repository provenance
- **Date:** 2026-10-30
- **Status:** Accepted
- **Decision:** The previously cloned `Hriday2108/cloudrescue` repository is unrelated and must not be treated as the team's project.
- **Rationale:** It was cloned by mistake and is not confirmed as team-owned work.

### DEC-003 — Research technique
- **Date:** 2026-10-30
- **Status:** Superseded by DEC-005
- **Decision:** Do not select or implement a technique until the assigned paper has been reviewed.
- **Rationale:** The implementation and research claims must be grounded in the assigned source.

### DEC-002 — Visual direction
- **Date:** 2026-10-30
- **Status:** Accepted
- **Decision:** Use Variant A — Brutalist Swiss Monograph.
- **Rationale:** The selected visual direction uses Instrument Serif, Geist Sans, IBM Plex Mono, warm paper, ink black and electric blue.

### DEC-001 — Project identity
- **Date:** 2026-10-30
- **Status:** Accepted
- **Decision:** CloudRescue is an academic cloud-resilience simulator and research evaluation platform, not a cloud backup management dashboard.
- **Rationale:** The core assessment requires implementation and experimental evaluation of a resilience technique.
