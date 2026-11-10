import React, { useState, useEffect } from 'react';
import { fetchScenarios } from '../api';
import ColophonFooter from '../components/ColophonFooter';
import { AlertTriangle, Zap, Server, ShieldAlert } from 'lucide-react';

export default function Screen2Inquiry({
  selectedScenario,
  setSelectedScenario,
  setActiveScreen,
}) {
  const [scenarios, setScenarios] = useState([]);

  useEffect(() => {
    fetchScenarios()
      .then((data) => {
        setScenarios(data);
      })
      .catch((err) => {
        console.error('Failed to load scenarios:', err);
      });
  }, []);

  const getScenarioIcon = (id) => {
    switch (id) {
      case 'server_failure':
        return <Server className="text-[#2457E8]" size={20} />;
      case 'flash_crowd':
        return <Zap className="text-[#F0A14A]" size={20} />;
      case 'compound_stress':
        return <ShieldAlert className="text-[#D94A45]" size={20} />;
      default:
        return <AlertTriangle className="text-[#5D6066]" size={20} />;
    }
  };

  return (
    <div className="w-full pt-16 min-h-screen bg-[#F4F1EA] text-[#141517]">
      <main className="w-full px-6 lg:px-12 py-10 lg:py-16">
        {/* Monograph Metadata Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-[#D8D4CA] font-mono text-[11px] uppercase tracking-wider text-[#5D6066]">
          <div className="flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 bg-[#2457E8]"></span>
            <span className="font-semibold text-[#141517]">SECTION 02 // EXPERIMENTAL INQUIRY</span>
            <span className="text-[#8C9099]">/</span>
            <span>STRESS VECTOR CONFIGURATION</span>
          </div>
          <div className="flex items-center gap-4 text-[#8C9099]">
            <span>CONTROLLED DISRUPTIONS</span>
            <span>FOLIO 02 / 18</span>
          </div>
        </div>

        {/* Lead Editorial Header */}
        <div className="pt-10 lg:pt-14 pb-8 space-y-4 max-w-3xl">
          <div className="font-mono text-xs uppercase tracking-[0.25em] text-[#2457E8] font-semibold">
            FAILURE & WORKLOAD VECTOR MATRIX
          </div>
          <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl text-[#141517] tracking-tight leading-none">
            What could <span className="italic font-normal">go wrong?</span>
          </h1>
          <p className="text-base text-[#5D6066] font-light leading-relaxed">
            In unmanaged distributed systems, localized queue saturation causes systemic latency collapse. Select an empirical stress scenario to examine how discrete brownout adaptation and brownout-aware routing respond.
          </p>
        </div>

        {/* 4 Interactive Scenario Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
          {scenarios.map((sc) => {
            const isSelected = selectedScenario === sc.id;
            return (
              <div
                key={sc.id}
                onClick={() => setSelectedScenario(sc.id)}
                className={`p-6 border transition-all cursor-pointer bg-[#F7F5EE] flex flex-col justify-between ${
                  isSelected
                    ? 'border-[#2457E8] ring-1 ring-[#2457E8] shadow-sm'
                    : 'border-[#D8D4CA] hover:border-[#141517]'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      {getScenarioIcon(sc.id)}
                      <span className="font-mono text-xs uppercase tracking-wider text-[#141517] font-semibold">
                        {sc.id.replace('_', ' ')}
                      </span>
                    </div>
                    <span
                      className={`font-mono text-[10px] uppercase px-2 py-0.5 border ${
                        isSelected
                          ? 'border-[#2457E8] text-[#2457E8] font-semibold bg-[#2457E8]/5'
                          : 'border-[#D8D4CA] text-[#8C9099]'
                      }`}
                    >
                      {isSelected ? 'ACTIVE VECTOR' : 'SELECT'}
                    </span>
                  </div>

                  <h2 className="font-serif text-2xl text-[#141517] font-medium mb-2">
                    {sc.name}
                  </h2>
                  <p className="text-xs text-[#5D6066] leading-relaxed mb-6 font-light">
                    {sc.description}
                  </p>
                </div>

                <div className="border-t border-[#D8D4CA] pt-4 grid grid-cols-3 gap-2 font-mono text-[10px] text-[#5D6066]">
                  <div>
                    <span className="text-[#8C9099] block uppercase">Nominal Rate</span>
                    <span className="text-[#141517] font-medium">{sc.arrival_rate_nom} req/s</span>
                  </div>
                  <div>
                    <span className="text-[#8C9099] block uppercase">Peak Rate</span>
                    <span className="text-[#141517] font-medium">{sc.arrival_rate_burst} req/s</span>
                  </div>
                  <div>
                    <span className="text-[#8C9099] block uppercase">Failed Workers</span>
                    <span className="text-[#141517] font-medium">
                      {sc.failed_workers.length > 0 ? sc.failed_workers.join(', ') : 'None (4/4 healthy)'}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Timeline Visualization of the Injected Stress Vector */}
        <div className="mt-12 p-6 border border-[#D8D4CA] bg-[#F7F5EE]">
          <div className="flex flex-col sm:flex-row items-baseline justify-between mb-4">
            <div className="font-mono text-xs uppercase tracking-widest text-[#141517] font-semibold">
              SIMULATION TIMELINE SCHEDULE [ T_SIM = 1,000s ]
            </div>
            <div className="font-mono text-[11px] text-[#8C9099] uppercase">
              ACTIVE SELECTION: {selectedScenario.toUpperCase()}
            </div>
          </div>

          {/* Graphical timeline strip */}
          <div className="relative w-full h-12 bg-[#ECE7DE] border border-[#D8D4CA] flex items-center font-mono text-[10px]">
            {/* Warm-up 0 - 100s */}
            <div
              style={{ width: '10%' }}
              className="h-full bg-[#D8D4CA]/50 border-r border-[#D8D4CA] flex items-center justify-center text-[#5D6066]"
            >
              WARMUP (100s)
            </div>

            {/* Nominal Pre-Shock 100 - 300s */}
            <div
              style={{ width: '20%' }}
              className="h-full border-r border-[#D8D4CA] flex items-center justify-center text-[#5D6066]"
            >
              PRE-SHOCK (200s)
            </div>

            {/* Shock Period 300 - 450s */}
            <div
              style={{ width: '15%' }}
              className={`h-full border-r border-[#D8D4CA] flex items-center justify-center font-semibold text-center ${
                selectedScenario === 'nominal'
                  ? 'bg-transparent text-[#8C9099]'
                  : 'bg-[#D94A45]/20 text-[#D94A45]'
              }`}
            >
              {selectedScenario === 'nominal' ? 'NO SHOCK' : 'STRESS [300-450s]'}
            </div>

            {/* Post-Restoration 450 - 1000s */}
            <div
              style={{ width: '55%' }}
              className="h-full bg-[#24845A]/10 flex items-center justify-center text-[#24845A] font-medium"
            >
              POST-RESTORATION & RECOVERY HORIZON (550s)
            </div>
          </div>

          <div className="flex justify-between font-mono text-[10px] text-[#8C9099] mt-2">
            <span>t = 0s</span>
            <span>t = 100s (Warmup End)</span>
            <span>t = 300s (Shock Start)</span>
            <span>t = 450s (Repair Time)</span>
            <span>t = 1,000s (Sim End)</span>
          </div>
        </div>

        {/* Parameter Inspector & Transition Bar */}
        <div className="mt-8 flex flex-col md:flex-row items-center justify-between gap-6 p-6 border border-[#D8D4CA] bg-[#141517] text-[#F4F1EA]">
          <div className="space-y-1">
            <div className="font-mono text-xs uppercase tracking-wider text-[#2457E8]">
              READY FOR ARCHITECTURE LAB
            </div>
            <div className="text-sm text-[#8C9099]">
              Replay this stress scenario under CFG-A (Baseline), CFG-B (Brownout Only), or CFG-C (Full CloudRescue with BALB).
            </div>
          </div>
          <button
            onClick={() => setActiveScreen('simulator')}
            className="w-full md:w-auto px-6 py-3 bg-[#2457E8] text-[#F4F1EA] font-mono text-xs uppercase tracking-widest hover:bg-[#1a44bf] transition-colors cursor-pointer"
          >
            [ LAUNCH SIMULATION LAB → ]
          </button>
        </div>
      </main>

      <ColophonFooter sectionNumber="02" />
    </div>
  );
}
