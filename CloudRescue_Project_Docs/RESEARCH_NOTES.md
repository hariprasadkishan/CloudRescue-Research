# CloudRescue — Research Paper Review Notes

## 1. Assigned paper

- **Title:** On Resilience in Cloud Computing: A Survey of Techniques across the Cloud Domain  
- **Authors:** Thomas Welsh (University of Limerick, Republic of Ireland) and Elhadj Benkhelifa (Staffordshire University, UK)  
- **Venue:** ACM Computing Surveys (CSUR), Vol. 53, No. 3, Article 59 (May 2020), 36 pages  
- **DOI:** [10.1145/3388922](https://doi.org/10.1145/3388922)  
- **Local PDF:** `research/assigned-paper.pdf` (verified present, 36 pages, SHA-256 verified)

---

## 2. Review status

- **PDF obtained:** Yes (`research/assigned-paper.pdf`)
- **Full paper reviewed:** Yes (all 36 pages examined, including 133 references)
- **Relevant sections identified:** 
  - Section 1: Scope & Resilinets Model (pp. 59:1–6)
  - Section 2.3: Cloud Management & Brownout (pp. 59:13–16, Tables 5 & 6)
  - Section 2.6: Evaluation and Models (pp. 59:22–24)
  - Section 3.1: Techniques, Discussion & Limitations (pp. 59:24–27, Table 9)
  - Section 3.2: Actor Influence (pp. 59:27–28, Table 10)
  - Section 4: Conclusion (p. 59:30)
- **Candidate techniques extracted:** 
  1. Brownout self-adaptive graceful degradation (Klein et al. [60, 61], p. 59:15)
  2. Resilient VM task scheduling and allocation (Cartlidge & Sriram [25], pp. 59:13–14)
  3. Component quality ranking service orchestration (FTCloud, Zheng et al. [132], p. 59:16)
- **Selected technique:** **Brownout-based self-adaptive graceful degradation with brownout-aware load balancing**
- **Selection approved by team:** Yes (official team decisions DEC-005, DEC-006, DEC-007, DEC-008, DEC-009)

---

## 3. Evidence extraction

| Topic | Paper's terminology / finding | Page or section | Notes & Citations |
|---|---|---|---|
| **Definition of resilience** | Multiple perspectives synthesized: Laprie [62] ("persistence of dependability / service delivery when facing changes"); Sterbenz et al. [112] ("provide and maintain an acceptable level of service in the face of various faults and challenges"); Queiroz et al. [95] ("capacity of critical services to adapt"); Abdullah et al. [1] ("capacity to survive and thrive... avoid, contain and mitigate"); Liu & Ji [67] ("percentage of lost traffic upon failures"). | Section 1, pp. 59:1–2 | Foundational conceptual scope for CloudRescue. |
| **Resilience classification framework** | **Resilinets model** (Sterbenz et al. [112]). Divides resilience into **Trustworthiness** (internal: Reliability, Availability, Confidentiality, Integrity, Maintainability, Safety) and **Challenge Tolerance** (external: Fault Tolerance, Survivability, Disruption Tolerance, Traffic Tolerance, Graceful Degradation). Governed by the **$D^2R^2 + DR$ cycle** (Defend, Detect, Remediate, Recover + Diagnose, Refine). | Section 1, p. 59:2; Section 1.2, p. 59:5 | Used as our theoretical evaluation framework. |
| **Cloud failure types** | Physical data-centre failures (power, fiber cuts, disaster); storage medium failures; instance crashes and memory subversions; virtual network link saturation/delays; and runtime traffic surges / flash crowds. | Section 2.1–2.5, pp. 59:6–22 | Informs failure scenario design for discrete-event simulation. |
| **Critique of redundancy** | Survey repeatedly highlights that centralised cloud resilience excessively relies on costly hardware/data replication ("seemingly unlimited resources... but costly and resource-intensive"). Highlights need for autonomic adaptive mechanisms that function under constrained resources. | Section 3.1, p. 59:24; Section 4, p. 59:30 | Core motivation for choosing Brownout over brute-force replication. |
| **Selected technique: Brownout** | *"Klein et al. discuss the brownout programming paradigm [60], proposed to provide enhanced robustness within cloud services. It attempts to mitigate the requirement to provision large amounts of replicated instances during traffic increase... A brownout program will downgrade a user experience, such as with enhanced features, to prevent excessive use of the system. They extend this by combining with load balancing, as the combination currently creates conflict [61]. They propose two novel algorithms and a production-ready load balancer. Their results indicate strong performance compared to alternative solutions."* | Section 2.3, p. 59:15, lines 742–749; Table 5, p. 59:13; Table 9, p. 59:25 | Primary literature ground. Citations: C. Klein et al. (ICSE 2014) [60] and (IEEE SRDS 2014) [61]. |
| **Brownout mechanism & workflow** | Dynamic control variable (dimmer $\theta \in [0, 1]$). Mandatory logic executes for 100% of admitted requests; optional logic is evaluated immediately before optional execution using the worker's instantaneous $\theta$. A velocity-form discrete PI controller adjusts $\theta$ based on response latency setpoint error. A brownout-aware load balancer routes requests to balance fidelity and queueing delay. | Section 2.3, p. 59:15; cited in Klein et al. [60, 61] | Adapted into CloudRescue discrete-event queueing model. |
| **Assumptions and limitations** | Table 5 (p. 59:13) and Table 9 (p. 59:25) list limitations: *"Single replica only, experience reduction"* for initial brownout; requires modular application architecture (mandatory vs. optional components); controller-balancer coupling must be carefully managed to avoid ping-pong oscillations and high-fidelity worker overload. | Table 5, p. 59:13; Table 9, p. 59:25; Section 3.1, p. 59:25 | These limitations are addressed in CloudRescue's composite scoring function, anti-overload penalty, and 3-way ablation design. |
| **Resilience metrics taxonomy** | Categorizes metrics into: (1) Binary feature-based, (2) State-based degradation metrics (Jabbar [52]), (3) Performance-oriented metrics (MTBF, MTTR, availability, QoS, provisioning delay, Ghosh et al. [42]), (4) Graph metrics (Alenazi & Sterbenz [6, 7]), and (5) Multi-criteria metrics (Sousa et al. [109]). | Section 2.6, pp. 59:22–24 | Forms the basis of CloudRescue's quantitative metric definitions. |

---

## 4. Technique selection

### Candidate assessment

1. **Brownout-based self-adaptive graceful degradation (Klein et al. [60, 61]):**
   - *Survey description:* Explicitly evaluated in Section 2.3 (p. 59:15), Table 5 (p. 59:13), and Table 9 (p. 59:25).
   - *Simulation feasibility:* Very high. Discrete-event queueing models (SimPy) naturally capture request arrivals, mandatory/optional service durations, queue delays, and discrete control updates.
   - *Baseline comparability:* Clean, controlled baseline (Join-Shortest-Queue without brownout, $\theta = 1.0$) versus treatment ($\theta_i(t)$ dynamic), with matched random seeds.
   - *Measurable outcomes:* Request success rate, latency SLA violations, overall SLA failures, 95th-percentile latency, service fidelity, dimmer adaptation, adaptation recovery time, post-restoration recovery time, utilization, load fairness.
   - *Score:* **Recommended candidate (Selected).**

2. **Resilience-driven task scheduling and VM allocation (Cartlidge & Sriram [25]):**
   - *Survey description:* Evaluated in Section 2.3 (pp. 59:13–14), Table 5 (p. 59:13).
   - *Simulation feasibility:* High. Host capacity matrices and Poisson crash schedules.
   - *Limitation:* Focuses on VM placement (IaaS); lacks dynamic runtime feedback behavior and end-to-end request latency dynamics.

3. **Component quality ranking and fault-tolerant orchestration (FTCloud, Zheng et al. [132]):**
   - *Survey description:* Evaluated in Section 2.3 (p. 59:16), Table 6 (p. 59:14).
   - *Simulation feasibility:* Moderate. Requires complex DAG workflow engine and graph ranking algorithms.
   - *Limitation:* High implementation complexity; assumes static workflow dependencies.

### Final selection
- **Selected technique:** **Brownout-based self-adaptive graceful degradation with brownout-aware load balancing**
- **Implementation scope:**
  1. Brownout feedback controller (velocity-form discrete PI control, dimmer $\theta_i \in [0, 1]$, intrinsic output clamping anti-windup, skip-and-hold on insufficient samples, derivative reset on resumption, feature restoration).
  2. Brownout-aware load balancer (composite scoring over queue length, utilization, and dimmer state; anti-overloading queue penalty; crash exclusion; soft-overload fallback with dimmer incentive disabled on cluster-wide overload).
- **Approved by team:** Yes (DEC-005, DEC-006, DEC-007, DEC-008, DEC-009).

---

## 5. Mapping paper concepts to CloudRescue simulation components

| Survey / Literature Concept | Klein et al. [60, 61] Finding | Planned CloudRescue Simulator Component | Implementation Status |
|---|---|---|---|
| Autonomic Management & Feedback Control (Section 2.3, p. 59:15) | PI feedback controller monitoring response time error $e(t) = r_{\text{target}} - \hat{r}(t)$ and adjusting dimmer $\theta$. | `simulator.cloudrescue.resilience.controller.BrownoutController` (velocity form, intrinsic anti-windup) | Architectural design complete; code implementation pending approval |
| Graceful Degradation / Experience Downgrade (Table 5, p. 59:13) | Applications modularized into mandatory code (always executed) and optional code (evaluated immediately before execution against current $\theta$). | `simulator.cloudrescue.cloud_model.server.ServerInstance` (dual-stage service model) | Architectural design complete; code implementation pending approval |
| Brownout-Aware Load Balancing (Section 2.3, p. 59:15; [61]) | Load balancer routing requests to servers with higher $\theta$ and shorter queues to prevent controller fighting. | `simulator.cloudrescue.resilience.load_balancer.BrownoutAwareLoadBalancer` (CloudRescue composite scoring function) | Architectural design complete; code implementation pending approval |
| Traffic Flash Crowds & Congestion (Section 2.3, p. 59:15; TT discipline) | Sudden burst of web requests saturating server processing capacity and causing timeouts. | `simulator.cloudrescue.workload.generator.WorkloadGenerator` (Poisson & Pareto burst) | Architectural design complete; code implementation pending approval |
| Cloud Worker Failure & Capacity Loss (Section 2.1–2.3; FT discipline) | Physical server dropouts reducing available cluster execution capacity. | `simulator.cloudrescue.failures.injector.FailureInjector` (crash-stop & recovery schedule) | Architectural design complete; code implementation pending approval |
| Standardized Baseline Load Balancer (DEC-008) | Isolating brownout control under standard Join-Shortest-Queue (JSQ) before evaluating brownout-aware routing. | `simulator.cloudrescue.resilience.load_balancer.JoinShortestQueueLoadBalancer` | Architectural design complete; code implementation pending approval |
| Multi-Stream Reproducibility Architecture (DEC-008) | Ensuring identical arrival sequences, service demands, and failure events across configurations. | `simulator.cloudrescue.workload.request.Request` pre-generation with 5 isolated PRNG streams | Architectural design complete; code implementation pending approval |
| Three-way Comparative Evaluation (Ablation, DEC-007) | Comparing baseline vs. brownout-only vs. full CloudRescue. | `simulator.cloudrescue.runner.ExperimentRunner` (executes CFG-A, CFG-B, CFG-C) | Architectural design complete; code implementation pending approval |
| Performance & QoS Metrics (Section 2.6, pp. 59:22–24) | Separating latency violations from overall SLA failures; strict subset service fidelity; recovery time. | `simulator.cloudrescue.metrics.calculator.MetricsCalculator` | Formally specified; formulas documented |

---

## 6. Research claims to verify & integrity constraints

1. **Authors' Survey vs. Original Cited Papers vs. CloudRescue Implementation:**
   - *Survey (Welsh & Benkhelifa, 2020):* Synthesizes and classifies Klein et al. [60, 61] under Cloud Management, highlighting its role in avoiding costly replication while identifying "experience reduction" and multi-node coupling as trade-offs.
   - *Original Papers (Klein et al. [60, 61]):* [60] introduces the brownout programming model in lighttpd and Rubis using a discrete PI controller. [61] introduces brownout-aware load balancing heuristics.
   - *CloudRescue Proposed Implementation:* Implements a discrete-event simulation model in Python (SimPy). The composite scoring function used by CloudRescue ($Score_i = \alpha \theta_i - \beta \frac{q_i}{Q_{\text{max}}} - \gamma U_i$) is a **CloudRescue design** that synthesizes the principles of Klein et al. [61] rather than a literal clone of their specific testbed heuristic.
2. **Provisional Hypotheses:**
   - Numerical performance targets in $H_1$ are pre-registered hypotheses, never claimed as observed facts until experiments are executed and recorded.
3. **No Fabricated Evidence:**
   - No mock data or pre-declared victory claims are permitted in results or documentation.

---

## 7. Phase 4 Empirical Validation Findings & Verified Limitations

The Phase 4 simulation experiment evaluated 360 primary simulation runs ($3\text{ configurations} \times 4\text{ scenarios} \times 30\text{ seeds}$) and 144 exploratory sensitivity runs. All findings were independently validated and audited in [`results/experiment_360/FINAL_RESEARCH_VALIDATION.md`](file:///home/andesindica/Downloads/CloudRescue-Research/results/experiment_360/FINAL_RESEARCH_VALIDATION.md).

### 7.1 Verified Hypothesis Outcomes

| Hypothesis | Evaluated Metric | Experimental Evidence (CFG-C vs Baselines) | Statistical Result | Status |
|---|---|---|---|:---:|
| **$H_{1,1}$ (SLA Compliance)** | Overall SLA Failure ($V_{\text{overall}}$), Latency Violations ($V_{\text{lat}}$), 95th-Percentile Latency ($L_{95}$) | - Flash Crowd: $V_{\text{overall}}$ reduced from $44.04\%$ to $2.94\%$ ($-41.10\%$).<br>- Server Crash: $V_{\text{overall}}$ reduced from $33.38\%$ to $6.33\%$ ($-27.05\%$).<br>- Compound: $V_{\text{overall}}$ reduced from $47.70\%$ to $35.33\%$ ($-12.37\%$).<br>- $L_{95}$ latency reduced by up to $101.47\text{ ms}$. | $p < 10^{-45}$ across all stress scenarios.<br>Bonferroni $p < 10^{-43}$, FDR $q < 10^{-45}$. Large effect sizes ($d_z = -33.25$ to $-121.71$). | **SUPPORTED** |
| **$H_{1,2}$ (Recovery Acceleration)** | Adaptation Recovery ($T_{\text{adapt}}$), Post-Restoration Recovery ($T_{\text{restore}}$) | - Flash Crowd: $T_{\text{adapt}}$ reduced from $150.0\text{ s}$ to $2.5\text{ s}$ ($22.7\times$ faster).<br>- Server Crash: $T_{\text{adapt}}$ reduced from $150.0\text{ s}$ to $2.0\text{ s}$ ($28.4\times$ faster).<br>- Server Crash $T_{\text{restore}}$ (30 seeds): Median accelerated from $286.5\text{ s}$ to $133.5\text{ s}$ ($2.15\times$ speedup, $96.7\%$ vs $83.3\%$).<br>- Compound $T_{\text{restore}}$ (30 seeds): Median accelerated from $291.0\text{ s}$ to $141.5\text{ s}$ ($2.06\times$ speedup, $96.7\%$ vs $86.7\%$). | - $T_{\text{adapt}}$: $p < 10^{-23}$, Rank-biserial $r = -1.00$.<br>- $T_{\text{restore}}$ Server Crash: Wilcoxon $p = 2.37 \times 10^{-5}$, Paired t $p = 2.03 \times 10^{-5}$, $d_z = -0.927$.<br>- $T_{\text{restore}}$ Compound: Wilcoxon $p = 4.07 \times 10^{-5}$, Paired t $p = 4.22 \times 10^{-6}$, $d_z = -1.031$. | **SUPPORTED** |
| **$H_{1,3}$ (BALB Incremental Impact)** | Load Distribution Fairness ($J$), Service Fidelity ($F$) | - **Fairness ($J$):** Decisively improved across all scenarios ($J \ge 0.997$ vs $0.654$–$0.766$ in CFG-B, $\Delta J = +0.23$ to $+0.34$).<br>- **Fidelity ($F$):** Consistently lower in CFG-C ($F = 9.5\% \text{ to } 13.8\%$ vs $20.9\% \text{ to } 29.7\%$ in CFG-B, $\Delta F = -11.4\% \text{ to } -15.9\%$). | - Fairness: $p < 10^{-8}$, $d_z = +18.50$ to $+43.96$.<br>- Fidelity: $p < 10^{-38}$, $d_z = -19.18$ to $-28.70$. | **PARTIALLY SUPPORTED**<br>(Fairness supported; Fidelity disproven) |

### 7.2 Key Scientific Insights

1. **The Fidelity-Fairness Architectural Trade-Off:**
   In $H_{1,3}$, Join-Shortest-Queue under brownout exhibits severe pathological skew ($J \approx 0.65$): degraded workers execute requests rapidly ($10\text{ ms}$), emptying queues quickly and attracting excessive traffic, while non-degraded workers ($40\text{ ms}$) build queues. BALB cures this pathology by routing traffic to degraded workers to prevent backlog build-up on healthy instances. This achieves near-perfect load parity ($J > 0.997$) and reduces latency SLA violations, but forces more workers to operate at degraded dimmers, intentionally sacrificing optional feature fidelity ($F$).
2. **Empirical Post-Restoration Recovery Across All 30 Seeds (DEC-010):**
   Evaluating post-restoration recovery against empirical nominal steady-state references ($\theta_{\text{nom}}^*$) across all 30 seeds proves that CFG-C restores healthy cluster operation **$2.06\times$ to $2.15\times$ faster** than CFG-B ($p < 4.1 \times 10^{-5}$), with a $96.7\%$ restoration rate ($29/30$ runs) versus $83.3\%$–$86.7\%$ for CFG-B.
3. **Statistical Effect Size Mechanics ($d_z = -121.71$):**
   The massive Cohen's $d_z$ effect sizes are a mathematical consequence of Common Random Numbers (CRN) variance reduction. Because arrival schedules and service demands are matched bit-for-bit across paired configurations, stochastic variance in paired differences is suppressed ($s_D = 0.3377\%$). When divided into a 41-percentage-point physical reduction in failure rate, $d_z$ naturally reaches $-121.71$ (pooled Cohen's $d = -187.23$).
4. **Sensitivity Robustness:**
   Default BALB weights ($\alpha=1.0, \beta=1.0, \gamma=0.5$) are confirmed to be highly robust across all 48 combinations in the 144-run exploratory grid sweep ($V_{\text{overall}} \in [34.53\%, 37.21\%]$, $S_r \in [86.37\%, 86.99\%]$, $J \ge 0.825$, with default $J = 0.999$).

### 7.3 Documented Limitations

1. **Synthetic Service Time Distributions:** Service durations are drawn from exponential distributions. Real-world services may exhibit heavy tails (Pareto/Weibull).
2. **Telemetry Pruning Scope:** Complete per-second controller telemetry (`controller_timeseries.csv`) and run metadata (`summary.json`) are preserved for 100% of all 360 runs. Granular discrete request event traces (`events.csv.gz`) are preserved on disk for reference seed `1001` only to manage storage constraints.
3. **Queueing Topology Scope:** The simulator evaluates an ingress load balancer dispatching to an $M=4$ worker pool. Multi-tier microservice chains with recursive brownout propagation remain an open avenue for future research.

---

## 8. Bibliography

- **Primary Source:**
  - Welsh, T., & Benkhelifa, E. (2020). *On Resilience in Cloud Computing: A Survey of Techniques across the Cloud Domain*. **ACM Computing Surveys**, 53(3), Article 59, pp. 1–36. DOI: [10.1145/3388922](https://doi.org/10.1145/3388922).
- **Primary Cited Works for Selected Technique:**
  - Klein, C., Papadopoulos, A. V., Manfredi, V., Epifani, I., Leva, A., & Arzen, K.-E. (2014). *Brownout: Building more robust cloud applications*. In **Proceedings of the 36th International Conference on Software Engineering (ICSE '14)**, pp. 700–711. DOI: [10.1145/2568225.2568227](https://doi.org/10.1145/2568225.2568227). [Paper ref [60]].
  - Klein, C., Maggio, M., Arzen, K.-E., & Hernandez-Rodriguez, F. (2014). *Improving cloud service resilience using brownout-aware load-balancing*. In **Proceedings of the IEEE 33rd International Symposium on Reliable Distributed Systems (SRDS '14)**, pp. 31–40. DOI: [10.1109/SRDS.2014.14](https://doi.org/10.1109/SRDS.2014.14). [Paper ref [61]].
- **Foundational Resilience Framework:**
  - Sterbenz, J. P. G., Hutchison, D., Çetinkaya, E. K., Jabbar, A., Rohrer, J. P., Schöller, M., & Smith, P. (2010). *Resilience and survivability in communication networks: Strategies, principles, and survey of disciplines*. **Computer Networks**, 54(8), pp. 1245–1265. DOI: [10.1016/j.comnet.2010.03.005](https://doi.org/10.1016/j.comnet.2010.03.005). [Paper ref [112]].

