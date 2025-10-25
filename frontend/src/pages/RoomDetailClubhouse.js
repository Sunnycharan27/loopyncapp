import React, { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useParams, useNavigate } from "react-router-dom";
import { 
  ArrowLeft, Mic, MicOff, Hand, UserPlus, MoreVertical, 
  Share2, Users, Crown, Shield, Volume2, VolumeX, LogOut
} from "lucide-react";
import { toast } from "sonner";
import DailyIframe from "@daily-co/daily-js";

const RoomDetailClubhouse = () => {
  const { roomId } = useParams();
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isMuted, setIsMuted] = useState(true);
  const [isHandRaised, setIsHandRaised] = useState(false);
  const [callFrame, setCallFrame] = useState(null);
  const dailyRef = useRef(null);

  useEffect(() => {
    fetchRoom();
    const interval = setInterval(fetchRoom, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [roomId]);

  useEffect(() => {
    if (room?.dailyRoomUrl && !callFrame) {
      initializeDailyAudio();
    }
    return () => {
      if (callFrame) {
        callFrame.leave();
        callFrame.destroy();
      }
    };
  }, [room]);

  const fetchRoom = async () => {
    try {
      const res = await axios.get(`${API}/rooms/${roomId}`);
      setRoom(res.data);
    } catch (error) {
      toast.error("Failed to load VibeRoom");
      navigate("/viberooms");
    } finally {
      setLoading(false);
    }
  };

  const initializeDailyAudio = async () => {
    if (!room?.dailyRoomUrl || !room?.dailyRoomName) {
      toast.error("Audio room not available");
      return;
    }

    try {
      // First, generate a meeting token for secure access
      const myRole = getCurrentUserRole();
      const isOwner = myRole === "host" || myRole === "moderator";
      
      const tokenRes = await axios.post(
        `${API}/daily/token?roomName=${room.dailyRoomName}&userName=${encodeURIComponent(currentUser.name)}&isOwner=${isOwner}`
      );
      
      if (!tokenRes.data?.token) {
        throw new Error("Failed to get meeting token");
      }

      const meetingToken = tokenRes.data.token;

      // Create Daily frame for audio-only
      const daily = DailyIframe.createFrame({
        iframeStyle: {
          position: "absolute",
          width: "0px",
          height: "0px",
          border: "0",
          visibility: "hidden"
        },
        showLeaveButton: false,
        showFullscreenButton: false,
      });

      // Join with token for authenticated access
      await daily.join({
        url: room.dailyRoomUrl,
        token: meetingToken,
        userName: currentUser.name
      });

      // Start with mic muted for audience
      if (myRole === "audience") {
        daily.setLocalAudio(false);
        setIsMuted(true);
      } else {
        // Speakers start unmuted
        daily.setLocalAudio(true);
        setIsMuted(false);
      }

      setCallFrame(daily);
      dailyRef.current = daily;

      // Listen for Daily.co events
      daily.on("participant-joined", () => fetchRoom());
      daily.on("participant-left", () => fetchRoom());
      daily.on("error", (error) => {
        console.error("Daily.co error:", error);
        toast.error("Audio connection error");
      });
      
      toast.success("Connected to audio!");
      
    } catch (error) {
      console.error("Failed to initialize audio:", error);
      toast.error(`Failed to connect to audio: ${error.message || 'Unknown error'}`);
    }
  };

  const handleLeaveRoom = async () => {
    try {
      await axios.post(`${API}/rooms/${roomId}/leave?userId=${currentUser.id}`);
      if (callFrame) {
        callFrame.leave();
        callFrame.destroy();
      }
      toast.success("Left VibeRoom");
      navigate("/viberooms");
    } catch (error) {
      toast.error("Failed to leave room");
    }
  };

  const toggleMute = () => {
    if (!callFrame) return;
    
    const myRole = getCurrentUserRole();
    if (myRole === "audience") {
      toast.error("You need to be on stage to speak. Raise your hand to request!");
      return;
    }

    const newMutedState = !isMuted;
    callFrame.setLocalAudio(!newMutedState);
    setIsMuted(newMutedState);
  };

  const handleRaiseHand = async () => {
    try {
      await axios.post(`${API}/rooms/${roomId}/raise-hand?userId=${currentUser.id}`);
      setIsHandRaised(!isHandRaised);
      toast.success(isHandRaised ? "Hand lowered" : "Hand raised! Wait for the host to invite you.");
      fetchRoom();
    } catch (error) {
      toast.error("Failed to raise hand");
    }
  };

  const handleInviteToStage = async (targetUserId) => {
    try {
      await axios.post(`${API}/rooms/${roomId}/invite-to-stage?userId=${currentUser.id}&targetUserId=${targetUserId}`);
      toast.success("Invited to stage!");
      fetchRoom();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to invite");
    }
  };

  const handleRemoveFromStage = async (targetUserId) => {
    try {
      await axios.post(`${API}/rooms/${roomId}/remove-from-stage?userId=${currentUser.id}&targetUserId=${targetUserId}`);
      toast.success("Removed from stage");
      fetchRoom();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to remove");
    }
  };

  const handleMakeModerator = async (targetUserId) => {
    try {
      await axios.post(`${API}/rooms/${roomId}/make-moderator?userId=${currentUser.id}&targetUserId=${targetUserId}`);
      toast.success("Made moderator!");
      fetchRoom();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to make moderator");
    }
  };

  const getCurrentUserRole = () => {
    const participant = room?.participants?.find(p => p.userId === currentUser.id);
    return participant?.role || "audience";
  };

  const getCurrentUserData = () => {
    return room?.participants?.find(p => p.userId === currentUser.id);
  };

  const canManageSpeakers = () => {
    const myRole = getCurrentUserRole();
    return myRole === "host" || myRole === "moderator";
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="text-white">Loading VibeRoom...</div>
      </div>
    );
  }

  const speakers = room?.participants?.filter(p => 
    p.role === "host" || p.role === "moderator" || p.role === "speaker"
  ) || [];
  
  const audience = room?.participants?.filter(p => p.role === "audience") || [];
  const raisedHands = audience.filter(p => p.raisedHand);
  const myRole = getCurrentUserRole();
  const myData = getCurrentUserData();

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      {/* Header */}
      <div className="sticky top-0 z-10 glass-surface p-4">
        <div className="flex items-center justify-between mb-2">
          <button onClick={handleLeaveRoom} className="text-cyan-400">
            <ArrowLeft size={24} />
          </button>
          <div className="flex items-center gap-2">
            <Share2 size={20} className="text-gray-400" />
            <MoreVertical size={20} className="text-gray-400" />
          </div>
        </div>
        <div className="text-center">
          <h1 className="text-xl font-bold text-white">{room?.name}</h1>
          <p className="text-sm text-gray-400 mt-1">{room?.description}</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-4 space-y-6 pb-32">
        {/* Stage - Speakers Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white font-semibold flex items-center gap-2">
              <Volume2 size={18} className="text-cyan-400" />
              On Stage ({speakers.length}/{room?.maxSpeakers || 20})
            </h2>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            {speakers.map(participant => (
              <SpeakerCard
                key={participant.userId}
                participant={participant}
                canManage={canManageSpeakers() && participant.userId !== currentUser.id}
                onRemoveFromStage={() => handleRemoveFromStage(participant.userId)}
                onMakeModerator={() => handleMakeModerator(participant.userId)}
                isHost={participant.role === "host"}
                isModerator={participant.role === "moderator"}
              />
            ))}
          </div>
        </div>

        {/* Raised Hands Section */}
        {raisedHands.length > 0 && canManageSpeakers() && (
          <div>
            <h2 className="text-white font-semibold mb-4 flex items-center gap-2">
              <Hand size={18} className="text-yellow-400" />
              Raised Hands ({raisedHands.length})
            </h2>
            <div className="grid grid-cols-4 gap-3">
              {raisedHands.map(participant => (
                <button
                  key={participant.userId}
                  onClick={() => handleInviteToStage(participant.userId)}
                  className="text-center group hover:scale-105 transition-transform"
                >
                  <div className="relative w-16 h-16 mx-auto mb-2">
                    <img
                      src={participant.avatar}
                      alt={participant.userName}
                      className="w-full h-full rounded-full ring-2 ring-yellow-400"
                    />
                    <Hand size={12} className="absolute -top-1 -right-1 text-yellow-400 bg-gray-900 rounded-full p-1" />
                  </div>
                  <p className="text-xs text-white truncate">{participant.userName}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Audience Section */}
        <div>
          <h2 className="text-gray-400 font-semibold mb-4 flex items-center gap-2">
            <Users size={18} />
            Others in Room ({audience.length})
          </h2>
          <div className="grid grid-cols-6 gap-3">
            {audience.slice(0, 30).map(participant => (
              <div key={participant.userId} className="text-center">
                <div className="relative w-14 h-14 mx-auto mb-1">
                  <img
                    src={participant.avatar}
                    alt={participant.userName}
                    className="w-full h-full rounded-full ring-1 ring-gray-700"
                  />
                  {participant.raisedHand && (
                    <Hand size={10} className="absolute -top-1 -right-1 text-yellow-400 bg-gray-900 rounded-full p-0.5" />
                  )}
                </div>
                <p className="text-xs text-gray-400 truncate">{participant.userName}</p>
              </div>
            ))}
          </div>
          {audience.length > 30 && (
            <p className="text-xs text-gray-500 text-center mt-3">
              +{audience.length - 30} more
            </p>
          )}
        </div>
      </div>

      {/* Bottom Control Panel */}
      <div className="fixed bottom-0 left-0 right-0 glass-surface p-6 border-t border-gray-700">
        <div className="max-w-md mx-auto">
          {myRole === "audience" ? (
            // Audience Controls
            <div className="flex items-center justify-between">
              <button
                onClick={handleLeaveRoom}
                className="flex items-center gap-2 px-6 py-3 rounded-full bg-red-500/20 text-red-400 font-semibold hover:bg-red-500/30 transition-all"
              >
                <LogOut size={18} />
                Leave Quietly
              </button>
              
              <button
                onClick={handleRaiseHand}
                className={`flex items-center gap-2 px-6 py-3 rounded-full font-semibold transition-all ${
                  myData?.raisedHand
                    ? "bg-yellow-400 text-black"
                    : "bg-gray-700 text-white hover:bg-gray-600"
                }`}
              >
                <Hand size={18} />
                {myData?.raisedHand ? "Hand Raised" : "Raise Hand"}
              </button>
            </div>
          ) : (
            // Speaker Controls
            <div className="flex items-center justify-between">
              <button
                onClick={handleLeaveRoom}
                className="flex items-center gap-2 px-4 py-3 rounded-full bg-gray-700 text-white hover:bg-gray-600 transition-all"
              >
                <LogOut size={18} />
                Leave
              </button>

              <button
                onClick={toggleMute}
                className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                  isMuted
                    ? "bg-gray-700 text-white"
                    : "bg-cyan-400 text-black shadow-lg shadow-cyan-400/50"
                }`}
              >
                {isMuted ? <MicOff size={28} /> : <Mic size={28} />}
              </button>

              {canManageSpeakers() && (
                <div className="text-xs text-cyan-400">
                  <Shield size={16} className="inline mr-1" />
                  Moderator
                </div>
              )}
            </div>
          )}

          {/* Status Info */}
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-400">
              {myRole === "host" && "🎙️ You're hosting"}
              {myRole === "moderator" && "🛡️ You're a moderator"}
              {myRole === "speaker" && "🎤 You're on stage"}
              {myRole === "audience" && "👂 You're listening"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Speaker Card Component
const SpeakerCard = ({ participant, canManage, onRemoveFromStage, onMakeModerator, isHost, isModerator }) => {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div className="relative">
      <div className="text-center group">
        <div className="relative w-20 h-20 mx-auto mb-2">
          <img
            src={participant.avatar}
            alt={participant.userName}
            className={`w-full h-full rounded-full ${
              participant.isMuted ? "ring-2 ring-gray-600" : "ring-4 ring-cyan-400 animate-pulse"
            }`}
          />
          {isHost && (
            <Crown size={14} className="absolute -top-1 -right-1 text-yellow-400 bg-gray-900 rounded-full p-1" />
          )}
          {isModerator && !isHost && (
            <Shield size={14} className="absolute -top-1 -right-1 text-cyan-400 bg-gray-900 rounded-full p-1" />
          )}
          {participant.isMuted ? (
            <MicOff size={14} className="absolute -bottom-1 -right-1 bg-gray-700 text-white rounded-full p-1" />
          ) : (
            <Mic size={14} className="absolute -bottom-1 -right-1 bg-cyan-400 text-black rounded-full p-1" />
          )}
        </div>
        <p className="text-sm text-white font-medium truncate">{participant.userName}</p>
        
        {canManage && (
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="mt-1 text-gray-400 hover:text-white"
          >
            <MoreVertical size={14} />
          </button>
        )}
      </div>

      {/* Context Menu */}
      {showMenu && canManage && (
        <div className="absolute top-0 right-0 z-20 bg-gray-800 rounded-xl shadow-lg border border-gray-700 min-w-[150px]">
          {!isModerator && (
            <button
              onClick={() => {
                onMakeModerator();
                setShowMenu(false);
              }}
              className="w-full px-4 py-2 text-left text-sm text-white hover:bg-gray-700 rounded-t-xl"
            >
              Make Moderator
            </button>
          )}
          {!isHost && (
            <button
              onClick={() => {
                onRemoveFromStage();
                setShowMenu(false);
              }}
              className="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-gray-700 rounded-b-xl"
            >
              Remove from Stage
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default RoomDetailClubhouse;
