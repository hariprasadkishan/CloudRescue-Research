# CloudRescue — Final Reproducibility & Deployment Audit Report

**Date:** November 10, 2026  
**Auditor:** Independent Academic Audit & Reproducibility Agent  
**Repository:** [https://github.com/hariprasadkishan/CloudRescue-Research](https://github.com/hariprasadkishan/CloudRescue-Research)  
**Project Root:** `/home/andesindica/Downloads/CloudRescue-Research`  
**Git Commit Audited:** `c60fb2b651f7ba0aaa8f3ca24708230fa10b5130` (Initial publication commit)  
**Target Environment:** Linux x86_64, Python 3.10–3.14, Node.js 18+  

---

## 1. Executive Summary & Audit Scorecard

This audit independently inspects and empirically tests the reproducibility, environment isolation, testing harness, backend services, frontend dashboard, CLI reproduction pipelines, and research documentation of the CloudRescue research project.

### Audit Verdict Summary
- **Total Audit Items:** 14
- **PASS:** 9 items (64.3%)
- **WARNING:** 3 items (21.4%)
- **FAIL:** 2 items (14.3%)

| Audit Dimension | Target / Subsystem | Status | Key Finding |
| :--- | :--- | :---: | :--- |
| **1. Repository Documentation** | Root Repository README | **FAIL** | No `README.md` exists at the repository root. GitHub landing page shows *"This repository does not have a README"*. |
| **2. Dependency Specification** | Python `requirements.txt` | **FAIL** | No `requirements.txt`, `pyproject.toml`, or `setup.py` exists anywhere in the repository. |
| **3. Fresh Environment Install** | Clean Virtualenv Installation | **PASS** | Dependencies (`simpy`, `numpy`, `scipy`, `pandas`, `matplotlib`, `fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`) resolve and install cleanly in an isolated venv. |
| **4. Automated Test Suite** | 56 Unit & Integration Tests | **PASS** | **56 / 56 tests passed** (100% pass rate in 1.72s) on a completely clean Python environment. |
| **5. Backend Service Startup** | FastAPI / Uvicorn REST API | **PASS** | `server.main:app` starts cleanly on port 8000/8888. All 11 registered API routes return HTTP 200 with valid JSON/PNG payloads. |
| **6. Frontend Build & Install** | Vite + React + Tailwind v4 | **PASS** | `npm install --dry-run` and `npm run build` succeed in 724ms. `dist/` bundle generated cleanly. |
| **7. Frontend Code Quality** | Oxlint Linter | **WARNING** | Oxlint reports 25 non-fatal warnings (unused imports/variables in screens 2, 3, 5, 6, 7). Zero compilation errors. |
| **8. Experimental Reproducibility** | Paired Statistical Tests | **PASS** | `scripts/analyze_results.py` executed against `master_results.csv` produces a byte-for-byte identical `statistical_comparisons.csv`. |
| **9. Validation CLI Scripts** | Baseline, Brownout, BALB CLIs | **PASS** | `run_baseline.py`, `run_brownout.py`, and `run_balb.py` execute successfully and generate complete validation artifacts. |
| **10. Script CLI Safety** | Auxiliary Script Invocation | **WARNING** | `scripts/reconcile_recovery_metrics.py` lacks CLI arguments and overwrites frozen CSVs in place if executed directly without flags. |
| **11. Research Artifacts** | Frozen Results & Tables | **PASS** | All 1,092 run traces, `master_results.csv`, `aggregated_metrics.csv`, and signoffs are 100% intact and uncorrupted. |
| **12. Publication Plots** | 6 Vector/Raster Figures | **PASS** | All 6 publication-ready figures exist at 300 DPI in `results/experiment_360/plots/`. |
| **13. Research Manuscript** | Complete Paper Draft | **PASS** | 995-line draft with Sections 1–10, 17/17 verified IEEE references, and 0 data cell discrepancies. |
| **14. Architecture Docs Sync** | `ARCHITECTURE.md` Directory Tree | **WARNING** | `ARCHITECTURE.md` Section 4 contains early pre-implementation package layout (`cloud_model/`, `failures/`) rather than implemented layout (`models/`, `control/`, `engine/`). |

---

## 2. Detailed Findings by Task

### Task 1: Repository Structure & Root README Inspection
- **Status:** **FAIL**
- **Empirical Evidence:**
  Executing `ls -la /home/andesindica/Downloads/CloudRescue-Research` confirms the absence of `README.md`.
  While subordinate READMEs exist in `CloudRescue_Project_Docs/README.md`, `results/experiment_360/README.md`, and `frontend/README.md`, GitHub displays a blank repository landing page without a project overview, quick-start guide, citation notice, or architecture summary.
- **Reproducibility Impact:** Critical onboarding barrier. Outside researchers cloning the repository cannot immediately discern how to configure the environment, run the simulator, start the dashboard, or cite the work.

---

### Task 2 & 3: Python Dependencies & Clean Environment Installation
- **Status:** **FAIL** (Missing specification file) / **PASS** (Package resolution feasibility)
- **Empirical Evidence:**
  1. **Missing Files:** Neither `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`, nor `setup.cfg` exists in the repository.
  2. **Clean Virtualenv Test:** Created an isolated virtual environment at `/tmp/test_cloudrescue_clean_env` (isolated from system site-packages). Installed the deduced core dependencies:
     ```bash
     pip install "simpy>=4.1.0" "numpy>=2.0.0" "scipy>=1.15.0" "pandas>=2.2.0" \
                 "matplotlib>=3.9.0" "fastapi>=0.115.0" "uvicorn>=0.30.0" \
                 "pydantic>=2.8.0" "pytest>=8.0.0" "httpx>=0.27.0"
     ```
  3. **Result:** Pip successfully resolved and installed all packages and their wheels without compilation errors or dependency conflicts.
- **Identified Core Dependency Matrix:**
  | Package | Minimum Compatible | Certified Local Version | Role in CloudRescue |
  | :--- | :---: | :---: | :--- |
  | `simpy` | `>=4.1.0` | `4.1.2` | Core discrete-event simulation engine |
  | `numpy` | `>=2.0.0` | `2.4.6` | PRNG streams (`SeedSequence`), numerical vectors |
  | `scipy` | `>=1.15.0` | `1.18.1` | Paired Student's t-test, Wilcoxon signed-rank, Shapiro-Wilk |
  | `pandas` | `>=2.2.0` | `3.1.0` | Telemetry logs, `master_results.csv`, data aggregation |
  | `matplotlib` | `>=3.9.0` | `3.11.2` | Publication figure generation (300 DPI, colorblind-safe) |
  | `fastapi` | `>=0.115.0` | `0.162.0` | Read-only REST API backend for research dashboard |
  | `uvicorn` | `>=0.30.0` | `0.54.0` | Production ASGI web server |
  | `pydantic` | `>=2.8.0` | `2.14.2` | Configuration schema modeling and validation |
  | `pytest` | `>=8.0.0` | `9.2.0` | Automated test suite execution |
  | `httpx` | `>=0.27.0` | `0.28.1` | HTTP client / FastAPI TestClient backend testing |

---

### Task 4: Automated Test Suite Verification (56 Tests)
- **Status:** **PASS**
- **Empirical Evidence:**
  Executed `.venv/bin/pytest tests/ -v` and repeated on `/tmp/test_cloudrescue_clean_env`:
  - **Total Tests Collected:** 56
  - **Passed:** 56 (100.0%)
  - **Failed / Errored:** 0
  - **Execution Duration:** 1.72s to 2.24s
- **Module Test Coverage Breakdown:**
  - `tests/test_brownout_aware.py`: 12 tests (BALB multi-attribute scoring, queue/utilization penalties, crashed worker exclusion, soft-overload fallback, deterministic tie-breaking, configuration validation).
  - `tests/test_brownout_controller.py`: 12 tests (PI feedback error response, output clamping bounds $[0, 1]$, anti-windup, derivative kick prevention, insufficient sample holding, stalled queue safety decrement, worker crash reset).
  - `tests/test_experiment_matrix.py`: 3 tests (paired analysis logic, normal vs. non-normal difference handling).
  - `tests/test_fairness_metric.py`: 5 tests (Jain's index excluding warm-up, active zero-downtime worker evaluation pool per DEC-008, all-crash fallback).
  - `tests/test_recovery_analyzer.py`: 5 tests (nominal referenced recovery detection per DEC-010, right-censoring handling).
  - `tests/test_request.py`: 4 tests (request initialization, completion latency, timeout drop status).
  - `tests/test_shortest_queue.py`: 3 tests (Join-Shortest-Queue routing, crashed worker exclusion).
  - `tests/test_simulation.py`: 4 tests (full lifecycle, failure scheduling, Common Random Numbers seed determinism).
  - `tests/test_worker.py`: 5 tests (queue capacity, buffer rejection, dual-stage execution lifecycle, head-of-line timeout drop, crash/recovery).
  - `tests/test_workload.py`: 3 tests (5-stream PRNG isolation, burst rate transitions).

---

### Task 5: FastAPI Backend Verification
- **Status:** **PASS**
- **Empirical Evidence:**
  1. Tested endpoints directly using `fastapi.testclient.TestClient(app)`:
     - `/docs`: HTTP 200 (Interactive OpenAPI / Swagger UI).
     - `/api/summary`: HTTP 200 (Experiment status, 360 primary runs, 144 sensitivity runs).
     - `/api/scenarios`: HTTP 200 (Compound stress, flash crowd, nominal, server failure).
     - `/api/benchmarks`: HTTP 200 (Grouped SLA violations, response times, fairness).
     - `/api/analytics`: HTTP 200 (Detailed statistical distributions).
     - `/api/recovery`: HTTP 200 (Adaptation and nominal post-restoration recovery times).
     - `/api/sensitivity`: HTTP 200 (144-run parameter weight grid sweep).
     - `/api/statistics`: HTTP 200 (Paired t-test, Wilcoxon, Cohen's $d$, 95% CIs).
     - `/api/publication`: HTTP 200 (Paper metadata, hypothesis evaluation).
     - `/api/plots/sla_violation_rates_bar.png`: HTTP 200 (Binary image stream, 216 KB).
     - `/api/timeseries/compound_stress/CFG-C/1001`: HTTP 200 (Per-second telemetry stream).
  2. Tested live daemon startup using `uvicorn server.main:app --port 8888`. Verified HTTP connectivity via `curl http://127.0.0.1:8888/api/summary`.

---

### Task 6: React Frontend Build & Dependencies
- **Status:** **PASS** (Build & dependencies) / **WARNING** (Linter warnings)
- **Empirical Evidence:**
  1. `cd frontend && npm install --dry-run`: Succeeded cleanly against committed `package-lock.json`.
  2. `cd frontend && npm run build`: Vite v8.3.5 built production client bundle in 724ms:
     - `dist/index.html` (0.95 kB)
     - `dist/assets/index-D119qVYT.css` (34.90 kB)
     - `dist/assets/index-DHCT3pKa.js` (718.32 kB)
  3. `cd frontend && npm run lint`: Oxlint scanned 13 files and reported 25 warnings (0 errors).
     - Warnings relate entirely to unused variables and imports in `Screen2Inquiry.jsx`, `Screen3Simulator.jsx`, `Screen5Analytics.jsx`, `Screen6Methodology.jsx`, and `Screen7Publication.jsx`.
  4. Proxy configuration in `frontend/vite.config.js`:
     ```javascript
     proxy: {
       '/api': {
         target: 'http://127.0.0.1:8000',
         changeOrigin: true,
       }
     }
     ```
     Correctly routes frontend API queries to the local FastAPI backend.

---

### Task 7: Documented Commands & Reproduction Paths
- **Status:** **PASS** (Core pipelines) / **WARNING** (Auxiliary script defaults)
- **Empirical Evidence:**
  1. **Primary CLI Scripts:**
     - `scripts/run_baseline.py --help`: Verified valid argparse CLI.
     - `scripts/run_brownout.py --help`: Verified valid argparse CLI.
     - `scripts/run_balb.py --help`: Verified valid argparse CLI.
     - `scripts/run_experiment_matrix.py --help`: Verified valid argparse CLI.
     - `scripts/analyze_results.py --help`: Verified valid argparse CLI.
     - `scripts/run_sensitivity.py --help`: Verified valid argparse CLI.
     - `scripts/generate_plots.py --help`: Verified valid argparse CLI.
  2. **Empirical Execution Test:**
     - Ran short baseline, brownout, and BALB validation runs (`sim_time=2.0s`) to `/tmp/test_val_*`. All executed without runtime exceptions and wrote valid JSON and CSV outputs.
     - Ran `scripts/analyze_results.py` against `results/experiment_360/master_results.csv` outputting to `/tmp/test_analysis`. Generated statistical comparisons matched certified repository outputs with **zero diff**.
  3. **Script Safety Warning:**
     - `scripts/reconcile_recovery_metrics.py` has no `--help` flag and hardcodes default paths directly targeting `results/experiment_360/`. Running it inadvertently executes a full recovery recalculation and overwrites `master_results.csv`.
     - `scripts/compare_ablation.py` runs immediately on execution without CLI argument handling.

---

### Task 8: Accessibility of Experiment Results, Plots, and Paper
- **Status:** **PASS**
- **Empirical Evidence:**
  All key files exist on disk, are tracked in Git, and are readable:
  - `paper/CloudRescue_Research_Paper_Draft.md`: 141 KB (995 lines, complete Sections 1–10).
  - `paper/SECTION_8_AUDIT_REPORT.md`: 21 KB (770 verified data points).
  - `paper/FINAL_ACADEMIC_REVIEW.md`: 16 KB (10-criterion academic audit).
  - `paper/REFERENCES_TO_VERIFY.md`: 12 KB (17 verified IEEE citations).
  - `FINAL_FREEZE_SIGNOFF.md`: 8 KB (Formal signoff).
  - `results/experiment_360/master_results.csv`: 66 KB (360 rows $\times$ 28 metrics).
  - `results/experiment_360/aggregated_metrics.csv`: 11 KB (12 condition summaries).
  - `results/experiment_360/statistical_comparisons.csv`: 36 KB (Paired hypotheses).
  - `results/experiment_360/plots/*.png`: 6 figures totaling 2.1 MB.
  - `results/experiment_360/runs/`: 1,092 individual per-seed run artifacts.

---

### Task 9: Missing Files, Broken Paths, and Prerequisites
- **Status:** Summarized in the gap matrix below.

| Identified Item | Category | Severity | Description |
| :--- | :--- | :---: | :--- |
| **Root `README.md`** | Documentation | **HIGH** | Missing from repository root. GitHub displays no project overview. |
| **`requirements.txt`** | Dependency | **HIGH** | Missing from repository root. Fresh clones cannot install with `pip install -r requirements.txt`. |
| **`frontend/README.md`** | Documentation | **LOW** | Contains Vite starter boilerplate rather than instructions for running the dashboard. |
| **`ARCHITECTURE.md` Structure** | Documentation | **MEDIUM** | Section 4 directory tree lists initial design layout (`cloud_model/`, `failures/`) rather than the actual implemented modules (`models/`, `control/`, `engine/`). |
| **Auxiliary Script Safety** | Code / CLI | **MEDIUM** | `scripts/reconcile_recovery_metrics.py` lacks `--help` and defaults to overwriting `results/experiment_360/` if invoked without parameters. |
| **Frontend Linter Warnings** | Code Quality | **LOW** | 25 unused variables/imports in frontend JSX files trigger Oxlint warnings. |

---

## 3. Prioritized List of Corrections

In accordance with strict audit constraints, **no files have been modified**. The following prioritized corrections are recommended for user approval:

### Priority 0 (Critical — Immediate Fix Required for Public Usability)

1. **Create Root `README.md` (`/README.md`):**
   - Provide a comprehensive, professional research overview.
   - Include project title, author affiliation (IIIT Dharwad), and abstract summary.
   - Document prerequisites: Python 3.10+, Node.js 18+.
   - Add clear Quick-Start commands:
     - Setting up the Python virtual environment and installing dependencies.
     - Running the 56 unit tests (`pytest tests/`).
     - Launching the FastAPI backend (`uvicorn server.main:app --port 8000`).
     - Launching the React dashboard (`cd frontend && npm install && npm run dev`).
   - Document the experimental reproduction pipeline (`scripts/run_experiment_matrix.py`, `scripts/analyze_results.py`, `scripts/generate_plots.py`).
   - Link to `paper/CloudRescue_Research_Paper_Draft.md` and `CloudRescue_Project_Docs/`.

2. **Create Standard `requirements.txt` (`/requirements.txt`):**
   - Provide pinned or bounded dependencies matching the verified environment:
     ```text
     simpy>=4.1.0,<5.0.0
     numpy>=2.0.0,<3.0.0
     scipy>=1.15.0,<2.0.0
     pandas>=2.2.0,<4.0.0
     matplotlib>=3.9.0,<4.0.0
     fastapi>=0.115.0,<1.0.0
     uvicorn[standard]>=0.30.0,<1.0.0
     pydantic>=2.8.0,<3.0.0
     pytest>=8.0.0,<10.0.0
     httpx>=0.27.0,<1.0.0
     ```

### Priority 1 (Medium — Documentation Accuracy & Script Safety)

3. **Synchronize `CloudRescue_Project_Docs/ARCHITECTURE.md`:**
   - Update Section 4 directory layout diagram to reflect the actual implemented layout (`simulator/cloudrescue/models/`, `control/`, `balancing/`, `engine/`, `monitoring/`, `workload/`).
   - Add a historical note indicating that the original RFC structure was modularized during implementation.

4. **Add Safety Guards to `scripts/reconcile_recovery_metrics.py`:**
   - Add standard `argparse` with `--results-dir` (defaulting to a required flag or explicit `--dry-run` confirmation) to prevent accidental in-place overwriting of frozen research datasets.

5. **Update `frontend/README.md`:**
   - Replace standard Vite template text with dedicated dashboard instructions (how to run dev server, build production assets, and configure API proxy).

### Priority 2 (Low — Polish & Code Cleanliness)

6. **Clean Up Frontend Oxlint Warnings:**
   - Remove unused variable declarations (`loading`, `pubData`, `copiedManifest`, etc.) and unused icon imports (`Download`, `Info`, `Activity`, etc.) across `frontend/src/screens/` to achieve 0 linter warnings.

