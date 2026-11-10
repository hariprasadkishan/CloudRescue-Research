# CloudRescue — Team Defense Preparation & Topic Allocation Guide

**Document Version:** 1.0 (Submission-Ready)  
**Project:** Autonomic Cloud Resilience Through Brownout-Based Graceful Degradation  
**Department:** Department of Computer Science and Engineering  
**Institution:** Indian Institute of Information Technology Dharwad (IIIT Dharwad), Karnataka, India  
**Date:** November 2026  

---

## 1. Executive Summary & Team Roles

This document establishes the formal division of responsibility, presentation assignments, and question-routing protocols among the three co-authors for the final academic defense and viva voce examination.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CORE ROLES & DOMAIN SPECIALIZATIONS                             │
├─────────────────────┬──────────────────────────────┬───────────────────────────────────┤
│ Team Member         │ Primary Defense Domain       │ Core Technical Specialization     │
├─────────────────────┼──────────────────────────────┼───────────────────────────────────┤
│ Hari Prasad L       │ System Architect & Lead      │ Problem Formulation, Motivation,   │
│                     │                              │ Literature, BALB Design & DEC-010 │
├─────────────────────┼──────────────────────────────┼───────────────────────────────────┤
│ Yeruva Mahesh Reddy │ Evaluation & Statistics Lead │ 360-Run Factorial Benchmark,      │
│                     │                              │ Statistical Tests & Sensitivity   │
├─────────────────────┼──────────────────────────────┼───────────────────────────────────┤
│ K. Ram Charan       │ Control & Implementation Lead│ Velocity PI Mathematics, SimPy    │
│                     │                              │ Simulator, Telemetry & Trade-Offs │
└─────────────────────┴──────────────────────────────┴───────────────────────────────────┘
```

---

## 2. Topic Allocation Matrix

Every technical subject in the research manuscript and presentation deck is assigned a **Primary Respondent** (who answers first) and a **Secondary Respondent** (who adds technical depth or supporting data if needed).

| Subject Area | Specific Topics Covered | Primary Respondent | Secondary Respondent |
| :--- | :--- | :--- | :--- |
| **1. Problem & Context** | Microservice queuing physics, non-linear tipping point, SLA violation definitions ($V_{\text{lat}}$ vs. $V_{\text{overall}}$) | **Hari Prasad L** | Yeruva Mahesh Reddy |
| **2. Prior Literature** | Resilinets ($D^2R^2+DR$), Welsh & Benkhelifa survey, Klein et al. brownout, Cartlidge & Sriram auto-scaling critique | **Hari Prasad L** | K. Ram Charan |
| **3. The JSQ Pathology** | Agnostic shortest-queue failure mode, degraded worker starvation cycle, load skew mechanics | **Hari Prasad L** | K. Ram Charan |
| **4. System Architecture** | Ingress proxy, worker cluster topology ($M=4$), dual-stage request decomposition (10 ms mandatory, 30 ms optional) | **K. Ram Charan** | Hari Prasad L |
| **5. Controller Design** | Velocity-form discrete PI update, error formulation $e_w(t)$, intrinsic anti-windup clamping, telemetry guard | **K. Ram Charan** | Yeruva Mahesh Reddy |
| **6. BALB Algorithm** | Multi-attribute scoring formula, weights $(\alpha, \beta, \gamma)$, soft-overload threshold ($Q_{\text{soft}}=40$), fallback | **Hari Prasad L** | K. Ram Charan |
| **7. Simulation Methodology** | SimPy 4.x process engine, discrete-event timing, multi-stream PRNG (PCG64 Streams 1–3), Common Random Numbers | **K. Ram Charan** | Yeruva Mahesh Reddy |
| **8. Experimental Design** | Three-way ablation matrix (CFG-A, CFG-B, CFG-C), 4 stress scenarios, 30 matched seeds (360 primary runs) | **Yeruva Mahesh Reddy** | Hari Prasad L |
| **9. Statistical Battery** | Shapiro-Wilk normality, paired Student's t-test, Wilcoxon signed-rank, Cohen's $d_z$, Bonferroni & FDR adjustments | **Yeruva Mahesh Reddy** | K. Ram Charan |
| **10. Numerical Results** | 41.10% failure reduction in Flash Crowd, $P_{95}$ compressed to 82.9 ms, Compound Stress collapse prevention | **Yeruva Mahesh Reddy** | Hari Prasad L |
| **11. Recovery Dynamics** | Adaptation speed ($T_{\text{adapt}}$ speedups of $22.7\times$ to $28.4\times$), DEC-010 nominal baseline, uncensored stats | **Hari Prasad L** | Yeruva Mahesh Reddy |
| **12. The Trade-Off** | Workload equity ($J \ge 0.985$) vs. service fidelity drop ($-11.4$ to $-17.9\%$), rejection of $H_{1,3}$ fidelity hypothesis | **K. Ram Charan** | Hari Prasad L |
| **13. Sensitivity Sweep** | 144-run parameter sweep across 48 combinations, parameter stability across $\beta \ge 1.0$ and $\gamma \ge 0.5$ | **Yeruva Mahesh Reddy** | K. Ram Charan |
| **14. Threats to Validity** | $M/M/1$-FIFO assumptions, single-tier proxy, static weights, discrete-event vs. Linux kernel timing abstractions | **K. Ram Charan** | Hari Prasad L |
| **15. Future Testbed** | Kubernetes, Envoy WASM filters, Istio service mesh, DeathStarBench social network microservices | **Hari Prasad L** | K. Ram Charan |

---

## 3. Member-by-Member Defense Briefing

### Member 1: Hari Prasad L (Lead Author & System Architect)
- **Presentation Allocation:** Slides 1 through 5 (~3.5 minutes).
- **Core Defense Focus:** Conceptual leadership, problem framing, literature positioning, BALB dispatch scoring rationale, DEC-010 formulation, and architectural conclusions.
- **Key Equations & Metrics to Master:**
  - BALB dispatch score: $\text{Score}_w(t) = \alpha \theta_w - \beta \frac{q_w}{Q_{\max}} - \gamma U_w$.
  - Soft-overload threshold: $Q_{\text{soft}} = 40$ (80% of $Q_{\max} = 50$).
  - DEC-010 nominal tolerance: $\theta_{\text{nom}, w, s} \pm 0.05$.
- **Sample Examiner Questions Assigned:**
  - *"Why did you create a new load balancing algorithm instead of tuning JSQ?"*
  - *"What is DEC-010, and why was static thresholding flawed for post-restoration recovery?"*
  - *"How does CloudRescue differ from the original brownout papers by Klein et al.?"*
- **Handoff Phrase to Member 2 (Mahesh):**
  > *"I will now hand over to Yeruva Mahesh Reddy to walk us through the system architecture, controller mathematics, and experimental design."*

---

### Member 2: Yeruva Mahesh Reddy (Evaluation & Statistical Lead)
- **Presentation Allocation:** Slides 6 through 10 (~3.5 minutes).
- **Core Defense Focus:** Factorial ablation design, statistical battery, p-value adjustments, effect sizes, scenario timelines, and numerical benchmark verification.
- **Key Equations & Metrics to Master:**
  - Cohen's $d_z = \bar{D} / s_D$ (and why $d_z = -121.71$ under Flash Crowd).
  - Bonferroni adjustment: $p_{\text{adj}} = \min(1.0, p \times 114)$.
  - Benjamini-Hochberg False Discovery Rate (FDR $q$-values).
  - Overall SLA Failure rates: CFG-A ($44.04\%$), CFG-B ($5.69\%$), CFG-C ($2.94\%$) under Flash Crowd.
  - Compound Stress failure rates: CFG-A ($60.59\%$), CFG-B ($30.01\%$), CFG-C ($27.97\%$).
- **Sample Examiner Questions Assigned:**
  - *"Why is your Cohen's d_z effect size over 100? Is that mathematically valid?"*
  - *"How did you test for normality, and which tests were used when data was non-normal?"*
  - *"What did the 144-run sensitivity sweep reveal about parameter sensitivity?"*
- **Handoff Phrase to Member 3 (Ram Charan):**
  > *"I will now invite Ram Charan to present our primary performance results, recovery dynamics, and architectural trade-offs."*

---

### Member 3: K. Ram Charan (Control & Simulation Implementation Lead)
- **Presentation Allocation:** Slides 11 through 15 (~3.0 minutes).
- **Core Defense Focus:** Discrete-event simulation implementation (SimPy), velocity-form PI algorithm, intrinsic anti-windup clamping, telemetry engine, the fairness-fidelity trade-off, and threats to validity.
- **Key Equations & Metrics to Master:**
  - Error: $e_w(t) = r_{\text{target}} - \hat{r}_{95, w}(t)$ with $r_{\text{target}} = 80.0\text{ ms}$.
  - Velocity PI update: $\Delta \theta_w(t) = K_p (e_w(t) - e_w(t-1)) + K_i e_w(t) \Delta t_{\text{ctrl}}$.
  - Clamping: $\theta_w(t) = \min(1.0, \max(0.0, \theta_w^{\text{raw}}(t)))$.
  - Jain's Fairness Index formula: $J = (\sum x_w)^2 / (n \sum x_w^2)$.
  - Trade-off numbers: $J$ elevated from $0.607$ to $0.989$ ($p < 10^{-8}$); Fidelity $F$ dropped by $11.4$ to $17.9$ percentage points ($p < 10^{-38}$).
- **Sample Examiner Questions Assigned:**
  - *"Why did BALB reduce service fidelity if pre-registered hypothesis H1,3 expected an increase?"*
  - *"Why velocity-form PI instead of positional PID?"*
  - *"What are the limitations of assuming M/M/1-FIFO queues?"*
- **Closing Phrase for Q&A:**
  > *"Thank you. All three of us are now open to receive questions and discussion from the committee."*

---

## 4. Question-Routing & Defense Etiquette Protocol

To ensure seamless coordination during the examination committee Q&A:

1. **The Lead Acknowledges:** Hari Prasad L acts as team coordinator. When a question is asked, Hari makes brief eye contact with the relevant specialist and either begins answering or passes the floor:
   - *"That is a central question regarding our statistical methodology; I will ask Mahesh to explain our paired testing battery."*
   - *"Ram implemented our velocity-form PI controller; he will address the anti-windup mechanics."*
2. **Never Interrupt a Teammate:** Allow the primary respondent to complete their core answer. If you have a critical supporting data point, wait for them to finish, then add:
   - *"To add to what Ram noted, in Table 4 of our paper, that exact difference yielded a p-value of..."*
3. **Never Disagree Publicly:** All experimental findings are frozen and certified. If an examiner questions a discrepancy, refer back to the certified Master Dataset (`master_results.csv`) and the Decision Log (`DECISIONS.md`).
4. **Honesty over Bluffing:** If an examiner asks about a physical deployment aspect outside our discrete-event scope:
   - *"In our discrete-event simulation model, we abstracted that specific kernel socket buffer behavior. However, as noted in Section 9.7 of our paper, evaluating that under an Envoy physical testbed is our first priority for future work."*

---

## 5. Mock Defense Rehearsal Schedule

| Rehearsal Session | Objective | Duration | Checklist |
| :--- | :--- | :--- | :--- |
| **Session 1 (Timing)** | Strict 10-minute slide transitions | 45 min | Verify 3.5 min / 3.5 min / 3.0 min split; eliminate rambling. |
| **Session 2 (Handoffs)** | Verbal handoffs and slide pointers | 30 min | Rehearse physical transitions at the lectern without awkward gaps. |
| **Session 3 (Q&A Drill)** | Cross-examination on all 65 questions | 60 min | Fire tough questions from `docs/CloudRescue_Viva_Preparation.md`. |
| **Session 4 (Final Run)** | Complete dry run with mock examiners | 30 min | Full dress rehearsal with live dashboard demo fallback. |

