import React from "react";
import { Sparkles, Heart, Zap } from "lucide-react";

const VibeScore = ({ score = 85, userHandle }) => {
  const getVibeLevel = (score) => {
    if (score >= 90) return { label: "Perfect Match", color: "from-pink-400 to-rose-500", emoji: "🔥" };
    if (score >= 75) return { label: "Great Vibe", color: "from-purple-400 to-pink-500", emoji: "✨" };
    if (score >= 60) return { label: "Good Match", color: "from-cyan-400 to-blue-500", emoji: "💫" };
    return { label: "New Connection", color: "from-gray-400 to-gray-600", emoji: "🌟" };
  };

  const vibe = getVibeLevel(score);

  return (
    <div className="relative group">
      <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r ${vibe.color} text-white text-sm font-semibold cursor-pointer hover:scale-105 transition-transform`}>
        <Sparkles size={14} />
        <span>{score}% Vibe</span>
      </div>
      
      {/* Tooltip on hover */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-50">
        <div className="glass-card px-4 py-3 rounded-xl shadow-2xl whitespace-nowrap">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{vibe.emoji}</span>
            <span className="font-bold text-white">{vibe.label}</span>
          </div>
          <div className="text-xs text-gray-400 space-y-1">
            <div className="flex items-center gap-2">
              <Heart size={12} className="text-pink-400" />
              <span>Shared interests: 8</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap size={12} className="text-yellow-400" />
              <span>Activity sync: High</span>
            </div>
          </div>
        </div>
        <div className="w-3 h-3 bg-gray-800 transform rotate-45 absolute -bottom-1 left-1/2 -translate-x-1/2"></div>
      </div>
    </div>
  );
};

export default VibeScore;
