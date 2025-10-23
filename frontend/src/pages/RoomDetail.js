import React, { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useParams, useNavigate } from "react-router-dom";
import DailyIframe from "@daily-co/daily-js";
import { DailyProvider, useDaily, useParticipantIds, useLocalParticipant, useParticipantProperty } from "@daily-co/daily-react";
import { 
  ArrowLeft, Mic, MicOff, Crown, Shield, LogOut, Users, 
  Send, Smile, Hand, UserX, MessageCircle, Loader, UserPlus, Share2
} from "lucide-react";
import { toast } from "sonner";
import InviteFriendsModal from "../components/InviteFriendsModal";

const RoomDetail = () => {
  const { roomId } = useParams();
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [callObject, setCallObject] = useState(null);
  const [joiningCall, setJoiningCall] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);

const RoomDetail = () => {
  const { roomId } = useParams();
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [callObject, setCallObject] = useState(null);
  const [joiningCall, setJoiningCall] = useState(false);
  
  useEffect(() => {
    fetchRoom();
  }, [roomId]);

  const fetchRoom = async () => {
    try {
      const res = await axios.get(`${API}/rooms/${roomId}`);
      setRoom(res.data);
    } catch (error) {
      toast.error("Failed to load room");
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async () => {
    if (!room?.dailyRoomUrl) {
      toast.error("Audio room not available");
      return;
    }

    setJoiningCall(true);
    try {
      // Join MongoDB room first
      await axios.post(`${API}/rooms/${roomId}/join?userId=${currentUser.id}`);
      
      // Create Daily call object
      const newCallObject = DailyIframe.createCallObject({
        audioSource: true,
        videoSource: false,
      });

      setCallObject(newCallObject);
      
      // Join Daily room
      await newCallObject.join({ 
        url: room.dailyRoomUrl,
        userName: currentUser.name 
      });
      
      toast.success("Joined audio room!");
      fetchRoom();
    } catch (error) {
      toast.error("Failed to join audio");
      setCallObject(null);
    } finally {
      setJoiningCall(false);
    }
  };

  const handleLeaveRoom = async () => {
    try {
      if (callObject) {
        await callObject.leave();
        await callObject.destroy();
        setCallObject(null);
      }
      await axios.post(`${API}/rooms/${roomId}/leave?userId=${currentUser.id}`);
      toast.success("Left room");
      navigate("/rooms");
    } catch (error) {
      toast.error("Failed to leave");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <Loader className="animate-spin w-12 h-12 text-cyan-400" />
      </div>
    );
  }

  if (!room) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="text-center">
          <p className="text-gray-400 mb-4">Room not found</p>
          <button onClick={() => navigate("/rooms")} className="px-6 py-2 rounded-full bg-cyan-400 text-black font-semibold">
            Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="sticky top-0 z-10 glass-surface px-4 py-3 flex items-center justify-between border-b border-cyan-400/10">
        <button onClick={() => navigate("/rooms")} className="w-10 h-10 rounded-full flex items-center justify-center bg-gray-800/50">
          <ArrowLeft size={20} className="text-white" />
        </button>
        
        <div className="flex-1 mx-4 text-center">
          <h1 className="font-bold text-white flex items-center justify-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
            {room.name}
          </h1>
          <p className="text-xs text-gray-400">
            {room.participants?.length || 0} in room
          </p>
        </div>

        <div className="flex items-center gap-2">
          {callObject && (
            <button
              onClick={() => setShowInviteModal(true)}
              className="px-3 py-2 rounded-full bg-cyan-400/20 text-cyan-400 text-sm font-semibold hover:bg-cyan-400/30 flex items-center gap-1"
            >
              <UserPlus size={16} />
              <span className="hidden sm:inline">Invite</span>
            </button>
          )}
          {room.hostId === currentUser.id && callObject && (
            <button onClick={handleLeaveRoom} className="px-4 py-2 rounded-full bg-red-500/20 text-red-400 text-sm font-semibold">
              End
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        {callObject ? (
          <DailyProvider callObject={callObject}>
            <AudioRoomContent 
              room={room} 
              currentUser={currentUser}
              onLeave={handleLeaveRoom}
            />
          </DailyProvider>
        ) : (
          <div className="max-w-2xl mx-auto p-6">
            <div className="glass-card p-8 text-center">
              <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                <Mic size={48} className="text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">{room.name}</h2>
              {room.description && <p className="text-gray-400 mb-6">{room.description}</p>}
              
              <div className="mb-6">
                <p className="text-sm text-gray-400 mb-2">Currently in room:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {room.participants?.map((p, idx) => (
                    <div key={idx} className="px-3 py-1 rounded-full bg-gray-800/50 text-white text-sm flex items-center gap-2">
                      {p.userName}
                      {p.userId === room.hostId && <Crown size={12} className="text-yellow-400" />}
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={handleJoinRoom}
                disabled={joiningCall}
                className="w-full max-w-sm py-4 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold text-lg disabled:opacity-50"
              >
                {joiningCall ? "Connecting..." : "🎤 Join with Audio"}
              </button>
              
              <p className="text-xs text-gray-500 mt-4">
                Real-time voice powered by Daily.co
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <InviteFriendsModal
          room={room}
          onClose={() => setShowInviteModal(false)}
        />
      )}
    </div>
  );
};

const AudioRoomContent = ({ room, currentUser, onLeave }) => {
  const callObject = useDaily();
  const localParticipant = useLocalParticipant();
  const remoteParticipantIds = useParticipantIds({ filter: 'remote' });
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchMessages = async () => {
    try {
      const res = await axios.get(`${API}/rooms/${room.id}/messages?limit=50`);
      setMessages(res.data);
    } catch (error) {
      // Silent
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      await axios.post(`${API}/rooms/${room.id}/messages?userId=${currentUser.id}&message=${encodeURIComponent(newMessage)}`);
      setNewMessage("");
      fetchMessages();
    } catch (error) {
      toast.error("Failed to send");
    }
  };

  const toggleMute = () => {
    if (callObject) {
      const isMuted = localParticipant?.audio === false;
      callObject.setLocalAudio(!isMuted);
    }
  };

  const isMuted = localParticipant?.audio === false;

  return (
    <div className="max-w-4xl mx-auto p-4 flex flex-col h-full">
      <div className="flex gap-4 flex-1 min-h-0">
        {/* Participants */}
        <div className="w-1/3 glass-card p-4">
          <h3 className="text-white font-bold mb-3 flex items-center gap-2">
            <Users size={16} />
            Live Audio ({remoteParticipantIds.length + 1})
          </h3>
          <div className="space-y-2">
            {localParticipant && (
              <ParticipantCard 
                participant={localParticipant} 
                isLocal={true} 
                isHost={room.hostId === currentUser.id}
              />
            )}
            {remoteParticipantIds.map(id => (
              <RemoteParticipant key={id} id={id} hostId={room.hostId} />
            ))}
          </div>
        </div>

        {/* Chat */}
        <div className="flex-1 glass-card p-4 flex flex-col">
          <h3 className="text-white font-bold mb-3 flex items-center gap-2">
            <MessageCircle size={16} />
            Chat
          </h3>
          <div className="flex-1 overflow-y-auto space-y-2 mb-3">
            {messages.map((msg, idx) => (
              <div key={idx} className="text-sm">
                {msg.type === 'system' ? (
                  <p className="text-gray-500 text-xs text-center">{msg.message}</p>
                ) : (
                  <div>
                    <span className="text-cyan-400 font-semibold">{msg.userName}: </span>
                    <span className="text-gray-300">{msg.message}</span>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Message..."
              className="flex-1 px-3 py-2 bg-gray-800/50 border border-cyan-400/30 rounded-lg text-white text-sm"
            />
            <button type="submit" className="px-4 py-2 rounded-lg bg-cyan-400 text-black font-semibold text-sm">
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>

      {/* Controls */}
      <div className="mt-4 flex gap-3 justify-center">
        <button
          onClick={toggleMute}
          className={`px-8 py-3 rounded-full font-semibold flex items-center gap-2 ${
            isMuted ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
          }`}
        >
          {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
          {isMuted ? "Unmute" : "Mute"}
        </button>
        <button
          onClick={onLeave}
          className="px-8 py-3 rounded-full bg-gray-700/50 text-white font-semibold flex items-center gap-2"
        >
          <LogOut size={20} />
          Leave
        </button>
      </div>
    </div>
  );
};

const ParticipantCard = ({ participant, isLocal, isHost }) => {
  const isMuted = participant?.audio === false;
  const isSpeaking = participant?.audio && !isMuted;

  return (
    <div className={`p-3 rounded-lg ${isSpeaking ? 'bg-green-500/20 border border-green-400/50' : 'bg-gray-800/50'}`}>
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
          <span className="text-white text-xs font-bold">
            {(participant?.user_name || 'You').charAt(0).toUpperCase()}
          </span>
        </div>
        <div className="flex-1">
          <p className="text-white text-sm font-semibold flex items-center gap-1">
            {participant?.user_name || 'You'}
            {isHost && <Crown size={12} className="text-yellow-400" />}
            {isLocal && <span className="text-xs text-gray-400">(You)</span>}
          </p>
        </div>
        {isMuted ? (
          <MicOff size={14} className="text-red-400" />
        ) : (
          <Mic size={14} className="text-green-400" />
        )}
      </div>
    </div>
  );
};

const RemoteParticipant = ({ id, hostId }) => {
  const participant = useParticipantProperty(id, 'user_name');
  const audio = useParticipantProperty(id, 'audio');
  
  const isMuted = audio === false;
  const isHost = participant?.user_id === hostId;

  if (!participant) return null;

  return <ParticipantCard participant={{ user_name: participant, audio, user_id: id }} isLocal={false} isHost={isHost} />;
};

export default RoomDetail;
