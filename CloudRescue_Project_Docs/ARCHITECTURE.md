# CloudRescue — Software & Simulation Architecture

**Status:** Approved — Simulation Architecture & Methodological Formulations Finalized  
**Date:** 2026-10-31  
**Simulation Engine:** Python 3.10+ / SimPy (Discrete-Event Simulation)  

---

## 1. Architectural goals

1. **Scientific Testability & Decoupling:** Maintain complete architectural separation between the simulation engine, metrics computation, and presentation layers. The simulation must run autonomously from a CLI or Python script without requiring a web server or frontend.
2. **Multi-Stream Deterministic Reproducibility:** Every simulation execution must produce identical event sequences and metrics when supplied with an identical configuration snapshot and random seed. Request entities must use pre-sampled attributes across isolated random streams so that skipping optional tasks in one configuration does not desynchronize random inputs for subsequent requests.
3. **Faithful Control Abstraction:** Accurately implement the control-theoretic brownout paradigm (Klein et al. [60, 61]) and brownout-aware load balancing as a discrete-event queueing network. The composite scoring function used by CloudRescue is explicitly a CloudRescue design that synthesizes the principles of Klein et al. [61] rather than a literal clone of their Rubis benchmark heuristic.

---

## 2. Logical system architecture

```text
+---------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER                                 |
|   React (Vite + Tailwind CSS) — Brutalist Swiss Monograph Direction (DESIGN.md)       |
|   [Overview] [Config Lab] [Sim Lab] [3-Way Benchmark] [Analytics] [Methodology] [Pub] |
+---------------------------------------------------------------------------------------+
                                           │ HTTP / JSON
                                           ▼
+---------------------------------------------------------------------------------------+
|                                APPLICATION & API LAYER                                |
|   FastAPI / Lightweight Python Service                                                |
|   - Configuration Validation (Typed schemas)                                          |
|   - Experiment Orchestrator & Multi-Run Dispatcher                                    |
|   - Run Artifact Serialization & Retrieval                                            |
+---------------------------------------------------------------------------------------+
                                           │
                                           ▼
+---------------------------------------------------------------------------------------+
|                              SIMULATION CORE (SimPy Engine)                           |
|                                                                                       |
|   +-------------------------------------------------------------------------------+   |
|   | 1. Workload Generator (`workload.py`)                                         |   |
|   |    - Multi-Stream PRNG Architecture (Streams 1, 2, 3, 4)                      |   |
|   |    - Pre-generates immutable Request tuples:                                  |   |
|   |      (k, t_arrive, S_mand, S_opt, U_opt, T_timeout)                           |   |
|   +-------------------------------------------------------------------------------+   |
|                                          │                                            |
|                                          ▼ Incoming Requests                          |
|   +-------------------------------------------------------------------------------+   |
|   | 2. Load Balancer (`load_balancer.py`)                                         |   |
|   |    - CFG-A & CFG-B: Standardized Join-Shortest-Queue (JSQ)                     |   |
|   |    - CFG-C: Brownout-Aware Load Balancer (BALB)                               |   |
|   |      Score_i = α*θ_i - β*(q_i/Q_max) - γ*U_i                                  |   |
|   |    - Anti-Overloading: Queue penalty prevents saturating high-θ workers       |   |
|   |    - Fallback: Disables α when all workers exceed Q_soft (retains q & U penalties)|   |
|   |    - Failure Masking: Excludes crashed worker instances                       |   |
|   +-------------------------------------------------------------------------------+   |
|                                          │ Dispatched Requests                        |
|                                          ▼                                            |
|   +-------------------------------------------------------------------------------+   |
|   | 3. Cloud Worker Instances (`server.py`) [M=4 Instances]                       |   |
|   |    - Individual FIFO Request Queues (Capacity Q_max)                          |   |
|   |    - Timeout Checker: Drops requests exceeding T_timeout in queue             |   |
|   |    - Stage 1: Mandatory Computation (Always executed, S_mand)                 |   |
|   |    - Stage 2: Instantaneous Optional Decision:                                |   |
|   |      Execute S_opt iff U_opt <= θ_i(t_mand_end), else Bypass                  |   |
|   +-------------------------------------------------------------------------------+   |
|                         ▲                                 │                           |
|                         │ Adjusts θ_i                     │ Reports Latency & State   |
|   +-------------------------------------------------------------------------------+   |
|   | 4. Brownout Feedback Controller (`controller.py`)                             |   |
|   |    - Velocity Form PI Control: Δθ_i = Kp*(e - e_prev) + Ki*e*Δt               |   |
|   |    - Error: e_i(t) = r_target - r_measured(t) (Sign: latency > target => e<0) |   |
|   |    - Intrinsic Anti-Windup Clamping: θ_i in [θ_min, θ_max]                    |   |
|   |    - Insufficient Data Hold: If samples < N_min_ctrl, skips update & holds θ  |   |
|   |    - Stalled Queue Detection: Decrements θ if queue > 0 and wait > r_target   |   |
|   |    - Feature Restorer: Gradually recovers θ_i to 1.0 when load drops          |   |
|   +-------------------------------------------------------------------------------+   |
|                         ▲                                                             |
|                         │ Failure Events (Stream 5)                                   |
|   +-------------------------------------------------------------------------------+   |
|   | 5. Failure Injector (`failures.py`)                                           |   |
|   |    - Crash-Stop Schedule (Halts workers, drops in-flight tasks)               |   |
|   |    - Recovery Schedule (Re-enables workers, resets queues)                    |   |
|   +-------------------------------------------------------------------------------+   |
|                                          │                                            |
|                                          ▼ Raw Simulation Events                      |
|   +-------------------------------------------------------------------------------+   |
|   | 6. Event Recorder (`events.py`)                                               |   |
|   |    - Structured timestamped events (arrival, queue, mand, opt, drop, etc.)     |   |
|   +-------------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------------+
                                           │
                                           ▼
+---------------------------------------------------------------------------------------+
|                                METRICS & STORAGE LAYER                                |
|   - Metrics Engine (`metrics.py`): Computes 10 standardized metrics                   |
|     (Sr, V_lat, V_overall, L_mean, L_95, F, θ_mean, T_adapt, T_restore, U, J)         |
|   - Artifact Store (`storage.py`): Preserves `config.json`, `events.csv.gz`,          |
|     `metrics.json`, and run execution logs under `results/{run_id}/`                  |
+---------------------------------------------------------------------------------------+
```

---

## 3. Core simulation components

### 3.1 Workload Generator (`simulator/cloudrescue/workload/`)
- Pre-generates immutable `Request` tuples using isolated pseudorandom number generator (PRNG) streams:
  - **Stream 1 (Arrival Process):** Inter-arrival times $\Delta t_k$ for stationary Poisson or bursty flash crowd.
  - **Stream 2 (Mandatory Service Duration):** $S_{\text{mand}, k} \sim \text{Exp}(\mu_{\text{mand}})$.
  - **Stream 3 (Optional Service Duration):** $S_{\text{opt}, k} \sim \text{Exp}(\mu_{\text{opt}})$.
  - **Stream 4 (Optional Execution Draw):** $U_{\text{opt}, k} \sim \text{Uniform}(0.0, 1.0)$.
  - **Stream 5 (Failure Injector):** Exact timestamps for crash and repair events.
- **Request Tuple Definition:**
  $$\text{Request}_k = \left( k, t_{\text{arrive}, k}, S_{\text{mand}, k}, S_{\text{opt}, k}, U_{\text{opt}, k}, T_{\text{timeout}} \right)$$
- Because attributes are pre-sampled, skipping optional execution in one configuration draws zero additional random numbers, preserving 100% matched arrivals and workloads across all configurations under the same master seed.

### 3.2 Cloud Worker / Server Model (`simulator/cloudrescue/cloud_model/`)
- Models $M = 4$ worker instances.
- Each worker manages:
  - An independent FIFO queue bounded by $Q_{\text{max}}$. Arriving requests are dropped if $q_i \ge Q_{\text{max}}$ (`DROP_QUEUE_FULL`).
  - Timeout enforcement: When a request reaches the head of the queue, if its queue waiting time $t - t_{\text{arrive}} > T_{\text{timeout}}$, it is aborted prior to execution (`DROP_TIMEOUT`).
  - **Stage 1 (Mandatory Logic):** Executed for all admitted requests for duration $S_{\text{mand}, k}$.
  - **Stage 2 (Optional Logic — Instantaneous Decision):** Evaluated immediately at timestamp $t_{\text{mand\_end}}$ using the worker's instantaneous dimmer $\theta_i(t_{\text{mand\_end}})$:
    - If $U_{\text{opt}, k} \le \theta_i(t_{\text{mand\_end}})$: Executes Stage 2 for duration $S_{\text{opt}, k}$. Emits `OPTIONAL_EXECUTED(k, i, t, \theta_i)`.
    - If $U_{\text{opt}, k} > \theta_i(t_{\text{mand\_end}})$: Bypasses Stage 2 immediately. Emits `OPTIONAL_BYPASSED(k, i, t, \theta_i)`.

### 3.3 Brownout Feedback Controller (`simulator/cloudrescue/resilience/controller/`)
- Operates as a periodic SimPy process invoked every $\Delta t_{\text{ctrl}} = 1.0\text{ s}$ per worker instance.
- **Error Calculation & Sign Convention:**
  $$e_i(t) = r_{\text{target}} - \hat{r}_{95, i}(t)$$
  Where $\hat{r}_{95, i}(t)$ is the 95th-percentile response latency of requests completed on worker $i$ during $[t - \Delta t_{\text{ctrl}}, t]$.
  - If latency exceeds target ($\hat{r}_{95, i}(t) > r_{\text{target}}$): $e_i(t) < 0$ (overloaded).
  - If latency is below target ($\hat{r}_{95, i}(t) \le r_{\text{target}}$): $e_i(t) \ge 0$ (headroom available).
- **Handling Insufficient / Missing Data:**
  - If completed sample count $n_i(t) < N_{\text{min\_ctrl}}$ (default 5 requests): Latency cannot be reliably estimated.
    1. The PI computation is **skipped entirely**.
    2. Dimmer is held constant: $\theta_i(t) = \theta_i(t - \Delta t_{\text{ctrl}})$.
    3. The error state is marked invalid.
    4. **State Resumption:** When valid measurements resume at a later tick $t_{\text{resume}}$ ($n_i \ge N_{\text{min\_ctrl}}$), the previous error is re-initialized: $e_{i,\text{prev}} \leftarrow e_i(t_{\text{resume}})$. The derivative term $K_p (e_i - e_{i,\text{prev}})$ evaluates to zero on the first resumption step, preventing an artificial derivative kick.
  - If $n_i(t) < N_{\text{min\_ctrl}}$ but queue depth $q_i(t) > 0$ and the head-of-line request waiting time exceeds $r_{\text{target}}$, the controller detects queue stall and forces $\theta_i(t) = \max(\theta_{\text{min}}, \theta_i(t - \Delta t_{\text{ctrl}}) - \delta_{\text{stall}})$.
- **Velocity Form Discrete PI Control Update:**
  $$\Delta \theta_i(t) = K_p \left( e_i(t) - e_i(t - \Delta t_{\text{ctrl}}) \right) + K_i \cdot e_i(t) \cdot \Delta t_{\text{ctrl}}$$
  $$\theta_{\text{cand}, i}(t) = \theta_i(t - \Delta t_{\text{ctrl}}) + \Delta \theta_i(t)$$
  *(Negative error produces $\Delta \theta_i(t) < 0$, smoothly decreasing the dimmer.)*
- **Intrinsic Anti-Windup Clamping:**
  $$\theta_i(t) = \begin{cases} \theta_{\text{min}} & \text{if } \theta_{\text{cand}, i}(t) < \theta_{\text{min}} \\ \theta_{\text{max}} & \text{if } \theta_{\text{cand}, i}(t) > \theta_{\text{max}} \\ \theta_{\text{cand}, i}(t) & \text{otherwise} \end{cases}$$
  Where $[\theta_{\text{min}}, \theta_{\text{max}}] = [0.0, 1.0]$.
  *Intrinsic Anti-Windup Mechanism:* Because subsequent updates compute $\theta_{\text{cand}, i}(t + \Delta t_{\text{ctrl}})$ from the **clamped value** $\theta_i(t)$ rather than an unbounded unconstrained accumulator, no hidden integral accumulation exists beyond $[0.0, 1.0]$. The instant the error reverses sign ($e_i(t) > 0$), $\theta_i(t)$ immediately begins recovering upward without unwinding delay.
- **Feature Restoration:** As queues clear, $\hat{r}_{95, i}(t) < r_{\text{target}} \implies e_i(t) > 0$. The controller smoothly drives $\theta_i(t)$ back to $1.0$.

### 3.4 Load Balancer Architecture (`simulator/cloudrescue/resilience/load_balancer/`)
- **Conventional Policy (Used in `CFG-A` and `CFG-B`):**
  - **Join-Shortest-Queue (JSQ):** Routes incoming requests to the operational worker with the smallest current queue length $q_i(t)$. Excludes crashed workers.
- **Brownout-Aware Policy (Used exclusively in `CFG-C`):**
  - Evaluates candidate operational workers using the composite utility score:
    $$Score_i(t) = \alpha \cdot \theta_i(t) - \beta \cdot \left(\frac{q_i(t)}{Q_{\text{max}}}\right) - \gamma \cdot U_i(t)$$
  - *Provenance:* This scoring function is a **CloudRescue design** synthesizing the principles of Klein et al. [61].
  - **Roles of Queue Depth vs. CPU Utilization:**
    - Queue depth ($q_i$) is a **forward-looking backlog indicator** reflecting requests waiting in the buffer, directly governing queue waiting time and drop risk.
    - CPU utilization ($U_i$) is the **cumulative mean operational utilization up to the decision timestamp**, reflecting historical processor busy-time over operational uptime ($T_{\text{busy}, i} / T_{\text{operational}, i}$).
    - Under brownout, when $\theta_i$ drops, requests take shorter service times ($S_{\text{mand}}$ only), decoupling queue depth from CPU utilization. Both terms are required to capture instantaneous buffer risk and compute capacity.
    - Weights $\alpha, \beta, \gamma$ are not assumed optimal; they will be calibrated empirically via sensitivity experiments.
  - **Anti-Overloading Penalty:** As queue depth $q_i$ grows, the penalty term $-\beta \left(\frac{q_i}{Q_{\text{max}}}\right)$ scales dynamically, preventing the balancer from continuously routing traffic to a high-fidelity worker ($\theta_i = 1.0$) until its queue explodes.
  - **Soft Overload Fallback:** If all operational workers have $q_i(t) \ge Q_{\text{soft}}$ ($80\%$ of $Q_{\text{max}}$), the balancer disables dimmer weighting ($\alpha = 0$), transitioning to the fallback score $Score_i^{\text{fallback}}(t) = -\beta \left(\frac{q_i(t)}{Q_{\text{max}}}\right) - \gamma U_i(t)$. This eliminates optional-computation incentives while preserving queue backlog and CPU capacity penalties to prevent queue drops.
  - **Failure Masking:** Crashed workers are immediately excluded from routing.

### 3.5 Failure Injector (`simulator/cloudrescue/failures/`)
- Triggers scheduled failure and recovery events:
  - At $t_{\text{fail}}$, signals target workers to crash. In-flight requests are aborted (`FAILED_SERVER_CRASH`); subsequent requests bypass crashed workers.
  - At $t_{\text{repair}}$, signals workers to recover, clears failure states, and re-registers them with the load balancer.

### 3.6 Event Recorder (`simulator/cloudrescue/events/`)
- Emits structured event logs:
  - `REQUEST_SUBMITTED(request_id, timestamp)`
  - `REQUEST_QUEUED(request_id, worker_id, timestamp, queue_depth)`
  - `REQUEST_DROPPED_QUEUE(request_id, timestamp)`
  - `REQUEST_DROPPED_TIMEOUT(request_id, worker_id, timestamp, wait_time)`
  - `MANDATORY_START(request_id, worker_id, timestamp)`
  - `MANDATORY_END(request_id, worker_id, timestamp, duration)`
  - `OPTIONAL_EXECUTED(request_id, worker_id, timestamp, theta, duration)`
  - `OPTIONAL_BYPASSED(request_id, worker_id, timestamp, theta)`
  - `REQUEST_COMPLETED(request_id, worker_id, timestamp, total_latency, full_fidelity)`
  - `CONTROLLER_UPDATED(worker_id, timestamp, measured_lat, error, old_theta, new_theta)`
  - `SERVER_CRASHED(worker_id, timestamp)`
  - `SERVER_RECOVERED(worker_id, timestamp)`

### 3.7 Metrics Calculator (`simulator/cloudrescue/metrics/`)
- Computes the ten standardized metrics strictly from event logs:
  1. $S_r = \frac{N_{\text{success}}}{N_{\text{submitted}}} \times 100\%$
  2. $V_{\text{lat}} = \frac{N_{\text{lat\_violation}}}{N_{\text{success}}} \times 100\%$ (successful requests)
  3. $V_{\text{overall}} = \frac{N_{\text{drop\_queue}} + N_{\text{drop\_timeout}} + N_{\text{failed\_crash}} + N_{\text{lat\_violation}}}{N_{\text{submitted}}} \times 100\%$ (all submitted requests)
  4. $\bar{L} = \frac{1}{N_{\text{success}}} \sum L_i$
  5. $L_{95} = \text{Percentile}_{95}(\{L_i\})$
  6. $F = \frac{N_{\text{success, opt}}}{N_{\text{success}}} \times 100\%$ ($N_{\text{success, opt}} \le N_{\text{success}}$; $0\%$ if $N_{\text{success}} = 0$)
  7. $\bar{\theta}$ (time-weighted operational worker dimmer average)
  8. $T_{\text{adapt}}$ (adaptation recovery time during stress)
  9. $T_{\text{restore}}$ (post-restoration recovery time after repair)
  10. $U_i / \bar{U}$ (busy time over operational time) and $J$ (Jain's index over active workers)

### 3.8 Experiment Runner (`simulator/cloudrescue/runner/`)
- Executes the three-way ablation experiment:
  - `CFG-A`: Baseline ($\theta = 1.0$, JSQ)
  - `CFG-B`: Brownout Only ($\theta_i(t)$, JSQ)
  - `CFG-C`: Full CloudRescue ($\theta_i(t)$, BALB)
- Feeds identical pre-sampled request tuples to all three configurations per master seed $S$.

---

## 4. Implemented codebase layout

```text
CloudRescue-Research/
├── CloudRescue_Project_Docs/      # Formal research requirements, PRD, architecture, and ADRs
│   ├── AGENTS.md                  # Rules of engagement and safety constraints
│   ├── ARCHITECTURE.md            # Simulator architecture & mathematical derivations
│   ├── DECISIONS.md               # ADRs logging decisions DEC-001 through DEC-010
│   ├── DESIGN.md                  # Visual design system & screen specifications
│   ├── EXPERIMENT_PLAN.md         # Pre-registered experimental methodology
│   ├── PRD.md                     # Product requirements & 10 standardized metrics
│   ├── README.md                  # Documentation index & status map
│   └── RESEARCH_NOTES.md          # Literature survey mapping (Welsh & Benkhelifa; Klein et al.)
├── frontend/                      # React 19 + Vite 8 + Tailwind CSS 4 research dashboard
│   ├── src/
│   │   ├── components/            # Navigation and Colophon footer
│   │   ├── screens/               # 7 editorial monograph screens (Screens 1–7)
│   │   └── api.js                 # Frontend REST API client
│   ├── package.json
│   └── vite.config.js             # Dev server & backend proxy configuration
├── paper/                         # Formal academic research manuscript & audits
│   ├── CloudRescue_Research_Paper_Draft.md  # Complete 10-section paper draft
│   ├── SECTION_8_AUDIT_REPORT.md  # Certified 770-cell data audit
│   ├── FINAL_ACADEMIC_REVIEW.md   # 10-criterion academic audit
│   └── REFERENCES_TO_VERIFY.md    # 17/17 verified IEEE citations
├── research/
│   └── assigned-paper.pdf         # Foundational survey paper (Welsh & Benkhelifa 2020)
├── results/                       # Certified experimental outputs
│   └── experiment_360/            # Primary evaluation (360 runs, 30 matched seeds)
│       ├── master_results.csv     # Master results table (360 rows × 28 metrics)
│       ├── aggregated_metrics.csv # Summary metrics by scenario and configuration
│       ├── statistical_comparisons.csv # Paired hypothesis test battery
│       ├── plots/                 # 6 publication-ready figures (300 DPI)
│       ├── sensitivity/           # 144-run BALB weight grid sweeps
│       └── runs/                  # Per-run traces, configs, and controller timeseries
├── scripts/                       # CLI experiment orchestrators and analysis tools
│   ├── run_experiment_matrix.py   # 360-run master execution orchestrator
│   ├── analyze_results.py         # Paired statistical hypothesis tests
│   ├── run_sensitivity.py         # 144-run BALB weight grid sweeps
│   ├── generate_plots.py          # 300 DPI publication figure generator
│   ├── run_baseline.py            # CFG-A preliminary validation runner
│   ├── run_brownout.py            # CFG-B preliminary validation runner
│   ├── run_balb.py                # CFG-C preliminary validation runner
│   ├── compare_ablation.py        # 3-way validation run comparison table
│   └── reconcile_recovery_metrics.py # DEC-010 nominal reference reconciliation
├── server/                        # FastAPI REST API backend
│   └── main.py                    # Read-only service exposing verified experiment data
├── simulator/cloudrescue/         # Discrete-event simulation package (SimPy)
│   ├── __init__.py
│   ├── config.py                  # Pydantic configuration schemas and validation
│   ├── balancing/                 # Ingress load balancing policies
│   │   ├── __init__.py
│   │   ├── brownout_aware.py      # BALB composite scoring with anti-overload penalties
│   │   └── shortest_queue.py      # Standard Join-Shortest-Queue (JSQ) baseline
│   ├── control/                   # Autonomic feedback controllers
│   │   ├── __init__.py
│   │   └── brownout_controller.py # Discrete velocity-form PI controller with anti-windup
│   ├── engine/                    # Simulation execution engine
│   │   ├── __init__.py
│   │   └── simulation.py          # SimPy coordinator and failure injection lifecycle
│   ├── models/                    # Simulation domain entities
│   │   ├── __init__.py
│   │   ├── request.py             # Request data tuple and lifecycle states
│   │   └── worker.py              # Dual-stage compute worker with bounded FIFO queue
│   ├── monitoring/                # Telemetry and post-simulation analysis
│   │   ├── __init__.py
│   │   ├── event_logger.py        # Structured event streams and CSV serialization
│   │   └── recovery_analyzer.py   # DEC-010 nominal-referenced recovery analyzer
│   └── workload/                  # Workload generation
│       ├── __init__.py
│       └── generator.py           # 5-stream PRNG-isolated arrival and service generator
├── tests/                         # 56 automated unit and regression tests
├── FINAL_FREEZE_SIGNOFF.md        # Formal research freeze certificate
├── FINAL_REPRODUCIBILITY_AUDIT.md # Comprehensive independent reproducibility audit report
├── pytest.ini                     # Pytest configuration
├── requirements.txt               # Pinned Python dependencies
└── README.md                      # Root project overview and reproduction guide
```

---

## 5. Simulation execution contract

Every execution directory in `results/{run_id}/` must contain:
1. `config.json`: Unaltered configuration snapshot.
2. `metadata.json`: Commit hash, Python version, platform details, run duration.
3. `seed.txt`: The random seed used.
4. `events.csv.gz`: Compressed raw event log.
5. `metrics.json`: Evaluated 10 standardized metrics.
6. `integrity.json`: Checksums (SHA-256) of input config and output metrics.
