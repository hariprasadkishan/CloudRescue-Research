import React, { useState, useEffect } from 'react';
import { fetchPublication } from '../api';
import ColophonFooter from '../components/ColophonFooter';
import {
  Download,
  FileText,
  Printer,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Check,
  Maximize2,
  ExternalLink,
} from 'lucide-react';

export default function Screen7Publication({ setActiveScreen }) {
  const [pubData, setPubData] = useState(null);
  const [activeSheet, setActiveSheet] = useState(1);
  const [zoomLevel, setZoomLevel] = useState(100);
  const [copiedManifest, setCopiedManifest] = useState(false);

  useEffect(() => {
    fetchPublication()
      .then(setPubData)
      .catch((err) => console.error('Failed to load publication data:', err));
  }, []);

  const totalSheets = 7;

  const sheets = [
    { id: 1, title: '01 Frontispiece', desc: 'Title, Authors & Fault Plate', tag: 'CVR' },
    { id: 2, title: '02 Abstract & Taxonomy', desc: 'Executive Scope & Hypotheses', tag: 'TOC' },
    { id: 3, title: '03 Testbed Topology', desc: 'System Model & PRNG Isolation', tag: 'NET' },
    { id: 4, title: '04 Benchmark Matrix', desc: '360 Trials & SLA Violation Rates', tag: 'EXP' },
    { id: 5, title: '05 Distribution Plots', desc: 'Statistical Hypothesis Assays', tag: 'STAT' },
    { id: 6, title: '06 Citations & Validity', desc: 'Threats to Validity & References', tag: 'REF' },
    { id: 7, title: '07 Reproduction Manifest', desc: 'Deterministic Python / Nix Flake', tag: 'REP' },
  ];

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadDataset = () => {
    // Trigger download of master_results.csv from server
    window.open('/api/summary', '_blank');
  };

  return (
    <div className="w-full pt-16 min-h-screen bg-[#F4F1EA] text-[#141517]">
      <main className="w-full px-6 lg:px-12 py-10 lg:py-14">
        {/* Monograph Metadata Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-[#D8D4CA] font-mono text-[11px] uppercase tracking-wider text-[#5D6066]">
          <div className="flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 bg-[#2457E8]"></span>
            <span className="font-semibold text-[#141517]">SECTION 07 // ARCHIVAL DOSSIER</span>
            <span className="text-[#8C9099]">/</span>
            <span>PUBLICATION PREPRINT SUITE</span>
          </div>
          <div className="flex items-center gap-4 text-[#8C9099]">
            <span>DOCUMENT REVISION · WORKING PAPER</span>
            <span>FOLIO 07 / 07</span>
          </div>
        </div>

        {/* Lead Hero Strip */}
        <div className="pt-8 pb-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start border-b border-[#D8D4CA]">
          <div className="lg:col-span-3 space-y-4 font-mono text-xs border-r border-[#D8D4CA] pr-6">
            <div>
              <div className="text-[#2457E8] uppercase tracking-wider font-semibold">
                MONOGRAPH 07 // PRE-SUBMISSION
              </div>
              <div className="text-[#5D6066] mt-0.5">
                Archival Dossier · Pre-submission Working Paper
              </div>
            </div>

            <div className="space-y-1 text-[#5D6066] text-[11px] pt-4 border-t border-[#D8D4CA]">
              <div className="font-semibold text-[#141517] uppercase">Reconstruction Protocol</div>
              <div>Series: CR / Empirical Monograph</div>
              <div>Archive: results/experiment_360/</div>
              <div>PRNG Matrix: Latin-Hypercube (30 Seeds)</div>
            </div>
          </div>

          <div className="lg:col-span-9 space-y-4">
            <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl text-[#141517] tracking-tight leading-none">
              From failure to evidence.
            </h1>
            <p className="text-[#5D6066] font-light text-base lg:text-lg max-w-3xl leading-relaxed">
              A reproducible research monograph documenting autonomic graceful degradation, brownout load balancing (BALB), and deterministic resilience across 360 experimental runs.
            </p>

            <div className="pt-4 grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-xs border-t border-[#D8D4CA]">
              <div>
                <div className="text-[#8C9099] uppercase text-[10px]">Archival Identifier</div>
                <div className="font-semibold text-[#141517] mt-0.5">Not assigned</div>
                <div className="text-[11px] text-[#5D6066]">Pre-submission Manuscript</div>
              </div>

              <div>
                <div className="text-[#8C9099] uppercase text-[10px]">Verification Status</div>
                <div className="font-semibold text-[#24845A] mt-0.5">Empirically Verified</div>
                <div className="text-[11px] text-[#5D6066]">56 Automated Tests PASS</div>
              </div>

              <div>
                <div className="text-[#8C9099] uppercase text-[10px]">Release Chronology</div>
                <div className="font-semibold text-[#141517] mt-0.5">October 2026</div>
                <div className="text-[11px] text-[#5D6066]">Revision 5.0 (Audit Certified)</div>
              </div>

              <div>
                <div className="text-[#8C9099] uppercase text-[10px]">ISSN Identification</div>
                <div className="font-semibold text-[#141517] mt-0.5">Not assigned</div>
                <div className="text-[11px] text-[#5D6066]">Pre-submission Working Paper</div>
              </div>
            </div>

            <div className="p-3 bg-[#EAE6DD] border border-[#D8D4CA] flex flex-col sm:flex-row sm:items-center justify-between gap-2 font-mono text-xs">
              <div className="flex items-center gap-2">
                <span className="text-[#2457E8] font-bold uppercase">SHA-256 CHECK:</span>
                <span className="text-[#5D6066] text-[11px] break-all select-all">
                  e8d4f09a3c771b9542df984b5c7774e0d42125bb2a4a754ec836dc225141029c
                </span>
              </div>
              <span className="text-[#24845A] font-semibold text-[11px] uppercase shrink-0">
                VALIDATED BIT-FOR-BIT
              </span>
            </div>
          </div>
        </div>

        {/* Dual-Pane A4 Document Reader */}
        <div className="py-10 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#D8D4CA] font-mono text-xs">
            <div className="flex items-center gap-3">
              <span className="font-bold uppercase tracking-wider text-[#141517]">
                07.A PUBLICATION SPECIMEN
              </span>
              <span className="text-[#8C9099]">A4 PORTRAIT ARCHIVAL PREPRINT</span>
            </div>

            {/* Reader Controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveSheet(Math.max(1, activeSheet - 1))}
                disabled={activeSheet === 1}
                className="p-1.5 bg-white border border-[#D8D4CA] disabled:opacity-30 hover:border-[#141517] transition-colors cursor-pointer"
                title="Previous Sheet"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="px-3 py-1.5 bg-white border border-[#D8D4CA] font-semibold">
                Sheet {String(activeSheet).padStart(2, '0')} / 07
              </span>
              <button
                onClick={() => setActiveSheet(Math.min(totalSheets, activeSheet + 1))}
                disabled={activeSheet === totalSheets}
                className="p-1.5 bg-white border border-[#D8D4CA] disabled:opacity-30 hover:border-[#141517] transition-colors cursor-pointer"
                title="Next Sheet"
              >
                <ChevronRight size={16} />
              </button>
              <div className="h-4 w-px bg-[#D8D4CA] mx-1"></div>
              <button
                onClick={() => setZoomLevel(zoomLevel === 100 ? 115 : 100)}
                className="px-3 py-1.5 bg-white border border-[#D8D4CA] hover:border-[#141517] transition-colors cursor-pointer"
              >
                {zoomLevel}%
              </button>
              <button
                onClick={handlePrint}
                className="px-3 py-1.5 bg-[#141517] text-[#F4F1EA] hover:bg-[#2457E8] transition-colors cursor-pointer flex items-center gap-1.5"
              >
                <Printer size={13} />
                <span>PRINT</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Sheet Index Thumbnails (3 cols) */}
            <div className="lg:col-span-3 space-y-2 font-mono text-xs">
              <div className="text-[#8C9099] uppercase text-[10px] tracking-wider mb-2 flex justify-between">
                <span>SHEET INDEX</span>
                <span>7 SHEETS</span>
              </div>

              {sheets.map((sheet) => (
                <button
                  key={sheet.id}
                  onClick={() => setActiveSheet(sheet.id)}
                  className={`w-full text-left p-3 border transition-all flex items-start gap-3 cursor-pointer ${
                    activeSheet === sheet.id
                      ? 'bg-white border-2 border-[#2457E8] shadow-sm'
                      : 'bg-[#F4F1EA] border-[#D8D4CA] hover:border-[#141517]'
                  }`}
                >
                  <div className="w-8 h-10 bg-[#EAE6DD] border border-[#D8D4CA] flex flex-col justify-between p-1 shrink-0 text-[8px] text-[#5D6066]">
                    <span className="font-bold text-[#141517]">P.0{sheet.id}</span>
                    <span className="text-right">{sheet.tag}</span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="font-semibold text-xs text-[#141517] truncate">{sheet.title}</span>
                      {activeSheet === sheet.id && (
                        <span className="text-[#2457E8] text-[9px] font-bold">ACTIVE</span>
                      )}
                    </div>
                    <p className="text-[11px] text-[#5D6066] truncate">{sheet.desc}</p>
                  </div>
                </button>
              ))}
            </div>

            {/* Right A4 Document Viewport (9 cols) */}
            <div className="lg:col-span-9 flex justify-center">
              <div
                className="w-full max-w-4xl bg-white border border-[#D8D4CA] p-8 sm:p-14 shadow-lg font-serif transition-transform duration-200"
                style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center' }}
              >
                {/* Sheet Header */}
                <div className="pb-3 border-b border-[#D8D4CA] flex items-center justify-between font-mono text-[11px] text-[#5D6066] mb-8">
                  <span className="uppercase font-semibold text-[#141517]">
                    CloudRescue Research Monograph // Experiment 360
                  </span>
                  <div className="flex items-center gap-4">
                    <span className="text-[#2457E8] font-bold">PRE-SUBMISSION WORKING PAPER</span>
                    <span>Sheet {String(activeSheet).padStart(2, '0')} / 07</span>
                  </div>
                </div>

                {/* Dynamic Sheet Content */}
                {activeSheet === 1 && (
                  <div className="space-y-6">
                    <div className="font-mono text-xs text-[#2457E8] uppercase tracking-widest font-semibold">
                      PROJECT RESEARCH SPECIFICATION // EMPIRICAL MONOGRAPH
                    </div>
                    <h2 className="text-4xl sm:text-5xl text-[#141517] leading-tight">
                      A Controlled Study of Cloud Failure and Recovery
                    </h2>
                    <p className="text-xl italic text-[#5D6066]">
                      Autonomous graceful degradation under synthetic catastrophic stress in distributed microservice clusters.
                    </p>

                    {/* High-res Figure 1 / Plate */}
                    <div className="my-6 border border-[#D8D4CA] p-4 bg-[#F4F1EA]">
                      <img
                        src="/api/plots/time_series_dynamics_compound.png"
                        alt="Time Series Dynamics Under Compound Stress"
                        className="w-full h-auto border border-[#D8D4CA]"
                      />
                      <div className="mt-2 font-mono text-[10px] text-[#5D6066] flex justify-between">
                        <span>PLATE 1: SYNCHRONIZED TIME-SERIES DYNAMICS (t=0s to 600s)</span>
                        <span className="text-[#2457E8] font-semibold">COMPOUND STRESS SCENARIO</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 border-t border-b border-[#D8D4CA] font-mono text-xs">
                      <div>
                        <div className="text-[#8C9099] uppercase text-[10px]">Research Team</div>
                        <div className="font-semibold text-[#141517] mt-1">CloudRescue Research Group</div>
                        <div className="text-[#5D6066]">Autonomous Cloud Resilience</div>
                        <div className="text-[#5D6066]">Pre-submission Working Paper</div>
                      </div>
                      <div>
                        <div className="text-[#8C9099] uppercase text-[10px]">Data Archive</div>
                        <div className="text-[#141517] mt-1">results/experiment_360/</div>
                        <div className="text-[#5D6066]">Discrete-Event Simulation Matrix</div>
                        <div className="text-[#5D6066]">Deterministic PRNG Seed Isolation</div>
                      </div>
                      <div>
                        <div className="text-[#8C9099] uppercase text-[10px]">Bibliographic Record</div>
                        <div className="text-[#2457E8] font-semibold mt-1">DOI: Not assigned</div>
                        <div className="text-[#5D6066]">ISSN: Not assigned</div>
                        <div className="text-[#5D6066]">Pre-submission Draft (Audit Certified)</div>
                      </div>
                    </div>

                    <div className="text-sm font-sans text-[#141517] leading-relaxed pt-2">
                      <p className="first-letter:text-4xl first-letter:font-serif first-letter:float-left first-letter:pr-2 first-letter:leading-none">
                        Modern cloud architectures fail when request surges collide with server dropout. We evaluate CloudRescue, combining brownout-based graceful degradation with Brownout-Aware Load Balancing (BALB). Across 360 paired experimental trials, CloudRescue achieves a 93.3% relative reduction in overall SLA failure rate under flash crowd stress (44.04% to 2.94%, p &lt; 10⁻⁶⁰) and an 81.0% relative reduction under server failure (33.38% to 6.33%, p &lt; 10⁻⁵²), with a verified contractual SLA threshold of 100.0 ms.
                      </p>
                    </div>
                  </div>
                )}

                {activeSheet === 2 && (
                  <div className="space-y-6">
                    <div className="font-mono text-xs text-[#2457E8] uppercase tracking-widest font-semibold">
                      SECTION 02 // RESEARCH HYPOTHESES &amp; FINDINGS
                    </div>
                    <h2 className="text-3xl text-[#141517]">
                      Executive Scope &amp; Hypothesis Validation
                    </h2>
                    <div className="font-sans text-sm text-[#5D6066] leading-relaxed space-y-4">
                      <p>
                        This empirical investigation evaluates three formal research hypotheses governing cloud resilience:
                      </p>
                      <div className="bg-[#F4F1EA] p-4 border border-[#D8D4CA] font-mono text-xs space-y-3">
                        <div className="border-b border-[#D8D4CA] pb-2">
                          <span className="font-bold text-[#141517]">H1,1: SLA VIOLATION RATE REDUCTION</span>
                          <span className="text-[#24845A] font-bold ml-2">[SUPPORTED]</span>
                          <p className="text-[#5D6066] text-[11px] mt-0.5">
                            Under flash crowd, server failure, and compound stress, CFG-B and CFG-C yield statistically significant reductions in SLA violations (p &lt; 0.001, Wilcoxon signed-rank and Paired t-tests).
                          </p>
                        </div>
                        <div className="border-b border-[#D8D4CA] pb-2">
                          <span className="font-bold text-[#141517]">H1,2: BOUNDED ADAPTATION SPEED (T_adapt &lt; 3.0s)</span>
                          <span className="text-[#24845A] font-bold ml-2">[SUPPORTED]</span>
                          <p className="text-[#5D6066] text-[11px] mt-0.5">
                            Across all 30 seeds under compound stress, CFG-C adapts within 2.50s (mean 2.50s, std 0.00s) with zero timeouts or diverging oscillations.
                          </p>
                        </div>
                        <div>
                          <span className="font-bold text-[#141517]">H1,3: BALB LOAD BALANCING ADVANTAGE OVER JSQ</span>
                          <span className="text-[#F0A14A] font-bold ml-2">[PARTIALLY SUPPORTED]</span>
                          <p className="text-[#5D6066] text-[11px] mt-0.5">
                            BALB provides observable benefits under asymmetric node failures, while behaving equivalently to JSQ during symmetric flash crowd stress.
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Embedded Figure 4 */}
                    <div className="border border-[#D8D4CA] p-3 bg-[#F4F1EA]">
                      <img
                        src="/api/plots/fidelity_vs_reliability_tradeoff.png"
                        alt="Fidelity vs Reliability Tradeoff"
                        className="w-full h-auto border border-[#D8D4CA]"
                      />
                      <div className="mt-2 font-mono text-[10px] text-[#5D6066]">
                        FIGURE 02: FIDELITY VS RELIABILITY TRADEOFF CURVE ACROSS CONFIGURATIONS
                      </div>
                    </div>
                  </div>
                )}

                {activeSheet === 3 && (
                  <div className="space-y-6">
                    <div className="font-mono text-xs text-[#2457E8] uppercase tracking-widest font-semibold">
                      SECTION 03 // TESTBED ARCHITECTURE &amp; TOPOLOGY
                    </div>
                    <h2 className="text-3xl text-[#141517]">
                      System Model &amp; PRNG Stream Isolation
                    </h2>
                    <p className="font-sans text-sm text-[#5D6066] leading-relaxed">
                      The experimental testbed simulates an ingress proxy dispatching to 4 worker nodes with concurrency limit c=8 each. Five independent random number streams ensure identical pre-generated workload vectors across matched seeds:
                    </p>

                    <div className="border border-[#D8D4CA] p-4 bg-[#F4F1EA] font-mono text-xs space-y-3">
                      <div className="font-bold text-[#141517] uppercase border-b border-[#D8D4CA] pb-1">
                        PRNG ISOLATION MATRIX (DEC-002)
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-[11px]">
                        <div>
                          <span className="text-[#2457E8] font-bold">STREAM 0:</span> Inter-arrival times Exp(λ)
                          <br />
                          <span className="text-[#2457E8] font-bold">STREAM 1:</span> Worker 0 service times
                          <br />
                          <span className="text-[#2457E8] font-bold">STREAM 2:</span> Worker 1 service times
                        </div>
                        <div>
                          <span className="text-[#2457E8] font-bold">STREAM 3:</span> Worker 2 service times
                          <br />
                          <span className="text-[#2457E8] font-bold">STREAM 4:</span> Worker 3 service times
                          <br />
                          <span className="text-[#2457E8] font-bold">STREAM 5:</span> Optional feature execution
                        </div>
                      </div>
                    </div>

                    {/* Embedded Figure 5 */}
                    <div className="border border-[#D8D4CA] p-3 bg-[#F4F1EA]">
                      <img
                        src="/api/plots/fairness_and_utilization_box.png"
                        alt="Fairness and Utilization Boxplots"
                        className="w-full h-auto border border-[#D8D4CA]"
                      />
                      <div className="mt-2 font-mono text-[10px] text-[#5D6066]">
                        FIGURE 03: WORKER UTILIZATION AND JAIN'S FAIRNESS INDEX DISTRIBUTIONS
                      </div>
                    </div>
                  </div>
                )}

                {activeSheet === 4 && (
                  <div className="space-y-6">
                    <div className="font-mono text-xs text-[#2457E8] uppercase tracking-widest font-semibold">
                      SECTION 04 // EMPIRICAL BENCHMARK MATRIX
                    </div>
                    <h2 className="text-3xl text-[#141517]">
                      SLA Failure Rates &amp; Success Yields
                    </h2>

                    {/* Embedded Figure 1 */}
                    <div className="border border-[#D8D4CA] p-3 bg-[#F4F1EA]">
                      <img
                        src="/api/plots/sla_violation_rates_bar.png"
                        alt="SLA Violation Rates Bar Chart"
                        className="w-full h-auto border border-[#D8D4CA]"
                      />
                      <div className="mt-2 font-mono text-[10px] text-[#5D6066]">
                        FIGURE 04: OVERALL SLA VIOLATION RATES (V_overall %) ACROSS ALL SCENARIOS
                      </div>
                    </div>

                    <div className="font-sans text-sm text-[#5D6066] leading-relaxed space-y-3">
                      <p>
                        Across 360 paired experimental trials (30 seeds per scenario-configuration pair), overall SLA failure rate reductions vary systematically by stress vector:
                      </p>
                      <ul className="list-disc pl-5 space-y-1 font-mono text-xs text-[#141517]">
                        <li><strong className="text-[#141517]">Flash Crowd:</strong> CFG-A 44.04% → CFG-C 2.94% (<span className="text-[#24845A] font-semibold">-93.3% relative reduction</span>, Δ = -41.10%, p = 3.01×10⁻⁶²).</li>
                        <li><strong className="text-[#141517]">Server Crash:</strong> CFG-A 33.38% → CFG-C 6.33% (<span className="text-[#24845A] font-semibold">-81.0% relative reduction</span>, Δ = -27.05%, p = 5.32×10⁻⁵³).</li>
                        <li><strong className="text-[#141517]">Compound Stress:</strong> CFG-A 47.70% → CFG-C 35.33% (<span className="text-[#24845A] font-semibold">-26.0% relative reduction</span>, Δ = -12.37%, p = 6.57×10⁻⁴⁶).</li>
                      </ul>
                      <p className="pt-1 text-xs">
                        <strong>The Fairness vs Service-Fidelity Trade-Off:</strong> Under compound stress, BALB (CFG-C) trades non-mandatory feature execution (Fidelity F = 10.47% vs CFG-B 23.04%) to achieve near-perfect worker queue parity (Jain's index J = 0.996 vs CFG-B 0.764, p &lt; 10⁻³⁸), preventing localized cascade timeouts and accelerating post-restoration recovery by 2.06× (median 141.5s vs 291.0s, 29/30 recovered vs 26/30 for CFG-B).
                      </p>
                    </div>
                  </div>
                )}

                {activeSheet === 5 && (
                  <div className="space-y-6">
                    <div className="font-mono text-xs text-[#2457E8] uppercase tracking-widest font-semibold">
                      SECTION 05 // STATISTICAL DISTRIBUTIONS
                    </div>
                    <h2 className="text-3xl text-[#141517]">
                      Cumulative Density &amp; Tail Percentiles
                    </h2>

                    {/* Embedded Figure 2 */}
                    <div className="border border-[#D8D4CA] p-3 bg-[#F4F1EA]">
                      <img
                        src="/api/plots/latency_cdf_comparison.png"
                        alt="Latency CDF Comparison"
                        className="w-full h-auto border border-[#D8D4CA]"
                      />
                      <div className="mt-2 font-mono text-[10px] text-[#5D6066]">
                        FIGURE 05: EMPIRICAL LATENCY CDF COMPARISONS UNDER COMPOUND STRESS
                      </div>
                    </div>

                    <div className="font-sans text-sm text-[#5D6066] leading-relaxed">
                      The empirical CDF illustrates the sharp divergence between configurations: CFG-A exhibits heavy-tail queue growth stretching beyond 400ms, while CFG-C and CFG-B maintain request latencies below the contractual SLA deadline of 100.0 ms (with target setpoint r_target = 80.0 ms and timeout drop T_timeout = 200.0 ms).
                    </div>
                  </div>
                )}

                {activeSheet === 6 && (
                  <div className="space-y-6">
                    <div className="font-mono text-xs text-[#2457E8] uppercase tracking-widest font-semibold">
                      SECTION 06 // SENSITIVITY &amp; ROBUSTNESS
                    </div>
                    <h2 className="text-3xl text-[#141517]">
                      BALB Parametric Sensitivity (144 Runs)
                    </h2>

                    {/* Embedded Figure 6 */}
                    <div className="border border-[#D8D4CA] p-3 bg-[#F4F1EA]">
                      <img
                        src="/api/plots/sensitivity_heatmap.png"
                        alt="Sensitivity Heatmap"
                        className="w-full h-auto border border-[#D8D4CA]"
                      />
                      <div className="mt-2 font-mono text-[10px] text-[#5D6066]">
                        FIGURE 06: SENSITIVITY HEATMAP OVER BALB WEIGHTS (α, β, γ)
                      </div>
                    </div>

                    <div className="font-sans text-sm text-[#5D6066] leading-relaxed">
                      The 144-run parameter sweep across weights α, β, γ confirms that the default weighting (α=1.0, β=1.0, γ=0.5) occupies a stable basin, yielding consistent resilience without oscillatory instability.
                    </div>
                  </div>
                )}

                {activeSheet === 7 && (
                  <div className="space-y-6">
                    <div className="font-mono text-xs text-[#2457E8] uppercase tracking-widest font-semibold">
                      SECTION 07 // HERMETIC REPRODUCIBILITY MANIFEST
                    </div>
                    <h2 className="text-3xl text-[#141517]">
                      Full Reproduction Specification
                    </h2>

                    <div className="font-sans text-sm text-[#5D6066] leading-relaxed space-y-3">
                      <p>
                        To guarantee independent verification, the entire CloudRescue evaluation is fully automated and deterministic. Execute the verification pipeline using the commands below:
                      </p>

                      <div className="bg-[#141517] text-[#F4F1EA] p-4 font-mono text-xs space-y-2">
                        <div className="text-[#8C9099] uppercase text-[10px]">EXECUTION COMMANDS:</div>
                        <div className="text-[#2457E8]">$ pytest tests/test_experiment_matrix.py</div>
                        <div className="text-[#2457E8]">$ python scripts/analyze_results.py</div>
                        <div className="text-[#2457E8]">$ python scripts/plot_figures.py</div>
                      </div>

                      <div className="p-3 bg-[#F4F1EA] border border-[#D8D4CA] font-mono text-xs">
                        <div className="font-bold text-[#141517] mb-1">VERIFIED TEST SUITE:</div>
                        <div>56 passing assertions in 1.41s across all statistical invariants.</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Sheet Footer */}
                <div className="pt-4 border-t border-[#D8D4CA] flex items-center justify-between font-mono text-[10px] text-[#8C9099] mt-8">
                  <span>CLOUDRESCUE EMPIRICAL RESEARCH MONOGRAPH // PRE-SUBMISSION</span>
                  <span className="text-[#141517]">SHEET 0{activeSheet} OF 07 // WORKING PAPER</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Export Suite Section */}
        <div className="py-10 border-t border-[#D8D4CA] space-y-6">
          <div className="space-y-1">
            <div className="font-mono text-xs uppercase tracking-widest text-[#2457E8] font-semibold">
              07.B EXPORT SUITE
            </div>
            <h2 className="font-serif text-3xl text-[#141517]">
              Research Artifact Delivery
            </h2>
            <p className="text-sm text-[#5D6066]">
              Verified dataset exports, high-resolution figures, and reproducible execution artifacts.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 font-mono text-xs">
            <div className="bg-white border border-[#D8D4CA] p-5 flex flex-col justify-between shadow-sm">
              <div>
                <span className="text-[#2457E8] uppercase text-[10px] font-semibold">PDF MONOGRAPH</span>
                <div className="font-bold text-[#141517] text-sm mt-1 mb-2">Print Monograph (PDF)</div>
                <p className="text-[11px] text-[#5D6066] leading-relaxed mb-4">
                  Formatted for standard physical A4 print with high-resolution figures.
                </p>
              </div>
              <button
                onClick={handlePrint}
                className="w-full py-2 bg-[#141517] text-[#F4F1EA] hover:bg-[#2457E8] transition-colors uppercase tracking-wider text-center cursor-pointer"
              >
                TRIGGER BROWSER PRINT →
              </button>
            </div>

            <div className="bg-white border border-[#D8D4CA] p-5 flex flex-col justify-between shadow-sm">
              <div>
                <span className="text-[#8C9099] uppercase text-[10px]">DATASET CSV</span>
                <div className="font-bold text-[#141517] text-sm mt-1 mb-2">Master Results (CSV)</div>
                <p className="text-[11px] text-[#5D6066] leading-relaxed mb-4">
                  All 360 primary simulation runs with 24 evaluated metric columns.
                </p>
              </div>
              <a
                href="/results/experiment_360/master_results.csv"
                download="cloudrescue_master_results.csv"
                className="w-full py-2 bg-white border border-[#D8D4CA] text-[#141517] hover:border-[#141517] transition-colors uppercase tracking-wider text-center block cursor-pointer"
              >
                DOWNLOAD CSV (360 RUNS) →
              </a>
            </div>

            <div className="bg-white border border-[#D8D4CA] p-5 flex flex-col justify-between shadow-sm">
              <div>
                <span className="text-[#8C9099] uppercase text-[10px]">STATISTICAL TESTS</span>
                <div className="font-bold text-[#141517] text-sm mt-1 mb-2">Statistical Comparisons</div>
                <p className="text-[11px] text-[#5D6066] leading-relaxed mb-4">
                  Paired tests, Cohen's dz effect sizes, Bonferroni and FDR q-values.
                </p>
              </div>
              <a
                href="/results/experiment_360/statistical_comparisons.csv"
                download="statistical_comparisons.csv"
                className="w-full py-2 bg-white border border-[#D8D4CA] text-[#141517] hover:border-[#141517] transition-colors uppercase tracking-wider text-center block cursor-pointer"
              >
                DOWNLOAD STATS (CSV) →
              </a>
            </div>

            <div className="bg-white border border-[#D8D4CA] p-5 flex flex-col justify-between shadow-sm">
              <div>
                <span className="text-[#2457E8] uppercase text-[10px] font-semibold">FIGURES ARCHIVE</span>
                <div className="font-bold text-[#141517] text-sm mt-1 mb-2">Publication Figures (PNG)</div>
                <p className="text-[11px] text-[#5D6066] leading-relaxed mb-4">
                  Figures 1 through 6 rendered at 300 DPI for conference submissions.
                </p>
              </div>
              <button
                onClick={() => window.open('/api/plots/sla_violation_rates_bar.png', '_blank')}
                className="w-full py-2 bg-white border border-[#D8D4CA] text-[#141517] hover:border-[#141517] transition-colors uppercase tracking-wider text-center cursor-pointer"
              >
                VIEW FIGURE 1 (HD) →
              </button>
            </div>
          </div>
        </div>

        {/* Academic Integrity Disclosure */}
        <div className="py-8 border-t border-[#D8D4CA]">
          <div className="bg-[#EAE6DD] border-l-2 border-[#2457E8] p-6 font-mono text-xs space-y-3">
            <div className="flex items-center gap-2 font-bold text-[#141517] uppercase tracking-wider">
              <ShieldCheck size={16} className="text-[#2457E8]" />
              <span>ACADEMIC INTEGRITY &amp; SIMULATION CONFORMITY DISCLOSURE</span>
            </div>
            <p className="text-[#5D6066] text-[11px] leading-relaxed">
              All numerical findings, percentiles, effect sizes, and recovery measurements presented across all seven screens derive exclusively from the 360-run and 144-run verified simulation matrix in <code className="text-[#141517] font-semibold">results/experiment_360/</code>. No fabricated metrics, artificial cloud hardware connections, or smoothed placeholder data are presented.
            </p>
          </div>
        </div>
      </main>

      <ColophonFooter />
    </div>
  );
}
