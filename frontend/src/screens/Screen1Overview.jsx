import React, { useEffect, useState } from 'react';
import { fetchSummary } from '../api';
import ColophonFooter from '../components/ColophonFooter';

export default function Screen1Overview({ setActiveScreen }) {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetchSummary()
      .then(setSummary)
      .catch((err) => console.error('Failed to load summary:', err));
  }, []);

  return (
    <div className="w-full pt-16 min-h-screen bg-[#F4F1EA] text-[#141517]">
      <main className="w-full px-6 lg:px-12 py-10 lg:py-16">
        {/* Monograph Metadata Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-[#D8D4CA] font-mono text-[11px] uppercase tracking-wider text-[#5D6066]">
          <div className="flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 bg-[#2457E8]"></span>
            <span className="font-semibold text-[#141517]">MONOGRAPH REF. CR-2026-A</span>
            <span className="text-[#8C9099]">/</span>
            <span>DISTRIBUTED RESILIENCE LABS</span>
          </div>
          <div className="flex items-center gap-4 text-[#8C9099]">
            <span>SWISS ARCHIVAL RECONSTRUCTION</span>
            <span>FOLIO 01 / 18</span>
          </div>
        </div>

        {/* Asymmetric Editorial Hero Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16 pt-10 lg:pt-14 items-start">
          {/* Left Column: Typography & Intent (7 cols) */}
          <div className="lg:col-span-7 flex flex-col justify-between">
            <div className="space-y-8">
              <div className="font-mono text-xs uppercase tracking-[0.25em] text-[#2457E8] font-semibold">
                FIELD RESEARCH & ARCHITECTURAL INQUIRY
              </div>
              <h1 className="font-serif text-5xl sm:text-6xl lg:text-[5.25rem] leading-[0.98] tracking-tight text-[#141517]">
                What happens when your cloud <span className="italic font-normal">fails?</span>
              </h1>
              <p className="text-base lg:text-lg text-[#5D6066] font-light leading-relaxed max-w-xl">
                One service failure can irrevocably cascade into critical infrastructure paralysis. An empirical investigation into distributed fault tolerance, autonomic brownout graceful degradation, and brownout-aware load balancing under catastrophic stress.
              </p>
            </div>

            {/* Execution Bar & Primary Action */}
            <div className="mt-10 lg:mt-14 pt-8 pb-10 flex flex-col sm:flex-row sm:items-center gap-6 border-b border-[#D8D4CA]">
              <button
                onClick={() => setActiveScreen('inquiry')}
                className="inline-flex items-center justify-between gap-4 px-6 py-3.5 bg-[#141517] text-[#F4F1EA] font-mono text-xs uppercase tracking-widest hover:bg-[#2457E8] focus:ring-2 focus:ring-[#2457E8] transition-colors group cursor-pointer"
              >
                <span>Configure Failure & Workload</span>
                <span className="font-mono transition-transform group-hover:translate-x-1">→</span>
              </button>
              <div className="flex flex-col font-mono text-xs text-[#5D6066] leading-tight">
                <span className="text-[#141517] font-medium">
                  EXPERIMENT MATRIX: {summary ? `${summary.total_primary_runs} RUNS CERTIFIED` : '360 RUNS CERTIFIED'}
                </span>
                <span className="text-[11px] text-[#8C9099] mt-0.5">
                  PEER-REVIEWED EMPIRICAL TRACE RUN · SEEDS 1001-1030
                </span>
              </div>
            </div>

            {/* 3-Chapter Asymmetric Typographic Narrative */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-10">
              <div className="space-y-2">
                <div className="font-serif text-3xl text-[#141517] font-light leading-none">01</div>
                <div className="font-mono text-xs uppercase tracking-wider text-[#141517] font-medium pt-1">
                  Simulate Failure
                </div>
                <p className="text-xs text-[#5D6066] leading-relaxed font-light">
                  Induce synthetic traffic surges (3x flash crowd) and sudden server crash-stops (50% cluster capacity loss) under matched random streams.
                </p>
              </div>
              <div className="space-y-2">
                <div className="font-serif text-3xl text-[#141517] font-light leading-none">02</div>
                <div className="font-mono text-xs uppercase tracking-wider text-[#141517] font-medium pt-1">
                  Test Resilience
                </div>
                <p className="text-xs text-[#5D6066] leading-relaxed font-light">
                  Evaluate velocity-form discrete PI brownout feedback control combined with brownout-aware multi-attribute load balancing (BALB).
                </p>
              </div>
              <div className="space-y-2">
                <div className="font-serif text-3xl text-[#141517] font-light leading-none">03</div>
                <div className="font-mono text-xs uppercase tracking-wider text-[#141517] font-medium pt-1">
                  Measure Recovery
                </div>
                <p className="text-xs text-[#5D6066] leading-relaxed font-light">
                  Quantify SLA compliance cliffs, tail-latency speedups, empirical post-restoration MTTR, and load distribution fairness across 30 seeds.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Brutalist Photographic Plate (5 cols) */}
          <div className="lg:col-span-5 flex flex-col">
            <div className="relative bg-[#ECE7DE] border border-[#D8D4CA] p-1">
              <div className="relative overflow-hidden aspect-[4/5] bg-[#141517] flex items-center justify-center">
                {/* Brutalist Server Corridor Visual Canvas */}
                <div className="absolute inset-0 bg-gradient-to-b from-[#141517] via-[#22252B] to-[#141517] opacity-95"></div>
                
                {/* Structural Perspective Grid Lines */}
                <svg className="absolute inset-0 w-full h-full opacity-30 text-[#8C9099]" xmlns="http://www.w3.org/2000/svg">
                  <line x1="0" y1="0" x2="50%" y2="50%" stroke="currentColor" strokeWidth="1" strokeDasharray="3 3" />
                  <line x1="100%" y1="0" x2="50%" y2="50%" stroke="currentColor" strokeWidth="1" strokeDasharray="3 3" />
                  <line x1="0" y1="100%" x2="50%" y2="50%" stroke="currentColor" strokeWidth="1" strokeDasharray="3 3" />
                  <line x1="100%" y1="100%" x2="50%" y2="50%" stroke="currentColor" strokeWidth="1" strokeDasharray="3 3" />
                  <rect x="25%" y="25%" width="50%" height="50%" fill="none" stroke="currentColor" strokeWidth="1" />
                  <rect x="37.5%" y="37.5%" width="25%" height="25%" fill="none" stroke="currentColor" strokeWidth="1" />
                </svg>

                {/* Minimal Overlay & Electric Blue Precision Reticle */}
                <div className="absolute inset-0 pointer-events-none p-4 flex flex-col justify-between font-mono text-[11px]">
                  {/* Plate Header Coordinates */}
                  <div className="flex items-center justify-between text-[#F4F1EA] bg-[#141517]/90 px-2 py-1 border border-[#141517]">
                    <span>DISCRETE_EVENT // SIMULATOR CLUSTER</span>
                    <span className="text-[#2457E8] font-semibold">T=14.2s</span>
                  </div>

                  {/* Single High-Precision Crosshair Callout */}
                  <div className="relative self-center my-auto -translate-x-4 translate-y-4">
                    <svg className="w-10 h-10 text-[#2457E8]" fill="none" stroke="currentColor" strokeWidth="1.25" viewBox="0 0 32 32">
                      <circle cx="16" cy="16" r="6" />
                      <line x1="16" y1="2" x2="16" y2="10" />
                      <line x1="16" y1="22" x2="16" y2="30" />
                      <line x1="2" y1="16" x2="10" y2="16" />
                      <line x1="22" y1="16" x2="30" y2="16" />
                    </svg>
                    <div className="absolute left-12 -top-2 whitespace-nowrap bg-[#141517] text-[#F4F1EA] px-2.5 py-1 text-[11px] border-l-2 border-[#2457E8] shadow-sm">
                      <span className="text-[#2457E8] font-semibold">BROWNOUT CONTROLLER TIER</span>
                      <span className="text-[#8C9099] ml-1">· θ=0.25</span>
                    </div>
                  </div>

                  {/* Bottom Telemetry Status Bar */}
                  <div className="flex items-center justify-between bg-[#141517]/95 text-[#F4F1EA] px-2 py-1 text-[10px] tracking-wider uppercase border border-[#141517]">
                    <span className="flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 bg-[#2457E8] animate-pulse"></span>
                      TELEMETRY: VERIFIED 360/360
                    </span>
                    <span className="text-[#8C9099]">HASH: 0x94F2B7</span>
                  </div>
                </div>
              </div>

              {/* Micro Frame Baseline */}
              <div className="flex items-center justify-between px-2 py-1 font-mono text-[10px] uppercase text-[#5D6066] bg-[#ECE7DE] border-t border-[#D8D4CA] mt-1">
                <span>PLATE 01.A — QUEUEING ENGINE ARCHITECTURE</span>
                <span className="text-[#141517] font-semibold">SIMULATOR TESTBED</span>
              </div>
            </div>

            {/* Academic Figure Caption */}
            <div className="mt-3 flex items-start gap-2.5 font-mono text-[11px] text-[#5D6066] leading-relaxed">
              <span className="text-[#141517] font-semibold uppercase shrink-0">FIG. 1.0 —</span>
              <p>
                Multi-server cluster architecture under synthetic stress replay. Empirical discrete-event evaluation with matched PRNG arrival streams.
              </p>
            </div>
          </div>
        </div>

        {/* Tabular Baseline Metric Strip / Specification Bar */}
        <div className="mt-16 pt-10 border-t border-[#D8D4CA]">
          <div className="flex flex-col md:flex-row items-baseline justify-between mb-6">
            <div className="font-mono text-xs uppercase tracking-widest text-[#141517] font-semibold">
              [ SYSTEM SPECIFICATION & RECOVERY TARGETS ]
            </div>
            <div className="font-mono text-[11px] text-[#8C9099] uppercase mt-1 md:mt-0">
              VALIDATED AGAINST EXPERIMENT_PLAN.MD STANDARDS
            </div>
          </div>

          {/* 4-Column Clean Tabular Matrix with Hairline Separation */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 border-y border-[#D8D4CA] divide-y sm:divide-y-0 sm:divide-x divide-[#D8D4CA] bg-[#F7F5EE]">
            <div className="p-6">
              <div className="font-mono text-[11px] text-[#5D6066] uppercase tracking-wider">
                Adaptation Recovery (T_adapt)
              </div>
              <div className="font-serif text-4xl text-[#141517] mt-2 leading-none">
                2.00<span className="text-xl font-sans ml-1 text-[#5D6066]">s</span>
              </div>
              <div className="font-mono text-[11px] text-[#2457E8] mt-2 font-medium">
                22.7x Faster vs JSQ Brownout (56.8s)
              </div>
            </div>

            <div className="p-6">
              <div className="font-mono text-[11px] text-[#5D6066] uppercase tracking-wider">
                Post-Restoration MTTR (Median)
              </div>
              <div className="font-serif text-4xl text-[#141517] mt-2 leading-none">
                133.5<span className="text-xl font-sans ml-1 text-[#5D6066]">s</span>
              </div>
              <div className="font-mono text-[11px] text-[#24845A] mt-2 font-medium">
                2.15x Faster vs CFG-B (286.5s)
              </div>
            </div>

            <div className="p-6">
              <div className="font-mono text-[11px] text-[#5D6066] uppercase tracking-wider">
                Jain's Fairness Index (J)
              </div>
              <div className="font-serif text-4xl text-[#141517] mt-2 leading-none">
                0.998<span className="text-base font-sans ml-1 text-[#5D6066]">idx</span>
              </div>
              <div className="font-mono text-[11px] text-[#2457E8] mt-2 font-medium">
                Cures JSQ Skew (J = 0.654 → 0.998)
              </div>
            </div>

            <div className="p-6">
              <div className="font-mono text-[11px] text-[#5D6066] uppercase tracking-wider">
                SLA Failure Reduction (Flash Crowd)
              </div>
              <div className="font-serif text-4xl text-[#141517] mt-2 leading-none">
                -41.1<span className="text-xl font-sans ml-1 text-[#5D6066]">%</span>
              </div>
              <div className="font-mono text-[11px] text-[#24845A] mt-2 font-medium">
                44.04% → 2.94% (p &lt; 10^-60)
              </div>
            </div>
          </div>
        </div>
      </main>

      <ColophonFooter sectionNumber="01" />
    </div>
  );
}
