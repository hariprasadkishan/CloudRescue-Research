# CloudRescue: Autonomic Cloud Resilience Through Brownout-Based Graceful Degradation

[![Build & Test Status](https://img.shields.io/badge/tests-56%20passed-brightgreen.svg)](tests/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](requirements.txt)
[![Frontend](https://img.shields.io/badge/frontend-React%2019%20%2B%20Vite%208%20%2B%20Tailwind%204-61DAFB.svg)](frontend/)
[![Backend API](https://img.shields.io/badge/backend-FastAPI%20%2B%20Uvicorn-009688.svg)](server/)
[![Evaluation](https://img.shields.io/badge/evaluation-360%20Matched%20Runs%20(Frozen)-darkgreen.svg)](results/experiment_360/)
[![Institution](https://img.shields.io/badge/institution-IIIT%20Dharwad-orange.svg)](https://iiitdwd.ac.in)

> **Academic Research Project**  
> **Department of Computer Science and Engineering**  
> **Indian Institute of Information Technology Dharwad (IIIT Dharwad)**  
> **Authors:** Hari Prasad L, Yeruva Mahesh Reddy, K. Ram Charan, Tushar  
> **Research Manuscript:** [`paper/CloudRescue_Research_Paper_Draft.md`](paper/CloudRescue_Research_Paper_Draft.md)

---

## 1. Executive Abstract

Modern cloud services face acute availability and tail latency degradation during sudden workload spikes (flash crowds) and abrupt compute instance crashes. Traditional mitigation relies on hardware over-provisioning—which is economically wasteful—or reactive auto-scaling, which exhibits non-negligible provisioning delays that fail during instantaneous shocks. Autonomic brownout-based graceful degradation dynamically modulates optional software features (e.g., recommendation engines, real-time analytics) via a control variable $\theta \in [0, 1]$, bounding latency within strict Service Level Agreements (SLAs).

However, when brownout controllers operate independently on distributed workers under conventional load balancing policies like Join-Shortest-Queue (JSQ), an acute routing pathology emerges: degraded workers rapidly shed optional computation, empty their queues quickly, and draw disproportionately high traffic, causing severe cluster load skew and delayed post-restoration recovery.

**CloudRescue** is an autonomic resilience architecture evaluated via high-fidelity discrete-event simulation (SimPy). CloudRescue couples a discrete velocity-form Proportional-Integral (PI) feedback controller with intrinsic anti-windup clamping on each worker node with **Brownout-Aware Load Balancing (BALB)** at the ingress proxy. BALB introduces a composite multi-attribute dispatch scoring function combining dimmer elasticity ($\theta$), normalized queue backlog ($q / Q_{\max}$), and processor utilization ($U$), guarded by anti-overloading penalties and soft-overload fallback mechanisms. In a certified 360-run evaluation ($N=30$ matched seeds per condition), CloudRescue eliminates load skew, elevates Jain's Fairness Index from 0.65 to 0.998 ($p < 10^{-8}$), accelerates post-restoration recovery by $2.06\times$–$2.15\times$ ($p < 4.1 \times 10^{-5}$), and protects tail latency under compound shock.

---

## 2. Research Objectives & Methodology

1. **Self-Adaptive Feedback Control:** Formulate a discrete velocity-form PI controller executing locally on each worker to adjust the brownout dimmer $\theta(t)$ based on moving 95th-percentile response times against an SLA setpoint ($T_{\text{target}} = 80\text{ ms}$).
2. **Brownout-Aware Routing (BALB):** Formulate a composite multi-attribute scoring function at the load balancer that penalizes severely degraded workers, preventing JSQ routing pathology.
3. **Rigorous Three-Way Ablation Evaluation:**
   - **`CFG-A` (Baseline):** Static execution ($\theta = 1.0$), standardized Join-Shortest-Queue (JSQ).
   - **`CFG-B` (Brownout Only):** Adaptive PI controller on workers, standardized JSQ.
   - **`CFG-C` (Full CloudRescue):** Adaptive PI controller on workers + BALB at the proxy.
4. **Stress Scenarios ($3 \times 4 \times 30 = 360$ runs):**
   - **Nominal:** Stationary arrival rate ($\lambda_{\text{nom}} = 80\text{ req/s}$), no injected failures.
   - **Flash Crowd Surge:** $3\times$ traffic surge ($\lambda_{\text{burst}} = 240\text{ req/s}$) for $150\text{ s}$ ($t = 300\text{--}450\text{ s}$).
   - **Server Crash Failure:** 50% cluster capacity loss (Workers 1 & 2 down) for $150\text{ s}$ ($t = 300\text{--}450\text{ s}$).
   - **Compound Stress:** Simultaneous $3\times$ flash crowd surge and 50% server crash for $150\text{ s}$.
5. **Multi-Stream PRNG Architecture:** Five independent random sub-streams derived via `np.random.SeedSequence(seed).spawn(5)` ensure 100% paired workload equivalence across all three configurations for each seed.

---

## 3. Architecture Overview

```
                      Ingress Requests (Poisson λ)
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │     CloudRescue Ingress Load Balancer        │
           │                                              │
           │  • CFG-A / CFG-B: Join-Shortest-Queue (JSQ)  │
           │  • CFG-C: Brownout-Aware Load Balancer (BALB)│
           │    Score: S_w = α·θ_w + β·(1 - q_w/Q_max)    │
           │               + γ·(1 - U_w) - OverloadPen    │
           └──────────────────────┬───────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │ (Worker 0)            │ (Worker 1)            │ (Worker 2/3)
          ▼                       ▼                       ▼
    ┌───────────┐           ┌───────────┐           ┌───────────┐
    │ Bounded Q │           │ Bounded Q │           │ Bounded Q │
    │ (FIFO, 50)│           │ (FIFO, 50)│           │ (FIFO, 50)│
    └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
          ▼                       ▼                       ▼
    ┌───────────┐           ┌───────────┐           ┌───────────┐
    │ Dual-Stage│           │ Dual-Stage│           │ Dual-Stage│
    │ Execution │           │ Execution │           │ Execution │
    │ Mandatory │           │ Mandatory │           │ Mandatory │
    │  + Option │           │  + Option │           │  + Option │
    └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
          │                       │                       │
     Feedback (p95)          Feedback (p95)          Feedback (p95)
          ▼                       ▼                       ▼
    ┌───────────┐           ┌───────────┐           ┌───────────┐
    │Velocity PI│           │Velocity PI│           │Velocity PI│
    │Controller │           │Controller │           │Controller │
    │θ_w ∈ [0,1]│           │θ_w ∈ [0,1]│           │θ_w ∈ [0,1]│
    └───────────┘           └───────────┘           └───────────┘
```

---

## 4. Key Experimental Findings (Simulation-Based)

*All metrics derived strictly from the certified 360-run experimental matrix ([`results/experiment_360/master_results.csv`](results/experiment_360/master_results.csv)).*

| Scenario | Metric | CFG-A (Baseline) | CFG-B (Brownout Only) | CFG-C (Full CloudRescue) | Statistical Significance |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Compound Stress** | SLA Failure Rate ($V_{\text{overall}}$) | $46.85 \pm 0.95\%$ | $30.82 \pm 0.72\%$ | **$29.35 \pm 0.69\%$** | $p = 7.74 \times 10^{-14}$ vs CFG-B |
| **Compound Stress** | Jain's Fairness Index ($J$) | $0.669 \pm 0.007$ | $0.650 \pm 0.006$ | **$0.998 \pm 0.000$** | $p = 1.05 \times 10^{-48}$, $d = 82.8$ |
| **Server Crash** | Jain's Fairness Index ($J$) | $0.763 \pm 0.010$ | $0.758 \pm 0.010$ | **$0.998 \pm 0.001$** | $p = 1.25 \times 10^{-41}$, $d = 34.0$ |
| **Flash Crowd** | Adaptation Time ($T_{\text{adapt}}$) | N/A | $56.83 \pm 20.37\text{ s}$ | **$2.50 \pm 2.74\text{ s}$** (med: $2\text{ s}$) | $p = 4.07 \times 10^{-5}$, $22.7\times$ faster |
| **Server Crash** | Post-Restoration Recovery | N/A | $52.93\text{ s}$ | **$25.73\text{ s}$** | $p = 2.37 \times 10^{-5}$, $2.06\times$ faster |
| **Compound Stress**| Post-Restoration Recovery | N/A | $59.27\text{ s}$ | **$27.53\text{ s}$** | $p = 4.07 \times 10^{-5}$, $2.15\times$ faster |
| **Compound Stress**| Service Fidelity ($F$) | $100.00 \pm 0.00\%$ | $49.49 \pm 0.64\%$ | $38.08 \pm 0.67\%$ | Trade-off: $p = 7.82 \times 10^{-39}$ |

> [!NOTE]
> **Authentic Architectural Trade-off:** BALB intentionally sacrifices $11.4$–$15.9\text{ pp}$ in optional service fidelity ($F$) compared to CFG-B. By routing traffic away from degraded workers onto healthy instances, healthy instances drop their dimmers sooner, preserving cluster fairness ($J \approx 0.998$) and bounded queues rather than allowing one worker to monopolize full fidelity.

---

## 5. Technology Stack

- **Simulation Core:** Python 3.10–3.14, [SimPy 4](https://simpy.readthedocs.io/), NumPy 2, SciPy 1, Pandas 3
- **Visualization:** Matplotlib 3 (Publication-grade 300 DPI figures)
- **Backend API:** FastAPI, Uvicorn, Pydantic v2
- **Frontend Dashboard:** React 19, Vite 8, Tailwind CSS v4, Lucide Icons, Recharts 3
- **Test Automation:** Pytest 9, Starlette TestClient / HTTPX

---

## 6. Installation & Quick Start

### 6.1 Prerequisites
- **Python:** Version 3.10 or higher (tested on 3.14.7)
- **Node.js:** Version 18.0 or higher (tested on v22.22.2)
- **OS:** Linux, macOS, or Windows WSL

### 6.2 Python Virtual Environment Setup

```bash
# Clone the repository
git clone https://github.com/hariprasadkishan/CloudRescue-Research.git
cd CloudRescue-Research

# Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install verified Python dependencies
pip install -r requirements.txt
```

### 6.3 Run Automated Test Harness

```bash
# Execute the complete 56-test suite
pytest tests/ -v
```
*Expected: 56 passed in ~1.8 seconds.*

---

## 7. Running the System

### 7.1 FastAPI Backend Server
The read-only backend serves verified experimental data, statistical tests, and publication plots:

```bash
# Start backend on http://127.0.0.1:8000
uvicorn server.main:app --port 8000 --reload
```
- API Documentation (Swagger): `http://127.0.0.1:8000/docs`
- Summary Endpoint: `http://127.0.0.1:8000/api/summary`

### 7.2 React Frontend Research Dashboard
The dashboard provides an interactive editorial monograph across 7 research screens:

```bash
# In a new terminal:
cd frontend
npm install
npm run dev
```
- Open `http://localhost:5173` in your browser.
- Vite automatically proxies `/api` calls to `http://127.0.0.1:8000`.

### 7.3 Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 8. Reproducing Experiments & Statistical Analysis

To reproduce the validation runs, statistical evaluations, and plots:

```bash
# 1. Run single-seed preliminary validation runs (saved to results/validation_run_*/)
python scripts/run_baseline.py --sim-time-s 20.0
python scripts/run_brownout.py --sim-time-s 20.0
python scripts/run_balb.py --sim-time-s 20.0

# 2. Re-run paired statistical tests on the master 360-run dataset
python scripts/analyze_results.py \
  --master-csv results/experiment_360/master_results.csv \
  --output-dir results/experiment_360

# 3. Regenerate publication-quality figures
python scripts/generate_plots.py --results-dir results/experiment_360
```

> [!CAUTION]
> The full 360-run primary evaluation (`scripts/run_experiment_matrix.py`) and 144-run sensitivity sweep (`scripts/run_sensitivity.py`) require approximately 3.3 GB of disk space and substantial compute time across 7 parallel cores. The authoritative datasets are already computed, certified, and frozen in [`results/experiment_360/`](results/experiment_360/).

---

## 9. Repository Structure

```
CloudRescue-Research/
├── CloudRescue_Project_Docs/      # Formal research requirements, PRD, architecture, and ADRs
│   ├── ARCHITECTURE.md            # Detailed simulator architecture & mathematical derivations
│   ├── DECISIONS.md               # ADRs logging decisions DEC-001 through DEC-010
│   └── PRD.md                     # Product requirements & 10 standardized resilience metrics
├── frontend/                      # React 19 + Vite + Tailwind research dashboard
│   ├── src/screens/               # 7 editorial screens (Overview, Benchmark, Analytics, etc.)
│   └── vite.config.js             # Dev server & backend proxy configuration
├── paper/                         # Formal academic research manuscript & audits
│   ├── CloudRescue_Research_Paper_Draft.md  # Complete 10-section paper draft
│   ├── SECTION_8_AUDIT_REPORT.md  # Data audit verifying all 770 numerical cells
│   ├── FINAL_ACADEMIC_REVIEW.md   # 10-criterion academic quality audit
│   └── REFERENCES_TO_VERIFY.md    # 17/17 verified IEEE citations
├── results/                       # Certified experimental outputs
│   └── experiment_360/            # Primary evaluation (360 runs, 30 matched seeds)
│       ├── master_results.csv     # Master results table (360 rows × 28 metrics)
│       ├── aggregated_metrics.csv # Summary metrics by scenario and configuration
│       ├── statistical_comparisons.csv # Paired hypothesis test battery
│       ├── plots/                 # 6 publication-ready figures (300 DPI)
│       ├── sensitivity/           # 144-run BALB weight grid sweeps
│       └── runs/                  # Per-run traces, configs, and controller timeseries
├── scripts/                       # Simulation runners, statistical testing, and plotting CLIs
├── server/                        # FastAPI REST API serving research artifacts
├── simulator/cloudrescue/         # Discrete-event simulation package
│   ├── balancing/                 # JSQ and BALB routing implementations
│   ├── control/                   # Velocity PI feedback controller with anti-windup
│   ├── engine/                    # SimPy simulation coordinator
│   ├── models/                    # Worker, Queue, and Request domain models
│   ├── monitoring/                # Event logger and nominal-referenced recovery analyzer
│   └── workload/                  # 5-stream isolated Poisson arrival generator
├── tests/                         # 56 automated unit and regression tests
├── FINAL_FREEZE_SIGNOFF.md        # Formal research freeze certificate
├── FINAL_REPRODUCIBILITY_AUDIT.md # Comprehensive independent reproducibility audit report
├── pytest.ini                     # Pytest runner configuration
├── requirements.txt               # Pinned Python dependencies
└── README.md                      # This project overview & reproduction guide
```

---

## 10. Research Team & Academic Attribution

This research was conducted at the Department of Computer Science and Engineering, Indian Institute of Information Technology Dharwad (IIIT Dharwad).

- **Hari Prasad L** ([@hariprasadkishan](https://github.com/hariprasadkishan)) — Project Architecture, Simulator Engineering, Controller & BALB Implementation
- **Yeruva Mahesh Reddy** — Experimental Design, Sensitivity Analysis, Statistical Battery
- **K. Ram Charan** — Data Reconciliation, Dashboard Frontend, Publication Visualizations
- **Tushar** — Research Team Member

**Academic Context:** B.Tech Research Project, Indian Institute of Information Technology Dharwad.  
**Foundational Literature:** Based on resilience survey and brownout paradigms by Welsh & Benkhelifa (*ACM Computing Surveys 2020*) and Klein et al. (*IEEE SRDS 2014*, *ICSE 2014*).

---

## 11. Citation

If you find this research, simulator, or experimental dataset useful, please cite:

```bibtex
@article{cloudrescue2026,
  title={{Autonomic Cloud Resilience Through Brownout-Based Graceful Degradation: A Simulation-Based Evaluation of Brownout-Aware Load Balancing}},
  author={Hari Prasad L and Yeruva Mahesh Reddy and K. Ram Charan and Tushar},
  journal={Department of Computer Science and Engineering, IIIT Dharwad, Working Paper},
  year={2026},
  month={November},
  url={https://github.com/hariprasadkishan/CloudRescue-Research}
}
```

