import React from "react";
import { Users } from "lucide-react";
import { useNavigate } from "react-router-dom";

const TribeCard = ({ tribe, currentUser, onJoinLeave }) => {
  const navigate = useNavigate();
  const isMember = tribe.members?.includes(currentUser?.id);

  return (
    <div data-testid="tribe-card" className="glass-card p-5 hover:scale-[1.02] transition-transform cursor-pointer">
      <div onClick={() => navigate(`/tribes/${tribe.id}`)}>
        <img
          src={tribe.avatar}
          alt={tribe.name}
          className="w-16 h-16 rounded-3xl mb-3"
        />
        <h3 className="font-bold text-lg mb-1">{tribe.name}</h3>
        <p className="text-xs text-gray-400 mb-3 line-clamp-2">{tribe.description}</p>
        
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
          <Users size={14} />
          <span>{tribe.memberCount || 0} members</span>
        </div>

        <div className="flex flex-wrap gap-1 mb-3">
          {tribe.tags?.slice(0, 3).map((tag, idx) => (
            <span key={idx} className="px-2 py-1 rounded-full text-xs bg-cyan-400/10 text-cyan-400">
              #{tag}
            </span>
          ))}
        </div>
      </div>

      <button
        data-testid="tribe-join-btn"
        onClick={(e) => {
          e.stopPropagation();
          onJoinLeave(tribe.id, isMember);
        }}
        className={`w-full py-2 rounded-full text-sm font-semibold ${
          isMember
            ? 'bg-gray-700 text-white hover:bg-gray-600'
            : 'btn-primary'
        }`}
      >
        {isMember ? 'Leave' : 'Join Tribe'}
      </button>
    </div>
  );
};

export default TribeCard;