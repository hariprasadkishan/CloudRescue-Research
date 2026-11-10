# CloudRescue — Experimental Plan

**Status:** Approved — Experimental Methodology & Metric Formulations Finalized  
**Date:** 2026-10-31  
**Authors:** CloudRescue Research Team (IIIT Dharwad)  

---

## 1. Research question

> **RQ1:** Under stochastic traffic surges and sudden server crash failures in a simulated cloud service, to what extent does autonomic brownout self-adaptation (graceful feature degradation combined with brownout-aware load balancing) improve request success rate, latency SLA compliance, and overall SLA reliability compared to a conventional non-degrading baseline under Join-Shortest-Queue load balancing, and how does brownout-aware load balancing compare against local brownout control alone?

---

## 2. Hypotheses

*Note: All numerical percentage targets in the alternative hypotheses are provisional pre-registered research targets. They are not experimental findings and must not be reported as measured results until runs are executed.*

### Primary Hypothesis — Latency & SLA Compliance
- **Null Hypothesis ($H_{0,1}$):** Under simulated traffic spikes and instance failure scenarios, there is no statistically significant difference in 95th-percentile response latency ($L_{95}$), successful-request latency SLA violation rate ($V_{\text{lat}}$), or overall SLA failure rate ($V_{\text{overall}}$) between the brownout-enabled configurations and the static baseline ($p \ge 0.05$).
- **Alternative Hypothesis ($H_{1,1}$):** Under simulated traffic spikes and instance failure scenarios, the brownout-enabled configurations yield a statistically significant reduction in 95th-percentile latency ($L_{95}$), a statistically significant reduction in latency SLA violations ($V_{\text{lat}}$), and a statistically significant reduction in overall SLA failures ($V_{\text{overall}}$) compared to the static baseline ($p < 0.05$).

### Secondary Hypothesis — Failure Recovery Time
- **Null Hypothesis ($H_{0,2}$):** Following an abrupt 50% cluster capacity reduction (server crash-stop), the duration required for service response times to achieve adaptation recovery ($T_{\text{adapt}}$) during the failure or post-restoration recovery ($T_{\text{restore}}$) after server repair does not differ between the brownout-enabled systems and the baseline ($p \ge 0.05$).
- **Alternative Hypothesis ($H_{1,2}$):** Following an abrupt 50% cluster capacity reduction, the brownout-enabled systems achieve statistically significantly faster adaptation recovery ($T_{\text{adapt}}$) and post-restoration recovery ($T_{\text{restore}}$) than the baseline ($p < 0.05$).

### Ablation Hypothesis — Incremental Value of Brownout-Aware Load Balancing
- **Null Hypothesis ($H_{0,3}$):** Combining brownout-aware load balancing (BALB) with local brownout controllers (`CFG-C`) yields no statistically significant difference in service fidelity ($F$) or load distribution fairness ($J$) compared to local brownout controllers operating with conventional Join-Shortest-Queue load balancing (`CFG-B`) ($p \ge 0.05$).
- **Alternative Hypothesis ($H_{1,3}$):** Combining brownout-aware load balancing with local brownout controllers (`CFG-C`) yields a statistically significant improvement in service fidelity ($F$) and load distribution fairness ($J$) compared to local brownout controllers with conventional Join-Shortest-Queue load balancing (`CFG-B`) ($p < 0.05$).

---

## 3. Experimental variables

### 3.1 Independent variables

1. **Resilience Configuration (Ablation Factor — 3 levels):**
   - `CFG-A` (Baseline): No brownout ($\theta = 1.0$), standardized **Join-Shortest-Queue (JSQ)** load balancing.
   - `CFG-B` (Brownout Only): Adaptive velocity-form brownout PI feedback controller active on each worker ($\theta_i(t)$), standardized **Join-Shortest-Queue (JSQ)** load balancing.
   - `CFG-C` (Full CloudRescue): Adaptive velocity-form brownout PI feedback controller active on each worker ($\theta_i(t)$), **Brownout-Aware Load Balancing (BALB)**.

2. **Workload Scenario (2 levels):**
   - `WKL-1` (Nominal Stationary): Homogeneous Poisson arrivals at baseline rate $\lambda_{\text{nom}} = 80\text{ req/s}$.
   - `WKL-2` (Bursty Flash Crowd): Baseline Poisson arrivals $\lambda_{\text{nom}} = 80\text{ req/s}$ with a severe burst of $\lambda_{\text{burst}} = 240\text{ req/s}$ ($3\times$ surge) lasting from $t = 300\text{ s}$ to $t = 450\text{ s}$ ($\Delta t = 150\text{ s}$).

3. **Failure Schedule (2 levels):**
   - `FAIL-0` (No Failure): All $M = 4$ worker instances remain healthy throughout the run.
   - `FAIL-1` (Server Crash): At $t = 500\text{ s}$, 2 of the 4 worker instances experience an immediate crash-stop failure (50% cluster capacity drop) lasting until $t = 700\text{ s}$, after which they recover.

Cross-combining Workload and Failure yields **4 Stress Conditions**:
- Condition 1: Nominal (`WKL-1` + `FAIL-0`)
- Condition 2: Flash Crowd Surge (`WKL-2` + `FAIL-0`)
- Condition 3: Server Crash Failure (`WKL-1` + `FAIL-1`)
- Condition 4: Combined Flash Crowd & Server Crash (`WKL-2` + `FAIL-1`)

### 3.2 Controlled variables (Provisional Parameters Pending Calibration)

| Parameter | Symbol | Value | Unit | Rationale |
|---|---|---|---|---|
| Number of Worker Instances | $M$ | 4 | instances | Standard academic cluster size for multi-server queueing. |
| Mandatory Service Time Mean | $\mu_{\text{mand}}^{-1}$ | 10 | ms | Core business logic / DB query execution (exponentially distributed). |
| Optional Service Time Mean | $\mu_{\text{opt}}^{-1}$ | 30 | ms | Recommendation engine / widget rendering (exponentially distributed). |
| Worker Queue Capacity | $Q_{\text{max}}$ | 50 | requests | Maximum queue depth per worker before rejection/drop. |
| Request Timeout Deadline | $T_{\text{timeout}}$ | 200 | ms | Max permissible wait+service time before client drops connection. |
| SLA Response Time Threshold | $r_{\text{SLA}}$ | 100 | ms | Maximum acceptable response time for successful request. |
| Target Latency Setpoint | $r_{\text{target}}$ | 80 | ms | Controller reference setpoint, set with a safety margin below $r_{\text{SLA}}$. |
| Controller Update Interval | $\Delta t_{\text{ctrl}}$ | 1.0 | s | Discrete control period for re-evaluating dimmer $\theta_i$. |
| Min Sample Count for Controller | $N_{\text{min\_ctrl}}$ | 5 | requests | Threshold below which controller skips update and holds $\theta_i$. |
| Stalled Queue Step Decrement | $\delta_{\text{stall}}$ | 0.05 | — | Decrement applied when queue is non-empty but stalled ($L_{\text{wait}} > r_{\text{target}}$). |
| Proportional Gain | $K_p$ | 0.5 | — | Control gain governing immediate error response (provisional). |
| Integral Gain | $K_i$ | 0.1 | $\text{s}^{-1}$ | Control gain eliminating steady-state latency error (provisional). |
| Dimmer Variable Bounds | $[\theta_{\text{min}}, \theta_{\text{max}}]$ | $[0.0, 1.0]$ | — | 0.0 = mandatory only; 1.0 = mandatory + optional features. |
| BALB Routing Weights | $\alpha, \beta, \gamma$ | $1.0, 1.0, 0.5$ | — | Provisional weights for dimmer, queue penalty, and utilization. |
| Recovery Evaluation Window | $W_{\text{rec}}$ | 10.0 | s | Sliding window duration for evaluating rolling p95 latency. |
| Min Samples for Recovery Check | $N_{\text{rec\_min}}$ | 20 | requests | Minimum completed requests required in window to evaluate p95. |
| Total Simulation Duration | $T_{\text{sim}}$ | 1,000 | s | Captures warm-up, steady-state, burst, crash, and restoration. |
| Warm-Up Period | $T_{\text{warm}}$ | 100 | s | Initial period excluded from final steady-state metric calculations. |

---

## 4. Multi-stream reproducibility architecture

To guarantee **perfect input matching** across Baseline (`CFG-A`), Brownout-Only (`CFG-B`), and Full CloudRescue (`CFG-C`), the simulation architecture prevents random stream desynchronization. If optional tasks were sampled during runtime execution, a configuration that skips optional tasks would consume fewer random numbers, causing subsequent request arrival times and service demands to diverge between configurations.

CloudRescue solves this by pre-generating all request attributes before simulation execution using **five dedicated, isolated pseudorandom number generator (PRNG) sub-streams** initialized from master seed $S$:
1. **Stream 1 (Arrivals):** Generates inter-arrival times $\Delta t_k$ for request $k$.
2. **Stream 2 (Mandatory Service Duration):** Generates $S_{\text{mand}, k} \sim \text{Exp}(\mu_{\text{mand}})$.
3. **Stream 3 (Optional Service Duration):** Generates $S_{\text{opt}, k} \sim \text{Exp}(\mu_{\text{opt}})$.
4. **Stream 4 (Optional Execution Draw):** Generates $U_{\text{opt}, k} \sim \text{Uniform}(0.0, 1.0)$.
5. **Stream 5 (Failure Injector):** Generates exact crash and recovery event timestamps.

Each request entity is instantiated as an immutable tuple:
$$\text{Request}_k = \left( k, t_{\text{arrive}, k}, S_{\text{mand}, k}, S_{\text{opt}, k}, U_{\text{opt}, k}, T_{\text{timeout}} \right)$$

### Instantaneous Optional Execution Decision
When Request $k$ completes its mandatory processing stage on worker $i$ at timestamp $t_{\text{mand\_end}}$, worker $i$ evaluates its **current, instantaneous dimmer** $\theta_i(t_{\text{mand\_end}})$:
- **Execute Optional (Stage 2):** If $U_{\text{opt}, k} \le \theta_i(t_{\text{mand\_end}})$. Worker executes for duration $S_{\text{opt}, k}$ and emits `OPTIONAL_EXECUTED(k, i, t, \theta_i)`.
- **Bypass Optional (Stage 2):** If $U_{\text{opt}, k} > \theta_i(t_{\text{mand\_end}})$. Worker finishes the request immediately and emits `OPTIONAL_BYPASSED(k, i, t, \theta_i)`.

Because $S_{\text{opt}, k}$ and $U_{\text{opt}, k}$ are pre-associated with Request $k$, bypassing optional execution draws zero random numbers from the generator. Thus, arrival streams and processing demands for all future requests remain 100% identical across all three configurations.

---

## 5. Standardized metric definitions & mathematical rules

All metrics are computed strictly from raw recorded simulation events outside the warm-up window ($T_{\text{warm}} = 100\text{ s}$). Every denominator and boundary condition is explicitly defined:

### 1. Request Success Rate ($S_r$)
*Definition:* Proportion of submitted requests successfully completed within the timeout deadline ($T_{\text{timeout}}$).
$$S_r = \frac{N_{\text{success}}}{N_{\text{submitted}}} \times 100\%$$
*Denominator:* $N_{\text{submitted}}$ (Total requests arriving outside the warm-up window).  
*Rule:* A request is counted in $N_{\text{success}}$ iff it completes execution and $L_k \le T_{\text{timeout}}$. Dropped requests (queue full), timed-out requests, and crashed requests are excluded.

### 2. Latency SLA Violation Rate ($V_{\text{lat}}$) — Successful Requests
*Definition:* Proportion of successfully completed requests whose response latency exceeded the SLA threshold ($r_{\text{SLA}} = 100\text{ ms}$).
$$V_{\text{lat}} = \begin{cases} \frac{\sum_{i \in \mathcal{S}_{\text{success}}} \mathbb{I}(L_i > r_{\text{SLA}})}{N_{\text{success}}} \times 100\% & \text{if } N_{\text{success}} > 0 \\ 0\% & \text{if } N_{\text{success}} = 0 \end{cases}$$
*Denominator:* $N_{\text{success}}$ (Evaluated strictly over successful requests to isolate latency performance).

### 3. Overall SLA Failure Rate ($V_{\text{overall}}$) — All Submitted Requests
*Definition:* Proportion of all submitted requests that failed to satisfy the service SLA (either due to rejection, timeout, crash, or excessive latency).
$$N_{\text{SLA\_failure}} = N_{\text{drop\_queue}} + N_{\text{drop\_timeout}} + N_{\text{failed\_crash}} + \sum_{i \in \mathcal{S}_{\text{success}}} \mathbb{I}(L_i > r_{\text{SLA}})$$
$$V_{\text{overall}} = \frac{N_{\text{SLA\_failure}}}{N_{\text{submitted}}} \times 100\%$$
*Denominator:* $N_{\text{submitted}}$ (Provides a holistic availability and performance reliability measure from the end-user perspective).

### 4. Mean Response Latency ($\bar{L}$)
*Definition:* Arithmetic mean of end-to-end response times for successfully completed requests.
$$\bar{L} = \frac{1}{N_{\text{success}}} \sum_{i \in \mathcal{S}_{\text{success}}} L_i \quad (\text{ms}, \text{ defined for } N_{\text{success}} > 0)$$
*Rule:* $L_i = t_{\text{completed}, i} - t_{\text{arrive}, i}$ (includes both queue wait time and active CPU execution time).

### 5. 95th-Percentile Response Latency ($L_{95}$)
*Definition:* The 95th percentile of the response latency distribution for successful requests.
$$L_{95} = \text{Percentile}_{95}(\{L_i \mid i \in \mathcal{S}_{\text{success}}\}) \quad (\text{ms})$$
*Rule:* Computed using linear rank interpolation over all successful requests completed outside the warm-up window.

### 6. Service Fidelity ($F$) — Strict Subset Formulation
*Definition:* Proportion of successfully completed requests that also executed optional computation (Stage 2).
$$F = \begin{cases} \frac{N_{\text{success, opt}}}{N_{\text{success}}} \times 100\% & \text{if } N_{\text{success}} > 0 \\ 0\% & \text{if } N_{\text{success}} = 0 \end{cases}$$
*Numerator ($N_{\text{success, opt}}$):* Count of successfully completed requests ($L_k \le T_{\text{timeout}}$) whose optional task was executed ($U_{\text{opt}, k} \le \theta$).  
*Denominator ($N_{\text{success}}$):* Total count of successfully completed requests.  
*Subset Guarantee:* By definition, $\mathcal{S}_{\text{success, opt}} \subseteq \mathcal{S}_{\text{success}}$, ensuring $0 \le N_{\text{success, opt}} \le N_{\text{success}}$ strictly. If a request executes optional logic but subsequently drops or times out, it is excluded from both numerator and denominator. When $N_{\text{success}} = 0$, $F = 0\%$.

### 7. Mean Dimmer Value ($\bar{\theta}$)
*Definition:* Time-weighted average of dimmer variables across all operational worker instances.
$$\bar{\theta} = \frac{1}{\sum_{m=1}^{M} T_{\text{operational}, m}} \sum_{m=1}^{M} \int_{T_{\text{warm}}}^{T_{\text{sim}}} \theta_m(t) \cdot \mathbb{I}(\text{worker } m \text{ is operational at } t) \, dt$$
*Rule:* Excludes offline/crashed periods for individual workers to measure actual operational dimmer levels.

### 8. Failure Recovery Times ($T_{\text{adapt}}$ and $T_{\text{restore}}$)
CloudRescue explicitly distinguishes recovery during active stress from recovery following repair:
- **Rolling Latency Evaluation Window:**
  At any timestamp $t$, rolling 95th-percentile latency $\hat{r}_{95}(t)$ is computed over requests completing within $[t - W_{\text{rec}}, t]$ where $W_{\text{rec}} = 10.0\text{ s}$.
  *Minimum Sample Count:* Requires at least $N_{\text{rec\_min}} = 20$ completed requests in the window. If $n < 20$, $\hat{r}_{95}(t)$ is considered **indeterminate** and cannot satisfy recovery.
- **Adaptation Recovery Time ($T_{\text{adapt}}$):**
  Elapsed time from shock onset ($t_{\text{shock\_start}}$) until the rolling 95th-percentile latency drops back below $r_{\text{SLA}}$ ($100\text{ ms}$) *while the stress remains active*.
  $$T_{\text{adapt}} = t_{\text{adapted}} - t_{\text{shock\_start}}$$
  *Rule:* $t_{\text{adapted}}$ is the earliest timestamp where rolling $\hat{r}_{95}(t) \le r_{\text{SLA}}$ continuously for a stability duration of $t_{\text{stable}} = 3.0\text{ s}$ ($3 \times \Delta t_{\text{ctrl}}$), with each sub-window satisfying $N_{\text{rec\_min}} \ge 20$.
- **Post-Restoration Recovery Time ($T_{\text{restore}}$):**
  Elapsed time from failure repair ($t_{\text{repair}}$) until the system returns to nominal steady-state operation.
  $$T_{\text{restore}} = t_{\text{restored}} - t_{\text{repair}}$$
  *Rule (per DEC-010):* $t_{\text{restored}}$ is the earliest timestamp where each restored worker's dimmer achieves at least 95% of its configuration-, seed-, and worker-specific nominal steady-state reference ($\theta_w(t) \ge 0.95 \cdot \theta_{\text{nom}}^*(w)$) AND rolling cluster 95th-percentile response latency satisfies $\hat{r}_{95}(t) \le r_{\text{target}}$ ($80\text{ ms}$) continuously for $t_{\text{stable}} = 3.0\text{ s}$.
- **Right-Censoring Rule for Unrecovered Runs:**
  If recovery is not achieved before another stress begins or simulation ends at $T_{\text{sim}}$, the run is marked as **right-censored** at $T_{\text{censor}} = t_{\text{cutoff}} - t_{\text{event\_start}}$ with `recovered = False`. Unrecovered runs are evaluated using median survival times and non-parametric Kaplan-Meier survival curves rather than distorting arithmetic means with arbitrary penalty constants.

### 9. Server Utilization ($U_i$ and Aggregate $\bar{U}$)
*Definition:* Proportion of operational time server $i$ spends actively executing CPU tasks.
$$U_i = \begin{cases} \frac{T_{\text{busy}, i}}{T_{\text{operational}, i}} \times 100\% & \text{if } T_{\text{operational}, i} > 0 \\ 0\% & \text{if } T_{\text{operational}, i} = 0 \end{cases}$$
$$\bar{U} = \frac{\sum_{i=1}^{M} T_{\text{busy}, i}}{\sum_{i=1}^{M} T_{\text{operational}, i}} \times 100\%$$
*Rule:* Normalizing by $T_{\text{operational}, i}$ ensures that hardware crash downtime does not distort busy-time utilization measurements.

### 10. Load Distribution Fairness Index ($J$)
*Definition:* Jain's Fairness Index measuring the equality of request distribution across active workers.
$$J = \frac{\left(\sum_{i \in \mathcal{M}_{\text{active}}} N_i\right)^2}{|\mathcal{M}_{\text{active}}| \sum_{i \in \mathcal{M}_{\text{active}}} N_i^2}$$
*Rule:* Evaluated over the set of workers $\mathcal{M}_{\text{active}}$ that were operational during the evaluation window, preventing hardware outages from artificially degrading the load balancer's fairness score.

---

## 6. Brownout feedback controller formulation

Each worker instance $i$ executes an independent discrete Proportional-Integral (PI) feedback controller (velocity form) updated every $\Delta t_{\text{ctrl}} = 1.0\text{ s}$:

### 6.1 Sample Verification & Insufficient Data Handling
In window $[t - \Delta t_{\text{ctrl}}, t]$, worker $i$ counts completed requests $n_i(t)$ and computes the 95th-percentile latency $\hat{r}_{95, i}(t)$.
- **Insufficient Sample Rule:** If completed sample count $n_i(t) < N_{\text{min\_ctrl}}$ (default 5 requests):
  1. The PI computation is **skipped entirely**.
  2. Dimmer is held constant: $\theta_i(t) = \theta_i(t - \Delta t_{\text{ctrl}})$.
  3. The error state is marked as invalid.
  4. **State Resumption:** When valid measurements resume at a later tick $t_{\text{resume}}$ ($n_i \ge N_{\text{min\_ctrl}}$), the previous error is re-initialized: $e_{i,\text{prev}} \leftarrow e_i(t_{\text{resume}})$. The derivative term $K_p (e_i - e_{i,\text{prev}})$ evaluates to zero on the first resumption step, preventing an artificial derivative kick.
- **Stalled Queue Exception:** If $n_i(t) < N_{\text{min\_ctrl}}$ but queue depth $q_i(t) > 0$ and the head-of-line request waiting time exceeds $r_{\text{target}}$, the controller detects queue freeze and applies a safety decrement: $\theta_i(t) = \max(\theta_{\text{min}}, \theta_i(t - \Delta t_{\text{ctrl}}) - \delta_{\text{stall}})$, re-initializing $e_{i,\text{prev}}$ upon resumption.

### 6.2 Error Calculation & Sign Convention
$$e_i(t) = r_{\text{target}} - \hat{r}_{95, i}(t)$$
- When latency exceeds target ($\hat{r}_{95, i}(t) > r_{\text{target}}$): $e_i(t) < 0$ (overloaded).
- When latency is under control ($\hat{r}_{95, i}(t) \le r_{\text{target}}$): $e_i(t) \ge 0$ (nominal headroom).

### 6.3 Discrete PI Update (Velocity Form)
$$\Delta \theta_i(t) = K_p \left( e_i(t) - e_i(t - \Delta t_{\text{ctrl}}) \right) + K_i \cdot e_i(t) \cdot \Delta t_{\text{ctrl}}$$
$$\theta_{\text{cand}, i}(t) = \theta_i(t - \Delta t_{\text{ctrl}}) + \Delta \theta_i(t)$$
*(Because $e_i(t) < 0$ during overload, $\Delta \theta_i(t) < 0$, which smoothly drives down the dimmer.)*

### 6.4 Intrinsic Anti-Windup Clamping
$$\theta_i(t) = \begin{cases} \theta_{\text{min}} & \text{if } \theta_{\text{cand}, i}(t) < \theta_{\text{min}} \\ \theta_{\text{max}} & \text{if } \theta_{\text{cand}, i}(t) > \theta_{\text{max}} \\ \theta_{\text{cand}, i}(t) & \text{otherwise} \end{cases}$$
Where $[\theta_{\text{min}}, \theta_{\text{max}}] = [0.0, 1.0]$.
*Intrinsic Anti-Windup Mechanism:* Because subsequent updates compute $\theta_{\text{cand}, i}(t + \Delta t_{\text{ctrl}})$ from the **clamped value** $\theta_i(t)$ rather than an unbounded unconstrained accumulator, no hidden integral accumulation exists beyond $[0.0, 1.0]$. The instant the error reverses sign ($e_i(t) > 0$), $\theta_i(t)$ immediately begins recovering upward without unwinding delay.

### 6.5 Feature Restoration
When traffic stress subsides and $\hat{r}_{95, i}(t) < r_{\text{target}}$, $e_i(t) > 0$. The positive error drives $\theta_i(t)$ upward until it reaches $\theta_{\text{max}} = 1.0$, restoring full optional features smoothly.

---

## 7. Load balancer formulation & anti-overload rules

### 7.1 Conventional Baseline Balancer (`CFG-A` and `CFG-B`)
Standardized on **Join-Shortest-Queue (JSQ)**:
- Routes incoming requests to the operational worker with the smallest current queue length $q_i(t)$. Excludes crashed workers.

### 7.2 Brownout-Aware Load Balancer (`CFG-C`)
The Brownout-Aware Load Balancer uses a composite multi-attribute score:
$$Score_i(t) = \alpha \cdot \theta_i(t) - \beta \cdot \left(\frac{q_i(t)}{Q_{\text{max}}}\right) - \gamma \cdot U_i(t)$$
*Note on Provenance:* This scoring function is a **CloudRescue design** that synthesizes the principles of Klein et al. [61] (SRDS 2014) rather than a literal clone of their Rubis benchmark heuristic.

### 7.3 Roles of Queue Depth vs. CPU Utilization in Scoring
While queue depth ($q_i$) and CPU utilization ($U_i$) are correlated in steady-state M/M/1 systems, they provide **orthogonal physical information during transient shocks**:
1. **Queue Depth ($q_i$) — Forward-Looking Backlog Indicator:**
   Directly reflects buffered requests waiting for service. A worker can have $U_i = 100\%$ with $q_i = 0$ (actively servicing one request with zero queue delay), or $U_i = 100\%$ with $q_i = 45$ (dangerously close to queue dropouts). The normalized queue penalty $-\beta \left(\frac{q_i(t)}{Q_{\text{max}}}\right)$ directly mitigates queue drop risk and queuing latency.
2. **CPU Utilization ($U_i$) — Cumulative Operational Capacity Indicator:**
   Reflects cumulative mean operational utilization up to arrival timestamp $t$: $U_i(t) = \frac{T_{\text{busy}, i}(t)}{T_{\text{operational}, i}(t)} \in [0.0, 1.0]$. A worker with $q_i = 0$ may have high $U_i = 0.95$ because past requests had substantial execution times; dispatching another request to it immediately could overwhelm its processor. Conversely, a worker with $q_i = 1$ and $U_i = 0.20$ has substantial compute headroom.
3. **Decoupling Under Graceful Degradation:**
   Under brownout, when $\theta_i$ drops, requests take shorter service times ($S_{\text{mand}}$ only). Consequently, a worker can rapidly clear its queue with low CPU utilization even if arrival rates are steady, whereas a worker maintaining $\theta_i = 1.0$ will experience high CPU utilization with modest queue depths.
4. **Empirical Weight Calibration:**
   The weights $\alpha, \beta, \gamma$ are **not assumed optimal**. The default values ($\alpha = 1.0, \beta = 1.0, \gamma = 0.5$) are provisional. A multi-parameter sensitivity grid sweep across $\alpha \in [0.5, 2.0]$, $\beta \in [0.5, 2.0]$, and $\gamma \in [0.0, 1.0]$ will be conducted during experimental execution to calibrate optimal trade-offs.

### 7.4 Anti-Overloading & Fallback Mechanisms
1. **Preventing High-Fidelity Saturation:** As $q_i$ grows, the queue penalty drops $Score_i$ rapidly below that of slightly degraded workers with empty queues, ensuring traffic sheds dynamically before queue saturation occurs.
2. **Soft Overload Fallback:** If all operational workers have queue depths $q_i(t) \ge Q_{\text{soft}}$ ($80\%$ of $Q_{\text{max}}$), the balancer disables dimmer weighting ($\alpha = 0$), transitioning to the fallback score:
   $$Score_i^{\text{fallback}}(t) = -\beta \cdot \left(\frac{q_i(t)}{Q_{\text{max}}}\right) - \gamma \cdot U_i(t)$$
   This eliminates optional-computation incentives while preserving queue backlog and CPU capacity penalties to minimize immediate drop risk.
3. **Hard Saturation:** If all operational workers reach $Q_{\text{max}}$, the request cannot be admitted and is dropped (`DROP_QUEUE_FULL`).

---

## 8. Run protocol & statistical methodology

### 8.1 Paired Run Protocol
- Each of the 4 stress conditions is executed across $N = 30$ independent runs using pre-registered master seeds ($S_1, \dots, S_{30}$).
- For each seed $S_j$, the exact same pre-generated request stream is fed sequentially to:
  1. `CFG-A` (Baseline: $\theta = 1.0$, JSQ)
  2. `CFG-B` (Brownout Only: $\theta_i(t)$, JSQ)
  3. `CFG-C` (Full CloudRescue: $\theta_i(t)$, BALB)
- Total runs: $3 \times 4 \times 30 = \mathbf{360\text{ simulation executions}}$.

### 8.2 Statistical Testing
1. **Paired Differences:** Compute trial differences $\Delta_{j, B-A} = M_{j, B} - M_{j, A}$ and $\Delta_{j, C-B} = M_{j, C} - M_{j, B}$.
2. **Normality Check:** Apply the **Shapiro-Wilk test** ($\alpha = 0.05$) to paired differences.
3. **Hypothesis Testing:**
   - If normal: **Two-tailed Paired Student's t-test**.
   - If non-normal: **Non-parametric Wilcoxon Signed-Rank Test**.
   - Significance threshold: $\alpha = 0.05$.
4. **Effect Sizes:** Report Cohen's $d_z$ (parametric) or Rank-Biserial Correlation (non-parametric).
5. **Confidence Intervals:** 95% CIs reported for mean differences.
6. **Sensitivity Sweeps:** Systematic grid sweep over setpoint $r_{\text{target}} \in [50, 100]\text{ ms}$, $K_p \in [0.1, 1.0]$, $K_i \in [0.01, 0.5]\text{ s}^{-1}$, and load balancer weights $\alpha, \beta, \gamma$.

---

## 9. Threats to validity & integrity

- **Model Validity:** Dual-stage execution abstracts web applications into mandatory vs. optional branches. While grounded in Klein et al. [60, 61], real applications may have multi-stage dependency chains.
- **Construct Validity:** Response time percentiles, SLA violations, and fidelity provide comprehensive QoS measurement, but user satisfaction from degraded content cannot be directly measured in simulation.
- **Internal Validity:** Isolated random sub-streams, matched seeds, and deterministic queueing eliminate stochastic drift.
- **Integrity Rule:** No experimental findings or percentages are reported prior to execution. All reported numbers in results will derive strictly from preserved simulation runs.
