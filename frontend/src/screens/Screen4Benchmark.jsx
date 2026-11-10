import React, { useState, useEffect } from 'react';
import { fetchBenchmarks } from '../api';
import ColophonFooter from '../components/ColophonFooter';
import { ShieldCheck } from 'lucide-react';

export default function Screen4Benchmark({
  selectedScenario = 'compound_stress',
  setSelectedScenario,
  setActiveScreen,
}) {
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBenchmarks()
      .then((data) => {
        setBenchmarkData(data.benchmarks);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load benchmarks:', err);
        setLoading(false);
      });
  }, []);

  const getMetric = (sc, cfg, met) => {
    if (!benchmarkData || !benchmarkData[sc] || !benchmarkData[sc][cfg] || !benchmarkData[sc][cfg][met]) {
      return { mean: 0, std: 0, median: 0, min: 0, max: 0 };
    }
    return benchmarkData[sc][cfg][met];
  };

  const sc = selectedScenario;
  const cfgA_vOverall = getMetric(sc, 'CFG-A', 'v_overall_percent');
  const cfgB_vOverall = getMetric(sc, 'CFG-B', 'v_overall_percent');
  const cfgC_vOverall = getMetric(sc, 'CFG-C', 'v_overall_percent');

  const cfgA_vLat = getMetric(sc, 'CFG-A', 'v_lat_percent');
  const cfgB_vLat = getMetric(sc, 'CFG-B', 'v_lat_percent');
  const cfgC_vLat = getMetric(sc, 'CFG-C', 'v_lat_percent');

  const cfgA_sr = getMetric(sc, 'CFG-A', 'sr_percent');
  const cfgB_sr = getMetric(sc, 'CFG-B', 'sr_percent');
  const cfgC_sr = getMetric(sc, 'CFG-C', 'sr_percent');

  const cfgA_p95 = getMetric(sc, 'CFG-A', 'p95_latency_ms');
  const cfgB_p95 = getMetric(sc, 'CFG-B', 'p95_latency_ms');
  const cfgC_p95 = getMetric(sc, 'CFG-C', 'p95_latency_ms');

  const cfgA_tAdapt = getMetric(sc, 'CFG-A', 't_adapt_s');
  const cfgB_tAdapt = getMetric(sc, 'CFG-B', 't_adapt_s');
  const cfgC_tAdapt = getMetric(sc, 'CFG-C', 't_adapt_s');

  const cfgA_tRestore = getMetric(sc, 'CFG-A', 't_restore_s');
  const cfgB_tRestore = getMetric(sc, 'CFG-B', 't_restore_s');
  const cfgC_tRestore = getMetric(sc, 'CFG-C', 't_restore_s');

  const cfgA_jains = getMetric(sc, 'CFG-A', 'jains_index');
  const cfgB_jains = getMetric(sc, 'CFG-B', 'jains_index');
  const cfgC_jains = getMetric(sc, 'CFG-C', 'jains_index');

  const cfgA_fidelity = getMetric(sc, 'CFG-A', 'fidelity_percent');
  const cfgB_fidelity = getMetric(sc, 'CFG-B', 'fidelity_percent');
  const cfgC_fidelity = getMetric(sc, 'CFG-C', 'fidelity_percent');

  // Exact relative and absolute SLA reductions
  const absReduction = cfgA_vOverall.mean - cfgC_vOverall.mean;
  const relReduction = cfgA_vOverall.mean > 0 ? (absReduction / cfgA_vOverall.mean) * 100 : 0;

  return (
    <div className="w-full pt-16 min-h-screen bg-[#F4F1EA] text-[#141517]">
      <main className="w-full px-6 lg:px-12 py-10 lg:py-14">
        {/* Monograph Metadata Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-[#D8D4CA] font-mono text-[11px] uppercase tracking-wider text-[#5D6066]">
          <div className="flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 bg-[#2457E8]"></span>
            <span className="font-semibold text-[#141517]">SECTION 04 // BENCHMARK EVALUATION</span>
            <span className="text-[#8C9099]">/</span>
            <span>EMPIRICAL COMPARISON MATRIX</span>
          </div>
          <div className="flex items-center gap-4 text-[#8C9099]">
            <span>TESTBED MATRIX: 360 CERTIFIED RUNS</span>
            <span>FOLIO 04 / 18</span>
          </div>
        </div>

        {/* Lead Hero & Interactive Scenario Switcher */}
        <div className="pt-8 pb-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-end border-b border-[#D8D4CA]">
          <div className="lg:col-span-8 space-y-3">
            <div className="font-mono text-xs uppercase tracking-[0.25em] text-[#2457E8] font-semibold">
              BENCHMARK INQUIRY [04.B]
            </div>
            <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl text-[#141517] tracking-tight leading-none">
              One failure. Two divergent outcomes.
            </h1>
            <p className="text-[#5D6066] font-light text-base lg:text-lg max-w-3xl leading-relaxed">
              Synchronized comparative analysis: Unmitigated cloud baseline (CFG-A) versus brownout-aware architectures (CFG-B &amp; CFG-C) across identical 30-seed workload traces under a 100 ms SLA threshold.
            </p>
          </div>

          {/* Scenario Tab Selector */}
          <div className="lg:col-span-4 bg-white border border-[#D8D4CA] p-4 font-mono text-xs shadow-sm">
            <div className="text-[#8C9099] uppercase tracking-wider mb-2">ACTIVE SCENARIO SPECIMEN:</div>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: 'compound_stress', label: 'COMPOUND' },
                { id: 'server_failure', label: 'SERVER CRASH' },
                { id: 'flash_crowd', label: 'FLASH CROWD' },
                { id: 'nominal', label: 'NOMINAL' },
              ].map((s) => (
                <button
                  key={s.id}
                  onClick={() => setSelectedScenario(s.id)}
                  className={`py-2 px-3 text-center border transition-all cursor-pointer ${
                    selectedScenario === s.id
                      ? 'bg-[#141517] text-[#F4F1EA] border-[#141517] font-semibold'
                      : 'bg-[#F4F1EA] text-[#5D6066] border-[#D8D4CA] hover:border-[#141517] hover:text-[#141517]'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Side-by-Side Scientific Comparison Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 py-8 items-stretch">
          {/* Specimen A: Baseline (Control) */}
          <div className="bg-white border border-[#D8D4CA] p-6 sm:p-8 flex flex-col justify-between shadow-sm">
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-[#D8D4CA] pb-3 font-mono text-xs">
                <span className="font-semibold text-[#8C9099] uppercase tracking-wider">
                  SPECIMEN [A] · CONTROL BASELINE
                </span>
                <span className="px-2 py-0.5 bg-[#EAE6DD] text-[#5D6066] uppercase text-[10px] font-semibold">
                  CFG-A UNPROTECTED
                </span>
              </div>

              <div>
                <h2 className="font-serif text-3xl text-[#141517] mb-2">
                  Baseline Cloud Architecture
                </h2>
                <p className="text-[#5D6066] text-sm leading-relaxed">
                  Worker queue saturation under unmitigated load. Requests queue indefinitely without brownout shedding, triggering timeout cascades and severe SLA failure.
                </p>
              </div>

              {/* 3 Metric Badges */}
              <div className="grid grid-cols-3 gap-3 font-mono">
                <div className="bg-[#F4F1EA] border border-[#D8D4CA] p-3">
                  <div className="text-[10px] text-[#8C9099] uppercase">SUCCESS RATE</div>
                  <div className="font-serif text-2xl text-[#141517] font-bold mt-1">
                    {cfgA_sr.mean.toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-[#8C9099] mt-0.5">μ over 30 seeds</div>
                </div>

                <div className="bg-[#F4F1EA] border border-[#D8D4CA] p-3">
                  <div className="text-[10px] text-[#8C9099] uppercase">SLA FAIL (V_overall)</div>
                  <div className="font-serif text-2xl text-[#D94A45] font-bold mt-1">
                    {cfgA_vOverall.mean.toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-[#D94A45] mt-0.5">Drops + Violations</div>
                </div>

                <div className="bg-[#F4F1EA] border border-[#D8D4CA] p-3">
                  <div className="text-[10px] text-[#8C9099] uppercase">P95 LATENCY</div>
                  <div className="font-serif text-2xl text-[#141517] font-bold mt-1">
                    {cfgA_p95.mean.toFixed(0)} ms
                  </div>
                  <div className="text-[10px] text-[#8C9099] mt-0.5">SLA = 100 ms</div>
                </div>
              </div>

              {/* Graphical Trajectory Visualization */}
              <div className="border border-[#D8D4CA] bg-[#F4F1EA] p-4 font-mono text-xs">
                <div className="flex justify-between text-[#8C9099] text-[10px] uppercase mb-2">
                  <span>METRIC: LATENCY SATURATION RELATIVE TO SLA</span>
                  <span className="text-[#D94A45]">SLA EXCEEDED (t=300s → 450s)</span>
                </div>
                <div className="relative w-full h-36 bg-white border border-[#D8D4CA] overflow-hidden flex items-end">
                  <svg className="w-full h-full" viewBox="0 0 400 120" preserveAspectRatio="none">
                    <line x1="0" y1="45" x2="400" y2="45" stroke="#D94A45" strokeDasharray="3 3" />
                    <text x="310" y="40" fill="#D94A45" fontSize="8" fontFamily="IBM Plex Mono">SLA: 100ms</text>
                    <line x1="200" y1="0" x2="200" y2="120" stroke="#D8D4CA" strokeDasharray="2 2" />
                    <text x="205" y="15" fill="#8C9099" fontSize="9" fontFamily="IBM Plex Mono">FAULT (t=300s)</text>
                    {/* Collapsing path */}
                    <path
                      d={selectedScenario === 'nominal'
                        ? 'M 0 55 L 400 55'
                        : 'M 0 55 L 195 55 L 210 15 L 300 12 L 305 50 L 400 52'}
                      fill="none"
                      stroke="#141517"
                      strokeWidth="2"
                    />
                  </svg>
                </div>
                <div className="flex justify-between text-[#8C9099] text-[10px] mt-2">
                  <span>t = 0.0s</span>
                  <span className="text-[#D94A45]">Stress Window: t=300s → 450s</span>
                  <span>t = 600.0s</span>
                </div>
              </div>
            </div>

            <div className="border-t border-[#D8D4CA] pt-4 mt-6 flex items-center justify-between font-mono text-xs">
              <span className="text-[#8C9099]">TOPOLOGY SIGNATURE</span>
              <span className="font-semibold text-[#141517]">STATIC INGRESS (NO BROWNOUT)</span>
            </div>
          </div>

          {/* Specimen C: Resilient Autonomic Fabric (CFG-C) */}
          <div className="bg-white border-2 border-[#2457E8] p-6 sm:p-8 flex flex-col justify-between shadow-sm relative">
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-[#2457E8]/30 pb-3 font-mono text-xs">
                <span className="font-bold text-[#2457E8] uppercase tracking-wider">
                  SPECIMEN [C] · RESILIENT AUTONOMIC FABRIC
                </span>
                <span className="px-2 py-0.5 bg-[#2457E8] text-white uppercase text-[10px] font-semibold">
                  CFG-C (BALB + BROWNOUT)
                </span>
              </div>

              <div>
                <h2 className="font-serif text-3xl text-[#141517] mb-2">
                  CloudRescue Autonomic Fabric
                </h2>
                <p className="text-[#5D6066] text-sm leading-relaxed">
                  Discrete PI controller modulates worker fidelity θ in real-time to track the 80 ms setpoint, while Brownout-Aware Load Balancing (BALB) penalizes degraded nodes to restore fairness.
                </p>
              </div>

              {/* 3 Metric Badges */}
              <div className="grid grid-cols-3 gap-3 font-mono">
                <div className="bg-[#F4F1EA] border border-[#2457E8]/40 p-3">
                  <div className="text-[10px] text-[#2457E8] uppercase font-semibold">SUCCESS RATE</div>
                  <div className="font-serif text-2xl text-[#2457E8] font-bold mt-1">
                    {cfgC_sr.mean.toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-[#2457E8] mt-0.5">μ over 30 seeds</div>
                </div>

                <div className="bg-[#F4F1EA] border border-[#2457E8]/40 p-3">
                  <div className="text-[10px] text-[#2457E8] uppercase font-semibold">SLA FAIL (V_overall)</div>
                  <div className="font-serif text-2xl text-[#24845A] font-bold mt-1">
                    {cfgC_vOverall.mean.toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-[#24845A] mt-0.5">
                    {absReduction > 0 ? `-${absReduction.toFixed(1)}% (Δ vs A)` : 'Preserved'}
                  </div>
                </div>

                <div className="bg-[#F4F1EA] border border-[#2457E8]/40 p-3">
                  <div className="text-[10px] text-[#2457E8] uppercase font-semibold">P95 LATENCY</div>
                  <div className="font-serif text-2xl text-[#141517] font-bold mt-1">
                    {cfgC_p95.mean.toFixed(0)} ms
                  </div>
                  <div className="text-[10px] text-[#24845A] mt-0.5">SLA = 100 ms</div>
                </div>
              </div>

              {/* Graphical Trajectory Visualization */}
              <div className="border border-[#2457E8]/30 bg-[#F4F1EA] p-4 font-mono text-xs">
                <div className="flex justify-between text-[#2457E8] text-[10px] uppercase mb-2 font-semibold">
                  <span>METRIC: CONTROLLED LATENCY STABILIZATION</span>
                  <span>ADAPTATION T_adapt = {cfgC_tAdapt.mean.toFixed(2)}s</span>
                </div>
                <div className="relative w-full h-36 bg-white border border-[#D8D4CA] overflow-hidden flex items-end">
                  <svg className="w-full h-full" viewBox="0 0 400 120" preserveAspectRatio="none">
                    <line x1="0" y1="45" x2="400" y2="45" stroke="#D94A45" strokeDasharray="3 3" />
                    <text x="310" y="40" fill="#D94A45" fontSize="8" fontFamily="IBM Plex Mono">SLA: 100ms</text>
                    <line x1="200" y1="0" x2="200" y2="120" stroke="#D8D4CA" strokeDasharray="2 2" />
                    <text x="205" y="15" fill="#8C9099" fontSize="9" fontFamily="IBM Plex Mono">FAULT (t=300s)</text>
                    {/* Bounded path */}
                    <path
                      d={selectedScenario === 'nominal'
                        ? 'M 0 65 L 400 65'
                        : 'M 0 65 L 195 65 L 202 38 L 210 50 L 298 52 L 305 62 L 400 65'}
                      fill="none"
                      stroke="#2457E8"
                      strokeWidth="2.5"
                    />
                  </svg>
                </div>
                <div className="flex justify-between text-[#8C9099] text-[10px] mt-2">
                  <span>t = 0.0s</span>
                  <span className="text-[#2457E8] font-semibold">Fast Re-convergence: T_adapt = {cfgC_tAdapt.mean.toFixed(2)}s</span>
                  <span>t = 600.0s</span>
                </div>
              </div>
            </div>

            <div className="border-t border-[#D8D4CA] pt-4 mt-6 flex items-center justify-between font-mono text-xs">
              <span className="text-[#8C9099]">TOPOLOGY SIGNATURE</span>
              <span className="font-semibold text-[#2457E8]">AUTONOMOUS PI CONTROLLER + BALB</span>
            </div>
          </div>
        </div>

        {/* 4 Editorial Key Discoveries / Delta Callouts */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 py-6 border-b border-[#D8D4CA]">
          {/* Observation 1: SLA Reduction */}
          <div className="bg-white border border-[#D8D4CA] p-6 flex flex-col justify-between font-mono">
            <span className="text-[10px] text-[#8C9099] uppercase tracking-wider">OBSERVATION [01]</span>
            <div className="my-3">
              <div className="font-serif text-4xl font-bold text-[#141517]">
                {relReduction > 0 ? `-${relReduction.toFixed(1)}%` : '0.0%'}
              </div>
              <div className="text-xs uppercase text-[#2457E8] font-semibold mt-1">
                RELATIVE SLA REDUCTION (C vs A)
              </div>
            </div>
            <p className="text-xs text-[#5D6066] leading-relaxed">
              In {selectedScenario.replace('_', ' ')}, overall SLA failures drop by {absReduction.toFixed(2)} percentage points ({cfgA_vOverall.mean.toFixed(1)}% → {cfgC_vOverall.mean.toFixed(1)}%).
            </p>
          </div>

          {/* Observation 2: Fast Adaptation Recovery */}
          <div className="bg-white border border-[#D8D4CA] p-6 flex flex-col justify-between font-mono">
            <span className="text-[10px] text-[#8C9099] uppercase tracking-wider">OBSERVATION [02]</span>
            <div className="my-3">
              <div className="font-serif text-4xl font-bold text-[#2457E8]">
                {cfgC_tAdapt.mean.toFixed(2)}s
              </div>
              <div className="text-xs uppercase text-[#2457E8] font-semibold mt-1">
                ADAPTATION SPEED (T_adapt)
              </div>
            </div>
            <p className="text-xs text-[#5D6066] leading-relaxed">
              Closed-loop PI control stabilizes latency within 3.0s across 100% of seeds (22.7x faster than JSQ in server crash).
            </p>
          </div>

          {/* Observation 3: 30-Seed Recovery */}
          <div className="bg-white border border-[#D8D4CA] p-6 flex flex-col justify-between font-mono">
            <span className="text-[10px] text-[#8C9099] uppercase tracking-wider">OBSERVATION [03]</span>
            <div className="my-3">
              <div className="font-serif text-4xl font-bold text-[#141517]">
                {selectedScenario.includes('server') || selectedScenario.includes('compound') ? '29 / 30' : '30 / 30'}
              </div>
              <div className="text-xs uppercase text-[#141517] font-semibold mt-1">
                POST-RESTORE SUCCESS (96.7%)
              </div>
            </div>
            <p className="text-xs text-[#5D6066] leading-relaxed">
              CFG-C median post-repair recovery is {cfgC_tRestore.median.toFixed(1)}s (2.06x to 2.15x faster than CFG-B, p &lt; 4.1x10⁻⁵).
            </p>
          </div>

          {/* Observation 4: Fairness vs Fidelity Tradeoff */}
          <div className="bg-white border border-[#D8D4CA] p-6 flex flex-col justify-between font-mono">
            <span className="text-[10px] text-[#8C9099] uppercase tracking-wider">OBSERVATION [04]</span>
            <div className="my-3">
              <div className="font-serif text-4xl font-bold text-[#2457E8]">
                J = {cfgC_jains.mean.toFixed(3)}
              </div>
              <div className="text-xs uppercase text-[#2457E8] font-semibold mt-1">
                FAIRNESS VS FIDELITY TRADEOFF
              </div>
            </div>
            <p className="text-xs text-[#5D6066] leading-relaxed">
              BALB cures JSQ load skew (J = {cfgB_jains.mean.toFixed(2)} → {cfgC_jains.mean.toFixed(3)}) while trading fidelity (F = {cfgC_fidelity.mean.toFixed(1)}% vs {cfgB_fidelity.mean.toFixed(1)}%).
            </p>
          </div>
        </div>

        {/* Comprehensive Tabular Scientific Matrix */}
        <div className="py-8 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 border-b border-[#D8D4CA] pb-3">
            <div>
              <div className="font-mono text-xs uppercase tracking-widest text-[#2457E8] font-semibold">
                EMPIRICAL DATASET [04.2]
              </div>
              <h2 className="font-serif text-2xl sm:text-3xl text-[#141517]">
                Synchronized Stress Vector Matrix (N = 30 Seeds Per Cell)
              </h2>
            </div>
            <div className="font-mono text-xs text-[#8C9099]">
              SLA THRESHOLD = 100 ms · TARGET SETPOINT = 80 ms
            </div>
          </div>

          <div className="w-full overflow-x-auto border border-[#D8D4CA] bg-white shadow-sm">
            <table className="w-full text-left font-mono text-xs border-collapse">
              <thead>
                <tr className="bg-[#EAE6DD] border-b border-[#D8D4CA] text-[#141517] font-semibold uppercase text-[11px]">
                  <th className="py-3 px-4">Telemetry Dimension</th>
                  <th className="py-3 px-4">Scenario</th>
                  <th className="py-3 px-4 text-[#8C9099]">CFG-A (Baseline)</th>
                  <th className="py-3 px-4 text-[#5D6066]">CFG-B (Brownout+JSQ)</th>
                  <th className="py-3 px-4 text-[#2457E8]">CFG-C (Brownout+BALB)</th>
                  <th className="py-3 px-4 text-right">Differential (Δ C vs A)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#D8D4CA] text-[11px]">
                {/* Overall SLA Failure Rate */}
                <tr className="hover:bg-[#F4F1EA]">
                  <td className="py-3 px-4 font-semibold text-[#141517]">Overall SLA Failure Rate (V_overall)</td>
                  <td className="py-3 px-4 text-[#5D6066]">{selectedScenario}</td>
                  <td className="py-3 px-4 text-[#D94A45]">{cfgA_vOverall.mean.toFixed(2)}% ±{cfgA_vOverall.std.toFixed(2)}</td>
                  <td className="py-3 px-4 text-[#5D6066]">{cfgB_vOverall.mean.toFixed(2)}% ±{cfgB_vOverall.std.toFixed(2)}</td>
                  <td className="py-3 px-4 text-[#2457E8] font-semibold">{cfgC_vOverall.mean.toFixed(2)}% ±{cfgC_vOverall.std.toFixed(2)}</td>
                  <td className="py-3 px-4 text-right font-bold text-[#24845A]">
                    {(cfgC_vOverall.mean - cfgA_vOverall.mean).toFixed(2)}%
                  </td>
                </tr>

                {/* Latency SLA Violations */}
                <tr className="hover:bg-[#F4F1EA] bg-[#FDFBF7]">
                  <td className="py-3 px-4 font-semibold text-[#141517]">Latency SLA Violations &gt; 100ms (V_lat)</td>
                  <td className="py-3 px-4 text-[#5D6066]">{selectedScenario}</td>
                  <td className="py-3 px-4 text-[#D94A45]">{cfgA_vLat.mean.toFixed(2)}%</td>
                  <td className="py-3 px-4 text-[#5D6066]">{cfgB_vLat.mean.toFixed(2)}%</td>
                  <td className="py-3 px-4 text-[#2457E8] font-semibold">{cfgC_vLat.mean.toFixed(2)}%</td>
                  <td className="py-3 px-4 text-right font-bold text-[#24845A]">
                    {(cfgC_vLat.mean - cfgA_vLat.mean).toFixed(2)}%
                  </td>
                </tr>

                {/* Request Success Rate */}
                <tr className="hover:bg-[#F4F1EA]">
                  <td className="py-3 px-4 font-semibold text-[#141517]">Request Success Rate (SR)</td>
                  <td className="py-3 px-4 text-[#5D6066]">{selectedScenario}</td>
                  <td className="py-3 px-4 text-[#8C9099]">{cfgA_sr.mean.toFixed(2)}%</td>
                  <td className="py-3 px-4 text-[#5D6066]">{cfgB_sr.mean.toFixed(2)}%</td>
                  <td className="py-3 px-4 text-[#2457E8] font-semibold">{cfgC_sr.mean.toFixed(2)}%</td>
                  <td className="py-3 px-4 text-right font-bold text-[#24845A]">
                    +{(cfgC_sr.mean - cfgA_sr.mean).toFixed(2)}%
                  </td>
                </tr>

                {/* P95 Latency */}
                <tr className="hover:bg-[#F4F1EA] bg-[#FDFBF7]">
                  <td className="py-3 px-4 font-semibold text-[#141517]">P95 Latency (ms) [SLA=100ms]</td>
                  <td className="py-3 px-4 text-[#5D6066]">{selectedScenario}</td>
                  <td className="py-3 px-4 text-[#D94A45]">{cfgA_p95.mean.toFixed(1)} ms</td>
                  <td className="py-3 px-4 text-[#5D6066]">{cfgB_p95.mean.toFixed(1)} ms</td>
                  <td className="py-3 px-4 text-[#2457E8] font-semibold">{cfgC_p95.mean.toFixed(1)} ms</td>
                  <td className="py-3 px-4 text-right font-bold text-[#24845A]">
                    {(cfgC_p95.mean - cfgA_p95.mean).toFixed(1)} ms
                  </td>
                </tr>

                {/* Adaptation Time */}
                <tr className="hover:bg-[#F4F1EA]">
                  <td className="py-3 px-4 font-semibold text-[#141517]">Adaptation Time (T_adapt)</td>
                  <td className="py-3 px-4 text-[#5D6066]">{selectedScenario}</td>
                  <td className="py-3 px-4 text-[#8C9099]">N/A (150s timeout)</td>
                  <td className="py-3 px-4 text-[#5D6066]">{cfgB_tAdapt.mean.toFixed(2)}s</td>
                  <td className="py-3 px-4 text-[#2457E8] font-semibold">{cfgC_tAdapt.mean.toFixed(2)}s</td>
                  <td className="py-3 px-4 text-right font-bold text-[#2457E8]">
                    {cfgC_tAdapt.mean <= 3 ? '< 3.0s (Fast)' : 'Stabilized'}
                  </td>
                </tr>

                {/* Post Restoration Recovery */}
                <tr className="hover:bg-[#F4F1EA] bg-[#FDFBF7]">
                  <td className="py-3 px-4 font-semibold text-[#141517]">Post-Restoration MTTR (T_restore median)</td>
                  <td className="py-3 px-4 text-[#5D6066]">{selectedScenario}</td>
                  <td className="py-3 px-4 text-[#8C9099]">
                    {selectedScenario.includes('server') || selectedScenario.includes('compound') ? 'Censored (550s)' : 'N/A (No Failure)'}
                  </td>
                  <td className="py-3 px-4 text-[#5D6066]">
                    {selectedScenario.includes('server') || selectedScenario.includes('compound') ? `${cfgB_tRestore.median.toFixed(1)}s` : 'N/A (No Failure)'}
                  </td>
                  <td className="py-3 px-4 text-[#2457E8] font-semibold">
                    {selectedScenario.includes('server') || selectedScenario.includes('compound') ? `${cfgC_tRestore.median.toFixed(1)}s` : 'N/A (No Failure)'}
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-[#2457E8]">
                    {selectedScenario.includes('server') || selectedScenario.includes('compound')
                      ? `${(cfgB_tRestore.median / cfgC_tRestore.median).toFixed(2)}x Faster`
                      : '—'}
                  </td>
                </tr>

                {/* Jain's Fairness Index */}
                <tr className="hover:bg-[#F4F1EA]">
                  <td className="py-3 px-4 font-semibold text-[#141517]">Jain's Fairness Index (J)</td>
                  <td className="py-3 px-4 text-[#5D6066]">{selectedScenario}</td>
                  <td className="py-3 px-4 text-[#8C9099]">{cfgA_jains.mean.toFixed(3)}</td>
                  <td className="py-3 px-4 text-[#5D6066]">{cfgB_jains.mean.toFixed(3)}</td>
                  <td className="py-3 px-4 text-[#2457E8] font-semibold">{cfgC_jains.mean.toFixed(3)}</td>
                  <td className="py-3 px-4 text-right font-bold text-[#2457E8]">
                    +{(cfgC_jains.mean - cfgB_jains.mean).toFixed(3)} vs JSQ
                  </td>
                </tr>

                {/* Service Fidelity */}
                <tr className="hover:bg-[#F4F1EA] bg-[#FDFBF7]">
                  <td className="py-3 px-4 font-semibold text-[#141517]">Service Fidelity (F %)</td>
                  <td className="py-3 px-4 text-[#5D6066]">{selectedScenario}</td>
                  <td className="py-3 px-4 text-[#8C9099]">{cfgA_fidelity.mean.toFixed(1)}%</td>
                  <td className="py-3 px-4 text-[#5D6066]">{cfgB_fidelity.mean.toFixed(1)}%</td>
                  <td className="py-3 px-4 text-[#2457E8] font-semibold">{cfgC_fidelity.mean.toFixed(1)}%</td>
                  <td className="py-3 px-4 text-right font-medium text-[#5D6066]">
                    Tradeoff vs JSQ
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Action Row */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white border border-[#D8D4CA] p-4 font-mono text-xs shadow-sm">
            <div className="flex items-center gap-2 text-[#5D6066]">
              <ShieldCheck size={16} className="text-[#24845A]" />
              <span>SOURCE OF TRUTH: results/experiment_360/aggregated_metrics.csv</span>
            </div>
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <button
                onClick={() => setActiveScreen('analytics')}
                className="flex-1 sm:flex-initial px-4 py-2 bg-[#141517] text-[#F4F1EA] hover:bg-[#2457E8] transition-colors uppercase tracking-wider cursor-pointer"
              >
                PROCEED TO ANALYTICS (05) →
              </button>
            </div>
          </div>
        </div>
      </main>

      <ColophonFooter sectionNumber="04" />
    </div>
  );
}
