import React, { useEffect, useRef, useState } from "react";

// Lightweight, dependency-free guided tour using CSS overlays
// We attach data-tour-id attributes to highlight elements
// and render a small tooltip + overlay next to them.

const stepsNewUser = [
  { id: "header-notifications-btn", title: "Notifications", text: "See friend requests, likes, and messages here." },
  { id: "header-messenger-btn", title: "Messenger", text: "Chat with your friends in real-time." },
  { id: "btn-ai-safety", title: "AI Safety", text: "Run quick content safety checks using AI." },
  { id: "btn-ai-translate", title: "AI Translate", text: "Translate any text instantly." },
  { id: "btn-ai-rank", title: "AI Rank", text: "Rank documents by your query." },
  { id: "btn-ai-insights", title: "AI Insights", text: "Get quick insights or summaries." }
];

const stepsPowerUser = [
  { id: "header-messenger-btn", title: "Messenger Search", text: "Search friends and start DMs quickly in Messenger." },
  { id: "friend-search-input", title: "Friend Search", text: "Type to search your friends and start a chat instantly." },
];

const Tooltip = ({ targetEl, step, index, total, onNext, onPrev, onClose }) => {
  if (!targetEl) return null;
  const rect = targetEl.getBoundingClientRect();
  const top = rect.bottom + 8 + window.scrollY;
  const left = rect.left + window.scrollX;

  return (
    <div>
      {/* Backdrop overlay */}
      <div
        onClick={onClose}
        style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 1000 }}
      />
      {/* Highlight box */}
      <div
        style={{
          position: "absolute",
          top: rect.top + window.scrollY - 6,
          left: rect.left + window.scrollX - 6,
          width: rect.width + 12,
          height: rect.height + 12,
          border: "2px solid #22d3ee",
          borderRadius: 12,
          zIndex: 1002,
          pointerEvents: "none",
        }}
      />
      {/* Tooltip */}
      <div
        style={{ position: "absolute", top, left, zIndex: 1003, maxWidth: 280 }}
        className="glass-card p-4 rounded-2xl shadow-xl"
      >
        <h3 className="text-white font-bold mb-1">{step.title}</h3>
        <p className="text-gray-300 text-sm mb-3">{step.text}</p>
        <div className="flex items-center justify-between">
          <button onClick={onClose} className="px-3 py-1 rounded-full bg-gray-800 text-gray-300 border border-gray-700">Skip</button>
          <div className="flex items-center gap-2">
            <button onClick={onPrev} disabled={index === 0} className="px-3 py-1 rounded-full bg-gray-800 text-gray-300 border border-gray-700 disabled:opacity-50">Prev</button>
            <span className="text-gray-400 text-xs">{index + 1} / {total}</span>
            <button onClick={onNext} className="px-3 py-1 rounded-full bg-cyan-400 text-black">{index + 1 === total ? 'Done' : 'Next'}</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const GuidedTours = () => {
  const [active, setActive] = useState(null); // 'new' | 'power' | null
  const [index, setIndex] = useState(0);
  const [steps, setSteps] = useState([]);
  const [target, setTarget] = useState(null);

  // Attach data-tour-id on target elements via data-testid already present
  // We query by [data-testid] to find the element to highlight
  useEffect(() => {
    if (!active) return;
    const step = steps[index];
    if (!step) return;

    // Prefer data-testid-based lookup
    let el = document.querySelector(`[data-testid="${step.id}"]`);
    if (!el) {
      // Fallback to id lookup
      el = document.getElementById(step.id);
    }
    setTarget(el || null);
  }, [active, index, steps]);

  const startNewUserTour = () => {
    setSteps(stepsNewUser);
    setIndex(0);
    setActive('new');
  };

  const startPowerUserTour = () => {
    setSteps(stepsPowerUser);
    setIndex(0);
    setActive('power');
  };

  const closeTour = () => {
    setActive(null);
    setIndex(0);
    setSteps([]);
    setTarget(null);
  };

  return (
    <div className="fixed bottom-6 right-6 z-[999]">
      {/* Launcher */}
      {!active && (
        <div className="glass-card p-3 rounded-2xl flex gap-2">
          <button
            onClick={startNewUserTour}
            className="px-3 py-2 rounded-full bg-cyan-400/20 text-cyan-300 border border-cyan-500/30 text-xs"
            data-testid="tour-launch-new"
          >
            Start New User Tour
          </button>
          <button
            onClick={startPowerUserTour}
            className="px-3 py-2 rounded-full bg-purple-400/20 text-purple-300 border border-purple-500/30 text-xs"
            data-testid="tour-launch-power"
          >
            Start Power User Tour
          </button>
        </div>
      )}

      {/* Tooltip renderer */}
      {active && steps[index] && (
        <Tooltip
          targetEl={target}
          step={steps[index]}
          index={index}
          total={steps.length}
          onNext={() => {
            if (index + 1 >= steps.length) return closeTour();
            setIndex(index + 1);
          }}
          onPrev={() => setIndex(Math.max(0, index - 1))}
          onClose={closeTour}
        />
      )}
    </div>
  );
};

export default GuidedTours;
