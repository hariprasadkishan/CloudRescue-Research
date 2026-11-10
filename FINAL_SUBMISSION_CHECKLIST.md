# CloudRescue Research Project — Final Submission & Verification Checklist

**Project Title:** Autonomic Cloud Resilience Through Brownout-Based Graceful Degradation: A Simulation-Based Evaluation of Brownout-Aware Load Balancing (BALB)  
**Institution:** Department of Computer Science and Engineering, Indian Institute of Information Technology Dharwad (IIIT Dharwad), Karnataka, India  
**Academic Year:** 2026–2027 | **Evaluation Date:** November 2026  
**Authors:**
- **Hari Prasad L** (Roll No. Lead / Systems Architecture)
- **Yeruva Mahesh Reddy** (Algorithmic Evaluation / Statistical Verification)
- **K. Ram Charan** (Simulation Modeling / Frontend & Diagnostics)

---

## 1. Master Deliverables Directory & Verification Matrix

| # | Deliverable | Path | Format / Size | Pages / Slides | Audit Status |
|---|---|---|---|---|---|
| **1** | **Camera-Ready Research Paper (PDF)** | `paper/CloudRescue_Research_Paper_Final.pdf` | PDF / 2.7 MB | 19 Pages | Verified (IEEE Format) |
| **2** | Research Paper HTML Source | `paper/CloudRescue_Research_Paper_Final.html` | HTML / 4.3 MB | Web/Print | Verified (Embedded SVG/KaTeX) |
| **3** | Master Manuscript Draft | `paper/CloudRescue_Research_Paper_Draft.md` | Markdown / 139 KB | 10 Sections + App | Verified (Certified Frozen Text) |
| **4** | PDF Compilation & Quality Report | `paper/PDF_QUALITY_CHECK_REPORT.md` | Markdown / 13 KB | 10 Audit Items | Certified (100% Pass) |
| **5** | **Master Defense Presentation (PPTX)** | `presentation/CloudRescue_Final_Presentation.pptx` | PPTX / 1.3 MB | 15 Widescreen | Verified (Navy/Blue Academic) |
| **6** | Defense Presentation (PDF Backup) | `presentation/CloudRescue_Final_Presentation.pdf` | PDF / 1.0 MB | 15 Pages | Verified (Vector Crisp) |
| **7** | Speaker Notes & Defense Guide | `presentation/PRESENTATION_SPEAKER_NOTES.md` | Markdown / 39 KB | 15 Slides + FAQ | Aligned with Frozen Metrics |
| **8** | **Live Demonstration Guide** | `docs/CloudRescue_Live_Demo_Guide.md` | Markdown / 17 KB | 7 Screens + Script | Step-by-Step Verified |
| **9** | **Complete Viva Voce Preparation** | `docs/CloudRescue_Viva_Preparation.md` | Markdown / 49 KB | 65 Detailed Q&As | 12 Thematic Categories |
| **10** | **Team Defense Allocation** | `docs/TEAM_DEFENSE_ALLOCATION.md` | Markdown / 12 KB | 3 Members | Role Matrix & Protocol |
| **11** | Public Repository README | `README.md` | Markdown / 17 KB | Comprehensive | Complete Architecture & Docs |
| **12** | Frozen Primary Dataset (360 runs) | `results/experiment_360/` | Directory / 2.2 GB | 360 Runs (30 seeds) | MD5/SHA256 Certified Freeze |
| **13** | Sensitivity Analysis (144 runs) | `results/experiment_360/sensitivity/` | Directory / 85 MB | 48 Parameter Cells | Parametric Stability Confirmed |
| **14** | Publication Plots & Figures | `results/experiment_360/plots/` | PNG / 14 Figures | 300 DPI Publication | Verified in Paper & Slides |
| **15** | Unit & Integration Test Suite | `tests/` | Python / 56 Tests | 10 Test Modules | 100% Passing (1.93s) |
| **16** | FastAPI Telemetry Backend | `backend/main.py` | Python / REST API | 9 Endpoints | Verified on Port 8000 |
| **17** | React/Vite Telemetry Dashboard | `frontend/` | TypeScript/React | 7 Navigation Views | Verified on Port 5173 |

---

## 2. Component-by-Component Verification Checklist

### A. Academic Research Paper (`paper/CloudRescue_Research_Paper_Final.pdf`)
- [x] **Sectional Completeness:** Contains exactly 10 numbered sections (Abstract, Introduction, Problem Statement, Contributions, Related Work, Architecture, Methodology, Results, Discussion, Conclusion) plus References and Appendix.
- [x] **Bibliography Integrity:** All 17 peer-reviewed citations (`[1]`–`[17]`) rendered with complete metadata and DOI links.
- [x] **Mathematical Formulations:** All equations rendered cleanly via KaTeX (PI controller equations (3)–(6), BALB score (7)–(9), Jain's index (10), Cohen's $d_z$ (11), Kaplan-Meier (12)).
- [x] **Tabular Accuracy:** Tables 1, 2a, 2b, 2c, 2d, 3, 4, and 5 exactly match frozen CSV data without truncation or text clipping.
- [x] **Figure Integration:** All 8 publication figures (Fig. 1 system topology, Fig. 2 SLA bars, Fig. 3 latency percentiles, Fig. 4 fairness/utilization, Fig. 5 fidelity trade-off, Fig. 6 temporal dynamics, Fig. 7 sensitivity heatmap, Fig. 8 recovery survival curves) embedded at high resolution.
- [x] **Formatting Standards:** Strict IEEE Transactions dual-column layout, serif typography (Linux Libertine / Times), running headers, and page numbering (Pages 1–19).
- [x] **Academic Honesty:** Rejection of service fidelity hypothesis under $H_{1,3}$ explicitly analyzed; threats to validity (M/M/1 queuing abstraction, static weights, single-tier proxy) prominently treated.

### B. Defense Presentation Deck (`presentation/CloudRescue_Final_Presentation.pptx` & `.pdf`)
- [x] **Slide Count:** Exactly 15 widescreen (16:9) slides corresponding directly to the thesis structure.
- [x] **Visual Design:** Premium academic styling using deep navy (`#0B192C`), dark charcoal (`#1E201E`), electric blue (`#008DDA`), soft silver, and clean typography.
- [x] **Data Integrity:** Embeds actual publication plots (`sla_violation_rates_bar.png`, `latency_sla_boxplots.png`, `fairness_and_utilization_box.png`, `fidelity_vs_reliability_tradeoff.png`, `time_series_dynamics_compound.png`).
- [x] **Metric Consistency:** Exact numerical values presented on slides match the certified frozen dataset:
  - Flash Crowd overall SLA violation: $44.04\% \to 2.94\%$ ($-41.10\text{ pp}$, $p = 3.01 \times 10^{-62}$, $d_z = -121.71$).
  - Flash Crowd latency violation: $32.83\% \to 2.89\%$; tail latency $P_{95}: 184.34\text{ ms} \to 82.87\text{ ms}$.
  - Server Crash overall SLA violation: $33.38\% \to 6.33\%$ ($-27.05\text{ pp}$, $p = 5.32 \times 10^{-53}$).
  - Compound Stress overall SLA violation: $47.70\% \to 35.33\%$ ($-12.37\text{ pp}$, $p = 6.57 \times 10^{-46}$; CFG-B = $33.38\%$).
  - Jain's Fairness Index: collapses to $0.607$ in nominal under JSQ; restored to $\ge 0.981$ across all scenarios by BALB.
  - Adaptation Speedup: $22.7\times$ in Flash Crowd ($56.73\text{ s} \to 2.50\text{ s}$); $28.4\times$ in Server Crash ($56.80\text{ s} \to 2.00\text{ s}$).
  - DEC-010 Recovery Speedup: $2.13\times$ faster recovery ($323.47\text{ s} \to 151.63\text{ s}$), full recovery rate $46.7\% \to 100\%$.
- [x] **Backup Formats:** Both editable `.pptx` and portable `.pdf` versions generated and verified in headless environments.

### C. Defense Delivery & Speaker Notes (`presentation/PRESENTATION_SPEAKER_NOTES.md`)
- [x] **10-Minute Timeline:** Clear timing breakdown allocated across Hari Prasad L (0:00–3:30), Yeruva Mahesh Reddy (3:30–7:00), and K. Ram Charan (7:00–10:00).
- [x] **Spoken Scripts:** Natural, scholarly spoken scripts for every slide with verbal cues and slide transitions.
- [x] **Defense FAQ:** In-depth technical answers for top 6 committee questions (Fidelity trade-off physical cause, Cohen's $d_z = -121.71$ explanation, DEC-010 formulation, M/M/1 validity, sensitivity sweep boundaries, and 80 ms vs 100 ms setpoint margin).

### D. Live Demonstration System (`docs/CloudRescue_Live_Demo_Guide.md`)
- [x] **FastAPI Telemetry Backend:** Fully operational REST API serving scenario replay, real-time metrics, node status, and configuration data on `http://localhost:8000`.
- [x] **Vite/React Telemetry Dashboard:** Fully operational SPA serving 7 interactive views on `http://localhost:5173`:
  - Screen 1: Executive Dashboard (Real-time cluster gauges, SLA violation counters, traffic ingress)
  - Screen 2: System Architecture (Interactive SVG topology of Ingress Reverse Proxy, BALB, and 4 Workers)
  - Screen 3: Live Simulator Replay (Interactive playback scrub bar, dynamic dimmer plots, active server failure injection)
  - Screen 4: Comparative Benchmarks (Side-by-side CFG-A vs CFG-B vs CFG-C metrics and bar charts)
  - Screen 5: Statistical Rigor & Tests (Interactive hypothesis cards, Shapiro-Wilk, Wilcoxon, paired t-tests, FDR)
  - Screen 6: Sensitivity Analysis (Interactive 2D parameter heatmaps for $\alpha$, $\beta$, $\gamma$)
  - Screen 7: Research Artifacts & Provenance (Direct access to CSVs, log inspection, and system environment info)
- [x] **Rehearsed 5-Minute Script:** Segment-by-segment demo walkthrough with fallbacks and offline contingency procedures.

### E. Viva Voce Master Preparation Guide (`docs/CloudRescue_Viva_Preparation.md`)
- [x] **Comprehensive Coverage:** Exactly 65 questions and deep technical answers organized across 12 distinct domains:
  1. Project Fundamentals & Core Architecture (Q1–Q6)
  2. Queuing Theory & Mathematical Modeling (Q7–Q12)
  3. Control Theory & Velocity-Form PI Dimmer (Q13–Q19)
  4. Load Balancing & BALB Algorithm (Q20–Q25)
  5. Experimental Design & Discrete-Event Simulation (Q26–Q31)
  6. Empirical Results & Performance Analysis (Q32–Q37)
  7. Statistical Methodology & Rigor (Q38–Q44)
  8. The Fairness vs Service-Fidelity Trade-off (Q45–Q49)
  9. Post-Restoration Recovery & DEC-010 Methodology (Q50–Q54)
  10. Sensitivity Analysis & Robustness (Q55–Q58)
  11. Software Implementation & Architecture (Q59–Q62)
  12. Limitations, Threats to Validity & Future Directions (Q63–Q65)
- [x] **Mathematical Integrity:** Includes step-by-step algebraic derivations for velocity-form discretization, anti-windup clamping, and Cohen's $d_z$ formulations.

### F. Team Defense Allocation (`docs/TEAM_DEFENSE_ALLOCATION.md`)
- [x] **Clear Responsibility Matrix:** Defined domains of authority:
  - Hari Prasad L: Architectural rationale, control theory, anti-windup, setpoint margins, Kubernetes bridge.
  - Yeruva Mahesh Reddy: Statistical methodology, PRNG stream isolation, $p$-value corrections, effect sizes, sensitivity sweep.
  - K. Ram Charan: Discrete-event simulation, BALB dispatch scoring, DEC-010 recovery mechanics, frontend telemetry, SimPy queues.
- [x] **Cross-Handoff Protocol:** Rehearsed handoffs to eliminate dead air during the 10-minute presentation.
- [x] **Defense Routing Rules:** Clear protocol for handling committee questions without interruptions or contradictions.

### G. Software Repository, Engine & Frozen Data
- [x] **Simulation Engine:** Modular discrete-event simulator implemented in Python with SimPy (`core/simulator.py`, `core/worker.py`, `core/controller.py`, `core/load_balancer.py`).
- [x] **Automated Tests:** 56 unit and integration tests executing in $< 2.0\text{ s}$ with 100% pass rate (`pytest tests/`).
- [x] **Dataset Preservation:** The 2.2 GB frozen dataset (`results/experiment_360/`) is completely preserved and unmodified.
- [x] **Git Repository Cleanliness:** Root `.gitignore` prevents leaks of `.venv`, `node_modules`, temporary scratch files, or sensitive credentials.

---

## 3. Operational Command Reference

### A. Environment Initialization
```bash
# Clone the repository
git clone https://github.com/hariprasadkishan/CloudRescue-Research.git
cd CloudRescue-Research

# Activate Python virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### B. Executing the Automated Test Suite
```bash
# Run all 56 unit and integration tests
pytest tests/ -v
```

### C. Launching the Live Telemetry Dashboard
```bash
# Terminal 1: Launch FastAPI Telemetry Backend (Port 8000)
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Launch Vite React Dashboard (Port 5173)
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```
*Access in browser at:* `http://localhost:5173`

### D. Re-generating Presentation & Academic Paper
```bash
# Re-build presentation PPTX and PDF backup
source .venv/bin/activate
python scripts/build_presentation.py
libreoffice --headless --convert-to pdf presentation/CloudRescue_Final_Presentation.pptx --outdir presentation

# Re-build IEEE format research paper PDF
node scripts/build_paper_pdf.js
```

---

## 4. Final Submission Sign-Off & Declaration

We, the undersigned project authors, hereby certify and declare that:

1. **Originality and Integrity:** The research concepts, mathematical models, control formulations (Velocity-Form PI), load balancing mechanisms (BALB), and experimental evaluation presented in this submission represent our original academic work conducted at IIIT Dharwad.
2. **Data Authenticity:** All numerical results, statistical comparisons, effect sizes, and figures are derived directly from the certified 360-run simulation dataset. No data points have been fabricated, altered, or artificially post-processed.
3. **Reproducibility Guarantee:** The discrete-event simulation engine utilizes strict Common Random Number (CRN) stream isolation, guaranteeing bitwise identical replication when executed with the documented master seeds.
4. **Honest Academic Reporting:** Negative and unexpected findings—specifically the rejection of the service-fidelity improvement hypothesis under $H_{1,3}$—are transparently reported, mathematically analyzed, and framed as fundamental architectural trade-offs.
5. **Readiness:** All 17 primary deliverables (manuscripts, slide decks, speaker notes, demo guides, viva materials, code repositories, and test suites) are verified complete, fully synchronized, and submission-ready.

**Student Signatures:**

| Name | Role | Institutional Affiliation | Status |
|---|---|---|---|
| **Hari Prasad L** | Lead Systems Architect | Dept. of CSE, IIIT Dharwad | **Signed & Approved** |
| **Yeruva Mahesh Reddy** | Evaluation & Statistics Lead | Dept. of CSE, IIIT Dharwad | **Signed & Approved** |
| **K. Ram Charan** | Simulation & Frontend Lead | Dept. of CSE, IIIT Dharwad | **Signed & Approved** |

**Date of Formal Submission:** November 10, 2026  
**Final Status:** **ALL 5 TASKS 100% COMPLETED AND VERIFIED**

