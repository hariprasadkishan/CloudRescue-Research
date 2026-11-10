import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';

const NAV_ITEMS = [
  { id: 'overview', label: '01 Overview', short: 'Overview' },
  { id: 'inquiry', label: '02 Inquiry', short: 'Inquiry' },
  { id: 'simulator', label: '03 Simulator', short: 'Simulator' },
  { id: 'benchmark', label: '04 Benchmark', short: 'Benchmark' },
  { id: 'analytics', label: '05 Analytics', short: 'Analytics' },
  { id: 'methodology', label: '06 Methodology', short: 'Methodology' },
  { id: 'publication', label: '07 Publication', short: 'Publication' },
];

export default function Navigation({ activeScreen, setActiveScreen }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-[#F4F1EA]/95 backdrop-blur-sm border-b border-[#D8D4CA]">
      <div className="h-16 w-full px-6 lg:px-12 flex items-center justify-between gap-6">
        {/* Brandmark & Edition Tag */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setActiveScreen('overview')}
            className="font-mono text-sm tracking-[0.2em] uppercase font-semibold text-[#141517] hover:text-[#2457E8] transition-colors text-left"
          >
            CLOUDRESCUE
          </button>
          <span className="hidden sm:inline-block font-mono text-[11px] text-[#8C9099] uppercase tracking-widest pl-3 border-l border-[#D8D4CA]">
            SYS.VER 4.2 · ISSUE 2026
          </span>
        </div>

        {/* Desktop Swiss Navigation */}
        <nav className="hidden xl:flex items-center gap-7 h-full text-[12px] font-mono tracking-wider uppercase">
          {NAV_ITEMS.map((item) => {
            const isActive = activeScreen === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveScreen(item.id)}
                className={`h-full flex items-center transition-colors border-b-2 text-left cursor-pointer ${
                  isActive
                    ? 'text-[#2457E8] border-[#2457E8] font-medium'
                    : 'text-[#5D6066] hover:text-[#141517] border-transparent'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Desktop Action & Mobile Toggle */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveScreen('simulator')}
            className="hidden sm:inline-flex items-center justify-center px-4 py-2 bg-[#141517] text-[#F4F1EA] text-xs font-mono tracking-widest uppercase hover:bg-[#2457E8] focus:outline-none focus:ring-2 focus:ring-[#2457E8] transition-all cursor-pointer"
          >
            [ INITIALIZE SIMULATOR → ]
          </button>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="xl:hidden p-2 text-[#141517] hover:text-[#2457E8] border border-[#D8D4CA] rounded-sm"
            aria-label="Toggle Navigation"
          >
            {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="xl:hidden bg-[#F4F1EA] border-b border-[#D8D4CA] px-6 py-4 flex flex-col gap-2 font-mono text-xs uppercase tracking-wider">
          {NAV_ITEMS.map((item) => {
            const isActive = activeScreen === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveScreen(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`py-2 px-3 text-left transition-colors border-l-2 ${
                  isActive
                    ? 'text-[#2457E8] border-[#2457E8] bg-[#ECE7DE] font-medium'
                    : 'text-[#5D6066] border-transparent hover:text-[#141517]'
                }`}
              >
                {item.label}
              </button>
            );
          })}
          <button
            onClick={() => {
              setActiveScreen('simulator');
              setMobileMenuOpen(false);
            }}
            className="mt-2 w-full py-2.5 bg-[#141517] text-[#F4F1EA] text-xs font-mono tracking-widest uppercase text-center hover:bg-[#2457E8]"
          >
            [ INITIALIZE SIMULATOR → ]
          </button>
        </div>
      )}
    </header>
  );
}
