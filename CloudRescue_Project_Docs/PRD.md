# CloudRescue — Product Requirements Document

**Version:** 1.3  
**Status:** Approved — Research Methodology, Metric Formulations & Simulation Architecture Finalized  
**Institution:** IIIT Dharwad  
**Project type:** Academic research, simulation and software implementation  
**Team:** Hari Prasad L, Yeruva Mahesh Reddy, K. Ram Charan  

---

## 1. Product overview

CloudRescue is an academic cloud-resilience simulation and research evaluation platform. It provides a controlled, reproducible environment to model cloud-service workloads, introduce stress scenarios (traffic surges and server failures), apply a formally grounded resilience mechanism, and evaluate system behavior against baseline configurations.

The primary resilience technique implemented in CloudRescue is:
> **Brownout-based self-adaptive graceful degradation with brownout-aware load balancing**

This technique is traceably grounded in the assigned survey paper, *On Resilience in Cloud Computing: A Survey of Techniques across the Cloud Domain* (Welsh & Benkhelifa, ACM Computing Surveys, 2020, DOI: 10.1145/3388922, Section 2.3, Table 5, Table 9), and its foundational primary literature: Klein et al. (ICSE 2014) [60] and Klein et al. (IEEE SRDS 2014) [61].

CloudRescue is an academic discrete-event simulator and research evaluation tool; it is **not** a production cloud-control plane, cloud backup manager, or disaster-recovery dashboard.

---

## 2. Problem statement

Cloud services regularly face severe disruptions driven by two complementary phenomena:
1. **Traffic Surges (Flash Crowds):** Unexpected spikes in user request arrival rates that overwhelm server processing capacity.
2. **Component & Server Dropouts:** Crash-stop failures of compute instances that abruptly reduce the aggregate serving capacity of a cluster while demand remains high.

Traditional cloud solutions rely on:
- *Static Over-Provisioning:* Maintaining large pools of idle replicas, which Welsh & Benkhelifa critique as economically wasteful and unsustainable (Section 3.1, p. 59:24; Section 4, p. 59:30).
- *Reactive Auto-Scaling:* Provisioning new virtual machines or containers, which incurs non-negligible cold-start latencies (often tens of seconds to minutes), leaving the system vulnerable to queue saturation and cascading timeouts during the critical onset of a shock.

Without adaptive mitigation, overloaded worker queues experience exponential delay inflation, causing extensive SLA violations, connection timeouts, and catastrophic service failure. CloudRescue implements and evaluates the **Brownout** paradigm—a control-theoretic self-adaptation mechanism that temporarily sheds optional application features to stabilize response latency, prevent service crashes, and maintain high request throughput under constrained capacity.

---

## 3. Goals

1. **Simulation Fidelity:** Model a realistic multi-worker cloud service in Python using discrete-event simulation (SimPy), incorporating request queues, finite worker capacity, and dual-stage (mandatory vs. optional) execution.
2. **Technique Implementation:** Implement an adaptive velocity-form brownout feedback controller (PI control loop adjusting dimmer $\theta_i \in [0, 1]$ with intrinsic anti-windup output clamping) and a brownout-aware load balancer that routes traffic preferentially to high-fidelity, low-queue workers without systematically overloading them.
3. **Three-Way Ablation Evaluation:** Compare three distinct configurations under identical conditions:
   - *Configuration A (Baseline):* Conventional cloud service without brownout ($\theta = 1.0$) and standardized Join-Shortest-Queue (JSQ) load balancing.
   - *Configuration B (Brownout Only):* Brownout feedback controller active with standardized Join-Shortest-Queue (JSQ) load balancing.
   - *Configuration C (Full CloudRescue):* Brownout feedback controller active with brownout-aware load balancing (BALB).
4. **Controlled Stress Testing:** Evaluate resilience across four standardized scenarios:
   - Scenario 1: Stationary / Nominal Workload.
   - Scenario 2: Bursty Flash-Crowd Surge.
   - Scenario 3: Server Failure (abrupt capacity reduction).
   - Scenario 4: Combined Flash Crowd and Server Failure.
5. **Rigorous Empirical Measurement:** Quantify outcomes using ten unambiguous metrics covering availability, latency, successful-request SLA violations, overall SLA failures, strict-subset service fidelity, adaptation/restoration recovery dynamics, server utilization, and load distribution.
6. **Academic Reproducibility:** Ensure all runs use deterministic pseudo-random seeds, maintain isolated random sub-streams to preserve input matching across configurations, preserve full configuration snapshots and event logs, and produce verified evidence suitable for academic reporting.

### 3.1 Non-goals

- Managing, modifying, or connecting to live production cloud providers (AWS, Azure, GCP).
- Deploying real production infrastructure or distributed container clusters.
- Claiming that the simulated discrete-event model is an exact bytecode-level reproduction of the Rubis/lighttpd benchmark in Klein et al. [60, 61]. The multi-attribute scoring function is explicitly a CloudRescue design.
- Fabricating experimental runs, performance numbers, or claims of statistical significance.
- Implementing non-selected techniques from the survey (e.g., hypervisor introspection, optical network routing).

---

## 4. Target users

- **Project Team:** Designing, configuring, running, and analyzing reproducible resilience experiments.
- **Academic Evaluators & Faculty:** Reviewing methodology, statistical validity, architecture, and code traceability against the assigned survey.
- **Distributed Systems Students & Researchers:** Exploring how graceful degradation and control theory interact with cloud load balancing.

---

## 5. Product workflow

```text
[ Configure Experiment ]
        │  (Workload, Failure Schedule, Server Sizing, Controller Gains, Seed)
        ▼
[ Validate Configuration ]
        │  (Verify parameter ranges, positive rates, valid setpoints)
        ▼
[ Generate Pre-Sampled Request Stream ]
        │  (Decoupled streams for arrival, mandatory time, optional time, threshold)
        ▼
[ Execute Three-Way Ablation ]
        ├── Run Configuration A: Baseline (θ=1.0, Join-Shortest-Queue)
        ├── Run Configuration B: Brownout Only (θ_i(t), Join-Shortest-Queue)
        └── Run Configuration C: Full CloudRescue (θ_i(t), Brownout-Aware LB)
        │  (All using identical pre-sampled requests and failure schedules)
        ▼
[ Record Raw Event Traces ]
        │  (Arrival, queue, start_mand, opt_eval, complete, timeout, drop, controller)
        ▼
[ Compute Documented Metrics ]
        │  (Success rate, Latency SLA rate, Overall SLA failure rate, Fidelity, Recovery)
        ▼
[ Analyze & Compare ]
        │  (Side-by-side tables, time-series response plots, statistical tests)
        ▼
[ Export Verified Artifacts ]
        └── (CSV data, run metadata JSON, summary report Markdown)
```

---

## 6. Functional requirements

### FR-01 — Experiment Configuration
The system shall allow users to configure typed simulation parameters, including:
- *Workload Parameters:* Mean arrival rate $\lambda_{\text{nom}}$, burst arrival rate $\lambda_{\text{burst}}$, burst start time $t_{\text{burst\_start}}$, burst duration $\Delta t_{\text{burst}}$, request timeout deadline $T_{\text{timeout}}$.
- *Cloud Worker Parameters:* Number of worker instances $M$, worker service rates (mandatory processing $\mu_{\text{mand}}$, optional processing $\mu_{\text{opt}}$), per-worker queue capacity $Q_{\text{max}}$.
- *Brownout Controller Parameters:* Target response latency setpoint $r_{\text{target}}$, controller update period $\Delta t_{\text{ctrl}}$, proportional gain $K_p$, integral gain $K_i$, dimmer bounds $[\theta_{\text{min}}, \theta_{\text{max}}]$, minimum sample threshold $N_{\text{min\_ctrl}}$, stall step decrement $\delta_{\text{stall}}$.
- *Load Balancer Parameters:* Routing policy selection (Join-Shortest-Queue for Baseline/Brownout-Only; Brownout-Aware composite scoring weights $\alpha, \beta, \gamma$ for Full CloudRescue).
- *Execution Parameters:* Total simulation time $T_{\text{sim}}$, warm-up period $T_{\text{warm}}$, random seed $S$.

### FR-02 — Failure Scenario Configuration
The simulator shall support four explicit, validated stress scenarios:
- `SCN-1` (Nominal): Constant Poisson arrival rate with all $M$ workers operational.
- `SCN-2` (Flash Crowd): Traffic surge where arrival rate jumps by a factor of $k_{\text{burst}}$ for duration $\Delta t_{\text{burst}}$.
- `SCN-3` (Server Crash): At time $t_{\text{fail}}$, one or more active workers experience an abrupt crash-stop failure (capacity loss), with optional recovery at $t_{\text{repair}}$.
- `SCN-4` (Combined Stress): Flash-crowd arrival surge occurring concurrently with a server crash failure.

### FR-03 — Baseline Execution (CFG-A)
The simulator shall execute a baseline configuration where:
- The dimmer variable is fixed at $\theta = 1.0$ (no brownout adaptation).
- All requests attempt both mandatory and optional computations.
- The load balancer routes requests using the standardized **Join-Shortest-Queue (JSQ)** policy.

### FR-04 — Brownout-Only Execution (CFG-B)
The simulator shall execute an intermediate configuration where:
- Each worker instance runs a local brownout feedback controller adjusting $\theta_i(t)$.
- Requests execute mandatory computation unconditionally; optional computation is evaluated immediately before optional execution begins using the worker's instantaneous dimmer $\theta_i(t)$.
- The load balancer routes requests using the standardized **Join-Shortest-Queue (JSQ)** policy, blind to worker dimmer values.

### FR-05 — Full CloudRescue Execution (CFG-C)
The simulator shall execute the full resilient configuration where:
- Brownout feedback controllers dynamically modulate worker dimmers $\theta_i(t)$.
- The load balancer employs **Brownout-Aware Load Balancing (BALB)**, using the composite scoring function $Score_i(t) = \alpha \theta_i(t) - \beta \frac{q_i(t)}{Q_{\text{max}}} - \gamma U_i(t)$ to balance fidelity, queue backlog, and CPU capacity without systematically overloading high-fidelity workers, where $U_i(t) \in [0.0, 1.0]$ represents cumulative mean operational utilization up to decision timestamp $t$.
- Crashed workers are immediately excluded from routing; if all operational workers exceed an overload threshold $Q_{\text{soft}}$, the balancer triggers soft-overload fallback ($Score_i^{\text{fallback}}(t) = -\beta \frac{q_i(t)}{Q_{\text{max}}} - \gamma U_i(t)$), disabling dimmer incentives ($\alpha = 0$) while retaining queue backlog and CPU capacity penalties.

### FR-06 — Fair Comparison Protocol & Multi-Stream Reproducibility
The execution engine shall guarantee that comparisons between Baseline, Brownout-Only, and Full CloudRescue use:
- Pre-generated request tuples with isolated random streams (Stream 1 for arrivals, Stream 2 for mandatory duration, Stream 3 for optional duration, Stream 4 for optional threshold, Stream 5 for failures).
- Identical arrival timestamps, processing requirements, and failure injection schedules across all three configurations under the same master seed.

### FR-07 — Metrics Collection
The simulator shall record raw timestamped events and compute ten standardized metrics:
1. Request Success Rate ($S_r$, $\%$, denominator: $N_{\text{submitted}}$)
2. Latency SLA Violation Rate ($V_{\text{lat}}$, $\%$, denominator: $N_{\text{success}}$)
3. Overall SLA Failure Rate ($V_{\text{overall}}$, $\%$, denominator: $N_{\text{submitted}}$, including drops, timeouts, crashes, and latency violations)
4. Mean Response Latency ($\bar{L}$, ms, denominator: $N_{\text{success}}$)
5. 95th-Percentile Response Latency ($L_{95}$, ms)
6. Service Fidelity ($F$, $\%$, numerator: $N_{\text{success, opt}}$, denominator: $N_{\text{success}}$)
7. Mean Dimmer Value ($\bar{\theta}$, $[0, 1]$, operational workers)
8. Adaptation Recovery Time ($T_{\text{adapt}}$, seconds, rolling $L_{95} \le r_{\text{SLA}}$ during stress)
9. Post-Restoration Recovery Time ($T_{\text{restore}}$, seconds, return to nominal $\bar{\theta} \ge 0.95$ and $L_{95} \le r_{\text{target}}$)
10. Server Utilization ($U_i$, $\%$, cumulative active execution vs. operational time up to decision/evaluation timestamp) and Load Fairness ($J$, Jain's Index over active workers)

### FR-08 — Results Visualization
The interface shall render comparison charts and tables using the approved *Brutalist Swiss Monograph* visual design:
- Time-series line charts showing response latency and dimmer evolution over time.
- Side-by-side ablation summary tables.
- Latency cumulative distribution function (CDF) curves.

### FR-09 — Experiment History & Persistence
The system shall preserve every completed experiment run as an immutable directory containing:
- Snapshot of input configuration (`config.json`).
- Compressed raw event log (`events.csv.gz`).
- Computed metrics summary (`metrics.json`).
- Run execution metadata (code version, start/end timestamps, seed).

### FR-10 — Validation & Error Handling
Configurations containing invalid parameter values (e.g., negative service rates, $r_{\text{target}} \le 0$, $\theta_{\text{min}} > \theta_{\text{max}}$) shall be rejected with informative error messages before simulation startup.

---

## 7. Non-functional requirements

- **Scientific Reproducibility:** Given the same configuration and random seed, the simulator must produce identical event traces and metric outputs across runs.
- **Decoupled Architecture:** Core simulation logic must have zero dependencies on frontend libraries, web servers, or external services.
- **Automated Test Coverage:** Automated unit and regression tests (using `pytest`) must cover controller mathematical stability, queue bounds, load balancer routing decisions, multi-stream independence, and metric calculation formulas.
- **Execution Performance:** A standard simulation run (e.g., 50,000 requests over 1,000 simulated seconds) should execute within a reasonable compute budget (under 10 seconds on commodity hardware).
- **Honest Academic Reporting:** Missing, failed, or incomplete runs must be explicitly flagged and never converted to zeroes or treated as successful trials. Right-censored recovery times must be clearly designated.

---

## 8. Technology stack

- **Simulation Framework:** Python 3.10+ with `simpy` (discrete-event simulation engine).
- **Scientific Computing & Data Analysis:** `numpy` (random distributions, percentiles) and `pandas` (event trace manipulation and aggregation).
- **Statistical Testing:** `scipy.stats` (normality testing, paired Wilcoxon signed-rank tests, t-tests).
- **Research Visualizations:** `matplotlib` (static publication-quality plots).
- **Automated Testing:** `pytest` (unit and integration tests).
- **Application / UI Layer:** Python API service with React frontend (Vite, Tailwind CSS, following `DESIGN.md`), to be implemented following simulation engine verification.

---

## 9. Main interface areas (Seven Screens)

1. **Overview / Cover:** Project provenance, citation of Welsh & Benkhelifa (2020), research question, and verified execution status.
2. **Configuration Lab:** Form controls for workload arrival rates, failure timing, cluster size, controller gains, and random seeds.
3. **Simulation Execution:** Real-time run controls, execution progress, event timeline, and execution logs.
4. **Three-Way Benchmark Comparison:** Side-by-side view comparing Baseline, Brownout-Only, and Full CloudRescue.
5. **Experimental Analytics:** Interactive time-series graphs ($\theta(t)$, latency over time), CDF distributions, and metric tables.
6. **Research Methodology:** Detailed documentation of the Brownout PI controller formulas, load-balancing heuristics, and metric definitions.
7. **Publication / Report Preview:** Exportable summary of experimental evidence, statistical confidence intervals, and research limitations.

---

## 10. Acceptance criteria

The project meets the requirements for academic evaluation when:
1. The Brownout controller and brownout-aware load balancer are implemented in Python discrete-event simulation and traceably mapped to Welsh & Benkhelifa (2020) and Klein et al. [60, 61].
2. The three-way comparison (Baseline, Brownout-Only, Full CloudRescue) executes under identical workload and failure conditions using isolated multi-stream PRNGs.
3. Automated test suites pass for all queueing, control, routing, and metric modules.
4. All ten metrics are computed strictly from raw recorded simulation events using documented formulas.
5. Repeated runs with matched seeds yield valid statistical distributions and confidence intervals.
6. No placeholder or mock values are presented as verified experimental measurements.
