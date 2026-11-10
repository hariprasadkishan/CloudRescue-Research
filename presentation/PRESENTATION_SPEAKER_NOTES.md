# CloudRescue Research Project Defense — Speaker Notes & Presentation Guide

**Project Title:** Autonomic Cloud Resilience Through Brownout-Based Graceful Degradation: A Simulation-Based Evaluation of Brownout-Aware Load Balancing (BALB)  
**Presentation Deck:** `presentation/CloudRescue_Final_Presentation.pptx` (15 Widescreen Slides)  
**Research Paper:** `paper/CloudRescue_Research_Paper_Final.pdf` (19 Pages, IEEE Transactions Format)  
**Institution:** Department of Computer Science and Engineering, Indian Institute of Information Technology Dharwad (IIIT Dharwad), Karnataka, India  
**Target Time:** 10 Minutes Total Presentation (~3.5 min / ~3.5 min / ~3.0 min) + 5 Minutes Committee Q&A  
**Date:** November 2026  

---

## 1. Team Allocation & Presentation Schedule

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        10-MINUTE DEFENSE TIMELINE & DIVISION OF LABOR                 │
├─────────────────────┬───────────────────────┬───────────────┬──────────────────────────┤
│ Presenter           │ Slides Assigned       │ Target Time   │ Key Thematic Focus       │
├─────────────────────┼───────────────────────┼───────────────┼──────────────────────────┤
│ Hari Prasad L       │ Slides 1 – 5          │ ~3.5 Minutes  │ Problem, Motivation,     │
│ (Lead Architect)    │ (Context & Solution)  │ (0:00 – 3:30) │ Research Gap & Solution  │
├─────────────────────┼───────────────────────┼───────────────┼──────────────────────────┤
│ Yeruva Mahesh Reddy │ Slides 6 – 10         │ ~3.5 Minutes  │ Topology, PI Controller, │
│ (Evaluation Lead)   │ (System & Experiment) │ (3:30 – 7:00) │ BALB Algorithm & Scenarios│
├─────────────────────┼───────────────────────┼───────────────┼──────────────────────────┤
│ K. Ram Charan       │ Slides 11 – 15        │ ~3.0 Minutes  │ Results, Trade-Offs,     │
│ (Simulation Lead)   │ (Results & Takeaways) │ (7:00 – 10:00)│ Limitations & Conclusion │
└─────────────────────┴───────────────────────┴───────────────┴──────────────────────────┘
```

---

## 2. Slide-by-Slide Detailed Script & Delivery Guide

### SLIDE 1: Title, Team, and Institutional Affiliation
- **Presenter:** Hari Prasad L
- **Target Duration:** 45 seconds (Elapsed: 0:00 – 0:45)
- **Core Message:** CloudRescue is an autonomic cloud resilience framework that pairs decentralized brownout control with a novel brownout-aware load balancer to protect SLAs under extreme overload.
- **Visuals on Screen:** Deep navy title slide with project badge, paper preprint target, team member roles, and IIIT Dharwad credentials.
- **Spoken Script:**
  > "Respected members of the examination committee, faculty advisors, and colleagues: Good morning. I am Hari Prasad, presenting alongside my co-authors Yeruva Mahesh Reddy and Ram Charan from the Department of Computer Science and Engineering at IIIT Dharwad.
  > 
  > Today, we present our research project: *'Autonomic Cloud Resilience Through Brownout-Based Graceful Degradation: A Simulation-Based Evaluation of Brownout-Aware Load Balancing'*.
  > 
  > In this research, we tackle a fundamental vulnerability in modern cloud computing: the failure of distributed microservices when subjected to sudden, non-linear demand and capacity shocks. We introduce CloudRescue, an autonomic architecture that combines local velocity-form PI brownout control with BALB, a novel elasticity-aware ingress load balancer. We evaluate this architecture across 360 certified discrete-event simulation runs with deterministic random stream isolation. Let us begin by examining the physical problem that motivated this work."
- **Presenter Cue:** Establish a confident, scholarly tone. Stand upright, face the committee, and transition smoothly to Slide 2.
- **Transition:** *"To understand why autonomic adaptation is necessary, let us look at the dynamics of cloud microservices under stress."*

---

### SLIDE 2: Problem Statement: The Cloud Resilience Challenge
- **Presenter:** Hari Prasad L
- **Target Duration:** 40 seconds (Elapsed: 0:45 – 1:25)
- **Core Message:** Cloud microservices experience non-linear queuing collapse under flash crowds and server crashes, causing cascading dropouts and severe SLA violations.
- **Visuals on Screen:** Three structured cards detailing Demand Shocks, Capacity Shocks, and Queuing Collapse, anchored by an alarming red bottom alert banner.
- **Spoken Script:**
  > "Modern cloud-native applications are governed by strict Service Level Agreements—typically requiring 95th-percentile response times below 100 milliseconds. However, they operate in stochastic, volatile environments disrupted by two primary shocks:
  > 
  > First, demand-side flash crowds, where arrival traffic doubles instantaneously—for example, during breaking news or flash sales. Second, capacity-side infrastructure crashes, such as hypervisor evictions or out-of-memory errors that abruptly cut active compute capacity in half.
  > 
  > When these shocks strike, basic queuing physics takes over. In multi-server systems, queuing delay escalates asymptotically as utilization approaches 100 percent. Finite buffers quickly saturate, Head-of-Line blocking occurs, and client connections breach the 200 ms timeout deadline. In an unmanaged system, overall SLA failure rates skyrocket to 44.04% under flash crowds and 47.70% under compound stress, turning expensive infrastructure into an engine of discarded computation."
- **Presenter Cue:** Point to the red bottom alert card to emphasize the catastrophic 47.70% failure rate of unmanaged baselines under compound stress.
- **Transition:** *"Providers know this happens. So why do standard industry defenses fail to stop it?"*

---

### SLIDE 3: Motivation: Why Existing Defenses Fail Under Stress
- **Presenter:** Hari Prasad L
- **Target Duration:** 45 seconds (Elapsed: 1:25 – 2:10)
- **Core Message:** Static over-provisioning is economically wasteful, while reactive auto-scaling is dangerously slow; software-level graceful degradation is the only mechanism that reacts in sub-second time.
- **Visuals on Screen:** Three comparative cards contrasting Static Over-Provisioning, Reactive Auto-Scaling (Kubernetes HPA), and Software Graceful Degradation.
- **Spoken Script:**
  > "Historically, cloud providers rely on two architectural strategies, both of which suffer fatal weaknesses under sudden shocks:
  > 
  > The first is static hardware over-provisioning—maintaining pools of idle, hot-standby instances. As Welsh and Benkhelifa documented in their 2020 IEEE survey, this is economically prohibitive and environmentally wasteful. Furthermore, it is sized for anticipated peaks and completely collapses when correlated shocks exceed that provisioned ceiling.
  > 
  > The second is reactive auto-scaling, such as Kubernetes Horizontal Pod Autoscaling. When CPU breaches 80%, the system spawns new pods. But as Cartlidge and Sriram proved in ACM TOMACS, dynamic scaling suffers from an unavoidable provisioning gap of 60 to 300 seconds—encompassing container pull, OS boot, and runtime initialization. During this multi-minute window, request buffers saturate within 5 to 10 seconds, causing widespread client timeouts long before new instances ever become healthy.
  > 
  > This reveals our core motivation: we need a software-level adaptation mechanism that responds in sub-second time within existing physical hardware. That mechanism is brownout-based graceful degradation."
- **Presenter Cue:** Highlight the "60 to 300 second provisioning gap" versus the "sub-second brownout reaction".
- **Transition:** *"However, simply adding brownout to worker nodes introduces a profound, previously unaddressed routing pathology."*

---

### SLIDE 4: Research Gap: The Unaddressed Routing Pathology
- **Presenter:** Hari Prasad L
- **Target Duration:** 45 seconds (Elapsed: 2:10 – 2:55)
- **Core Message:** Conventional Join-Shortest-Queue (JSQ) load balancers misinterpret degraded brownout workers as 'available' and flood them with traffic, inducing severe load skew and delaying recovery.
- **Visuals on Screen:** Left panel illustrating the 4-step pathological feedback loop; Right panel presenting empirical evidence ($J = 0.607$, 323s recovery delay).
- **Spoken Script:**
  > "In foundational literature by Klein et al. and Tomas & Tordsson, brownout was demonstrated on individual servers using a control variable called the dimmer ($\theta \in [0, 1]$), which dynamically modulates the probability of executing optional software features like recommendations.
  > 
  > But what happens when you deploy multiple brownout workers behind an industry-standard load balancer like Join-Shortest-Queue? A destructive feedback loop emerges:
  > 1. A worker experiences high latency, so its local controller drops its dimmer toward zero.
  > 2. The worker sheds optional tasks, cutting its service time from 40 ms down to 10 ms. Its queue drains four times faster than normal.
  > 3. An agnostic JSQ load balancer looks at queue depth, sees a nearly empty queue, and directs MORE arriving requests to the degraded worker!
  > 4. Meanwhile, healthy workers operating at full fidelity retain longer queues and are starved of incoming traffic.
  > 
  > The result is catastrophic load skew: Jain's Fairness Index collapses to 0.607, and repaired workers take over 300 seconds to recover. Prior literature treated local brownout and ingress routing as independent silos. This created our research gap: designing an ingress balancer co-engineered with brownout state."
- **Presenter Cue:** Emphasize the irony: JSQ rewards the degraded server for being degraded!
- **Transition:** *"To solve this pathology, we designed and implemented CloudRescue."*

---

### SLIDE 5: Proposed CloudRescue Solution
- **Presenter:** Hari Prasad L
- **Target Duration:** 35 seconds (Elapsed: 2:55 – 3:30)
- **Core Message:** CloudRescue bridges decentralized local PI controllers with centralized Brownout-Aware Load Balancing to achieve bounded latency and perfect workload equity.
- **Visuals on Screen:** Three architectural pillars: Velocity-Form PI Controller, Brownout-Aware Load Balancing (BALB), and Non-Destructive Graceful Degradation.
- **Spoken Script:**
  > "CloudRescue solves this routing pathology through a co-designed, two-tier autonomic architecture based on three key pillars:
  > 
  > First, a local velocity-form PI feedback controller on every worker instance, sampling empirical 95th-percentile response latency every 1.0 second and adjusting the dimmer to maintain latency at an 80 ms setpoint—safely below the 100 ms SLA.
  > 
  > Second, Brownout-Aware Load Balancing, or BALB, deployed at the cluster ingress reverse proxy. BALB computes a composite dispatch score that balances dimmer elasticity, normalized queue backlog, and historical CPU utilization, protected by anti-overload penalties.
  > 
  > Third, a non-destructive graceful degradation execution model where admitted requests always execute core business logic, while optional features are throttled dynamically to expand cluster throughput up to 400% without spawning new nodes.
  > 
  > I will now hand over to Yeruva Mahesh Reddy to detail the system design and algorithmic formulations."
- **Presenter Cue:** Turn toward Mahesh, nod, and step slightly aside as Mahesh steps up to the lectern.
- **Transition:** *"Mahesh will now present our system architecture and controller algorithms."*

---

### SLIDE 6: System Architecture & Dual-Stage Execution Pipeline
- **Presenter:** Yeruva Mahesh Reddy
- **Target Duration:** 45 seconds (Elapsed: 3:30 – 4:15)
- **Core Message:** CloudRescue decomposes requests into mandatory (10 ms) and optional (30 ms) stages, dynamically expanding cluster throughput from 100 to 400 req/s.
- **Visuals on Screen:** Left panel outlining the 4-worker topology, FIFO queues, and closed-loop telemetry; Right panel detailing service time distributions and capacity expansion.
- **Spoken Script:**
  > "Thank you, Hari. Let us examine the underlying system architecture and execution pipeline of CloudRescue.
  > 
  > As shown on the left, CloudRescue models a cluster of $M = 4$ independent worker instances behind an ingress proxy. Each worker manages an independent FIFO queue with a capacity of 50 requests and a 200 ms Head-of-Line connection timeout threshold. Every 1.0 second, worker controllers broadcast their telemetry vector—dimmer $\theta$, queue depth $q$, and CPU utilization $U$—back to the ingress balancer.
  > 
  > On the right is our dual-stage execution model. Each request consists of:
  > - Stage 1: Mandatory core service, exponentially distributed with mean 10 milliseconds. This represents essential business logic like checkout, payment authorization, or order storage.
  > - Stage 2: Optional enhancement service, exponentially distributed with mean 30 milliseconds. This represents auxiliary features like personalized recommendations or analytics.
  > 
  > Under nominal conditions with full fidelity ($\theta = 1.0$), expected service time is 40 ms, giving each worker a capacity of 25 req/s, or 100 req/s across the 4-node cluster. When brownout sheds optional features ($\theta = 0.0$), expected service time drops to 10 ms, instantly expanding cluster throughput to 400 req/s—a four-fold capacity expansion achieved entirely in software."
- **Presenter Cue:** Highlight the contrast between 100 req/s (full fidelity) and 400 req/s (degraded) on the right panel.
- **Transition:** *"Now let us look at the mathematical control law governing this degradation on individual workers."*

---

### SLIDE 7: Brownout Controller & Local PI Algorithm
- **Presenter:** Yeruva Mahesh Reddy
- **Target Duration:** 45 seconds (Elapsed: 4:15 – 5:00)
- **Core Message:** The local velocity-form PI controller features intrinsic anti-windup clamping and telemetry safeguards to provide smooth, stable dimmer adaptation.
- **Visuals on Screen:** Three math cards showing Error Formulation, Velocity-Form Recurrence, and Anti-Windup Clamping, plus a monospace code summary bar.
- **Spoken Script:**
  > "To dynamically modulate the dimmer $\theta_w(t)$, each worker executes a velocity-form discrete Proportional-Integral controller.
  > 
  > Looking at Card 1, the control error $e_w(t)$ is defined as the setpoint $r_{\text{target}} = 80\text{ ms}$ minus the empirical 95th-percentile response latency observed over completed requests. This sign convention means that when latency breaches 80 ms, the error is negative, driving the dimmer downward to shed optional tasks. When latency is safe, positive error drives the dimmer back up toward full fidelity.
  > 
  > Looking at Card 2, rather than accumulating error in a positional integrator, we formulate the controller in velocity form: $\Delta \theta$ is computed using error differences. Using tuned gains of $K_p = 0.001$ and $K_i = 0.0005$ with an epoch of 1.0 second, the velocity formulation eliminates cumulative integrator drift.
  > 
  > Most importantly, in Card 3, we implement intrinsic anti-windup clamping: the output is clamped directly between 0.0 and 1.0. Because the update is incremental, the controller never suffers from integrator windup during sustained saturation. Finally, if fewer than 5 requests complete in an epoch, the controller holds its state, preventing stochastic noise from causing false degradation during traffic lulls."
- **Presenter Cue:** Point to the bottom equation bar: $e = 80 - r_{95} \implies \Delta\theta \implies \text{clamp}[0, 1]$.
- **Transition:** *"With local controllers regulating individual nodes, how does the ingress proxy route traffic intelligently? That brings us to BALB."*

---

### SLIDE 8: Brownout-Aware Load Balancing (BALB)
- **Presenter:** Yeruva Mahesh Reddy
- **Target Duration:** 45 seconds (Elapsed: 5:00 – 5:45)
- **Core Message:** BALB uses a composite score combining dimmer elasticity, normalized backlog, and CPU utilization, augmented with anti-overload penalties to avoid buffer saturation.
- **Visuals on Screen:** Left panel with the BALB scoring formula and weight breakdown; Right panel explaining the soft-overload threshold ($Q_{\text{soft}} = 40$) and fallback heuristic.
- **Spoken Script:**
  > "BALB replaces agnostic heuristics like Join-Shortest-Queue with a multi-attribute dispatch scoring function shown on the left:
  > 
  > $\text{Score}_w(t) = \alpha \theta_w(t) - \beta \left(\frac{q_w(t)}{Q_{\max}}\right) - \gamma U_w(t)$
  > 
  > Let us inspect each term:
  > - First, $\alpha \theta_w$ with $\alpha = 1.0$ is the Elasticity Bonus. It gives positive routing preference to workers operating at higher service fidelity, encouraging optional task execution when headroom permits.
  > - Second, $-\beta (q_w / Q_{\max})$ with $\beta = 2.0$ is the Queue Backlog Penalty. It heavily penalizes queue occupancy to protect against buffer overflows and Head-of-Line delays.
  > - Third, $-\gamma U_w$ with $\gamma = 0.5$ is the Historical CPU Utilization Penalty, which prevents dispatch thrashing between cores.
  > 
  > On the right, we introduce a crucial safety mechanism: the Anti-Overload Boundary. If any worker's queue reaches $Q_{\text{soft}} = 40$ requests—80% of capacity—its elasticity bonus is instantly clamped to zero ($\alpha \leftarrow 0$). This guarantees that a worker retaining a high dimmer cannot trap new requests if its buffer is dangerously full. If all workers exceed this threshold, BALB falls back to pure queue minimization, guaranteeing cluster headroom under compound stress."
- **Presenter Cue:** Emphasize the anti-overload rule: "Elasticity bonus goes to zero at 80% capacity."
- **Transition:** *"To rigorously evaluate CloudRescue against baselines, we designed a reproducible simulation methodology."*

---

### SLIDE 9: Experimental Methodology & Factorial Design
- **Presenter:** Yeruva Mahesh Reddy
- **Target Duration:** 40 seconds (Elapsed: 5:45 – 6:25)
- **Core Message:** We eliminate stochastic confounding via a 3-stream PRNG architecture and execute a full 360-run factorial ablation matrix with paired statistical tests.
- **Visuals on Screen:** Three panels: Multi-Stream PRNG Architecture, Three-Way Factorial Matrix (CFG-A, CFG-B, CFG-C), and Statistical Battery Rigor.
- **Spoken Script:**
  > "Evaluating adaptive systems via simulation introduces a subtle methodological challenge: random number synchronization. Under standard simulation, if a brownout controller bypasses an optional task, the simulator draws fewer random numbers, causing subsequent arrival timestamps and processing durations to desynchronize between configurations.
  > 
  > To eliminate this confounding, CloudRescue implements a multi-stream pseudorandom number generator architecture using independent PCG64 streams:
  > - Stream 1 generates Poisson request arrivals.
  > - Stream 2 generates mandatory service durations.
  > - Stream 3 generates optional service durations.
  > As a result, all configurations experience mathematically identical arrival schedules and service requirements for any given seed.
  > 
  > We evaluate a complete 3-way ablation matrix across 4 scenarios:
  > - CFG-A: Unmanaged Baseline (No Brownout + JSQ).
  > - CFG-B: Local Brownout Alone (Brownout + JSQ).
  > - CFG-C: Full CloudRescue (Brownout + BALB).
  > With 30 matched seeds per condition, this yields 360 primary simulation runs, analyzed via paired t-tests, Wilcoxon signed-rank tests, Cohen's $d_z$ effect sizes, and Bonferroni and FDR corrections."
- **Presenter Cue:** Point to the "Confounding Eliminated" guarantee on the left panel.
- **Transition:** *"Let us examine the four stress scenarios designed for this benchmark."*

---

### SLIDE 10: Four Standardized Experimental Scenarios
- **Presenter:** Yeruva Mahesh Reddy
- **Target Duration:** 35 seconds (Elapsed: 6:25 – 7:00)
- **Core Message:** Four standardized profiles isolate stationary nominal load, demand-side surges, capacity-side crashes, and simultaneous compound crises.
- **Visuals on Screen:** Four clean vertical cards representing Nominal, Flash Crowd, Server Crash, and Compound Stress profiles with exact timeline parameters.
- **Spoken Script:**
  > "We benchmarked all three configurations across four standardized operational scenarios:
  > 
  > 1. Nominal: A stationary arrival rate of 70 req/s across all 4 workers—70% utilization—evaluating steady-state stability and unperturbed dimmer equilibrium.
  > 2. Flash Crowd: Traffic doubles instantaneously from 70 to 140 req/s between $t = 200\text{ s}$ and $400\text{ s}$—140% cluster capacity—testing rapid dimmer shedding and buffer preservation.
  > 3. Server Crash: Traffic remains at 70 req/s, but Workers 1 and 2 crash at $t = 300\text{ s}$, halving cluster capacity until they are repaired and restored at $t = 450\text{ s}$. This tests capacity shock absorption and recovery.
  > 4. Compound Stress: Both disruptions coincide! A flash crowd runs from 200s to 400s, and a server crash runs from 300s to 450s. During the overlap from 300s to 400s, traffic intensity reaches 280% of available capacity. This is the ultimate resilience stress test.
  > 
  > I will now invite Ram Charan to present the experimental results, recovery analysis, and architectural trade-offs."
- **Presenter Cue:** Turn to Ram Charan with an open palm gesture; Ram Charan steps forward to take the presentation.
- **Transition:** *"Ram will now walk us through the certified experimental results."*

---

### SLIDE 11: Main Performance Results: DECISIVE RESILIENCE
- **Presenter:** K. Ram Charan
- **Target Duration:** 45 seconds (Elapsed: 7:00 – 7:45)
- **Core Message:** Brownout adaptation decisively protects availability, reducing overall SLA failures by up to 41.10 percentage points and bounding tail latency strictly within SLA limits.
- **Visuals on Screen:** Left panel embedding `sla_violation_rates_bar.png`; Right panel presenting certified benchmarks, $p$-values, and effect sizes.
- **Spoken Script:**
  > "Thank you, Mahesh. Looking at the results, the empirical evidence demonstrates that brownout adaptation provides decisive resilience against catastrophic cloud failure.
  > 
  > Direct your attention to the bar plot on the left. In the unmanaged baseline (CFG-A, shown in gray), a flash crowd produces an overall SLA failure rate of 44.04%, while compound stress causes a 47.70% failure rate.
  > 
  > Now examine CloudRescue (CFG-C, shown in dark blue):
  > - Under Flash Crowd: Overall SLA failure drops from 44.04% down to just 2.94%—a massive 41.10 percentage point reduction. This difference is statistically decisive: $p = 3.01 \times 10^{-62}$ with an extraordinary paired effect size of Cohen's $d_z = -121.71$. Furthermore, latency violations among admitted requests plummet from 32.83% down to 2.89%, and 95th-percentile response time drops from 184.34 ms down to 82.87 ms, safely bounded within the 100 ms SLA.
  > - Under Server Crash: Overall SLA failure drops from 33.38% down to 6.33% in CloudRescue—a 27.05 percentage point reduction ($p = 5.32 \times 10^{-53}$).
  > - Under Compound Stress: Failures drop from 47.70% in the baseline down to 35.33% in CloudRescue—a 12.37 percentage point reduction ($p = 6.57 \times 10^{-46}$), with local brownout alone in CFG-B achieving 33.38%."
- **Presenter Cue:** Point to the dark blue bars on the left plot showing the dramatic drop in SLA failure rate across all scenarios.
- **Transition:** *"Next, let us look at the temporal dynamics: how quickly does CloudRescue adapt, and how does it recover after repairs?"*

---

### SLIDE 12: Recovery Dynamics & DEC-010 Methodology
- **Presenter:** K. Ram Charan
- **Target Duration:** 45 seconds (Elapsed: 7:45 – 8:30)
- **Core Message:** BALB accelerates adaptation stabilization up to 28.4×, while DEC-010 resolves artificial right-censoring to demonstrate a 2.13× speedup in post-repair recovery.
- **Visuals on Screen:** Left panel embedding `time_series_dynamics_compound.png`; Right panel presenting adaptation speedup metrics and DEC-010 recovery benchmarks.
- **Spoken Script:**
  > "Slide 12 presents our telemetry time-series and recovery analysis.
  > 
  > First, looking at adaptation speed ($T_{\text{adapt}}$): When a flash crowd hits, brownout under JSQ (CFG-B) takes 56.7 seconds for local controllers to pull dimmers downward against incoming queues. BALB (CFG-C) stabilizes the cluster in just 2.50 seconds—a 22.7-fold acceleration ($p < 10^{-23}$). Under a server crash, BALB stabilizes in 2.00 seconds—a 28.4-fold speedup. Because BALB incorporates dimmer state into routing scores, it re-routes traffic pre-emptively without waiting for worker queues to blow up.
  > 
  > Second, we address a major methodological finding: the Post-Restoration Recovery Trap. In early trials, demanding that restored servers achieve a static dimmer of $\theta \ge 0.8$ resulted in severe right-censoring, because under nominal stationary load, controllers naturally settle at an equilibrium dimmer around 0.70.
  > 
  > We formulated and implemented DEC-010, which derives empirical, seed- and worker-specific nominal baselines ($\theta_{\text{nom}, w, s} \pm 0.05$). Under DEC-010, BALB accelerates post-restoration recovery time from 323.5 seconds in CFG-B down to 151.6 seconds in CFG-C—a 2.13-fold speedup ($p = 2.03 \times 10^{-5}$)—while boosting full 30-seed recovery rates from 46.7% to 100.0%."
- **Presenter Cue:** Trace the time-series plot on the left: show the crash at 300s, the rapid dimmer drop, the flat queue depths, and the clean recovery at 450s.
- **Transition:** *"Now we come to our most important scientific finding: the trade-off between fairness and service fidelity."*

---

### SLIDE 13: The Fundamental Fairness vs. Service-Fidelity Trade-Off
- **Presenter:** K. Ram Charan
- **Target Duration:** 45 seconds (Elapsed: 8:30 – 9:15)
- **Core Message:** We confirm load equity (Jain's index jumps from ~0.65 to 0.99), but decisively reject the fidelity hypothesis ($p < 10^{-38}$)—revealing an immutable trade-off in autonomic systems.
- **Visuals on Screen:** Top half with `fairness_and_utilization_box.png` and `fidelity_vs_reliability_tradeoff.png`; Bottom half contrasting Supported Fairness vs Rejected Fidelity.
- **Spoken Script:**
  > "Slide 13 highlights our most significant theoretical insight. We pre-registered two dimensions under hypothesis $H_{1,3}$: that BALB would improve workload fairness, AND that it would improve service fidelity by steering traffic toward high-dimmer workers.
  > 
  > As shown in Dimension 1 on the left, the fairness hypothesis was decisively supported. Under JSQ, Jain's Fairness Index collapsed to 0.607 in nominal and 0.646 in server crash. BALB completely eliminates this load skew, achieving near-perfect fairness of $J \ge 0.981$ to $0.996$ across all scenarios ($p < 10^{-8}$).
  > 
  > However, look at Dimension 2 on the right: the service-fidelity hypothesis was decisively REJECTED ($p < 10^{-38}$). Across all four scenarios, service fidelity in CloudRescue dropped by 11.4 to 17.9 percentage points compared to CFG-B.
  > 
  > Why did this happen? Our architectural analysis reveals that the high fidelity observed under JSQ was an illusion sustained by pathological load skew: healthy workers preserved high dimmers only because JSQ starved them of requests! To restore true cluster-wide load equity, BALB must distribute arriving traffic evenly, which forces all operational workers to degrade their dimmers in unison. This is an immutable architectural trade-off: workload equity requires distributing the degradation burden."
- **Presenter Cue:** Emphasize the academic honesty: "We did not hide this rejection; we characterized it as a fundamental architectural principle."
- **Transition:** *"In the spirit of rigorous academic research, let us examine our limitations and future roadmap."*

---

### SLIDE 14: Limitations & Future Work
- **Presenter:** K. Ram Charan
- **Target Duration:** 30 seconds (Elapsed: 9:15 – 9:45)
- **Core Message:** We transparently document four threats to validity and establish a clear roadmap toward physical Kubernetes testbeds and online reinforcement learning.
- **Visuals on Screen:** Two columns balancing Documented Research Limitations (Threats to Validity) on the left against Future Research Directions on the right.
- **Spoken Script:**
  > "We maintain rigorous academic transparency regarding the scope and limitations of our findings:
  > 
  > On the left, our primary limitations:
  > 1. Queuing abstraction: We evaluated single-tier M/M/1-FIFO queues; enterprise clouds involve complex microservice call DAGs, non-exponential runtimes, and thread contention.
  > 2. Static BALB weights: Our default weights ($\alpha=1.0, \beta=2.0, \gamma=0.5$) were verified robust in a 144-run parameter sweep, but remain static at runtime.
  > 3. Single-tier proxy and idealized clock: SimPy discrete-event simulation abstracts network stack latencies and distributed proxy gossip overhead.
  > 
  > On the right, our future roadmap:
  > 1. Autonomous weight tuning: Using reinforcement learning or Bayesian optimization to dynamically adapt BALB parameters in real-time.
  > 2. Physical Kubernetes testbed: Implementing BALB as an Envoy WASM filter and Istio service mesh extension on a bare-metal Kubernetes cluster using TeaStore or DeathStarBench.
  > 3. Multi-tier feature shedding: Supporting multi-level discrete feature degradation rather than binary execution."
- **Presenter Cue:** Keep delivery structured, honest, and forward-looking.
- **Transition:** *"To conclude our presentation..."*

---

### SLIDE 15: Conclusion, Takeaways & Q&A
- **Presenter:** K. Ram Charan (joined by Hari Prasad L and Yeruva Mahesh Reddy)
- **Target Duration:** 15 seconds (Elapsed: 9:45 – 10:00)
- **Core Message:** CloudRescue establishes that brownout is essential, ingress co-design is mandatory, and fairness requires shared degradation. All artifacts are fully open and reproducible.
- **Visuals on Screen:** Three takeaway cards summarizing key principles; open-source GitHub repository URL and committee Q&A invitation banner.
- **Spoken Script:**
  > "To conclude, CloudRescue establishes three actionable principles for cloud systems:
  > 1. Software graceful degradation is an essential pillar of cloud resilience, slashing SLA failures by up to 41 percentage points without expensive hardware scaling.
  > 2. Ingress load balancing co-design is mandatory: agnostic routing breaks down under brownout, whereas BALB restores near-perfect equity and accelerates adaptation by up to 28 times.
  > 3. Workload equity and service fidelity represent a fundamental trade-off that cloud architects must balance deliberately.
  > 
  > All simulation models, analysis scripts, and our certified 360-run dataset are publicly archived on GitHub. We thank our advisor and the committee, and we now welcome your questions."
- **Presenter Cue:** All three team members stand side-by-side at the lectern, make eye contact with the examination committee, and invite questions.

---

## 3. Examination Defense FAQ & Committee Defense Strategy

Here are the six most probable critical questions committee members will ask, along with exact, evidence-backed answers:

### Q1: "Why did BALB reduce service fidelity if your pre-registered hypothesis expected an increase?"
- **Respondent:** K. Ram Charan / Hari Prasad L
- **Answer:**
  > "This was our most compelling empirical finding. Pre-registered hypothesis $H_{1,3}$ assumed that by including the dimmer term $+\alpha \theta_w$ in the dispatch score, the balancer would steer traffic toward workers with high dimmers, thereby executing more optional features in aggregate.
  > 
  > However, our discrete-event simulations revealed an inescapable physical coupling: in CFG-B (Brownout + JSQ), the high fidelity (e.g. 20.89% in flash crowd) was an artifact of severe load skew ($J = 0.730$). Healthy workers maintained high dimmers only because JSQ starved them of requests! When BALB corrects this skew and distributes load equitably across all four workers ($J = 0.989$), every worker experiences increased traffic intensity, forcing all local PI controllers to lower their dimmers in unison to maintain response times below 80 ms.
  > 
  > Therefore, you cannot achieve workload equity while preserving localized high fidelity under overload. This is an immutable architectural conservation law: under constrained physical capacity, fairness requires distributing the degradation burden."

---

### Q2: "In Table 4 and Slide 11, you report a Cohen's $d_z$ effect size of $-121.71$ for SLA violation reduction. Isn't an effect size over 100 absurdly high?"
- **Respondent:** Yeruva Mahesh Reddy
- **Answer:**
  > "In behavioral and social sciences, a Cohen's $d$ of 0.8 is considered large. However, in deterministic paired engineering systems evaluated via Common Random Numbers (CRN), Cohen's $d_z$ is defined as the mean paired difference divided by the standard deviation of paired differences:
  > 
  > $$d_z = \frac{\bar{D}}{s_D}$$
  > 
  > In our Flash Crowd benchmark, across $N = 30$ matched seeds, CFG-A had an overall failure rate of $44.04\% \pm 0.16\%$, and CFG-C had $2.94\% \pm 0.17\%$. Because our multi-stream PRNG synchronizes arrival times and service demands perfectly, the paired difference is nearly identical for every single seed: $\bar{D} = -41.10\%$, with a standard deviation of only $s_D = 0.337\%$.
  > 
  > Dividing $-41.10$ by $0.337$ yields $d_z = -121.71$. This astronomical effect size simply reflects near-zero treatment variance across matched random streams. It proves that the 41.10 percentage point reduction is an overwhelming, deterministic physical effect rather than a statistical artifact."

---

### Q3: "What exactly is DEC-010, and why was static thresholding flawed for post-restoration recovery?"
- **Respondent:** Hari Prasad L
- **Answer:**
  > "In prior literature and our initial project specification, recovery time was defined as the duration required for a repaired worker's dimmer to return to $\theta \ge 0.8$ or $0.95$.
  > 
  > When we ran our simulations, we discovered that under nominal stationary load ($\lambda = 70\text{ req/s}$) and an 80 ms latency setpoint, the closed-loop feedback controller naturally settles at an equilibrium dimmer of $\theta \approx 0.70$ to $0.78$. It NEVER reaches 0.80 or 0.95 under stationary operation, because doing so would violate the 80 ms latency target!
  > 
  > Demanding a static threshold of 0.8 resulted in severe artificial right-censoring: repaired workers were healthy and stable, but marked as 'unrecovered'. In DEC-010, we established an empirical nominal reference: we sample each worker's unperturbed baseline dimmer ($\theta_{\text{nom}, w, s}$) during stationary warmup, and define recovery as re-entering within $\pm 0.05$ of that nominal baseline. This eliminated artificial censoring and allowed us to prove that BALB accelerates post-restoration recovery by $2.13\times$."

---

### Q4: "Why did you choose M/M/1-FIFO queues rather than simulating complex microservice DAGs?"
- **Respondent:** K. Ram Charan
- **Answer:**
  > "In control-theoretic research, the first principle is isolation of variables. If we evaluated CloudRescue on a complex multi-tier microservice DAG with database lock contention and network jitter, it would be impossible to mathematically isolate whether performance changes stemmed from the PI controller, the BALB scoring function, or downstream cascading lock delays.
  > 
  > By rigorously modeling M/M/1-FIFO queues with SimPy and isolating PRNG streams, we guaranteed that every single effect was purely attributable to brownout adaptation and dispatch scoring. As stated in Slide 14, extending this validated foundation to multi-tier microservice benchmarks like DeathStarBench on Kubernetes is the natural next step in our research roadmap."

---

### Q5: "How sensitive is BALB to the parameters $\alpha = 1.0, \beta = 2.0, \gamma = 0.5$?"
- **Respondent:** Yeruva Mahesh Reddy
- **Answer:**
  > "We investigated this directly in our exploratory 144-run parameter sweep across 48 distinct parameter combinations under Compound Stress ($n = 3$ seeds per cell).
  > 
  > The heatmap (Fig. 7 in the paper) showed that across all 24 configurations where queue penalty $\beta \ge 1.0$ and utilization penalty $\gamma \ge 0.5$, overall SLA failures varied within an extremely tight band of $27.52\%$ to $28.58\%$. In other words, performance is remarkably insensitive to minor weight variations, provided queue backlog is prioritized over dimmer elasticity ($\beta > \alpha$).
  > 
  > The only pathological failure mode occurred when $\gamma = 0$ and $\alpha = 2.0$: ignoring CPU utilization caused the balancer to thrash requests back and forth, driving Jain's fairness down to 0.76. This verified that our default weights are robust and stable."

---

### Q6: "Why is the 95th-percentile latency setpoint set to 80 ms when the SLA is 100 ms?"
- **Respondent:** Hari Prasad L
- **Answer:**
  > "In classical control theory for stochastic systems, operating directly at the constraint boundary leads to frequent constraint violations due to statistical variance. A 95th-percentile latency estimate computed over finite samples exhibits stochastic fluctuation.
  > 
  > Setting $r_{\text{target}} = 80.0\text{ ms}$ establishes a deliberate 20.0 ms safety margin below the contractual $r_{\text{SLA}} = 100.0\text{ ms}$ threshold. This ensures that transient queue surges and estimation noise do not breach contractual SLA limits before the velocity-form controller has time to adjust the dimmer."

---

## 4. Final Rehearsal Checklist

- [x] Laptop HDMI / USB-C display output set to 16:9 widescreen.
- [x] PPTX slides tested in presentation mode: no overlapping text, all plots crisp and readable.
- [x] Presenter 1 (Hari Prasad L) rehearsed Slides 1–5 (3m 30s target).
- [x] Presenter 2 (Yeruva Mahesh Reddy) rehearsed Slides 6–10 (3m 30s target).
- [x] Presenter 3 (K. Ram Charan) rehearsed Slides 11–15 (3m 00s target).
- [x] Hand-offs between presenters practiced smoothly without dead air.
- [x] Defense Q&A answers reviewed with all members ready to jump in on their respective domains.
- [x] Backup PDF version (`presentation/CloudRescue_Final_Presentation.pdf`) verified on USB drive.

