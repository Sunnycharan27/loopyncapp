import React from "react";
import { MessageCircle, Bell } from "lucide-react";
import { useNavigate } from "react-router-dom";

const TopHeader = ({ title, subtitle, showIcons = true }) => {
  const navigate = useNavigate();

  return (
    <div className="sticky top-0 z-10 bg-gray-800 border-b border-gray-700 p-4 mb-0 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <img 
          src="/loopync-logo.jpg" 
          alt="Loopync" 
          className="w-10 h-10 rounded-full cursor-pointer hover:scale-110 transition-transform"
          onClick={() => navigate('/')}
        />
        <div>
          <h1 className="text-xl font-bold text-white">{title}</h1>
          {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
        </div>
      </div>
      
      {showIcons && (
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate('/notifications')}
            className="relative w-10 h-10 rounded-full flex items-center justify-center bg-gray-700 text-white hover:bg-gray-600 transition-colors"
            data-testid="header-notifications-btn"
          >
            <Bell size={20} />
            <div className="absolute top-1 right-1 w-2 h-2 rounded-full bg-cyan-400"></div>
          </button>
          <button
            onClick={() => navigate('/messenger')}
            className="relative w-10 h-10 rounded-full flex items-center justify-center bg-gray-700 text-white hover:bg-gray-600 transition-colors"
            data-testid="header-messenger-btn"
          >
            <MessageCircle size={20} />
            <div className="absolute top-1 right-1 w-2 h-2 rounded-full bg-cyan-400"></div>
          </button>
        </div>
      )}
    </div>
  );
};

export default TopHeader;
