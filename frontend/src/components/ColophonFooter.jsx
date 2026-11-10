import React from 'react';

export default function ColophonFooter({ sectionNumber = '01' }) {
  return (
    <footer className="w-full bg-[#F4F1EA] border-t border-[#D8D4CA] py-12">
      <div className="w-full px-6 lg:px-12">
        <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-12 gap-8 pb-10 border-b border-[#D8D4CA] font-mono text-[11px] text-[#5D6066] leading-relaxed">
          {/* Mission / Scope */}
          <div className="lg:col-span-4 space-y-2">
            <div className="text-[#141517] font-semibold tracking-wider uppercase">
              CLOUDRESCUE COLOPHON
            </div>
            <p className="max-w-sm">
              Archival research record of discrete-event simulation experiments on distributed graceful degradation and brownout-aware adaptive load balancing (BALB).
            </p>
          </div>

          {/* Bibliographic Index */}
          <div className="lg:col-span-3 space-y-1.5">
            <div className="text-[#141517] font-semibold tracking-wider uppercase mb-1">
              BIBLIOGRAPHIC RECORD
            </div>
            <div>ISSN: Not assigned</div>
            <div>DOI: Not assigned (Pre-submission)</div>
            <div>SERIES: Cloud Resilience Working Papers</div>
            <div>DATA DEPOT: results/experiment_360/</div>
          </div>

          {/* System Coordinates */}
          <div className="lg:col-span-3 space-y-1.5">
            <div className="text-[#141517] font-semibold tracking-wider uppercase mb-1">
              TESTBED SPECIFICATIONS
            </div>
            <div>ENGINE: Discrete-Event Queuing Simulator</div>
            <div>TOPOLOGY: 4-Worker Cluster (c=8/worker)</div>
            <div>SLA THRESHOLD: 100 ms (Setpoint: 80 ms)</div>
            <div>DESIGN: Brutalist Swiss Monograph</div>
          </div>

          {/* System State & Section Code */}
          <div className="lg:col-span-2 flex flex-col justify-between items-start md:items-end">
            <div className="text-left md:text-right">
              STATUS: AUDIT CERTIFIED<br />
              DATASET: 360 / 360 RUNS
            </div>
            <span className="inline-block mt-4 px-2 py-0.5 border border-[#D8D4CA] text-[#141517] font-mono text-[10px]">
              SECTION [{sectionNumber}]
            </span>
          </div>
        </div>

        {/* Legal & Edition Baseline */}
        <div className="pt-6 flex flex-col sm:flex-row items-baseline justify-between gap-4 font-mono text-[10px] uppercase text-[#8C9099]">
          <div>
            © 2026 CLOUDRESCUE RESEARCH PROJECT. VERIFIED EXPERIMENTAL SIMULATION ARTIFACTS.
          </div>
          <div>
            EDITION VARIANT A — BRUTALIST SWISS MONOGRAPH
          </div>
        </div>
      </div>
    </footer>
  );
}
