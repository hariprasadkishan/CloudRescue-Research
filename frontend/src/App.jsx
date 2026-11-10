import React, { useState, useEffect } from 'react';
import Navigation from './components/Navigation';
import Screen1Overview from './screens/Screen1Overview';
import Screen2Inquiry from './screens/Screen2Inquiry';
import Screen3Simulator from './screens/Screen3Simulator';
import Screen4Benchmark from './screens/Screen4Benchmark';
import Screen5Analytics from './screens/Screen5Analytics';
import Screen6Methodology from './screens/Screen6Methodology';
import Screen7Publication from './screens/Screen7Publication';

export default function App() {
  const [activeScreen, setActiveScreen] = useState('overview');
  const [selectedScenario, setSelectedScenario] = useState('compound_stress');

  // Scroll to top whenever screen changes
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [activeScreen]);

  return (
    <div className="min-h-screen bg-[#F4F1EA] text-[#141517] font-sans antialiased selection:bg-[#2457E8] selection:text-white">
      {/* Global Swiss Navigation Masthead */}
      <Navigation
        activeScreen={activeScreen}
        setActiveScreen={setActiveScreen}
      />

      {/* Dynamic Screen Viewport */}
      {activeScreen === 'overview' && (
        <Screen1Overview setActiveScreen={setActiveScreen} />
      )}

      {activeScreen === 'inquiry' && (
        <Screen2Inquiry
          selectedScenario={selectedScenario}
          setSelectedScenario={setSelectedScenario}
          setActiveScreen={setActiveScreen}
        />
      )}

      {activeScreen === 'simulator' && (
        <Screen3Simulator
          selectedScenario={selectedScenario}
          setSelectedScenario={setSelectedScenario}
          setActiveScreen={setActiveScreen}
        />
      )}

      {activeScreen === 'benchmark' && (
        <Screen4Benchmark
          selectedScenario={selectedScenario}
          setSelectedScenario={setSelectedScenario}
          setActiveScreen={setActiveScreen}
        />
      )}

      {activeScreen === 'analytics' && (
        <Screen5Analytics
          selectedScenario={selectedScenario}
          setSelectedScenario={setSelectedScenario}
          setActiveScreen={setActiveScreen}
        />
      )}

      {activeScreen === 'methodology' && (
        <Screen6Methodology
          setActiveScreen={setActiveScreen}
        />
      )}

      {activeScreen === 'publication' && (
        <Screen7Publication
          setActiveScreen={setActiveScreen}
        />
      )}
    </div>
  );
}
