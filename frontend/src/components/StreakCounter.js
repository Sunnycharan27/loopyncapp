import React, { useState, useContext } from "react";
import { AuthContext } from "../App";
import { Flame, Award, Target, TrendingUp } from "lucide-react";

const StreakCounter = () => {
  const { currentUser } = useContext(AuthContext);
  const [streak, setStreak] = useState(7); // Mock data
  const [showDetails, setShowDetails] = useState(false);

  const getStreakEmoji = (days) => {
    if (days >= 30) return "🏆";
    if (days >= 14) return "🔥";
    if (days >= 7) return "⚡";
    return "✨";
  };

  const getNextMilestone = (days) => {
    if (days < 7) return { target: 7, reward: "50 Credits" };
    if (days < 14) return { target: 14, reward: "100 Credits" };
    if (days < 30) return { target: 30, reward: "250 Credits" };
    return { target: 60, reward: "500 Credits" };
  };

  const milestone = getNextMilestone(streak);

  return (
    <div className="relative">
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-orange-400 to-red-500 text-white font-bold hover:scale-105 transition-transform"
      >
        <Flame size={18} />
        <span>{streak} Day Streak</span>
        <span className="text-xl">{getStreakEmoji(streak)}</span>
      </button>

      {showDetails && (
        <div className="absolute top-full right-0 mt-2 w-72 glass-card p-4 rounded-xl shadow-2xl z-50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-white">Your Streak</h3>
            <button onClick={() => setShowDetails(false)} className="text-gray-400 hover:text-white">
              ✕
            </button>
          </div>

          <div className="space-y-4">
            {/* Current Streak */}
            <div className="text-center py-4 bg-gradient-to-r from-orange-400/20 to-red-500/20 rounded-xl">
              <div className="text-4xl mb-2">{getStreakEmoji(streak)}</div>
              <div className="text-3xl font-bold text-white">{streak}</div>
              <div className="text-sm text-gray-400">Days Active</div>
            </div>

            {/* Next Milestone */}
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-400">Next Milestone</span>
                <span className="text-white font-semibold">{milestone.target} days</span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-orange-400 to-red-500 transition-all"
                  style={{ width: `${(streak / milestone.target) * 100}%` }}
                ></div>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <Award size={14} className="text-yellow-400" />
                <span className="text-xs text-gray-400">Reward: {milestone.reward}</span>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-3">
              <div className="glass-card p-3 rounded-lg text-center">
                <Target size={20} className="text-cyan-400 mx-auto mb-1" />
                <div className="text-lg font-bold text-white">45</div>
                <div className="text-xs text-gray-400">Posts</div>
              </div>
              <div className="glass-card p-3 rounded-lg text-center">
                <TrendingUp size={20} className="text-green-400 mx-auto mb-1" />
                <div className="text-lg font-bold text-white">127</div>
                <div className="text-xs text-gray-400">Interactions</div>
              </div>
            </div>

            <p className="text-xs text-center text-gray-500">
              Keep the streak alive! Post daily to earn rewards
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default StreakCounter;
