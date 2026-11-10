import React, { useState } from 'react';
import ColophonFooter from '../components/ColophonFooter';
import { Copy, Check, Info } from 'lucide-react';

export default function Screen6Methodology({ setActiveScreen }) {
  const [copied, setCopied] = useState(false);
  const [bibtexOpen, setBibtexOpen] = useState(false);

  const cliCommand =
    'python scripts/run_experiments.py --workers 4 --seeds 30 --duration 600';

  const copyToClipboard = () => {
    navigator.clipboard.writeText(cliCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full pt-16 min-h-screen bg-[#F4F1EA] text-[#141517]">
      <main className="w-full px-6 lg:px-12 py-10 lg:py-14">
        {/* Top Academic Header Tape */}
        <div className="w-full bg-[#EAE6DD] border-b border-[#D8D4CA] px-4 py-2 flex flex-wrap items-center justify-between gap-3 font-mono text-[11px] text-[#5D6066]">
          <div className="flex items-center gap-3">
            <span className="text-[#141517] font-semibold uppercase tracking-wider">
              CLOUD RESILIENCE RESEARCH PROTOCOL
            </span>
            <span>·</span>
            <span>WORKING PAPER SERIES</span>
            <span>·</span>
            <span>DOI: NOT ASSIGNED (PRE-SUBMISSION)</span>
          </div>
          <div className="flex items-center gap-4">
            <span>AUDIT: VERIFIED BIT-FOR-BIT</span>
            <span className="px-2 py-0.5 bg-[#2457E8] text-white uppercase font-bold text-[10px]">
              REPRODUCIBLE RESEARCH
            </span>
          </div>
        </div>

        {/* Title & Metadata Masthead */}
        <div className="py-10 border-b border-[#D8D4CA] space-y-4">
          <div className="flex flex-wrap items-baseline justify-between gap-3 font-mono text-xs">
            <div className="flex items-center gap-2 text-[#2457E8] font-semibold uppercase tracking-wider">
              <span>PROTOCOL SPECIFICATION</span>
              <span>·</span>
              <span>SECTION 06 // METHODOLOGY</span>
              <span>·</span>
              <span>ISSN: NOT ASSIGNED</span>
            </div>
            <div className="text-[#8C9099] uppercase tracking-wider">
              SIMULATION STUDY · 360-RUN PRIMARY EVALUATION MATRIX
            </div>
          </div>

          <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl text-[#141517] tracking-tight leading-none max-w-5xl">
            A controlled study of cloud failure and recovery.
          </h1>

          <p className="text-[#5D6066] font-light text-base lg:text-lg max-w-4xl leading-relaxed">
            Experimental methodology, discrete-event simulation architecture, and empirical verification protocols for autonomic brownout graceful degradation and brownout-aware load balancing (BALB).
          </p>

          {/* 4 Investigator & Project Tiles */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-6 border-t border-[#D8D4CA] font-mono text-xs">
            <div>
              <div className="text-[#8C9099] uppercase text-[10px] tracking-wider mb-1">
                RESEARCH GROUP
              </div>
              <div className="font-serif text-lg text-[#141517] font-semibold">
                CloudRescue Research Team
              </div>
              <div className="text-[#5D6066] text-[11px] mt-0.5">Distributed Resilience Lab</div>
              <div className="text-[#2457E8] text-[11px]">Pre-submission Working Paper</div>
            </div>

            <div>
              <div className="text-[#8C9099] uppercase text-[10px] tracking-wider mb-1">
                INSTITUTIONAL AFFILIATION
              </div>
              <div className="font-serif text-lg text-[#141517] font-semibold">
                IIIT Dharwad
              </div>
              <div className="text-[#5D6066] text-[11px] mt-0.5">Department of Computer Science</div>
              <div className="text-[#5D6066] text-[11px]">Cloud Systems Laboratory</div>
            </div>

            <div>
              <div className="text-[#8C9099] uppercase text-[10px] tracking-wider mb-1">
                TESTBED ENGINE
              </div>
              <div className="font-serif text-lg text-[#141517] font-semibold">
                Discrete-Event Simulator
              </div>
              <div className="text-[#5D6066] text-[11px] mt-0.5">Python SimPy-based Harness</div>
              <div className="text-[#2457E8] text-[11px]">Independent Simulation Core</div>
            </div>

            <div className="bg-[#EAE6DD] border border-[#D8D4CA] p-3 flex flex-col justify-between">
              <div>
                <div className="text-[#8C9099] uppercase text-[10px] tracking-wider mb-0.5">
                  ARTIFACT REPOSITORY
                </div>
                <div className="text-[#141517] font-medium text-[11px]">
                  results/experiment_360/
                  <br />
                  Total Primary Runs: 360
                  <br />
                  Seeds: 1001 to 1030 (Matched)
                </div>
              </div>
              <div className="text-[#2457E8] font-bold text-[10px] mt-2">
                SLA THRESHOLD: 100.0 ms
              </div>
            </div>
          </div>
        </div>

        {/* Academic Body: 2 Columns */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 py-10 items-start">
          {/* Left Column (7 cols) */}
          <div className="lg:col-span-7 space-y-8">
            {/* [01] Abstract */}
            <article className="bg-white border border-[#D8D4CA] p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-[#D8D4CA] pb-2 font-mono text-xs">
                <span className="font-bold text-[#2457E8] uppercase tracking-wider">
                  [01] ABSTRACT &amp; ARCHIVAL TAXONOMY
                </span>
                <span className="text-[#8C9099]">SECTION 06.01</span>
              </div>
              <p className="text-sm leading-relaxed text-[#141517] text-justify font-sans">
                Contemporary hyper-scale cloud recovery mechanisms inherently rely on heuristic-driven retry intervals and unbounded backoff models. Under saturated ingress conditions exceeding normal capacity, these heuristic timeouts generate self-inflicted retry storms, causing transient micro-outages to cascade into total multi-node failure domains. This investigation demonstrates an empirical methodology for measuring failover determinism using active brownout graceful degradation and brownout-aware load balancing (BALB) within an isolated, reproducible simulation test harness.
              </p>
              <div className="flex flex-wrap gap-2 pt-2 border-t border-[#D8D4CA] font-mono text-[10px]">
                <span className="font-semibold text-[#141517] uppercase">INDEX TERMS:</span>
                <span className="bg-[#F4F1EA] px-2 py-0.5 border border-[#D8D4CA]">Brownout Degradation</span>
                <span className="bg-[#F4F1EA] px-2 py-0.5 border border-[#D8D4CA]">BALB Load Balancing</span>
                <span className="bg-[#F4F1EA] px-2 py-0.5 border border-[#D8D4CA]">PI Velocity Controller</span>
                <span className="bg-[#F4F1EA] px-2 py-0.5 border border-[#D8D4CA]">Anti-Windup Clamping</span>
                <span className="bg-[#F4F1EA] px-2 py-0.5 border border-[#D8D4CA]">Common Random Numbers (CRN)</span>
              </div>
            </article>

            {/* [02] Research Hypotheses */}
            <article className="bg-white border border-[#D8D4CA] p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-[#D8D4CA] pb-2 font-mono text-xs">
                <span className="font-bold text-[#2457E8] uppercase tracking-wider">
                  [02] FORMAL RESEARCH HYPOTHESES (H1,1 - H1,3)
                </span>
                <span className="text-[#8C9099]">EVALUATION STATUS</span>
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div className="p-3 bg-[#F4F1EA] border border-[#D8D4CA]">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-[#141517]">HYPOTHESIS H1,1: SLA VIOLATION REDUCTION</span>
                    <span className="text-[#24845A] font-bold">[SUPPORTED: p &lt; 10⁻⁴⁵]</span>
                  </div>
                  <p className="text-[11px] text-[#5D6066] leading-relaxed">
                    Brownout degradation (CFG-B &amp; CFG-C) significantly reduces overall SLA failure rates (V_overall) across all stress scenarios compared to unprotected baseline (CFG-A). In Flash Crowd, V_overall falls by 41.10% (p &lt; 10⁻⁶⁰); in Server Crash, V_overall falls by 27.05% (p &lt; 10⁻⁵²).
                  </p>
                </div>

                <div className="p-3 bg-[#F4F1EA] border border-[#D8D4CA]">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-[#141517]">HYPOTHESIS H1,2: RECOVERY ACCELERATION</span>
                    <span className="text-[#24845A] font-bold">[SUPPORTED: 2.1x SPEEDUP]</span>
                  </div>
                  <p className="text-[11px] text-[#5D6066] leading-relaxed">
                    During active stress, the closed-loop PI controller adapts within 2.50s across 100% of seeds. Post-repair recovery (DEC-010) is accelerated 2.06x to 2.15x over CFG-B (133.5s vs 286.5s median in Server Crash, p = 2.37x10⁻⁵, 29/30 recovered).
                  </p>
                </div>

                <div className="p-3 bg-[#F4F1EA] border border-[#D8D4CA]">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-[#141517]">HYPOTHESIS H1,3: BALB LOAD BALANCING VALUE</span>
                    <span className="text-[#F0A14A] font-bold">[PARTIALLY SUPPORTED]</span>
                  </div>
                  <p className="text-[11px] text-[#5D6066] leading-relaxed">
                    BALB decisively cures JSQ load imbalance under brownout (Jain's index J increases from 0.65 to 0.998, p &lt; 10⁻⁸), but trades off service fidelity (F drops by 11% to 16%, p &lt; 10⁻³⁸), establishing an authentic engineering trade-off.
                  </p>
                </div>
              </div>
            </article>

            {/* [03] Multi-Stream PRNG Isolation Diagram */}
            <article className="bg-white border border-[#D8D4CA] p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-[#D8D4CA] pb-2 font-mono text-xs">
                <span className="font-bold text-[#2457E8] uppercase tracking-wider">
                  [03] MULTI-STREAM PRNG DETERMINISTIC ISOLATION
                </span>
                <span className="text-[#8C9099]">DEC-002 SPECIFICATION</span>
              </div>

              <p className="text-xs text-[#5D6066] leading-relaxed">
                To guarantee strict ceteris paribus across CFG-A, CFG-B, and CFG-C, each simulation run instantiates independent PRNG sub-streams from the master seed:
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 font-mono text-[10px] text-center">
                <div className="p-2.5 bg-[#F4F1EA] border border-[#D8D4CA]">
                  <div className="font-bold text-[#141517]">STREAM 0</div>
                  <div className="text-[#5D6066] mt-1">Arrivals</div>
                  <div className="text-[#2457E8] mt-0.5">Exp(λ)</div>
                </div>
                <div className="p-2.5 bg-[#F4F1EA] border border-[#D8D4CA]">
                  <div className="font-bold text-[#141517]">STREAM 1</div>
                  <div className="text-[#5D6066] mt-1">Worker 0 Service</div>
                  <div className="text-[#2457E8] mt-0.5">Exp(μ_mand)</div>
                </div>
                <div className="p-2.5 bg-[#F4F1EA] border border-[#D8D4CA]">
                  <div className="font-bold text-[#141517]">STREAM 2</div>
                  <div className="text-[#5D6066] mt-1">Worker 1 Service</div>
                  <div className="text-[#2457E8] mt-0.5">Exp(μ_mand)</div>
                </div>
                <div className="p-2.5 bg-[#F4F1EA] border border-[#D8D4CA]">
                  <div className="font-bold text-[#141517]">STREAM 3</div>
                  <div className="text-[#5D6066] mt-1">Worker 2 Service</div>
                  <div className="text-[#2457E8] mt-0.5">Exp(μ_mand)</div>
                </div>
                <div className="p-2.5 bg-[#F4F1EA] border border-[#D8D4CA]">
                  <div className="font-bold text-[#141517]">STREAM 4</div>
                  <div className="text-[#5D6066] mt-1">Worker 3 Service</div>
                  <div className="text-[#2457E8] mt-0.5">Exp(μ_mand)</div>
                </div>
              </div>

              <div className="p-3 bg-[#EAE6DD] border-l-2 border-[#2457E8] font-mono text-xs text-[#141517]">
                INVARIANT VERIFIED: Across all 360 runs, identical request arrival sequences were delivered with Δt = 0.000 ms between matched configurations.
              </div>
            </article>
          </div>

          {/* Right Column (5 cols) */}
          <div className="lg:col-span-5 space-y-8">
            {/* [04] Mathematical Formulations */}
            <article className="bg-white border border-[#D8D4CA] p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-[#D8D4CA] pb-2 font-mono text-xs">
                <span className="font-bold text-[#2457E8] uppercase tracking-wider">
                  [04] MATHEMATICAL FORMULATIONS
                </span>
                <span className="text-[#8C9099]">CONTROL THEORY</span>
              </div>

              <div className="space-y-4 font-mono text-xs">
                <div>
                  <span className="text-[#8C9099] uppercase text-[10px] block mb-1">
                    1. PI VELOCITY-FORM CONTROLLER WITH CLAMPING
                  </span>
                  <div className="p-2.5 bg-[#F4F1EA] border border-[#D8D4CA] text-center italic text-sm">
                    Δθ_k = K_p · (e_k − e_{'{k-1}'}) + K_i · e_k
                  </div>
                  <p className="text-[11px] text-[#5D6066] mt-1">
                    Where error e_k = LAT_target − P95_k (LAT_target = 80 ms, SLA = 100 ms). Output clamped: θ_{'{k}'} = max(0, min(1, θ_{'{k-1}'} + Δθ_k)).
                  </p>
                </div>

                <div>
                  <span className="text-[#8C9099] uppercase text-[10px] block mb-1">
                    2. BALB COMPOSITE DISPATCH SCORE
                  </span>
                  <div className="p-2.5 bg-[#F4F1EA] border border-[#D8D4CA] text-center italic text-sm">
                    S_i = α · q_i + β · (1 − θ_i) · q_max + γ · max(0, P95_i − SLA)
                  </div>
                  <p className="text-[11px] text-[#5D6066] mt-1">
                    Ingress dispatched to worker argmin_i(S_i). Default parameters: α=1.0, β=1.0, γ=0.5.
                  </p>
                </div>

                <div>
                  <span className="text-[#8C9099] uppercase text-[10px] block mb-1">
                    3. DEC-010 NOMINAL REFERENCE RESTORATION
                  </span>
                  <div className="p-2.5 bg-[#F4F1EA] border border-[#D8D4CA] text-center italic text-sm">
                    θ_w(t) ≥ 0.95 · θ_nom*(c, s, w) and P95_w(t) ≤ 80 ms (sustained 3.0s)
                  </div>
                  <p className="text-[11px] text-[#5D6066] mt-1">
                    Where θ_nom* is calculated individually per worker from matching stable nominal runs.
                  </p>
                </div>
              </div>
            </article>

            {/* [05] Reproducibility Test Harness */}
            <article className="bg-[#141517] text-[#F4F1EA] p-6 shadow-sm space-y-4 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-white/20 pb-2">
                <span className="text-[#2457E8] font-bold uppercase tracking-wider">
                  [05] REPRODUCIBILITY TEST HARNESS
                </span>
                <span className="text-white/60">CLI REPLICATION</span>
              </div>

              <p className="text-white/80 text-[11px] leading-relaxed">
                Replicate the complete 360-run experimental matrix locally using Python and the verified seed matrix:
              </p>

              <div className="bg-black/50 p-3 border border-white/10 relative group">
                <code className="text-[#2457E8] break-all leading-normal text-xs block">
                  $ {cliCommand}
                </code>
                <button
                  onClick={copyToClipboard}
                  className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 bg-white/10 hover:bg-white/20 text-white text-[10px] uppercase tracking-wider transition-colors cursor-pointer"
                >
                  {copied ? <Check size={12} className="text-[#24845A]" /> : <Copy size={12} />}
                  <span>{copied ? 'COPIED' : 'COPY COMMAND'}</span>
                </button>
              </div>

              <div className="pt-2 text-[10px] text-white/60 flex justify-between">
                <span>RUNTIME: ~12 MIN (PARALLEL)</span>
                <span className="text-[#2457E8]">DATA: results/experiment_360/</span>
              </div>
            </article>

            {/* [06] Research Assumptions & Scope */}
            <article className="bg-white border border-[#D8D4CA] p-6 shadow-sm space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-[#D8D4CA] pb-2">
                <span className="font-bold text-[#141517] uppercase tracking-wider">
                  [06] SIMULATION SCOPE &amp; BOUNDARIES
                </span>
                <span className="text-[#8C9099]">METHODOLOGICAL DISCLOSURE</span>
              </div>
              <ul className="space-y-2 text-[11px] text-[#5D6066]">
                <li className="flex items-start gap-2">
                  <span className="text-[#2457E8] font-bold">1.</span>
                  <span>Results derive from discrete-event queuing simulations, not physical multi-tenant cloud hardware.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#2457E8] font-bold">2.</span>
                  <span>Arrival processes follow Poisson distributions with stationary rates (nominal 80 req/s, surge 240 req/s).</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#2457E8] font-bold">3.</span>
                  <span>Crash-stop failures assume instantaneous node dropouts without kernel hangs or partial socket leakage.</span>
                </li>
              </ul>
            </article>
          </div>
        </div>

        {/* Bottom BibTeX Drawer & Action Strip */}
        <div className="border-t border-[#D8D4CA] pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-xs">
          <div className="text-[#5D6066]">
            CloudRescue Research Project. (2026). <em className="text-[#141517]">A controlled study of cloud failure and recovery: Discrete-event simulation and empirical analysis</em>. Working Paper.
          </div>
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={() => setBibtexOpen(!bibtexOpen)}
              className="flex-1 sm:flex-initial px-4 py-2 bg-white border border-[#D8D4CA] text-[#141517] hover:border-[#141517] transition-colors cursor-pointer uppercase tracking-wider"
            >
              {bibtexOpen ? 'HIDE CITATION' : 'EXPORT CITATION'}
            </button>
            <button
              onClick={() => setActiveScreen('publication')}
              className="flex-1 sm:flex-initial px-4 py-2 bg-[#141517] text-[#F4F1EA] hover:bg-[#2457E8] transition-colors cursor-pointer uppercase tracking-wider"
            >
              PROCEED TO DOSSIER (07) →
            </button>
          </div>
        </div>

        {bibtexOpen && (
          <div className="mt-4 p-4 bg-white border border-[#D8D4CA] font-mono text-xs text-[#141517] shadow-sm overflow-x-auto">
            <pre className="text-[11px] leading-relaxed">
{`@techreport{cloudrescue2026controlled,
  author      = {{CloudRescue Research Team}},
  title       = {A controlled study of cloud failure and recovery: Experimental methodology and empirical verification},
  institution = {Department of Computer Science, IIIT Dharwad},
  year        = {2026},
  note        = {Pre-submission research working paper, certified 360-run simulation matrix},
  url         = {results/experiment_360/master_results.csv}
}`}
            </pre>
          </div>
        )}
      </main>

      <ColophonFooter sectionNumber="06" />
    </div>
  );
}
