import React from "react";
import { Home, Film, Compass, Wallet, User, Radio } from "lucide-react";
import { useNavigate } from "react-router-dom";

const BottomNav = ({ active }) => {
  const navigate = useNavigate();

  const navItems = [
    { id: "home", label: "Timeline", icon: Home, path: "/" },
    { id: "vibezone", label: "VibeZone", icon: Film, path: "/vibezone" },
    { id: "viberooms", label: "VibeRooms", icon: Radio, path: "/viberooms" },
    { id: "discover", label: "Discover", icon: Compass, path: "/discover" },
    { id: "profile", label: "Profile", icon: User, path: "/profile" },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 glass-surface border-t border-cyan-400/10 z-50">
      <div className="flex justify-around items-center py-3 max-w-2xl mx-auto">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = active === item.id;
          return (
            <button
              key={item.id}
              data-testid={`nav-${item.id}-btn`}
              onClick={() => navigate(item.path)}
              className={`flex flex-col items-center gap-1 px-3 py-2 rounded-2xl transition-all ${
                isActive
                  ? 'text-cyan-400 bg-cyan-400/10'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <Icon size={20} className={isActive ? 'neon-glow' : ''} />
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default BottomNav;