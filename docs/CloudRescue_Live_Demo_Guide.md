# CloudRescue — Live Demonstration Guide & Defense Walkthrough

**Document Version:** 1.0 (Submission-Ready)  
**Authors:** Hari Prasad L, Yeruva Mahesh Reddy, K. Ram Charan  
**Affiliation:** Department of Computer Science and Engineering, Indian Institute of Information Technology Dharwad  
**Repository:** `https://github.com/hariprasadkishan/CloudRescue-Research`  
**Target Audience:** Academic Examiners, Project Reviewers, and Live Demo Operators  

---

## 1. Quick-Start Terminal Commands

Follow these exact commands to spin up the CloudRescue interactive research monograph and backend server.

### Terminal 1: Launch FastAPI Telemetry Backend
```bash
# Navigate to project root
cd /home/andesindica/Downloads/CloudRescue-Research

# Activate Python virtual environment
source .venv/bin/activate

# Launch Uvicorn ASGI server
uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload
```
*Expected Output:*
```text
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Terminal 2: Launch Vite React Frontend
```bash
# Navigate to frontend directory
cd /home/andesindica/Downloads/CloudRescue-Research/frontend

# Launch Vite development server
npm run dev
```
*Expected Output:*
```text
  VITE v8.x.x  ready in 250 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Terminal 3 (Verification / Health-Check)
```bash
# Verify backend API response
curl -s http://127.0.0.1:8000/api/summary | jq .

# Verify scenario list
curl -s http://127.0.0.1:8000/api/scenarios | jq .
```

*Open your browser and navigate to:* **`http://localhost:5173`**

---

## 2. Seven-Screen Interactive Dashboard Navigation

The CloudRescue dashboard is designed as an interactive academic monograph with 7 dedicated screens:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   DASHBOARD TOP NAVIGATION BAR                        │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬────────────┤
│ Screen 1│ Screen 2│ Screen 3│ Screen 4│ Screen 5│ Screen 6│  Screen 7  │
│ Overview│ Inquiry │Simulator│Benchmark│Analytics│ Methods │Publication │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴────────────┘
```

---

### Screen 1 — Executive Overview & Scorecard
- **Route / Tab:** `Overview`
- **What to Demonstrate:**
  1. **Academic Title & Context:** Point out the title, research badges, and attribution to IIIT Dharwad.
  2. **Executive Scorecard:** Direct attention to the four primary high-level metric cards:
     - **Overall SLA Failure Reduction:** Flash crowd failure slashed from **44.04%** to **2.94%** ($-41.10\%$ reduction).
     - **Tail Latency Compliance:** 95th-percentile response latency bounded at **82.87 ms** (well within the 100 ms SLA setpoint).
     - **Workload Fairness Restoration:** Jain's Fairness Index elevated from **0.607** to **0.989** ($+0.382$ gain).
     - **Post-Restoration Recovery:** $2.13\times$ faster recovery under DEC-010 empirical criteria ($151.63\text{ s}$ vs. $323.47\text{ s}$).
  3. **Problem Statement Summary:** Explain the non-linear queuing tipping point ($\rho \to 1.0$) and why traditional auto-scaling fails due to the 60–300s provisioning gap.

---

### Screen 2 — Research Inquiry & Ablation Explorer
- **Route / Tab:** `Inquiry`
- **What to Demonstrate:**
  1. **Three-Way Ablation Matrix:** Explain the three configurations:
     - **CFG-A (Baseline):** Agnostic JSQ + No Brownout (industry default).
     - **CFG-B (Ablation):** Agnostic JSQ + Local Brownout (state-of-the-art literature baseline).
     - **CFG-C (CloudRescue):** Brownout-Aware Load Balancing (BALB) + Local Brownout (proposed full framework).
  2. **Interactive Scenario Toggle:** Switch between the four operational profiles:
     - `Nominal` (Stationary 70% load).
     - `Flash Crowd` ($2\times$ traffic surge, $\lambda = 140\text{ req/s}$).
     - `Server Crash` (50% capacity dropout at $t=300\text{ s}$, restored at $t=450\text{ s}$).
     - `Compound Stress` (Simultaneous traffic surge and worker outages).
  3. **Comparative Metric Delta Cards:** Click through scenarios and highlight how CFG-C drastically outperforms CFG-A on reliability while resolving the load-skew pathology of CFG-B.

---

### Screen 3 — Simulation Environment & Live Telemetry Inspector
- **Route / Tab:** `Simulator`
- **What to Demonstrate:**
  1. **Telemetry Playback Engine:** Select `Compound Stress` and `Seed 1001`, then hit **Play** or scrub through the timeline ($0\text{ s}$ to $600\text{ s}$).
  2. **Onset of Stress ($t = 200\text{ s}$ to $300\text{ s}$):**
     - Show the flash crowd triggering dimmer reduction on operational workers.
     - Observe how worker dimmers smoothly adjust to maintain 95th-percentile latency at 80 ms.
  3. **Crash Event ($t = 300\text{ s}$):**
     - Show Workers 1 and 2 dropping offline (rendered with clear offline badges).
     - Observe Workers 0 and 3 shedding optional features ($\theta \to 0$) to absorb the entire 140 req/s load.
     - Note that FIFO queue buffers remain bounded ($q \le 20$), preventing queue drops and Head-of-Line connection timeouts ($W_i \le 200\text{ ms}$).
  4. **Restoration & Recovery ($t = 450\text{ s}$):**
     - Watch Workers 1 and 2 rejoin the cluster.
     - Observe BALB intelligently steering requests to restored nodes to accelerate dimmer recovery.

---

### Screen 4 — Empirical Benchmark & Latency Analysis
- **Route / Tab:** `Benchmark`
- **What to Demonstrate:**
  1. **Grouped SLA Failure Bar Chart (`sla_violation_rates_bar.png`):**
     - Compare CFG-A, CFG-B, and CFG-C across all four scenarios.
     - Emphasize that CFG-A experiences 44.04% failure under flash crowds and 60.59% under compound stress.
     - Point out that CloudRescue (CFG-C) keeps SLA failures at 2.94% and 27.97%, respectively.
  2. **Response Latency Cumulative Distribution Function (CDF):**
     - Show `latency_cdf_comparison.png` under Compound Stress.
     - Highlight the steep vertical cliff of CFG-C below the 100 ms SLA line.
     - Contrast this with the heavy tail of CFG-A stretching past 200 ms timeouts.

---

### Screen 5 — Statistical Analytics & Trade-Off Explorer
- **Route / Tab:** `Analytics`
- **What to Demonstrate:**
  1. **Jain's Fairness Index Boxplot:**
     - Point out the severe load skew in CFG-B ($J \approx 0.607\text{--}0.764$) caused by agnostic JSQ.
     - Show CFG-C restoring near-perfect workload equity ($J \ge 0.985$ across all runs, $p < 10^{-8}$).
  2. **The Fundamental Architectural Trade-off:**
     - Open the Fidelity vs. Reliability scatter envelope (`fidelity_vs_reliability_tradeoff.png`).
     - **Crucial Academic Honesty Point:** Explain why BALB decreased service fidelity by 11.4 to 17.9 percentage points. High fidelity in CFG-B was an illusion sustained by starving healthy workers. To balance load, BALB must distribute degradation across all active workers.
  3. **Recovery Speedup (DEC-010):**
     - Show adaptation recovery times ($T_{\text{adapt}}$) dropping from 56.7s to 2.5s ($22.7\times$ speedup).
     - Show post-restoration recovery time ($T_{\text{restore}}$) under DEC-010 dropping from 323.5s to 151.6s ($2.13\times$ speedup).

---

### Screen 6 — Methodology, Equations & Provenance
- **Route / Tab:** `Methods`
- **What to Demonstrate:**
  1. **Mathematical Control Laws:**
     - Show Eq. (5): Error formulation $e_w(t) = r_{\text{target}} - \hat{r}_{95, w}(t)$.
     - Show Eq. (6)–(8): Velocity-form PI recurrence and intrinsic anti-windup clamping.
     - Show Eq. (3): BALB multi-attribute dispatch scoring formula $\text{Score}_w(t) = \alpha \theta_w - \beta \frac{q_w}{Q_{\max}} - \gamma U_w$.
     - Show the soft-overload fallback rule: $\alpha = 0$ when $q_w \ge Q_{\text{soft}} = 40$.
  2. **Multi-Stream PRNG Architecture:**
     - Explain the 3 isolated PCG64 streams (Arrivals, Mandatory Service, Optional Service) guaranteeing zero stochastic confounding.
  3. **Architectural Decision Records (ADRs):**
     - Highlight DEC-007 (CRN isolation), DEC-008 (BALB weights), and DEC-010 (Empirical nominal recovery baseline).

---

### Screen 7 — Publication, Artifacts & Verification
- **Route / Tab:** `Publication`
- **What to Demonstrate:**
  1. **Downloadable Research Artifacts:**
     - Point out links to `CloudRescue_Research_Paper_Final.pdf`, `CloudRescue_Final_Presentation.pptx`, and `master_results.csv`.
  2. **Certified Freeze Signoff:**
     - Show the signoff badge and verification cryptographic hashes for the frozen 360-run experiment.
  3. **IEEE Bibliography:**
     - Display references [1] through [17] traceably aligned with the final research paper draft.

---

## 3. Explaining Architecture & Ablation Configurations

When the examination committee asks you to explain the difference between configurations, use this concise explanation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THREE-WAY ABLATION MATRIX MATRIX                       │
├───────────────┬──────────────────────┬──────────────────────────────────────┤
│ Configuration │ Load Balancing Layer │ Worker-Level Resilience Layer        │
├───────────────┼──────────────────────┼──────────────────────────────────────┤
│ CFG-A         │ Join-Shortest-Queue  │ None (Full Fidelity Always)          │
│ (Baseline)    │ (Agnostic JSQ)       │ Queue saturated, drops requests      │
├───────────────┼──────────────────────┼──────────────────────────────────────┤
│ CFG-B         │ Join-Shortest-Queue  │ Velocity-Form Discrete PI Controller │
│ (Ablation)    │ (Agnostic JSQ)       │ Sheds optional tasks; causes skew    │
├───────────────┼──────────────────────┼──────────────────────────────────────┤
│ CFG-C         │ BALB                 │ Velocity-Form Discrete PI Controller │
│ (CloudRescue) │ (Elasticity-Aware)   │ Coordinated degradation & equity     │
└───────────────┴──────────────────────┴──────────────────────────────────────┘
```

### Explaining the Architectural Flow
1. **Ingress Proxy (BALB):** Receives client HTTP requests. Instead of simply routing to the shortest queue, BALB queries worker telemetry ($[\theta_w, q_w, U_w]$) and routes to the worker maximizing $\text{Score}_w = \alpha\theta_w - \beta(q_w/Q_{\max}) - \gamma U_w$.
2. **Worker Instances ($M=4$):**
   - Each worker has a FIFO queue ($Q_{\max}=50$).
   - Upon dequeue, the request executes **Stage 1 (Mandatory)**, taking $\approx 10\text{ ms}$.
   - The worker then draws a uniform random number $U \in [0, 1]$. If $U \le \theta_w$, it executes **Stage 2 (Optional)**, taking $\approx 30\text{ ms}$. Otherwise, it skips Stage 2.
3. **Local PI Controller:** Every second, each worker measures its completed 95th-percentile latency. If latency exceeds 80 ms, it decrements $\theta_w$. If latency is low, it increments $\theta_w$.

---

## 4. 5-Minute Live Demonstration Script

Use this time-coded script for a crisp, 5-minute presentation:

| Time | Target Screen | Speaker Action & Dialogue |
| :---: | :--- | :--- |
| **0:00 – 0:45** | **Screen 1 (Overview)** | *"Welcome. Here is the CloudRescue live research monograph. Under flash crowds and server crashes, unmanaged cloud services collapse due to non-linear queuing delays. As shown on our scorecard, CloudRescue reduces SLA failures by up to 41.10% and restores near-perfect workload equity."* |
| **0:45 – 1:30** | **Screen 2 (Inquiry)** | *"Let us explore our three-way ablation matrix. Notice CFG-A (Baseline), CFG-B (Brownout with standard JSQ), and CFG-C (CloudRescue). When we toggle to Compound Stress, notice how CFG-A fails 60.59% of requests, while CloudRescue cuts this down to 27.97%."* |
| **1:30 – 2:45** | **Screen 3 (Simulator)** | *"Now let us inspect live telemetry. We select Compound Stress, Seed 1001. At t=200s, the traffic doubles. Notice how worker dimmers immediately pull down, expanding capacity from 100 to 400 req/s. At t=300s, Workers 1 and 2 crash. The remaining two workers shed optional tasks completely, but their queues never exceed 20 requests. Not a single request times out! At t=450s, the nodes recover and smoothly re-enter nominal equilibrium."* |
| **2:45 – 3:45** | **Screen 4 & 5 (Results & Analytics)** | *"Here in our empirical benchmark, the bar chart shows overall SLA failures collapsing across all scenarios. Looking at Screen 5, notice Jain's Fairness Index: under JSQ (CFG-B), load skew drops fairness to 0.607. BALB (CFG-C) restores fairness to 0.989. However, notice our honest trade-off: service fidelity dropped by 11.4 percentage points because fair load distribution requires sharing the degradation burden."* |
| **3:45 – 4:30** | **Screen 6 (Methods)** | *"Under the hood, Screen 6 shows our velocity-form PI control law with intrinsic anti-windup clamping, our BALB dispatch formula with soft-overload fallback at 80% buffer capacity, and our 3-stream PRNG architecture that guarantees deterministic comparability across all 360 runs."* |
| **4:30 – 5:00** | **Screen 7 (Publication)** | *"Finally, on Screen 7, all experimental master CSVs, the final 19-page IEEE research paper PDF, and our 15-slide defense deck are fully accessible. Thank you, and we welcome your questions."* |

---

## 5. Contingency Plan: What If Live Demo Fails?

If the live demo network port is blocked, the browser fails to connect, or an unexpected dependency error occurs, execute this backup plan:

### Fallback Step 1: Check Process Status
```bash
# Check if backend is listening on port 8000
ss -tulpn | grep 8000

# Check if Vite frontend is listening on port 5173
ss -tulpn | grep 5173
```

### Fallback Step 2: Restart Both Services Cleanly
```bash
# Kill any lingering instances
pkill -f "uvicorn server.main:app"
pkill -f "vite"

# Restart backend in background
cd /home/andesindica/Downloads/CloudRescue-Research
source .venv/bin/activate
nohup uvicorn server.main:app --port 8000 > /tmp/backend.log 2>&1 &

# Restart frontend in background
cd /home/andesindica/Downloads/CloudRescue-Research/frontend
nohup npm run dev > /tmp/frontend.log 2>&1 &
```

### Fallback Step 3: Use the Static Publication Presentation & Paper PDF
If live local web serving is entirely disallowed on the examination machine:
1. Open the pre-compiled **`presentation/CloudRescue_Final_Presentation.pdf`** or **`presentation/CloudRescue_Final_Presentation.pptx`**.
2. All 6 high-resolution publication plots are already embedded on Slides 11, 12, and 13.
3. Open **`paper/CloudRescue_Research_Paper_Final.pdf`** for immediate access to Tables I through V and Figures 1 through 7.
4. Show the raw dataset in terminal:
   ```bash
   head -n 25 results/experiment_360/aggregated_metrics.csv
   ```
   This immediately proves that all results are real, frozen, and reproducible.

