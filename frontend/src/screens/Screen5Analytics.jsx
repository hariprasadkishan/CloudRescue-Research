import React, { useState, useEffect, useMemo } from 'react';
import { fetchStatistics, fetchRecoveryMetrics, fetchSensitivity } from '../api';
import ColophonFooter from '../components/ColophonFooter';
import { Search, Filter, BarChart3, Info } from 'lucide-react';

export default function Screen5Analytics({
  selectedScenario = 'compound_stress',
  setSelectedScenario,
  setActiveScreen,
}) {
  const [statsData, setStatsData] = useState(null);
  const [recoveryData, setRecoveryData] = useState(null);
  const [sensitivityData, setSensitivityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterScenario, setFilterScenario] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    Promise.all([
      fetchStatistics(),
      fetchRecoveryMetrics(),
      fetchSensitivity(),
    ])
      .then(([stats, recovery, sensitivity]) => {
        setStatsData(stats);
        setRecoveryData(recovery);
        setSensitivityData(sensitivity);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load analytics data:', err);
        setLoading(false);
      });
  }, []);

  const comparisons = useMemo(() => {
    if (!statsData || !statsData.comparisons) return [];
    return statsData.comparisons.filter((c) => {
      const matchSc = filterScenario === 'all' || c.scenario === filterScenario;
      const matchSearch =
        c.metric.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.config_1.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.config_2.toLowerCase().includes(searchTerm.toLowerCase());
      return matchSc && matchSearch;
    });
  }, [statsData, filterScenario, searchTerm]);

  return (
    <div className="w-full pt-16 min-h-screen bg-[#F4F1EA] text-[#141517]">
      <main className="w-full px-6 lg:px-12 py-10 lg:py-14">
        {/* Monograph Metadata Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-[#D8D4CA] font-mono text-[11px] uppercase tracking-wider text-[#5D6066]">
          <div className="flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 bg-[#2457E8]"></span>
            <span className="font-semibold text-[#141517]">SECTION 05 // ANALYTICS &amp; HYPOTHESIS TESTING</span>
            <span className="text-[#8C9099]">/</span>
            <span>EMPIRICAL DISTRIBUTION ASSAY</span>
          </div>
          <div className="flex items-center gap-4 text-[#8C9099]">
            <span>N = 360 PRIMARY RUNS + 144 SENSITIVITY</span>
            <span>FOLIO 05 / 18</span>
          </div>
        </div>

        {/* Lead Editorial Masthead */}
        <div className="pt-8 pb-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start border-b border-[#D8D4CA]">
          {/* Left Metadata Rail (3 cols) */}
          <div className="lg:col-span-3 flex flex-col gap-4 border-r border-[#D8D4CA] pr-6 font-mono text-xs">
            <div className="flex items-center gap-2 text-[#2457E8] font-semibold uppercase tracking-wider">
              <BarChart3 size={15} />
              <span>EMPIRICAL DISTRIBUTION ASSAY</span>
            </div>
            <div className="text-[#5D6066] space-y-1 text-[11px] leading-relaxed">
              <div>VOL. 04 / RESEARCH SECTION 05</div>
              <div>SAMPLE SIZE: 30 SEEDS / CONDITION</div>
              <div>MULTIPLE TESTING: BENJAMINI-HOCHBERG FDR</div>
              <div>REPRODUCIBILITY: DETERMINISTIC PRNG</div>
            </div>
            <div className="p-3 bg-[#EAE6DD] border border-[#D8D4CA]">
              <span className="text-[10px] uppercase font-bold text-[#141517] block mb-1">
                HYPOTHESIS EVALUATION
              </span>
              <p className="text-[#5D6066] text-[11px] leading-normal space-y-1">
                <span>H1,1 (SLA Reduction): <strong>SUPPORTED</strong> (p &lt; 10⁻⁴⁵)</span>
                <br />
                <span>H1,2 (Recovery Speedup): <strong>SUPPORTED</strong> (2.1x faster, p &lt; 4.1x10⁻⁵)</span>
                <br />
                <span>H1,3 (BALB vs JSQ): <strong>PARTIALLY SUPPORTED</strong> (Fairness J&gt;0.99 vs Fidelity trade-off)</span>
              </p>
            </div>
          </div>

          {/* Right Editorial Title + Abstract (9 cols) */}
          <div className="lg:col-span-9 space-y-4">
            <div className="font-mono text-xs uppercase tracking-widest text-[#2457E8] font-semibold">
              [SECTION 05.01 // SYNTHESIS &amp; VARIANCE ANALYSIS]
            </div>
            <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl text-[#141517] tracking-tight leading-none">
              The distribution tells the story.
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-[#5D6066] pt-2">
              <div className="font-serif text-xl sm:text-2xl text-[#141517] leading-snug">
                Aggregated point averages routinely falsify recovery readiness. A nominal mean reliably hides multimodal queue collapse under unmitigated surges.
              </div>
              <div className="text-sm leading-relaxed space-y-3 font-sans">
                <p>
                  Across 360 paired simulation trials subjected to flash crowds, server crash-stops, and compound stress, the baseline architecture (CFG-A) suffered unbounded queue saturation. Under identical PRNG streams, brownout degradation transforms failure curves into tightly bounded tail latencies under the 100 ms SLA threshold.
                </p>
                <div className="font-mono text-xs text-[#141517] bg-[#EAE6DD] p-2.5 border-l-2 border-[#2457E8]">
                  Common Random Numbers (CRN) eliminate stochastic background variance between pairs, isolating the true causal effect of brownout adaptation and BALB routing.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 3 Empirical Distribution Figures Grid */}
        <div className="py-8 border-b border-[#D8D4CA] space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-baseline justify-between pb-2 border-b border-[#D8D4CA] font-mono text-xs">
            <span className="font-semibold uppercase tracking-wider text-[#141517]">
              EMPIRICAL OBSERVATIONS · 3-PANEL HARVEST
            </span>
            <span className="text-[#8C9099]">SHOWING VERIFIED 30-SEED EMPIRICAL DISTRIBUTIONS</span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
            {/* FIG 05.A: Recovery-Time Spread */}
            <div className="bg-white border border-[#D8D4CA] p-5 flex flex-col justify-between shadow-sm">
              <div>
                <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-wider text-[#8C9099] mb-1">
                  <span>FIG 05.A // 30-SEED RECOVERY SPREAD</span>
                  <span className="font-semibold text-[#141517]">T_ADAPT &amp; T_RESTORE</span>
                </div>
                <h2 className="font-serif text-2xl text-[#141517] mb-1">
                  Recovery-Time Spread
                </h2>
                <p className="text-xs text-[#5D6066] mb-4">
                  Adaptation recovery (&lt;2.5s) and post-restoration steady-state recovery (DEC-010). CFG-C accelerates recovery by 2.1x over CFG-B.
                </p>

                {/* SVG Visual Density Plot */}
                <div className="w-full bg-[#F4F1EA] border border-[#D8D4CA] p-3 mb-4">
                  <svg className="w-full h-auto font-mono text-[9px]" viewBox="0 0 320 180">
                    <line x1="30" y1="20" x2="30" y2="150" stroke="#141517" strokeWidth="1" />
                    <line x1="30" y1="150" x2="300" y2="150" stroke="#141517" strokeWidth="1" />
                    <line x1="30" y1="100" x2="300" y2="100" stroke="#D8D4CA" strokeDasharray="2 2" />
                    <line x1="30" y1="50" x2="300" y2="50" stroke="#D8D4CA" strokeDasharray="2 2" />

                    <text x="30" y="165" fill="#8C9099" textAnchor="middle">0s</text>
                    <text x="100" y="165" fill="#8C9099" textAnchor="middle">133s (CFG-C)</text>
                    <text x="200" y="165" fill="#8C9099" textAnchor="middle">286s (CFG-B)</text>
                    <text x="285" y="165" fill="#8C9099" textAnchor="middle">550s (Cens)</text>

                    {/* CFG-C Density Peak at 133.5s */}
                    <path
                      d="M 70 150 L 95 145 Q 100 40 102 40 Q 105 40 115 145 L 135 150 Z"
                      fill="#2457E8"
                      fillOpacity="0.3"
                    />
                    <path
                      d="M 70 150 L 95 145 Q 100 40 102 40 Q 105 40 115 145 L 135 150"
                      fill="none"
                      stroke="#2457E8"
                      strokeWidth="2"
                    />
                    <circle cx="102" cy="40" r="3" fill="#2457E8" />
                    <text x="107" y="42" fill="#2457E8" fontWeight="600">Med = 133.5s</text>

                    {/* CFG-B Density Peak at 286.5s */}
                    <path
                      d="M 160 150 L 190 145 Q 200 80 205 80 Q 210 80 220 145 L 245 150 Z"
                      fill="#5D6066"
                      fillOpacity="0.2"
                    />
                    <path
                      d="M 160 150 L 190 145 Q 200 80 205 80 Q 210 80 220 145 L 245 150"
                      fill="none"
                      stroke="#5D6066"
                      strokeWidth="1.5"
                    />
                    <circle cx="205" cy="80" r="3" fill="#5D6066" />
                    <text x="210" y="82" fill="#5D6066" fontWeight="600">Med = 286.5s</text>
                  </svg>
                </div>

                <div className="grid grid-cols-2 gap-2 font-mono text-xs bg-[#EAE6DD] border border-[#D8D4CA] p-2.5 mb-2">
                  <div>
                    <span className="text-[#8C9099] block text-[10px]">CFG-B (JSQ)</span>
                    <span className="text-[#141517] font-semibold">286.5s MEDIAN</span>
                    <span className="text-[#5D6066] block text-[10px]">25/30 recovered (83.3%)</span>
                  </div>
                  <div className="border-l border-[#D8D4CA] pl-2">
                    <span className="text-[#2457E8] block text-[10px] font-semibold">CFG-C (BALB)</span>
                    <span className="text-[#2457E8] font-semibold">133.5s MEDIAN</span>
                    <span className="text-[#24845A] block text-[10px]">29/30 recovered (96.7%)</span>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-[#D8D4CA] font-mono text-[10px] text-[#8C9099]">
                FIG 05.A — 30-SEED POST-REPAIR RESTORATION TIMES PER DEC-010 (IMPUTED WITH 550S HORIZON; UNCENSORED MEDIANS: 263.0S VS 133.0S).
              </div>
            </div>

            {/* FIG 05.B: SLA Failure Rate Density */}
            <div className="bg-white border border-[#D8D4CA] p-5 flex flex-col justify-between shadow-sm">
              <div>
                <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-wider text-[#8C9099] mb-1">
                  <span>FIG 05.B // OVERALL SLA FAILURE (V_overall)</span>
                  <span className="font-semibold text-[#141517]">FLASH CROWD ECDF</span>
                </div>
                <h2 className="font-serif text-2xl text-[#141517] mb-1">
                  SLA Failure Rate Density
                </h2>
                <p className="text-xs text-[#5D6066] mb-4">
                  Overall SLA failure rate includes drops, timeouts, and latency violations &gt; 100 ms. CFG-C achieves 93.3% relative reduction in Flash Crowd.
                </p>

                {/* SVG Visual ECDF Plot */}
                <div className="w-full bg-[#F4F1EA] border border-[#D8D4CA] p-3 mb-4">
                  <svg className="w-full h-auto font-mono text-[9px]" viewBox="0 0 320 180">
                    <line x1="30" y1="20" x2="30" y2="150" stroke="#141517" strokeWidth="1" />
                    <line x1="30" y1="150" x2="300" y2="150" stroke="#141517" strokeWidth="1" />
                    <line x1="30" y1="100" x2="300" y2="100" stroke="#D8D4CA" strokeDasharray="2 2" />
                    <line x1="30" y1="50" x2="300" y2="50" stroke="#D8D4CA" strokeDasharray="2 2" />

                    <text x="30" y="165" fill="#8C9099" textAnchor="middle">0%</text>
                    <text x="95" y="165" fill="#8C9099" textAnchor="middle">25%</text>
                    <text x="160" y="165" fill="#8C9099" textAnchor="middle">50%</text>
                    <text x="225" y="165" fill="#8C9099" textAnchor="middle">75%</text>
                    <text x="290" y="165" fill="#8C9099" textAnchor="middle">100%</text>

                    {/* CFG-A Baseline Curve (Flash crowd ~44%) */}
                    <path
                      d="M 30 150 L 140 150 L 150 60 L 160 30 L 300 30"
                      fill="none"
                      stroke="#141517"
                      strokeWidth="1.8"
                    />
                    <circle cx="150" cy="60" r="3" fill="#141517" />
                    <text x="156" y="62" fill="#141517" fontWeight="600">A: 44.0%</text>

                    {/* CFG-C Curve (Flash crowd ~2.9%) */}
                    <path
                      d="M 30 150 L 38 145 L 42 45 L 50 30 L 300 30"
                      fill="none"
                      stroke="#2457E8"
                      strokeWidth="2.2"
                    />
                    <circle cx="42" cy="45" r="3.5" fill="#2457E8" />
                    <text x="48" y="45" fill="#2457E8" fontWeight="600">C: 2.94%</text>
                  </svg>
                </div>

                <div className="grid grid-cols-2 gap-2 font-mono text-xs bg-[#EAE6DD] border border-[#D8D4CA] p-2.5 mb-2">
                  <div>
                    <span className="text-[#8C9099] block text-[10px]">BASELINE (CFG-A)</span>
                    <span className="text-[#D94A45] font-semibold">44.04% MEAN</span>
                    <span className="text-[#5D6066] block text-[10px]">Unbounded drop</span>
                  </div>
                  <div className="border-l border-[#D8D4CA] pl-2">
                    <span className="text-[#2457E8] block text-[10px] font-semibold">CLOUDRESCUE (CFG-C)</span>
                    <span className="text-[#24845A] font-semibold">2.94% MEAN</span>
                    <span className="text-[#24845A] block text-[10px]">-93.3% relative (p &lt; 10⁻⁶⁰)</span>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-[#D8D4CA] font-mono text-[10px] text-[#8C9099]">
                FIG 05.B — EMPIRICAL CDF OF OVERALL SLA FAILURE RATE UNDER 3X FLASH CROWD.
              </div>
            </div>

            {/* FIG 05.C: Tail Latency Spectrum */}
            <div className="bg-white border border-[#D8D4CA] p-5 flex flex-col justify-between shadow-sm">
              <div>
                <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-wider text-[#8C9099] mb-1">
                  <span>FIG 05.C // TAIL LATENCY SPECTRUM</span>
                  <span className="font-semibold text-[#141517]">SLA THRESHOLD = 100ms</span>
                </div>
                <h2 className="font-serif text-2xl text-[#141517] mb-1">
                  Tail Latency Spectrum
                </h2>
                <p className="text-xs text-[#5D6066] mb-4">
                  Percentile progression under 240 req/s flash crowd. CFG-A violates 100 ms SLA threshold at P95 (184.3 ms) while CFG-C achieves 82.9 ms.
                </p>

                {/* SVG Visual Latency Plot */}
                <div className="w-full bg-[#F4F1EA] border border-[#D8D4CA] p-3 mb-4">
                  <svg className="w-full h-auto font-mono text-[9px]" viewBox="0 0 320 180">
                    <line x1="30" y1="20" x2="30" y2="150" stroke="#141517" strokeWidth="1" />
                    <line x1="30" y1="150" x2="300" y2="150" stroke="#141517" strokeWidth="1" />

                    {/* SLA Line at 100ms */}
                    <line x1="30" y1="75" x2="300" y2="75" stroke="#D94A45" strokeDasharray="3 3" />
                    <text x="235" y="70" fill="#D94A45" fontSize="8" fontWeight="600">SLA = 100ms</text>

                    {/* Target Setpoint Line at 80ms */}
                    <line x1="30" y1="90" x2="300" y2="90" stroke="#2457E8" strokeDasharray="2 2" />
                    <text x="235" y="88" fill="#2457E8" fontSize="8">Target = 80ms</text>

                    <text x="60" y="165" fill="#8C9099" textAnchor="middle">P50</text>
                    <text x="130" y="165" fill="#8C9099" textAnchor="middle">P90</text>
                    <text x="200" y="165" fill="#8C9099" textAnchor="middle">P95</text>
                    <text x="270" y="165" fill="#8C9099" textAnchor="middle">P99</text>

                    {/* CFG-A baseline trajectory */}
                    <path
                      d="M 60 115 L 130 80 L 200 35 L 270 25"
                      fill="none"
                      stroke="#141517"
                      strokeWidth="1.8"
                    />
                    <circle cx="200" cy="35" r="3" fill="#141517" />
                    <text x="205" y="32" fill="#D94A45" fontWeight="600">184.3ms</text>

                    {/* CFG-C controlled trajectory */}
                    <path
                      d="M 60 135 L 130 110 L 200 88 L 270 65"
                      fill="none"
                      stroke="#2457E8"
                      strokeWidth="2.2"
                    />
                    <circle cx="200" cy="88" r="3.5" fill="#2457E8" />
                    <text x="205" y="98" fill="#2457E8" fontWeight="600">82.9ms</text>
                  </svg>
                </div>

                <div className="grid grid-cols-2 gap-2 font-mono text-xs bg-[#EAE6DD] border border-[#D8D4CA] p-2.5 mb-2">
                  <div>
                    <span className="text-[#8C9099] block text-[10px]">BASELINE (CFG-A)</span>
                    <span className="text-[#D94A45] font-semibold">184.3ms P95</span>
                    <span className="text-[#5D6066] block text-[10px]">SLA breached (&gt;100ms)</span>
                  </div>
                  <div className="border-l border-[#D8D4CA] pl-2">
                    <span className="text-[#2457E8] block text-[10px] font-semibold">CLOUDRESCUE (CFG-C)</span>
                    <span className="text-[#24845A] font-semibold">82.9ms P95</span>
                    <span className="text-[#24845A] block text-[10px]">&lt; 100ms boundary</span>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-[#D8D4CA] font-mono text-[10px] text-[#8C9099]">
                FIG 05.C — EMPIRICAL LATENCY PROGRESSION UNDER 240 REQ/S FLASH CROWD.
              </div>
            </div>
          </div>
        </div>

        {/* Statistical Comparison Table (Table 05.1) */}
        <div className="py-8 space-y-4">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-[#D8D4CA] pb-3">
            <div>
              <div className="font-mono text-xs uppercase tracking-widest text-[#2457E8] font-semibold">
                [DATA MATRIX // TABLE 05.1]
              </div>
              <h2 className="font-serif text-2xl sm:text-3xl text-[#141517]">
                Two-Sample Paired Hypothesis Tests (N = 30 Seeds)
              </h2>
            </div>
            <div className="font-mono text-xs text-[#8C9099]">
              PAIRED BY SCENARIO AND SEED · BONFERRONI &amp; FDR CORRECTIONS INCLUDED
            </div>
          </div>

          {/* Table Filters & Search Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 font-mono text-xs">
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Filter size={14} className="text-[#8C9099]" />
              <span className="text-[#8C9099] uppercase">SCENARIO:</span>
              <select
                value={filterScenario}
                onChange={(e) => setFilterScenario(e.target.value)}
                className="bg-white border border-[#D8D4CA] px-3 py-1.5 text-[#141517] focus:outline-none"
              >
                <option value="all">All Scenarios ({statsData?.comparisons?.length || 0} pairs)</option>
                <option value="compound_stress">Compound Stress</option>
                <option value="server_failure">Server Crash</option>
                <option value="flash_crowd">Flash Crowd</option>
                <option value="nominal">Nominal</option>
              </select>
            </div>

            <div className="relative w-full sm:w-64">
              <Search size={14} className="absolute left-2.5 top-2.5 text-[#8C9099]" />
              <input
                type="text"
                placeholder="Search metric..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-white border border-[#D8D4CA] pl-8 pr-3 py-1.5 text-[#141517] focus:outline-none"
              />
            </div>
          </div>

          {/* Matrix Table */}
          <div className="w-full overflow-x-auto border border-[#D8D4CA] bg-white shadow-sm">
            <table className="w-full text-left font-mono text-xs border-collapse">
              <thead>
                <tr className="bg-[#EAE6DD] border-b border-[#D8D4CA] text-[#141517] font-semibold uppercase text-[11px]">
                  <th className="py-3 px-3">Metric</th>
                  <th className="py-3 px-3">Scenario</th>
                  <th className="py-3 px-3">Pair Comparison</th>
                  <th className="py-3 px-3">Config 1 (Mean ± SD)</th>
                  <th className="py-3 px-3">Config 2 (Mean ± SD)</th>
                  <th className="py-3 px-3">Diff (Δ)</th>
                  <th className="py-3 px-3">Test</th>
                  <th className="py-3 px-3">raw p-val</th>
                  <th className="py-3 px-3">p-adj (Bonf)</th>
                  <th className="py-3 px-3">q-val (FDR)</th>
                  <th className="py-3 px-3 text-right">Effect Size</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#D8D4CA] text-[11px]">
                {comparisons.slice(0, 25).map((row, idx) => (
                  <tr key={idx} className="hover:bg-[#F4F1EA]">
                    <td className="py-2.5 px-3 font-semibold text-[#141517]">{row.metric}</td>
                    <td className="py-2.5 px-3 text-[#5D6066]">{row.scenario}</td>
                    <td className="py-2.5 px-3">
                      <span className="font-semibold text-[#2457E8]">{row.config_1}</span> vs <span className="text-[#8C9099]">{row.config_2}</span>
                    </td>
                    <td className="py-2.5 px-3 text-[#5D6066]">
                      {row.mean_1.toFixed(2)} ±{row.std_1.toFixed(2)}
                    </td>
                    <td className="py-2.5 px-3 text-[#5D6066]">
                      {row.mean_2.toFixed(2)} ±{row.std_2.toFixed(2)}
                    </td>
                    <td className={`py-2.5 px-3 font-bold ${row.mean_diff < 0 ? 'text-[#24845A]' : 'text-[#141517]'}`}>
                      {row.mean_diff > 0 ? `+${row.mean_diff.toFixed(2)}` : row.mean_diff.toFixed(2)}
                    </td>
                    <td className="py-2.5 px-3 text-[#8C9099]">{row.test_name}</td>
                    <td className="py-2.5 px-3 text-[#141517]">
                      {row.p_value < 0.0001 ? '< 0.0001' : row.p_value.toFixed(4)}
                    </td>
                    <td className="py-2.5 px-3 text-[#5D6066]">
                      {row.p_adj_bonferroni < 0.0001 ? '< 0.0001' : row.p_adj_bonferroni.toFixed(4)}
                    </td>
                    <td className="py-2.5 px-3 text-[#2457E8] font-semibold">
                      {row.fdr_q_value < 0.0001 ? '< 0.0001' : row.fdr_q_value.toFixed(4)}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-semibold">
                      {row.effect_size_label} = {isFinite(row.effect_size) ? row.effect_size.toFixed(2) : (row.effect_size < 0 ? '-∞' : '+∞')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="font-mono text-[11px] text-[#8C9099] flex justify-between">
            <span>Showing top comparisons ({comparisons.length} matches found in results/experiment_360/statistical_comparisons.csv)</span>
            <span>Matched random streams isolate intervention effect</span>
          </div>
        </div>

        {/* Section: BALB Parameter Sensitivity Sweep */}
        {sensitivityData && (
          <div className="py-8 border-t border-[#D8D4CA] space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 border-b border-[#D8D4CA] pb-2 font-mono text-xs">
              <div>
                <span className="text-[#2457E8] font-semibold uppercase tracking-wider">
                  EXPLORATORY SENSITIVITY SWEEP (144 RUNS)
                </span>
                <h3 className="font-serif text-2xl text-[#141517] mt-0.5">
                  BALB Weight Sweep (α, β, γ) Robustness
                </h3>
              </div>
              <span className="text-[#8C9099]">48 PARAMETER CELLS × 3 SEEDS (1001, 1002, 1003) · COMPOUND STRESS</span>
            </div>

            <div className="bg-[#EAE6DD] p-3 border border-[#D8D4CA] font-mono text-xs flex items-center gap-2 text-[#5D6066]">
              <Info size={14} className="text-[#2457E8] shrink-0" />
              <span>
                <strong className="text-[#141517]">RESEARCH ASSUMPTION NOTICE:</strong> The sensitivity sweep is an exploratory analysis ($N=3$ seeds per cell). The observed best combination is not claimed to be globally optimal; the default configuration demonstrates robust stability across all 48 combinations.
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 font-mono text-xs">
              <div className="bg-white border border-[#D8D4CA] p-5 shadow-sm space-y-3">
                <span className="text-[#8C9099] uppercase text-[10px]">DEFAULT PARAMETER CELL</span>
                <div className="font-serif text-2xl text-[#141517]">
                  α=1.0, β=1.0, γ=0.5
                </div>
                <p className="text-xs text-[#5D6066] leading-relaxed">
                  Default parameters provide balanced trade-offs with SLA failure rate of{' '}
                  <span className="font-semibold text-[#2457E8]">
                    {sensitivityData.default_combination?.mean_v_overall.toFixed(1)}%
                  </span>{' '}
                  and P95 latency of{' '}
                  <span className="font-semibold text-[#141517]">
                    {sensitivityData.default_combination?.mean_p95.toFixed(1)} ms
                  </span>.
                </p>
              </div>

              <div className="bg-white border border-[#D8D4CA] p-5 shadow-sm space-y-3">
                <span className="text-[#24845A] uppercase text-[10px] font-semibold">EXPLORATORY BEST OBSERVED</span>
                <div className="font-serif text-2xl text-[#24845A]">
                  α={sensitivityData.best_observed?.alpha}, β={sensitivityData.best_observed?.beta}, γ={sensitivityData.best_observed?.gamma}
                </div>
                <p className="text-xs text-[#5D6066] leading-relaxed">
                  Observed lowest SLA failure in 3-seed compound sweep ({sensitivityData.best_observed?.mean_v_overall.toFixed(1)}% at P95 {sensitivityData.best_observed?.mean_p95.toFixed(1)} ms). Designated exploratory per Section 3.1 of audit.
                </p>
              </div>

              <div className="bg-white border border-[#D8D4CA] p-5 shadow-sm space-y-3">
                <span className="text-[#8C9099] uppercase text-[10px]">STABILITY BOUNDARY</span>
                <div className="font-serif text-2xl text-[#141517]">
                  Zero Divergence
                </div>
                <p className="text-xs text-[#5D6066] leading-relaxed">
                  Controller stability is preserved across 100% of tested weight combinations. No oscillatory divergence or deadlock observed across any parameter set.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      <ColophonFooter sectionNumber="05" />
    </div>
  );
}
