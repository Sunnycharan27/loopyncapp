import React, { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useParams, useNavigate } from "react-router-dom";
import { 
  ArrowLeft, Mic, MicOff, Crown, Shield, LogOut, Users, 
  Send, Smile, Hand, MoreVertical, UserX, MessageCircle
} from "lucide-react";
import { toast } from "sonner";

const RoomDetail = () => {
  const { roomId } = useParams();
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hasJoined, setHasJoined] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [handRaised, setHandRaised] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const messagesEndRef = useRef(null);
  const chatInputRef = useRef(null);

  const emojis = ["❤️", "👍", "🔥", "✨", "⭐", "👏", "🎉", "😂"];

  useEffect(() => {
    fetchRoom();
    fetchMessages();
    const roomInterval = setInterval(fetchRoom, 3000);
    const msgInterval = setInterval(fetchMessages, 2000);
    return () => {
      clearInterval(roomInterval);
      clearInterval(msgInterval);
    };
  }, [roomId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchRoom = async () => {
    try {
      const res = await axios.get(`${API}/rooms/${roomId}`);
      setRoom(res.data);
      
      const inRoom = res.data.participants?.some(p => p.userId === currentUser.id);
      setHasJoined(inRoom);
      
      if (inRoom) {
        const me = res.data.participants.find(p => p.userId === currentUser.id);
        setIsMuted(me?.isMuted || false);
        setHandRaised(me?.handRaised || false);
      }
    } catch (error) {
      toast.error("Failed to load room");
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async () => {
    try {
      const res = await axios.get(`${API}/rooms/${roomId}/messages?limit=100`);
      setMessages(res.data);
    } catch (error) {
      // Silent fail
    }
  };

  const handleJoinRoom = async () => {
    try {
      await axios.post(`${API}/rooms/${roomId}/join?userId=${currentUser.id}`);
      toast.success("Joined room!");
      fetchRoom();
      fetchMessages();
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

  const handleToggleHandRaise = async () => {
    try {
      await axios.post(`${API}/rooms/${roomId}/handRaise?userId=${currentUser.id}`);
      setHandRaised(!handRaised);
      fetchRoom();
    } catch (error) {
      toast.error("Failed to toggle hand");
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      await axios.post(`${API}/rooms/${roomId}/messages?userId=${currentUser.id}&message=${encodeURIComponent(newMessage)}`);
      setNewMessage("");
      fetchMessages();
      chatInputRef.current?.focus();
    } catch (error) {
      toast.error("Failed to send message");
    }
  };

  const handleSendEmoji = async (emoji) => {
    try {
      await axios.post(`${API}/rooms/${roomId}/reaction?userId=${currentUser.id}&emoji=${emoji}`);
      fetchMessages();
      setShowEmojiPicker(false);
    } catch (error) {
      toast.error("Failed to send emoji");
    }
  };

  const handleKickUser = async (targetUserId) => {
    if (!window.confirm("Remove this user?")) return;
    
    try {
      await axios.post(`${API}/rooms/${roomId}/kick?userId=${currentUser.id}&targetUserId=${targetUserId}`);
      toast.success("User removed");
      fetchRoom();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to remove user");
    }
  };

  const handleEndRoom = async () => {
    if (!window.confirm("End this room?")) return;
    
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
  const canModerate = isHost || isModerator;

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
          <button onClick={() => navigate("/rooms")} className="px-6 py-2 rounded-full bg-cyan-400 text-black font-semibold">
            Back to Rooms
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      {/* Header */}
      <div className="sticky top-0 z-10 glass-surface px-4 py-3 flex items-center justify-between border-b border-cyan-400/10">
        <button onClick={() => navigate("/rooms")} className="w-10 h-10 rounded-full flex items-center justify-center bg-gray-800/50 hover:bg-gray-700/50">
          <ArrowLeft size={20} className="text-white" />
        </button>
        
        <div className="flex-1 mx-4 text-center">
          <h1 className="font-bold text-white flex items-center justify-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
            {room.name}
          </h1>
          <p className="text-xs text-gray-400 flex items-center justify-center gap-1">
            <Users size={12} />
            {room.participants?.length || 0} listening
          </p>
        </div>

        {isHost && (
          <button onClick={handleEndRoom} className="px-4 py-2 rounded-full bg-red-500/20 text-red-400 text-sm font-semibold hover:bg-red-500/30">
            End
          </button>
        )}
      </div>

      {/* Participants */}
      <div className="p-4 border-b border-cyan-400/10">
        <div className="max-w-2xl mx-auto">
          <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center gap-2">
            <Users size={16} />
            In this room ({room.participants?.length || 0})
          </h3>
          <div className="flex flex-wrap gap-3">
            {room.participants && room.participants.map((participant, idx) => (
              <div key={idx} className="flex items-center gap-2 px-3 py-2 rounded-full bg-gray-800/50 group">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                  <span className="text-white text-xs font-bold">{participant.userName.charAt(0).toUpperCase()}</span>
                </div>
                <span className="text-white text-sm">{participant.userName}</span>
                {participant.userId === room.hostId && <Crown size={12} className="text-yellow-400" />}
                {room.moderators?.includes(participant.userId) && participant.userId !== room.hostId && (
                  <Shield size={12} className="text-cyan-400" />
                )}
                {participant.handRaised && <Hand size={12} className="text-orange-400 animate-bounce" />}
                {participant.isMuted ? <MicOff size={12} className="text-red-400" /> : <Mic size={12} className="text-green-400" />}
                {canModerate && participant.userId !== currentUser.id && participant.userId !== room.hostId && (
                  <button onClick={() => handleKickUser(participant.userId)} className="opacity-0 group-hover:opacity-100">
                    <UserX size={14} className="text-red-400" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Chat */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        <div className="max-w-2xl mx-auto">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <MessageCircle size={48} className="text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400 text-sm">No messages yet</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex items-start gap-3 ${msg.type === 'system' ? 'justify-center' : ''}`}>
                {msg.type === 'system' ? (
                  <p className="text-xs text-gray-500 bg-gray-800/30 px-3 py-1 rounded-full">{msg.message}</p>
                ) : msg.type === 'emoji' ? (
                  <div className="flex items-center gap-2 bg-gray-800/50 px-3 py-2 rounded-full">
                    <span className="text-2xl">{msg.message}</span>
                    <span className="text-xs text-gray-400">{msg.userName}</span>
                  </div>
                ) : (
                  <>
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                      <span className="text-white text-xs font-bold">{msg.userName.charAt(0).toUpperCase()}</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-baseline gap-2 mb-1">
                        <span className="text-sm font-semibold text-white">{msg.userName}</span>
                        <span className="text-xs text-gray-500">{new Date(msg.createdAt).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</span>
                      </div>
                      <p className="text-sm text-gray-300 bg-gray-800/50 px-3 py-2 rounded-2xl inline-block">{msg.message}</p>
                    </div>
                  </>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Chat Input */}
      {hasJoined && (
        <div className="p-4 border-t border-cyan-400/10">
          <div className="max-w-2xl mx-auto">
            <form onSubmit={handleSendMessage} className="flex items-center gap-2">
              <div className="relative">
                <button type="button" onClick={() => setShowEmojiPicker(!showEmojiPicker)} className="w-10 h-10 rounded-full bg-gray-800/50 flex items-center justify-center">
                  <Smile size={20} className="text-gray-400" />
                </button>
                {showEmojiPicker && (
                  <div className="absolute bottom-full left-0 mb-2 p-3 rounded-xl bg-gray-900 border border-cyan-400/30 flex gap-2">
                    {emojis.map((emoji, idx) => (
                      <button key={idx} type="button" onClick={() => handleSendEmoji(emoji)} className="text-2xl hover:scale-125 transition-transform">
                        {emoji}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <input
                ref={chatInputRef}
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Say something..."
                className="flex-1 px-4 py-3 bg-gray-800/50 border border-cyan-400/30 rounded-full focus:border-cyan-400 focus:outline-none text-white"
              />
              <button type="submit" disabled={!newMessage.trim()} className="w-10 h-10 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 flex items-center justify-center disabled:opacity-50">
                <Send size={18} className="text-white" />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Controls */}
      {hasJoined ? (
        <div className="p-4 border-t border-cyan-400/10 bg-gray-900/50">
          <div className="max-w-2xl mx-auto flex gap-4 justify-center">
            <button onClick={handleToggleMute} className={`flex-1 max-w-xs py-3 rounded-full font-semibold flex items-center justify-center gap-2 ${isMuted ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
              {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
              {isMuted ? "Unmute" : "Mute"}
            </button>
            <button onClick={handleToggleHandRaise} className={`px-6 py-3 rounded-full font-semibold flex items-center gap-2 ${handRaised ? 'bg-orange-500/20 text-orange-400' : 'bg-gray-700/50 text-gray-400'}`}>
              <Hand size={20} />
            </button>
            <button onClick={handleLeaveRoom} className="px-6 py-3 rounded-full bg-gray-700/50 text-white font-semibold flex items-center gap-2">
              <LogOut size={20} />
              Leave
            </button>
          </div>
        </div>
      ) : (
        <div className="p-6 border-t border-cyan-400/10 bg-gray-900/50">
          <div className="max-w-2xl mx-auto text-center">
            <Mic size={48} className="text-cyan-400 mx-auto mb-3" />
            <h3 className="text-xl font-bold text-white mb-2">Join the Conversation</h3>
            <button onClick={handleJoinRoom} className="w-full max-w-sm py-4 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold text-lg">
              Join Room
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoomDetail;
