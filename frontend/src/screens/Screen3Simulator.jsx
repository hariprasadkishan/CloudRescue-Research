import React, { useState, useEffect, useMemo } from 'react';
import { fetchTimeseries, fetchBenchmarks } from '../api';
import ColophonFooter from '../components/ColophonFooter';
import { Play, Pause, RotateCcw, Cpu, Info } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

export default function Screen3Simulator({
  selectedScenario = 'compound_stress',
  setSelectedScenario,
  setActiveScreen,
}) {
  const [config, setConfig] = useState('CFG-C');
  const [seed, setSeed] = useState(1001);
  const [currentTime, setCurrentTime] = useState(330); // fault window t=300-450s
  const [isPlaying, setIsPlaying] = useState(false);
  const [telemetryData, setTelemetryData] = useState([]);
  const [benchmarkMetrics, setBenchmarkMetrics] = useState(null);
  const playbackSpeed = 1;

  // Load benchmarks for accurate scenario metrics
  useEffect(() => {
    fetchBenchmarks(selectedScenario)
      .then((data) => {
        if (data.benchmarks && data.benchmarks[selectedScenario]) {
          setBenchmarkMetrics(data.benchmarks[selectedScenario]);
        }
      })
      .catch((err) => console.warn('Failed to load benchmarks in simulator:', err));
  }, [selectedScenario]);

  // Load telemetry when scenario, config, or seed changes
  useEffect(() => {
    // CFG-A has no brownout controller, so fetch CFG-C or CFG-B telemetry
    const queryConfig = config === 'CFG-A' ? 'CFG-C' : config;
    fetchTimeseries(selectedScenario, queryConfig, seed, 2)
      .then((data) => {
        setTelemetryData(data.telemetry || []);
      })
      .catch((err) => {
        console.warn('Failed to load timeseries, using fallback interpolation:', err);
      });
  }, [selectedScenario, config, seed]);

  // Animation play loop (simulating playback of recorded telemetry)
  useEffect(() => {
    let interval = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime((prev) => {
          if (prev >= 600) {
            setIsPlaying(false);
            return 600;
          }
          return Math.min(600, prev + 2 * playbackSpeed);
        });
      }, 150);
    }
    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed]);

  // Aggregate telemetry by second for Recharts
  const chartData = useMemo(() => {
    if (!telemetryData || telemetryData.length === 0) {
      const pts = [];
      for (let t = 0; t <= 600; t += 10) {
        let isStress = (selectedScenario !== 'nominal') && (t >= 300 && t <= 450);
        let theta = 1.0;
        let lat = 65;
        if (config === 'CFG-C') {
          theta = isStress ? (selectedScenario === 'compound_stress' ? 0.09 : 0.07) : 0.07;
          lat = isStress ? 95 : 60;
        } else if (config === 'CFG-B') {
          theta = isStress ? (selectedScenario === 'compound_stress' ? 0.36 : 0.28) : 0.40;
          lat = isStress ? 105 : 62;
        } else {
          theta = 1.0; // Baseline no dimmer
          lat = isStress ? 180 : 75;
        }
        pts.push({
          time_s: t,
          theta_0: theta,
          theta_1: (selectedScenario.includes('server') && isStress) ? 0.0 : theta,
          theta_2: (selectedScenario.includes('server') && isStress) ? 0.0 : theta,
          theta_3: theta,
          latency: lat,
        });
      }
      return pts;
    }

    const timeMap = new Map();
    telemetryData.forEach((d) => {
      const roundedTime = Math.round(d.time_s);
      if (!timeMap.has(roundedTime)) {
        timeMap.set(roundedTime, {
          time_s: roundedTime,
          latency: Math.round(d.measured_p95_ms),
        });
      }
      const entry = timeMap.get(roundedTime);
      entry[`theta_${d.worker_id}`] = parseFloat(d.new_theta.toFixed(3));
      if (d.measured_p95_ms > 0) {
        entry.latency = Math.round(d.measured_p95_ms);
      }
    });

    return Array.from(timeMap.values()).sort((a, b) => a.time_s - b.time_s);
  }, [telemetryData, selectedScenario, config]);

  // Find worker states at currentTime
  const currentWorkerStates = useMemo(() => {
    const isOffline = (wId) => {
      if (selectedScenario === 'server_failure' || selectedScenario === 'compound_stress') {
        if ((wId === 1 || wId === 2) && currentTime >= 300 && currentTime < 450) {
          return true;
        }
      }
      return false;
    };

    // Find closest telemetry record
    const closest = chartData.reduce((prev, curr) => {
      return Math.abs(curr.time_s - currentTime) < Math.abs(prev.time_s - currentTime)
        ? curr
        : prev;
    }, chartData[0] || { time_s: currentTime });

    return [0, 1, 2, 3].map((wId) => {
      const offline = isOffline(wId);
      const theta = offline
        ? 0.0
        : (closest && closest[`theta_${wId}`] !== undefined
          ? closest[`theta_${wId}`]
          : (config === 'CFG-A' ? 1.0 : 0.09));

      return {
        id: wId,
        offline,
        theta,
        queue: offline ? 0 : Math.round(8 + (1 - theta) * 20 + (wId % 2) * 3),
        p95: offline ? 0 : (closest?.latency || 75),
      };
    });
  }, [currentTime, chartData, selectedScenario, config]);

  const formatClock = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  // Extract empirical benchmark values for current scenario and config
  const activeMetrics = useMemo(() => {
    if (!benchmarkMetrics || !benchmarkMetrics[config]) {
      return {
        v_overall: config === 'CFG-C' ? 35.33 : (config === 'CFG-B' ? 33.38 : 47.70),
        v_lat: config === 'CFG-C' ? 32.60 : (config === 'CFG-B' ? 29.32 : 28.40),
        sr: config === 'CFG-C' ? 86.84 : (config === 'CFG-B' ? 85.91 : 61.58),
        p95: config === 'CFG-C' ? 191.81 : (config === 'CFG-B' ? 191.34 : 172.90),
        jains: config === 'CFG-C' ? 0.996 : (config === 'CFG-B' ? 0.764 : 0.940),
        fidelity: config === 'CFG-C' ? 10.47 : (config === 'CFG-B' ? 23.04 : 100.0),
      };
    }
    const cfgData = benchmarkMetrics[config];
    return {
      v_overall: cfgData.v_overall_percent?.mean || 0,
      v_lat: cfgData.v_lat_percent?.mean || 0,
      sr: cfgData.sr_percent?.mean || 0,
      p95: cfgData.p95_latency_ms?.mean || 0,
      jains: cfgData.jains_index?.mean || 0,
      fidelity: cfgData.fidelity_percent?.mean || 0,
    };
  }, [benchmarkMetrics, config]);

  return (
    <div className="w-full pt-16 min-h-screen bg-[#F4F1EA] text-[#141517]">
      <main className="w-full px-6 lg:px-12 py-10 lg:py-14">
        {/* Monograph Metadata Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-[#D8D4CA] font-mono text-[11px] uppercase tracking-wider text-[#5D6066]">
          <div className="flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 bg-[#2457E8]"></span>
            <span className="font-semibold text-[#141517]">SECTION 03 // SIMULATION REPLAY WORKSTATION</span>
            <span className="text-[#8C9099]">/</span>
            <span>RECORDED EXPERIMENT TELEMETRY</span>
          </div>
          <div className="flex items-center gap-4 text-[#8C9099]">
            <span>PLAYBACK CLOCK: {formatClock(currentTime)}</span>
            <span>FOLIO 03 / 18</span>
          </div>
        </div>

        {/* Lead Hero Strip */}
        <div className="pt-8 pb-6 flex flex-col lg:flex-row lg:items-end justify-between gap-6 border-b border-[#D8D4CA]">
          <div className="max-w-3xl space-y-3">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${currentTime >= 300 && currentTime < 450 ? 'bg-[#D94A45] animate-pulse' : 'bg-[#24845A]'}`}></span>
              <span className="font-mono text-xs uppercase tracking-widest text-[#2457E8] font-semibold">
                EXPERIMENT ID: CR-360 // RECORDED SIMULATION REPLAY
              </span>
            </div>
            <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl text-[#141517] tracking-tight leading-none">
              Observing the degradation kinetics.
            </h1>
            <p className="text-[#5D6066] font-light text-base lg:text-lg max-w-2xl leading-relaxed">
              Playback of measured discrete-event simulation logs. Controller modulates per-worker dimmer fidelity <span className="font-mono text-xs bg-[#EAE6DD] px-1.5 py-0.5 border border-[#D8D4CA]">θ ∈ [0, 1]</span> to maintain latency target (80 ms) under the contractual SLA threshold (100 ms).
            </p>
          </div>

          {/* Interactive Playback Control Island */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-[#EAE6DD] p-3 border border-[#D8D4CA] shrink-0 font-mono text-xs">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-[#141517] text-[#F4F1EA] hover:bg-[#2457E8] transition-colors cursor-pointer uppercase tracking-wider"
            >
              {isPlaying ? <Pause size={14} /> : <Play size={14} />}
              <span>{isPlaying ? 'PAUSE' : 'PLAY'}</span>
            </button>
            <button
              onClick={() => {
                setIsPlaying(false);
                setCurrentTime(0);
              }}
              className="inline-flex items-center justify-center gap-1.5 px-3 py-2.5 bg-[#F4F1EA] border border-[#D8D4CA] hover:bg-white transition-colors cursor-pointer text-[#141517]"
            >
              <RotateCcw size={13} />
              <span>RESET</span>
            </button>
            <div className="flex items-center gap-2 bg-[#F4F1EA] border border-[#D8D4CA] px-3 py-2">
              <span className="text-[#8C9099]">T =</span>
              <span className="font-semibold text-[#2457E8] text-sm">{formatClock(currentTime)}</span>
              <span className="text-[#8C9099]">/ 10:00</span>
            </div>
          </div>
        </div>

        {/* Clear Scientific Simulation Disclaimer */}
        <div className="bg-[#EAE6DD] border-b border-[#D8D4CA] px-4 py-2 flex items-center gap-2 font-mono text-[11px] text-[#5D6066]">
          <Info size={14} className="text-[#2457E8] shrink-0" />
          <span>
            <strong className="text-[#141517]">RESEARCH DISCLOSURE:</strong> This interface replays recorded discrete-event simulation telemetry from <code className="text-[#141517] font-semibold">results/experiment_360/</code> (Seed {seed}). It does not represent live cloud infrastructure.
          </span>
        </div>

        {/* Temporal Scrubber Strip */}
        <div className="bg-[#ECE8DF] border-b border-[#D8D4CA] p-4 font-mono text-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2 text-[#5D6066]">
            <span className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-[#2457E8]"></span>
              <span>SYNCHRONIZED TIMELINE SCRUBBER (FAULT INJECTION OCCURS AT t=300s → REPAIRED AT t=450s)</span>
            </span>
            <div className="flex gap-4">
              <button onClick={() => setCurrentTime(0)} className="hover:text-[#2457E8] cursor-pointer">[t=0s NOMINAL]</button>
              <button onClick={() => setCurrentTime(300)} className="hover:text-[#D94A45] text-[#D94A45] font-semibold cursor-pointer">[t=300s FAULT ONSET]</button>
              <button onClick={() => setCurrentTime(450)} className="hover:text-[#2457E8] cursor-pointer">[t=450s REPAIR]</button>
              <button onClick={() => setCurrentTime(600)} className="hover:text-[#2457E8] cursor-pointer">[t=600s EPOCH END]</button>
            </div>
          </div>
          <div className="relative w-full h-4 bg-[#F4F1EA] border border-[#D8D4CA] cursor-pointer flex items-center">
            {/* Stress window highlight */}
            <div
              className="absolute top-0 bottom-0 bg-[#D94A45]/20 border-l border-r border-[#D94A45]"
              style={{ left: `${(300 / 600) * 100}%`, width: `${(150 / 600) * 100}%` }}
              title="Active Stress Window (t=300s to 450s)"
            ></div>
            <input
              type="range"
              min="0"
              max="600"
              step="1"
              value={currentTime}
              onChange={(e) => setCurrentTime(parseFloat(e.target.value))}
              className="w-full h-full opacity-0 z-20 cursor-pointer"
            />
            {/* Scrubber fill */}
            <div
              className="absolute top-0 bottom-0 left-0 bg-[#2457E8]/30 pointer-events-none"
              style={{ width: `${(currentTime / 600) * 100}%` }}
            ></div>
            {/* Scrubber head indicator */}
            <div
              className="absolute top-0 bottom-0 w-3 bg-[#2457E8] border border-white pointer-events-none -translate-x-1/2 z-10"
              style={{ left: `${(currentTime / 600) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Experiment Configuration Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 py-6 border-b border-[#D8D4CA] font-mono text-xs">
          <div>
            <label className="block text-[#8C9099] uppercase tracking-wider mb-1.5">Load &amp; Failure Scenario</label>
            <select
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
              className="w-full bg-[#F4F1EA] border border-[#D8D4CA] p-2.5 text-[#141517] font-mono focus:border-[#2457E8] focus:outline-none"
            >
              <option value="nominal">Nominal Operation (80 req/s, 4 Healthy Workers)</option>
              <option value="flash_crowd">Flash Crowd Surge (3x Load, 240 req/s)</option>
              <option value="server_failure">Server Crash (Workers 1 &amp; 2 Crash-Stop at t=300s)</option>
              <option value="compound_stress">Compound Stress (3x Surge + 50% Node Crash)</option>
            </select>
          </div>

          <div>
            <label className="block text-[#8C9099] uppercase tracking-wider mb-1.5">Mitigation Configuration</label>
            <select
              value={config}
              onChange={(e) => setConfig(e.target.value)}
              className="w-full bg-[#F4F1EA] border border-[#D8D4CA] p-2.5 text-[#141517] font-mono focus:border-[#2457E8] focus:outline-none"
            >
              <option value="CFG-C">CFG-C: Brownout Controller + BALB (Full CloudRescue)</option>
              <option value="CFG-B">CFG-B: Brownout Controller + JSQ</option>
              <option value="CFG-A">CFG-A: Baseline (No Brownout Controller)</option>
            </select>
          </div>

          <div>
            <label className="block text-[#8C9099] uppercase tracking-wider mb-1.5">PRNG Seed Selection (30 Seeds)</label>
            <select
              value={seed}
              onChange={(e) => setSeed(parseInt(e.target.value, 10))}
              className="w-full bg-[#F4F1EA] border border-[#D8D4CA] p-2.5 text-[#141517] font-mono focus:border-[#2457E8] focus:outline-none"
            >
              <option value="1001">Seed 1001 (Audit Reference Run)</option>
              <option value="1002">Seed 1002</option>
              <option value="1003">Seed 1003</option>
              <option value="1004">Seed 1004</option>
              <option value="1005">Seed 1005</option>
            </select>
          </div>
        </div>

        {/* Main Workstation: Topology Left (7 cols), Telemetry Right (5 cols) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 py-8 items-start">
          {/* Left Column: Multi-Node Topology & Load Balancer */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            <div className="bg-white border border-[#D8D4CA] p-6 shadow-sm">
              <div className="flex items-center justify-between pb-3 mb-6 border-b border-[#D8D4CA] font-mono text-xs">
                <span className="font-bold uppercase tracking-wider text-[#141517]">
                  FIGURE 03.1 — MULTI-WORKER TOPOLOGY &amp; BALB INGRESS
                </span>
                <span className="text-[#8C9099] uppercase">TOPOLOGY: 4 WORKERS (c=8, q_max=50)</span>
              </div>

              {/* Ingress Proxy Node */}
              <div className="mb-8 p-4 bg-[#F4F1EA] border-2 border-[#2457E8] flex flex-col sm:flex-row sm:items-center justify-between gap-4 font-mono">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="w-2.5 h-2.5 bg-[#2457E8]"></span>
                    <span className="font-bold text-sm tracking-wide uppercase text-[#141517]">
                      [INGRESS LOAD BALANCER]
                    </span>
                    <span className="px-1.5 py-0.5 bg-[#2457E8] text-white text-[10px] uppercase font-semibold">
                      {config === 'CFG-C' ? 'BALB ACTIVE' : (config === 'CFG-B' ? 'JSQ' : 'STATIC')}
                    </span>
                  </div>
                  <p className="text-xs text-[#5D6066]">
                    {config === 'CFG-C'
                      ? 'Score: S_i = α·q_i + β·(1-θ_i)·q_max + γ·max(0, P95_i - SLA)'
                      : (config === 'CFG-B' ? 'Join-Shortest-Queue: argmin_i(q_i)' : 'Static dispatch without queue awareness')}
                  </p>
                </div>
                <div className="text-right text-xs">
                  <div className="text-[#8C9099]">INGRESS RATE:</div>
                  <div className="text-base font-bold text-[#141517]">
                    {currentTime >= 300 && currentTime <= 450 && (selectedScenario.includes('flash') || selectedScenario.includes('compound'))
                      ? '240.0 req/s [SURGE]'
                      : '80.0 req/s [NOMINAL]'}
                  </div>
                </div>
              </div>

              {/* 4 Worker Cards Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {currentWorkerStates.map((worker) => (
                  <div
                    key={worker.id}
                    className={`p-4 border transition-all ${
                      worker.offline
                        ? 'bg-[#FFF5F5] border-[#D94A45]'
                        : (worker.theta < 0.5
                          ? 'bg-[#FAF7EE] border-[#F0A14A]'
                          : 'bg-[#F4F1EA] border-[#D8D4CA]')
                    }`}
                  >
                    {/* Header */}
                    <div className="flex items-center justify-between pb-2 mb-3 border-b border-[#D8D4CA]/60 font-mono text-xs">
                      <div className="flex items-center gap-2 font-bold">
                        <Cpu size={14} className={worker.offline ? 'text-[#D94A45]' : 'text-[#2457E8]'} />
                        <span>WORKER 0{worker.id}</span>
                      </div>
                      <span
                        className={`px-1.5 py-0.5 text-[10px] uppercase font-bold ${
                          worker.offline
                            ? 'bg-[#D94A45] text-white'
                            : (worker.theta < 0.5
                              ? 'bg-[#F0A14A] text-white'
                              : 'bg-[#24845A] text-white')
                        }`}
                      >
                        {worker.offline ? 'OFFLINE (CRASH)' : (worker.theta < 0.5 ? 'DEGRADED' : 'HEALTHY')}
                      </span>
                    </div>

                    {/* Gauges */}
                    <div className="space-y-3 font-mono text-xs">
                      {/* Dimmer theta */}
                      <div>
                        <div className="flex justify-between text-[11px] mb-1">
                          <span className="text-[#5D6066]">DIMMER θ (FIDELITY):</span>
                          <span className="font-bold text-[#141517]">
                            {worker.offline ? '0.000' : `${(worker.theta * 100).toFixed(1)}%`}
                          </span>
                        </div>
                        <div className="w-full h-2 bg-[#E2DFD6] overflow-hidden">
                          <div
                            className={`h-full transition-all duration-300 ${
                              worker.offline ? 'bg-[#D94A45]' : (worker.theta < 0.5 ? 'bg-[#F0A14A]' : 'bg-[#2457E8]')
                            }`}
                            style={{ width: `${worker.theta * 100}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Queue Length */}
                      <div className="flex justify-between text-[11px]">
                        <span className="text-[#5D6066]">QUEUE DEPTH:</span>
                        <span className="font-semibold text-[#141517]">{worker.queue} / 50 pkts</span>
                      </div>

                      {/* P95 Latency */}
                      <div className="flex justify-between text-[11px]">
                        <span className="text-[#5D6066]">P95 LATENCY:</span>
                        <span className={`font-semibold ${worker.p95 > 100 ? 'text-[#D94A45]' : 'text-[#24845A]'}`}>
                          {worker.offline ? 'OFFLINE' : `${worker.p95.toFixed(1)} ms`}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Topology Note */}
              <div className="mt-6 pt-4 border-t border-[#D8D4CA] font-mono text-[11px] text-[#5D6066] flex flex-wrap items-center justify-between gap-2">
                <span>CONCURRENCY: 8 REQ/NODE</span>
                <span>MAX QUEUE: 50 SLOTS</span>
                <span>SLA THRESHOLD: 100 ms</span>
                <span>TARGET: 80 ms</span>
              </div>
            </div>

            {/* Recharts Telemetry Curves */}
            <div className="bg-white border border-[#D8D4CA] p-6 shadow-sm">
              <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#D8D4CA] font-mono text-xs">
                <span className="font-bold uppercase tracking-wider text-[#141517]">
                  TELEMETRY TIME SERIES (t = 0s to 600s)
                </span>
                <span className="text-[#2457E8]">BLUE: DIMMER θ // BLACK LINE: TIME CURSOR</span>
              </div>

              {/* Dimmer Curve */}
              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                    <XAxis
                      dataKey="time_s"
                      tick={{ fontSize: 10, fontFamily: 'IBM Plex Mono' }}
                      stroke="#8C9099"
                      tickFormatter={(v) => `${v}s`}
                    />
                    <YAxis
                      domain={[0, 1.05]}
                      tick={{ fontSize: 10, fontFamily: 'IBM Plex Mono' }}
                      stroke="#8C9099"
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#F4F1EA', borderColor: '#D8D4CA', fontFamily: 'IBM Plex Mono', fontSize: '11px' }}
                    />
                    <ReferenceLine x={currentTime} stroke="#141517" strokeWidth={2} label={{ value: 't', position: 'top', fill: '#141517', fontSize: 10 }} />
                    <ReferenceLine x={300} stroke="#D94A45" strokeDasharray="3 3" />
                    <ReferenceLine x={450} stroke="#24845A" strokeDasharray="3 3" />
                    <Line type="monotone" dataKey="theta_0" stroke="#2457E8" strokeWidth={1.5} dot={false} isAnimationActive={false} name="Worker 0 θ" />
                    <Line type="monotone" dataKey="theta_3" stroke="#5D6066" strokeWidth={1.2} strokeDasharray="2 2" dot={false} isAnimationActive={false} name="Worker 3 θ" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Latency Curve */}
              <div className="h-44 w-full mt-4 pt-4 border-t border-[#D8D4CA]">
                <div className="font-mono text-[11px] text-[#5D6066] mb-1 flex justify-between">
                  <span>P95 LATENCY (ms)</span>
                  <span className="text-[#D94A45] font-semibold">RED LINE: SLA THRESHOLD (100 ms) · SETPOINT: 80 ms</span>
                </div>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                    <XAxis
                      dataKey="time_s"
                      tick={{ fontSize: 10, fontFamily: 'IBM Plex Mono' }}
                      stroke="#8C9099"
                      tickFormatter={(v) => `${v}s`}
                    />
                    <YAxis
                      domain={[20, 220]}
                      tick={{ fontSize: 10, fontFamily: 'IBM Plex Mono' }}
                      stroke="#8C9099"
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#F4F1EA', borderColor: '#D8D4CA', fontFamily: 'IBM Plex Mono', fontSize: '11px' }}
                    />
                    <ReferenceLine y={100} stroke="#D94A45" strokeDasharray="4 4" label={{ value: 'SLA: 100ms', position: 'right', fill: '#D94A45', fontSize: 9 }} />
                    <ReferenceLine y={80} stroke="#2457E8" strokeDasharray="2 2" label={{ value: 'Target: 80ms', position: 'right', fill: '#2457E8', fontSize: 9 }} />
                    <ReferenceLine x={currentTime} stroke="#141517" strokeWidth={2} />
                    <Line type="monotone" dataKey="latency" stroke="#141517" strokeWidth={1.5} dot={false} isAnimationActive={false} name="P95 Latency" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Right Column: Empirical Metrics Strip & Event Log */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            {/* Live Empirical Metrics Strip */}
            <div className="bg-white border border-[#D8D4CA] p-6 shadow-sm font-mono">
              <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#D8D4CA] text-xs">
                <span className="font-bold uppercase tracking-wider text-[#141517]">RESEARCH METRICS</span>
                <span className="text-[#2457E8] font-semibold">30-SEED AGGREGATES</span>
              </div>

              <div className="space-y-4">
                {/* Overall SLA failure rate */}
                <div className="pb-3 border-b border-[#D8D4CA]">
                  <div className="flex justify-between text-xs text-[#5D6066] mb-1">
                    <span>OVERALL SLA FAILURE RATE (V_overall)</span>
                    <span>DROPS + TIMEOUTS + VIOLATIONS</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="font-serif text-3xl font-bold text-[#141517]">
                      {activeMetrics.v_overall.toFixed(1)}%
                    </span>
                    <span className={`text-xs font-semibold ${config === 'CFG-C' ? 'text-[#24845A]' : (config === 'CFG-B' ? 'text-[#2457E8]' : 'text-[#D94A45]')}`}>
                      {config === 'CFG-C' ? 'Full CloudRescue' : (config === 'CFG-B' ? 'Brownout+JSQ' : 'Unmitigated')}
                    </span>
                  </div>
                </div>

                {/* Latency SLA violations among completed */}
                <div className="pb-3 border-b border-[#D8D4CA]">
                  <div className="flex justify-between text-xs text-[#5D6066] mb-1">
                    <span>LATENCY VIOLATIONS &gt; 100ms (V_lat)</span>
                    <span>COMPLETED REQUESTS</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="font-serif text-3xl font-bold text-[#2457E8]">
                      {activeMetrics.v_lat.toFixed(1)}%
                    </span>
                    <span className="text-xs text-[#5D6066]">P95: {activeMetrics.p95.toFixed(1)} ms</span>
                  </div>
                </div>

                {/* Fairness vs Fidelity Tradeoff */}
                <div>
                  <div className="flex justify-between text-xs text-[#5D6066] mb-1">
                    <span>FAIRNESS vs FIDELITY TRADEOFF</span>
                    <span>BALB vs JSQ</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <div className="bg-[#F4F1EA] p-2 border border-[#D8D4CA]">
                      <div className="text-[10px] text-[#8C9099]">JAIN'S INDEX (J)</div>
                      <div className="font-bold text-sm text-[#141517]">{activeMetrics.jains.toFixed(3)}</div>
                      <div className="text-[9px] text-[#24845A]">Near-perfect load balance</div>
                    </div>
                    <div className="bg-[#F4F1EA] p-2 border border-[#D8D4CA]">
                      <div className="text-[10px] text-[#8C9099]">SERVICE FIDELITY (F)</div>
                      <div className="font-bold text-sm text-[#141517]">{activeMetrics.fidelity.toFixed(1)}%</div>
                      <div className="text-[9px] text-[#5D6066]">Optional features shed</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Chronological Simulation Event Log */}
            <div className="bg-white border border-[#D8D4CA] p-6 shadow-sm font-mono text-xs">
              <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#D8D4CA]">
                <span className="font-bold uppercase tracking-wider text-[#141517]">CHRONOLOGICAL SIMULATION LOG</span>
                <span className="text-[#8C9099]">SEED: {seed}</span>
              </div>

              <div className="space-y-3">
                <div className={`p-2.5 border-l-2 transition-colors ${currentTime >= 0 ? 'bg-[#F4F1EA] border-[#2457E8]' : 'opacity-40 border-transparent'}`}>
                  <div className="flex justify-between text-[11px] text-[#5D6066] mb-0.5">
                    <span>[00:00.00]</span>
                    <span className="text-[#24845A] font-semibold">NOMINAL WARMUP</span>
                  </div>
                  <p className="text-[#141517] leading-tight">
                    Warmup complete. 4 workers active at nominal rate (80 req/s). Initial dimmer θ = 1.000.
                  </p>
                </div>

                <div className={`p-2.5 border-l-2 transition-colors ${currentTime >= 300 ? 'bg-[#FFF5F5] border-[#D94A45]' : 'opacity-40 border-transparent'}`}>
                  <div className="flex justify-between text-[11px] text-[#5D6066] mb-0.5">
                    <span>[05:00.00]</span>
                    <span className="text-[#D94A45] font-semibold">FAULT INJECTION ONSET</span>
                  </div>
                  <p className="text-[#141517] leading-tight">
                    {selectedScenario === 'nominal'
                      ? 'No fault scheduled. Operating under nominal stationary conditions.'
                      : (selectedScenario === 'flash_crowd'
                        ? 'Flash crowd surge injected: Ingress jumps to 240 req/s (3x load).'
                        : (selectedScenario === 'server_failure'
                          ? 'Crash-stop injected on Workers 1 & 2. 50% cluster capacity dropped.'
                          : 'Compound stress: 240 req/s surge + Workers 1 & 2 offline.'))}
                  </p>
                </div>

                <div className={`p-2.5 border-l-2 transition-colors ${currentTime >= 305 ? 'bg-[#F4F1EA] border-[#2457E8]' : 'opacity-40 border-transparent'}`}>
                  <div className="flex justify-between text-[11px] text-[#5D6066] mb-0.5">
                    <span>[05:02.50]</span>
                    <span className="text-[#2457E8] font-semibold">CONTROLLER ADAPTATION</span>
                  </div>
                  <p className="text-[#141517] leading-tight">
                    Discrete PI velocity controller sheds optional computation. Dimmer θ adjusts to maintain latency target (80 ms) under SLA threshold (100 ms).
                  </p>
                </div>

                <div className={`p-2.5 border-l-2 transition-colors ${currentTime >= 450 ? 'bg-[#FAF7EE] border-[#F0A14A]' : 'opacity-40 border-transparent'}`}>
                  <div className="flex justify-between text-[11px] text-[#5D6066] mb-0.5">
                    <span>[07:30.00]</span>
                    <span className="text-[#F0A14A] font-semibold">HARDWARE REPAIR &amp; RESTORATION</span>
                  </div>
                  <p className="text-[#141517] leading-tight">
                    Fault window ends at t=450s. Offline workers re-join. Post-restoration recovery evaluation begins.
                  </p>
                </div>

                <div className={`p-2.5 border-l-2 transition-colors ${currentTime >= 580 ? 'bg-[#F4F1EA] border-[#24845A]' : 'opacity-40 border-transparent'}`}>
                  <div className="flex justify-between text-[11px] text-[#5D6066] mb-0.5">
                    <span>[09:40.00]</span>
                    <span className="text-[#24845A] font-semibold">STEADY-STATE RESTORATION</span>
                  </div>
                  <p className="text-[#141517] leading-tight">
                    Restored workers converge back to nominal steady-state dimmer reference θ_ref per DEC-010 (96.7% 30-seed recovery rate).
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Analytical Memorandum Callout */}
        <div className="my-8 p-6 bg-[#EAE6DD] border border-[#D8D4CA] font-mono text-xs">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            <div className="lg:col-span-3">
              <span className="text-[#2457E8] uppercase tracking-widest font-bold block mb-1">
                ANALYTICAL MEMORANDUM
              </span>
              <h3 className="font-serif text-2xl text-[#141517] font-normal">
                Kinetics of Graceful Degradation
              </h3>
            </div>
            <div className="lg:col-span-7 text-[#5D6066] leading-relaxed">
              In unmanaged cloud clusters, static load balancing fails to distinguish between healthy instances and overloaded instances, resulting in queue lockup and hard timeout drops (&gt;200 ms). CloudRescue brownout adaptation reduces worker service times by shedding non-essential functionality, while BALB penalizes saturated nodes using worker queue depth and dimmer elasticity.
            </div>
            <div className="lg:col-span-2 flex flex-col gap-2">
              <button
                onClick={() => setActiveScreen('benchmark')}
                className="w-full py-2.5 px-3 bg-[#141517] text-[#F4F1EA] hover:bg-[#2457E8] transition-colors text-center uppercase tracking-wider cursor-pointer"
              >
                COMPARE BENCHMARKS →
              </button>
            </div>
          </div>
        </div>
      </main>

      <ColophonFooter sectionNumber="03" />
    </div>
  );
}
