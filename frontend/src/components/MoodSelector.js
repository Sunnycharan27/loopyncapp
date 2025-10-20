import React, { useState } from "react";
import { Smile, Music, Coffee, Book, Dumbbell, Plane, Heart, Zap } from "lucide-react";

const MoodSelector = ({ currentMood, onMoodChange }) => {
  const [showSelector, setShowSelector] = useState(false);

  const moods = [
    { id: "happy", label: "Happy", emoji: "😊", color: "from-yellow-400 to-orange-500", icon: Smile },
    { id: "energetic", label: "Energetic", emoji: "⚡", color: "from-orange-400 to-red-500", icon: Zap },
    { id: "chill", label: "Chill", emoji: "😌", color: "from-blue-400 to-cyan-500", icon: Music },
    { id: "productive", label: "Productive", emoji: "💪", color: "from-green-400 to-emerald-500", icon: Dumbbell },
    { id: "creative", label: "Creative", emoji: "🎨", color: "from-purple-400 to-pink-500", icon: Book },
    { id: "adventurous", label: "Adventurous", emoji: "✈️", color: "from-indigo-400 to-purple-500", icon: Plane },
    { id: "romantic", label: "Romantic", emoji: "❤️", color: "from-pink-400 to-rose-500", icon: Heart },
    { id: "cozy", label: "Cozy", emoji: "☕", color: "from-amber-400 to-orange-500", icon: Coffee },
  ];

  const selectedMood = moods.find(m => m.id === currentMood) || moods[0];

  return (
    <div className="relative">
      <button
        onClick={() => setShowSelector(!showSelector)}
        className={`flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r ${selectedMood.color} text-white font-semibold hover:scale-105 transition-transform shadow-lg`}
      >
        <span className="text-lg">{selectedMood.emoji}</span>
        <span className="text-sm">I'm {selectedMood.label}</span>
      </button>

      {showSelector && (
        <>
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setShowSelector(false)}
          ></div>
          <div className="absolute top-full left-0 mt-2 w-80 glass-card p-4 rounded-xl shadow-2xl z-50">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-white">Set Your Vibe</h3>
              <button onClick={() => setShowSelector(false)} className="text-gray-400 hover:text-white">
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2">
              {moods.map(mood => {
                const Icon = mood.icon;
                return (
                  <button
                    key={mood.id}
                    onClick={() => {
                      onMoodChange(mood.id);
                      setShowSelector(false);
                    }}
                    className={`flex items-center gap-2 p-3 rounded-xl transition-all ${
                      currentMood === mood.id
                        ? `bg-gradient-to-r ${mood.color} text-white scale-105`
                        : 'glass-card hover:bg-gray-700/50'
                    }`}
                  >
                    <span className="text-2xl">{mood.emoji}</span>
                    <div className="text-left flex-1">
                      <div className="text-sm font-semibold">{mood.label}</div>
                    </div>
                    {currentMood === mood.id && (
                      <div className="w-2 h-2 rounded-full bg-white"></div>
                    )}
                  </button>
                );
              })}
            </div>

            <p className="text-xs text-center text-gray-500 mt-3">
              Your vibe is visible to your connections
            </p>
          </div>
        </>
      )}
    </div>
  );
};

export default MoodSelector;
