# CloudRescue Research Paper — Final PDF Quality Check Report

**Generated File:** `paper/CloudRescue_Research_Paper_Final.pdf`  
**HTML Source:** `paper/CloudRescue_Research_Paper_Final.html`  
**Markdown Source:** `paper/CloudRescue_Research_Paper_Draft.md`  
**Compilation Date:** November 10, 2026  
**Document Stage:** Final Submission-Ready Research Manuscript  
**Affiliation Badge:** Department of Computer Science and Engineering, Indian Institute of Information Technology Dharwad  
**Target Venues:** IEEE Transactions on Cloud Computing / ACM Transactions on Autonomous and Adaptive Systems  

---

## 1. Executive Summary & Compilation Metadata

The submission-ready CloudRescue research manuscript has been successfully typeset in authentic **IEEE Transactions academic format** and compiled to a high-resolution PDF. All mathematical formulations, experimental metrics, figures, tables, and citations from the certified Markdown draft have been preserved without modification or truncation.

| Property | Value | Verification Status |
| :--- | :--- | :--- |
| **Output Path** | `paper/CloudRescue_Research_Paper_Final.pdf` | **VERIFIED** |
| **File Size** | 2,827,874 bytes (2.70 MB) | **VERIFIED** |
| **Page Count** | 19 Pages (Letter Size: 8.5" × 11") | **VERIFIED (No widow/orphan page)** |
| **Layout** | IEEE Two-Column Layout (0.22" gap, justified, 1.25em indent) | **VERIFIED** |
| **Typography** | Times New Roman / Liberation Serif, 9.5pt body, 1.22 line height | **VERIFIED** |
| **Math Renderer** | KaTeX v0.16.21 (Pre-rendered HTML + MathML vector typography) | **VERIFIED (0 errors, 0 raw placeholders)** |
| **PDF Producer** | Headless Chrome 154 with Skia/PDF Vector Subsystem | **VERIFIED** |
| **Page Margins** | Top: 0.70", Bottom: 0.75", Left: 0.65", Right: 0.65" | **VERIFIED** |
| **Running Headers** | Suppressed on Page 1; Title & Date on Pages 2–19 | **VERIFIED (CSS Paged Media)** |
| **Running Footers** | Centered page numbering `1` through `19` | **VERIFIED** |

---

## 2. Section-by-Section Structural Integrity Audit

All 10 major paper sections, formal IEEE Roman numeral headings, subsections, and reference artifacts were audited and located within the 19-page document:

| Section | Heading in Document | Page | Audit Status |
| :--- | :--- | :---: | :--- |
| **Header Block** | Title, Authors (Hari Prasad L, Yeruva Mahesh Reddy, K. Ram Charan, Tushar), IIIT Dharwad | Page 1 | **PASS** |
| **Abstract & Index Terms** | Spanning abstract block with bold-italic `Abstract—` and `Index Terms—` | Page 1 | **PASS** |
| **Section 1 / 2** | `I. INTRODUCTION` | Page 1 | **PASS** |
| **Section 3** | `II. PROBLEM STATEMENT AND RESEARCH OBJECTIVES` (Subsections A–D) | Page 1 | **PASS** |
| **Section 4** | `III. RESEARCH CONTRIBUTIONS` | Page 2 | **PASS** |
| **Section 5** | `IV. RELATED WORK` (Subsections A–D: Resilinets, Auto-scaling critique, Brownout) | Page 2 | **PASS** |
| **Section 6** | `V. PROPOSED CLOUDRESCUE ARCHITECTURE` (Subsections A–D) | Page 3 | **PASS** |
| **Section 7** | `VI. EXPERIMENTAL METHODOLOGY` (Subsections A–L: PRNG, Scenarios, DEC-010) | Page 6 | **PASS** |
| **Section 8** | `VII. RESULTS AND EVALUATION` (Subsections A–G: 360-run benchmark, Sensitivity) | Page 9 | **PASS** |
| **Section 9** | `VIII. DISCUSSION AND LIMITATIONS` (Subsections A–G: Physical mechanisms, Threats) | Page 17 | **PASS** |
| **Section 10** | `IX. CONCLUSION AND FUTURE WORK` (Subsections A–B: Summary, Future paths) | Page 19 | **PASS** |
| **References** | `REFERENCES` (17 complete IEEE bibliographic entries [1]–[17]) | Page 19 | **PASS** |
| **Appendix** | `APPENDIX: REPOSITORY ARTIFACTS & VERIFICATION PROVENANCE` | Page 19 | **PASS** |

---

## 3. Mathematical Formula Audit

Every mathematical expression was pre-rendered server-side into dual HTML+MathML vector structures via KaTeX. A text extraction scan confirmed that **zero** raw `INLINE_MATH_*` or `DISPLAY_MATH_*` placeholders remain in the compiled PDF.

| Category | Target Count | Verified Count in PDF | Status |
| :--- | :---: | :---: | :--- |
| **Display Equations** | 30 | 30 (Equations 1 through 30 labeled right-aligned) | **100% PASS** |
| **Inline Math Expressions** | 1,318+ | 1,318 rendered into MathML/HTML | **100% PASS** |
| **KaTeX Syntax Errors** | 0 | 0 | **100% PASS** |
| **Unrendered Delimiters** | 0 | 0 (`$` and `$$` completely processed) | **100% PASS** |

### Verified Equation Sampling:
- **Eq. (1) & (2):** Expected request execution time $E[S]$ and total latency $L_i = W_i + S_i$.
- **Eq. (3):** BALB composite dispatch scoring formula $\text{Score}_w = \alpha \theta_w - \beta \frac{q_w}{Q_{\max}} - \gamma U_w$.
- **Eq. (5):** Local velocity-form discrete PI error definition $e_w(t) = r_{\text{target}} - \hat{r}_{95, w}(t)$.
- **Eq. (8):** Intrinsic anti-windup dimmer clamping $\theta_w(t) = \min(1.0, \max(0.0, \theta_w^{\text{raw}}(t)))$.
- **Eq. (18) & (19):** Latency SLA violation rate $V_{\text{lat}}$ and overall SLA failure rate $V_{\text{overall}}$.
- **Eq. (21):** Mathematical non-additivity formulation $V_{\text{overall}} = V_{\text{lat}} \cdot S_r + D_{\text{drop\_rate}}$.
- **Eq. (24):** Jain's fairness index $J = \frac{(\sum x_w)^2}{M_{\text{active}} \sum x_w^2}$.
- **Eq. (27) & (28):** DEC-010 nominal baseline tolerance $\theta_{\text{nom}, w, s} \pm \epsilon_{\text{tol}}$ and post-restoration recovery time $T_{\text{restore}}$.

---

## 4. Figure Audit

All 7 research figures are embedded at publication resolution with authentic IEEE figure formatting (`Fig. N.` bold prefix with justified captions):

| Figure | Subject | Source Asset | Width / Column Span | Page in PDF | Status |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Fig. 1** | Logical system architecture diagram | Monospace ASCII container | Two-column (`column-span: all`) | Page 3–4 | **PASS** |
| **Fig. 2** | SLA failure and violation bar comparison | `sla_violation_rates_bar.png` | Two-column (`column-span: all`) | Page 10 | **PASS** |
| **Fig. 3** | Latency CDF distribution under Compound Stress | `latency_cdf_comparison.png` | Single-column | Page 11 | **PASS** |
| **Fig. 4** | Compound stress time-series telemetry (seed 1001) | `time_series_dynamics_compound.png` | Two-column (`column-span: all`) | Page 13 | **PASS** |
| **Fig. 5** | Service Fidelity vs. Reliability scatter envelope | `fidelity_vs_reliability_tradeoff.png` | Single-column | Page 14 | **PASS** |
| **Fig. 6** | Jain's fairness index & CPU utilization boxplots | `fairness_and_utilization_box.png` | Single-column | Page 15 | **PASS** |
| **Fig. 7** | BALB sensitivity sweep parameter heatmap | `sensitivity_heatmap.png` | Two-column (`column-span: all`) | Page 16 | **PASS** |

*Note: All images are inlined directly as Base64 data URIs inside the HTML compiler, guaranteeing that the generated PDF is 100% self-contained and free of external asset dependencies.*

---

## 5. Table Audit

All 8 experimental benchmark tables are formatted according to **IEEE Booktabs typography** (heavy top and bottom horizontal rules, light interior rule, small-caps headers, no vertical borders, centered numbers):

| Table | Caption & Title | Columns | Two-Column Span | Page in PDF | Status |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **TABLE I** | Primary 360-Run Experimental Benchmark | 7 | Yes (`column-span: all`) | Page 10 | **PASS** |
| **TABLE II-A** | Nominal Scenario Performance Breakdown | 5 | Yes (`column-span: all`) | Page 11 | **PASS** |
| **TABLE II-B** | Flash Crowd Scenario Performance Breakdown | 5 | Yes (`column-span: all`) | Page 11 | **PASS** |
| **TABLE II-C** | Server Crash Scenario Performance Breakdown | 5 | Yes (`column-span: all`) | Page 11 | **PASS** |
| **TABLE II-D** | Compound Stress Scenario Performance Breakdown | 5 | Yes (`column-span: all`) | Page 12 | **PASS** |
| **TABLE III** | 30-Seed Post-Restoration Recovery Metrics Under DEC-010 | 6 | Yes (`column-span: all`) | Page 13 | **PASS** |
| **TABLE IV** | Primary Paired Statistical Comparison Battery ($N = 30$) | 13 | Yes (`column-span: all`) | Page 16 | **PASS** |
| **TABLE V** | Representative BALB Parameter Configurations ($n = 3$) | 7 | Yes (`column-span: all`) | Page 17 | **PASS** |

*Note: For dense multi-column benchmark tables (Table I and Table IV), tight cell padding (`2pt 1.5pt`) and 6.7pt typography ensure that all 13 columns fit within the 7.2" printable page width without text clipping or awkward wrapping.*

---

## 6. Citations and References Verification

The bibliography conforms strictly to IEEE reference formatting guidelines. All 17 numbered citations were checked for existence in both the text body and the final `REFERENCES` list:

| Citation Key | Reference Details | Citation in Text | Reference Entry | Status |
| :--- | :--- | :---: | :---: | :--- |
| **[1]** | Welsh & Benkhelifa (IEEE TCC 2020) | Section 1, 2, 5.1, 5.2 | Page 19 | **VERIFIED** |
| **[2]** | Klein et al. (SEAMS 2014) | Section 1, 2, 5.3, 6.2 | Page 19 | **VERIFIED** |
| **[3]** | Klein et al. (ACM TAAS 2014) | Section 1, 5.3, 6.3 | Page 19 | **VERIFIED** |
| **[4]** | Sterbenz et al. (Computer Networks 2010) | Section 5.1 | Page 19 | **VERIFIED** |
| **[5]** | Cartlidge & Sriram (ACM TOMACS 2017) | Section 1, 2, 5.2 | Page 19 | **VERIFIED** |
| **[6]** | Hellerstein et al. (Feedback Control of Computing Systems 2004) | Section 5.3 | Page 19 | **VERIFIED** |
| **[7]** | Filieri et al. (IEEE TSE 2015) | Section 5.3 | Page 19 | **VERIFIED** |
| **[8]** | Tomas & Tordsson (IEEE TCC 2014) | Section 5.3 | Page 19 | **VERIFIED** |
| **[9]** | SimPy Team (Discrete-Event Simulation for Python 2024) | Section 7.1 | Page 19 | **VERIFIED** |
| **[10]** | Law (Simulation Modeling and Analysis 2015) | Section 7.4 | Page 19 | **VERIFIED** |
| **[11]** | Jain, Chiu, & Hawe (DEC Technical Report 1984) | Section 7.10 | Page 19 | **VERIFIED** |
| **[12]** | Shapiro & Wilk (Biometrika 1965) | Section 7.11 | Page 19 | **VERIFIED** |
| **[13]** | Wilcoxon (Biometrics Bulletin 1945) | Section 7.11 | Page 19 | **VERIFIED** |
| **[14]** | Cohen (Statistical Power Analysis 1988) | Section 7.11 | Page 19 | **VERIFIED** |
| **[15]** | Bonferroni (Pubbl. R. Ist. Super. Firenze 1936) | Section 7.11 | Page 19 | **VERIFIED** |
| **[16]** | Benjamini & Hochberg (JRSS-B 1995) | Section 7.11 | Page 19 | **VERIFIED** |
| **[17]** | Kaplan & Meier (JASA 1958) | Section 7.12 | Page 19 | **VERIFIED** |

---

## 7. Data Consistency and Academic Integrity Audit

1. **Experimental Data Integrity:**
   - Every number in Tables I–V matches the frozen experiment dataset (`results/experiment_360/aggregated_metrics.csv` and `master_results.csv`).
   - Mean differences, 95% confidence intervals, Cohen's $d_z$, Shapiro-Wilk $p$-values, raw $p$-values, Bonferroni $p_{\text{adj}}$, and Benjamini-Hochberg FDR $q$-values match the frozen battery (`statistical_comparisons.csv`) without modification.
2. **Pre-registered Hypotheses Treatment:**
   - Both supported hypotheses (e.g., $H_{1,1}$ SLA violation reduction, $H_{1,3}$ load fairness) and decisively rejected hypotheses (e.g., $H_{1,3}$ service fidelity superiority) are preserved with objective academic transparency.
3. **Limitations & Caveats:**
   - Section 9.7 ("Threats to Validity and Scientific Limitations") explicitly preserves all eight documented simulation caveats: synthetic queueing assumptions, single-tier proxy architecture, discrete-event clock abstractions, lack of physical OS context-switch overhead, and scope limitations regarding physical cloud deployment.
4. **Attribution and Clean Affiliation:**
   - Document metadata attributes the work to Hari Prasad L, Yeruva Mahesh Reddy, K. Ram Charan, and Tushar at the Indian Institute of Information Technology Dharwad.
   - No fictitious IEEE conference or journal template sponsorship/copyright stamps were invented.

---

## 8. Final Certification & Signoff

The CloudRescue research manuscript in `paper/CloudRescue_Research_Paper_Final.pdf` passes all academic quality, typographic, mathematical, and data integrity checks. It is certified as **complete, fully verified, and ready for submission or academic presentation**.

- **Audited By:** Antigravity Research Assistant (Pair Programming & Academic Reviewer)  
- **Signoff Date:** November 10, 2026  
- **Status:** **APPROVED & FROZEN (100% Submission Ready)**

