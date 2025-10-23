import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Mic, MicOff, UserPlus, Crown, Shield, LogOut, Users, MoreVertical } from "lucide-react";
import { toast } from "sonner";

const RoomDetail = () => {
  const { roomId } = useParams();
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hasJoined, setHasJoined] = useState(false);
  const [isMuted, setIsMuted] = useState(false);

  useEffect(() => {
    fetchRoom();
    const interval = setInterval(fetchRoom, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [roomId]);

  const fetchRoom = async () => {
    try {
      const res = await axios.get(`${API}/rooms/${roomId}`);
      setRoom(res.data);
      
      // Check if current user is in the room
      const inRoom = res.data.participants?.some(p => p.userId === currentUser.id);
      setHasJoined(inRoom);
      
      if (inRoom) {
        const me = res.data.participants.find(p => p.userId === currentUser.id);
        setIsMuted(me?.isMuted || false);
      }
    } catch (error) {
      toast.error("Failed to load room");
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async () => {
    try {
      await axios.post(`${API}/rooms/${roomId}/join?userId=${currentUser.id}`);
      toast.success("Joined room!");
      fetchRoom();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to join room");
    }
  };

  const handleLeaveRoom = async () => {
    try {
      await axios.post(`${API}/rooms/${roomId}/leave?userId=${currentUser.id}`);
      toast.success("Left room");
      navigate("/rooms");
    } catch (error) {
      toast.error("Failed to leave room");
    }
  };

  const handleToggleMute = async () => {
    try {
      await axios.post(`${API}/rooms/${roomId}/mute?userId=${currentUser.id}`);
      setIsMuted(!isMuted);
      fetchRoom();
    } catch (error) {
      toast.error("Failed to toggle mute");
    }
  };

  const handleEndRoom = async () => {
    if (!window.confirm("Are you sure you want to end this room?")) return;
    
    try {
      await axios.post(`${API}/rooms/${roomId}/end?userId=${currentUser.id}`);
      toast.success("Room ended");
      navigate("/rooms");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to end room");
    }
  };

  const isHost = room?.hostId === currentUser.id;
  const isModerator = room?.moderators?.includes(currentUser.id);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!room) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="text-center">
          <p className="text-gray-400 mb-4">Room not found</p>
          <button
            onClick={() => navigate("/rooms")}
            className="px-6 py-2 rounded-full bg-cyan-400 text-black font-semibold"
          >
            Back to Rooms
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      {/* Header */}
      <div className="sticky top-0 z-10 glass-surface px-4 py-3 flex items-center justify-between">
        <button
          onClick={() => navigate("/rooms")}
          className="w-10 h-10 rounded-full flex items-center justify-center bg-gray-800/50 hover:bg-gray-700/50"
        >
          <ArrowLeft size={20} className="text-white" />
        </button>
        
        <div className="flex-1 mx-4 text-center">
          <h1 className="font-bold text-white">{room.name}</h1>
          <p className="text-xs text-gray-400">
            <Users size={12} className="inline mr-1" />
            {room.participants?.length || 0} listening
          </p>
        </div>

        {isHost && (
          <button
            onClick={handleEndRoom}
            className="px-4 py-2 rounded-full bg-red-500/20 text-red-400 text-sm font-semibold hover:bg-red-500/30"
          >
            End Room
          </button>
        )}
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Room Info Card */}
        <div className="glass-card p-6 mb-6">
          <div className="text-center mb-4">
            <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
              <Mic size={48} className="text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">{room.name}</h2>
            {room.description && (
              <p className="text-gray-400 mb-4">{room.description}</p>
            )}
            <div className="flex items-center justify-center gap-3 text-sm">
              <span className="px-3 py-1 rounded-full bg-cyan-400/10 text-cyan-400 capitalize">
                {room.category}
              </span>
              <span className="text-gray-500">
                Hosted by {room.hostName}
              </span>
            </div>
          </div>

          {/* Join/Leave Button */}
          {!hasJoined ? (
            <button
              onClick={handleJoinRoom}
              className="w-full py-4 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold text-lg hover:opacity-90"
              data-testid="join-room-btn"
            >
              <Mic size={20} className="inline mr-2" />
              Join Room
            </button>
          ) : (
            <div className="flex gap-3">
              <button
                onClick={handleToggleMute}
                className={`flex-1 py-3 rounded-full font-semibold transition-all ${
                  isMuted
                    ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                    : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                }`}
              >
                {isMuted ? <MicOff size={20} className="inline mr-2" /> : <Mic size={20} className="inline mr-2" />}
                {isMuted ? "Unmute" : "Mute"}
              </button>
              <button
                onClick={handleLeaveRoom}
                className="flex-1 py-3 rounded-full bg-gray-700/50 text-white font-semibold hover:bg-gray-600/50"
                data-testid="leave-room-btn"
              >
                <LogOut size={20} className="inline mr-2" />
                Leave
              </button>
            </div>
          )}
        </div>

        {/* Participants List */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Users size={20} />
            Participants ({room.participants?.length || 0})
          </h3>

          <div className="space-y-3">
            {room.participants && room.participants.length > 0 ? (
              room.participants.map((participant, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold">
                      {participant.userName.charAt(0).toUpperCase()}
                    </span>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-white truncate">
                        {participant.userName}
                      </p>
                      {participant.userId === room.hostId && (
                        <Crown size={14} className="text-yellow-400" />
                      )}
                      {room.moderators?.includes(participant.userId) && participant.userId !== room.hostId && (
                        <Shield size={14} className="text-cyan-400" />
                      )}
                    </div>
                    <p className="text-xs text-gray-500">
                      {participant.isMuted ? "Muted" : "Speaking"}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    {participant.isMuted ? (
                      <MicOff size={16} className="text-red-400" />
                    ) : (
                      <Mic size={16} className="text-green-400" />
                    )}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-center text-gray-400 py-4">No participants yet</p>
            )}
          </div>
        </div>

        {/* Room Stats */}
        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="glass-card p-4 text-center">
            <p className="text-2xl font-bold text-white">{room.totalJoins || 0}</p>
            <p className="text-xs text-gray-400">Total Joins</p>
          </div>
          <div className="glass-card p-4 text-center">
            <p className="text-2xl font-bold text-white">{room.peakParticipants || 0}</p>
            <p className="text-xs text-gray-400">Peak Listeners</p>
          </div>
          <div className="glass-card p-4 text-center">
            <p className="text-2xl font-bold text-white">{room.participants?.length || 0}</p>
            <p className="text-xs text-gray-400">Current</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoomDetail;
