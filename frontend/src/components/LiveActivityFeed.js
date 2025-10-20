import React, { useState, useEffect } from "react";
import { Sparkles, TrendingUp, Users, MapPin, Ticket, ShoppingBag } from "lucide-react";

const LiveActivityFeed = () => {
  const [activities, setActivities] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  const mockActivities = [
    { id: 1, type: "post", user: "Arjun", action: "posted a new vibe", icon: Sparkles, color: "text-cyan-400" },
    { id: 2, type: "trending", text: "#TechTalk is trending in Mumbai", icon: TrendingUp, color: "text-green-400" },
    { id: 3, type: "venue", user: "Priya", action: "checked in at Cafe Mondegar", icon: MapPin, color: "text-purple-400" },
    { id: 4, type: "event", text: "50 people attending TechCrunch tonight", icon: Ticket, color: "text-yellow-400" },
    { id: 5, type: "tribe", user: "15 people", action: "joined Fitness Warriors", icon: Users, color: "text-pink-400" },
    { id: 6, type: "marketplace", user: "Raj", action: "bought Python Mastery course", icon: ShoppingBag, color: "text-orange-400" },
  ];

  useEffect(() => {
    setActivities(mockActivities);
    
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % mockActivities.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  if (activities.length === 0) return null;

  const activity = activities[currentIndex];
  const Icon = activity.icon;

  return (
    <div className="w-full bg-gradient-to-r from-gray-900/50 to-gray-800/50 backdrop-blur-sm border-y border-gray-700/30 py-3 px-4 overflow-hidden">
      <div className="flex items-center gap-3 animate-slideInRight">
        <div className={`w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center flex-shrink-0 ${activity.color}`}>
          <Icon size={16} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-white truncate">
            {activity.user && (
              <span className="font-semibold">{activity.user} </span>
            )}
            <span className="text-gray-400">{activity.action || activity.text}</span>
          </p>
        </div>
        <div className="flex gap-1">
          {activities.map((_, idx) => (
            <div
              key={idx}
              className={`w-1.5 h-1.5 rounded-full transition-all ${
                idx === currentIndex ? 'bg-cyan-400 w-4' : 'bg-gray-600'
              }`}
            ></div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LiveActivityFeed;
