import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useNavigate } from "react-router-dom";
import BottomNav from "../components/BottomNav";
import TopHeader from "../components/TopHeader";
import { Plus, Users, Radio, Lock, Mic, Music, Gamepad2, Code, Briefcase, Heart, Sparkles } from "lucide-react";
import { toast } from "sonner";

const Rooms = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [showCreateModal, setShowCreateModal] = useState(false);

  const categories = [
    { id: "all", name: "All Rooms", icon: <Radio size={16} /> },
    { id: "music", name: "Music", icon: <Music size={16} /> },
    { id: "tech", name: "Tech", icon: <Code size={16} /> },
    { id: "gaming", name: "Gaming", icon: <Gamepad2 size={16} /> },
    { id: "business", name: "Business", icon: <Briefcase size={16} /> },
    { id: "lifestyle", name: "Lifestyle", icon: <Heart size={16} /> },
    { id: "general", name: "General", icon: <Sparkles size={16} /> },
  ];

  useEffect(() => {
    fetchRooms();
  }, [selectedCategory]);

  const fetchRooms = async () => {
    try {
      const query = selectedCategory === "all" ? "" : `?category=${selectedCategory}`;
      const res = await axios.get(`${API}/rooms${query}`);
      setRooms(res.data);
    } catch (error) {
      toast.error("Failed to load rooms");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRoom = () => {
    setShowCreateModal(true);
  };

  const getCategoryIcon = (category) => {
    const cat = categories.find(c => c.id === category);
    return cat ? cat.icon : <Radio size={16} />;
  };

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <TopHeader title="VibeRooms" subtitle="Join live audio conversations 🎙️ Clubhouse-style" />

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Create Room Button */}
        <button
          onClick={handleCreateRoom}
          className="w-full mb-6 py-4 px-6 rounded-2xl bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold text-lg flex items-center justify-center gap-3 hover:opacity-90 transition-all neon-glow"
          data-testid="create-room-btn"
        >
          <Plus size={24} />
          Start a Vibe Room
        </button>

        {/* Category Filter */}
        <div className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide pb-2">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-full font-medium text-sm transition-all ${
                selectedCategory === cat.id
                  ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                  : 'glass-card text-gray-400 hover:bg-gray-800/50'
              }`}
            >
              {cat.icon}
              {cat.name}
            </button>
          ))}
        </div>

        {/* Rooms List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full mx-auto"></div>
          </div>
        ) : rooms.length === 0 ? (
          <div className="text-center py-12 glass-card">
            <Radio size={48} className="text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 mb-2">No active rooms</p>
            <p className="text-gray-500 text-sm">Be the first to start a conversation!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {rooms.map((room) => (
              <div
                key={room.id}
                onClick={() => navigate(`/rooms/${room.id}`)}
                className="glass-card p-5 cursor-pointer hover:scale-[1.01] transition-transform"
                data-testid="room-card"
              >
                <div className="flex items-start gap-4">
                  {/* Room Icon */}
                  <div className="w-14 h-14 flex-shrink-0 rounded-2xl bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                    {getCategoryIcon(room.category)}
                  </div>

                  {/* Room Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-bold text-lg text-white truncate">{room.name}</h3>
                      {room.isPrivate && <Lock size={14} className="text-gray-400" />}
                    </div>
                    
                    {room.description && (
                      <p className="text-gray-400 text-sm mb-2 line-clamp-2">{room.description}</p>
                    )}

                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <div className="flex items-center gap-1">
                        <Users size={14} />
                        <span>{room.participants?.length || 0} / {room.maxParticipants}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Mic size={14} />
                        <span>{room.hostName}</span>
                      </div>
                      {room.tags && room.tags.length > 0 && (
                        <span className="px-2 py-0.5 rounded-full bg-cyan-400/10 text-cyan-400">
                          {room.tags[0]}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Join Indicator */}
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse"></div>
                    <span className="text-green-400 text-xs font-semibold">LIVE</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <BottomNav active="rooms" />

      {/* Create Room Modal */}
      {showCreateModal && (
        <CreateRoomModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchRooms();
          }}
          currentUser={currentUser}
        />
      )}
    </div>
  );
};

const CreateRoomModal = ({ onClose, onSuccess, currentUser }) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("general");
  const [isPrivate, setIsPrivate] = useState(false);
  const [creating, setCreating] = useState(false);

  const categories = [
    { id: "general", name: "General" },
    { id: "music", name: "Music" },
    { id: "tech", name: "Tech" },
    { id: "gaming", name: "Gaming" },
    { id: "business", name: "Business" },
    { id: "lifestyle", name: "Lifestyle" },
  ];

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.error("Please enter room name");
      return;
    }

    setCreating(true);
    try {
      const res = await axios.post(`${API}/rooms?userId=${currentUser.id}`, {
        name: name.trim(),
        description: description.trim(),
        category,
        isPrivate,
        tags: []
      });
      
      toast.success("Room created successfully!");
      onSuccess();
      
      // Navigate to room
      window.location.href = `/rooms/${res.data.id}`;
    } catch (error) {
      toast.error("Failed to create room");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card p-6 w-full max-w-md">
        <h2 className="text-xl font-bold neon-text mb-4">Start a Vibe Room</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Room Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Late Night Music Chat"
              className="w-full px-4 py-3 bg-gray-900/50 border-2 border-cyan-400/30 rounded-xl focus:border-cyan-400 focus:outline-none text-white"
              maxLength={50}
              data-testid="room-name-input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Description (Optional)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What's this room about?"
              className="w-full px-4 py-3 bg-gray-900/50 border-2 border-cyan-400/30 rounded-xl focus:border-cyan-400 focus:outline-none text-white resize-none"
              rows={3}
              maxLength={200}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
            <div className="grid grid-cols-3 gap-2">
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setCategory(cat.id)}
                  className={`py-2 px-3 rounded-xl text-sm font-medium transition-all ${
                    category === cat.id
                      ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                      : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
                  }`}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="private"
              checked={isPrivate}
              onChange={(e) => setIsPrivate(e.target.checked)}
              className="w-5 h-5 rounded border-2 border-cyan-400/30 bg-gray-900/50"
            />
            <label htmlFor="private" className="text-sm text-gray-300">
              Make this room private (invite only)
            </label>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-full border-2 border-gray-600 text-gray-300 font-semibold hover:bg-gray-800/50"
            disabled={creating}
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            disabled={creating}
            className="flex-1 py-3 rounded-full text-white font-semibold bg-gradient-to-r from-cyan-400 to-purple-500 hover:opacity-90 disabled:opacity-50"
            data-testid="room-create-confirm"
          >
            {creating ? "Creating..." : "Start Room"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Rooms;
