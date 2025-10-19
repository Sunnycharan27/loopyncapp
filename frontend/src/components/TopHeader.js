import React from "react";
import { MessageCircle, Bell, User } from "lucide-react";
import { useNavigate } from "react-router-dom";

const TopHeader = ({ title, subtitle, showIcons = true }) => {
  const navigate = useNavigate();

  return (
    <div className="sticky top-0 z-10 glass-surface p-4 mb-4 flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold neon-text">{title}</h1>
        {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}
      </div>
      
      {showIcons && (
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/notifications')}
            className="relative w-10 h-10 rounded-full flex items-center justify-center bg-cyan-400/10 text-cyan-400 hover:bg-cyan-400/20"
            data-testid="header-notifications-btn"
          >
            <Bell size={20} />
            <div className="absolute top-1 right-1 w-2 h-2 rounded-full bg-pink-400"></div>
          </button>
          <button
            onClick={() => navigate('/messenger')}
            className="relative w-10 h-10 rounded-full flex items-center justify-center bg-cyan-400/10 text-cyan-400 hover:bg-cyan-400/20"
            data-testid="header-messenger-btn"
          >
            <MessageCircle size={20} />
            <div className="absolute top-1 right-1 w-2 h-2 rounded-full bg-pink-400"></div>
          </button>
          <button
            onClick={() => navigate('/profile')}
            className="w-10 h-10 rounded-full flex items-center justify-center bg-cyan-400/10 text-cyan-400 hover:bg-cyan-400/20"
            data-testid="header-profile-btn"
          >
            <User size={20} />
          </button>
        </div>
      )}
    </div>
  );
};

export default TopHeader;
