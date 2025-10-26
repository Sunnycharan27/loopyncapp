import React, { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useParams, useNavigate } from "react-router-dom";
import AgoraRTC from "agora-rtc-sdk-ng";
import { 
  ArrowLeft, Mic, MicOff, Hand, UserPlus, MoreVertical, 
  Share2, Users, Crown, Shield, Volume2, VolumeX, LogOut
} from "lucide-react";
import { toast } from "sonner";
import UniversalShareModal from "../components/UniversalShareModal";

const RoomDetailClubhouse = () => {
  const { roomId } = useParams();
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isMuted, setIsMuted] = useState(true);
  const [isHandRaised, setIsHandRaised] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  
  // Agora client refs
  const agoraClient = useRef(null);
  const localAudioTrack = useRef(null);

  useEffect(() => {
    fetchRoom();
    const interval = setInterval(fetchRoom, 5000);
    return () => clearInterval(interval);
  }, [roomId]);

  useEffect(() => {
    const initAudio = async () => {
      if (room?.agoraChannel && currentUser?.id && !isConnected) {
        try {
          await axios.post(`${API}/rooms/${roomId}/join?userId=${currentUser.id}`);
          await initializeAgoraAudio();
        } catch (error) {
          console.error("Failed to join room:", error);
          toast.error("Failed to join room");
        }
      }
    };
    
    initAudio();
    
    return () => {
      cleanupAgoraResources();
    };
  }, [room?.id, currentUser?.id]);

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

  const initializeAgoraAudio = async () => {
    if (!room?.agoraChannel) {
      toast.error("Audio room not available");
      return;
    }

    try {
      const myRole = getCurrentUserRole();
      
      // Generate a valid Agora UID (must be 0-10000)
      // Use a simple hash of user ID to keep it in range
      const hashCode = (str) => {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
          const char = str.charCodeAt(i);
          hash = ((hash << 5) - hash) + char;
          hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash);
      };
      
      const uid = hashCode(currentUser.id) % 10000; // Keep within 0-9999
      const role = myRole === "audience" ? "subscriber" : "publisher";
      
      // Request microphone permission early for speakers/hosts
      if (myRole !== "audience") {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          stream.getTracks().forEach(track => track.stop()); // Release the stream
          toast.success("Microphone access granted!");
        } catch (permError) {
          console.error("Microphone permission denied:", permError);
          toast.error("Please allow microphone access to speak in this room. Check your browser permissions.");
          throw new Error("Microphone permission denied");
        }
      }
      
      const tokenRes = await axios.post(
        `${API}/agora/token?channelName=${encodeURIComponent(room.agoraChannel)}&uid=${uid}&role=${role}`
      );
      
      if (!tokenRes.data?.token) {
        throw new Error("Failed to get Agora token");
      }

      const { token, appId } = tokenRes.data;

      // Create Agora client
      agoraClient.current = AgoraRTC.createClient({ 
        mode: "live", 
        codec: "vp8" 
      });

      // Set client role
      await agoraClient.current.setClientRole(
        myRole === "audience" ? "audience" : "host"
      );

      // Event listeners
      agoraClient.current.on("user-published", async (user, mediaType) => {
        try {
          console.log(`User ${user.uid} published ${mediaType}`);
          await agoraClient.current.subscribe(user, mediaType);
          
          if (mediaType === "audio") {
            console.log(`Playing audio for user ${user.uid}`);
            
            // Check if audioTrack exists
            if (user.audioTrack) {
              try {
                // Play audio with proper error handling
                await user.audioTrack.play();
                console.log(`✅ Audio playing for user ${user.uid}`);
                toast.success(`🔊 User is now speaking`);
              } catch (playError) {
                console.error(`Failed to play audio for user ${user.uid}:`, playError);
                
                // Handle browser autoplay policy
                if (playError.name === 'NotAllowedError' || playError.message?.includes('autoplay')) {
                  toast.warning(`Click anywhere to enable audio playback`, {
                    duration: 5000,
                  });
                  
                  // Add click listener to resume playback
                  const resumeAudio = async () => {
                    try {
                      await user.audioTrack.play();
                      toast.success(`🔊 Audio enabled!`);
                      document.removeEventListener('click', resumeAudio);
                    } catch (e) {
                      console.error('Failed to resume audio:', e);
                    }
                  };
                  document.addEventListener('click', resumeAudio, { once: true });
                } else {
                  toast.error(`Failed to play audio: ${playError.message}`);
                }
              }
            } else {
              console.warn(`⚠️ Audio track not available for user ${user.uid}`);
              toast.warning(`Audio track not ready for this user`);
            }
          }
        } catch (error) {
          console.error(`Error subscribing to user ${user.uid}:`, error);
          toast.error(`Failed to receive audio`);
        }
      });

      agoraClient.current.on("user-unpublished", (user, mediaType) => {
        console.log(`User ${user.uid} unpublished ${mediaType}`);
        if (mediaType === "audio") {
          toast.info(`User stopped speaking`);
        }
      });

      agoraClient.current.on("user-left", (user) => {
        console.log(`User ${user.uid} left the room`);
        fetchRoom();
      });
      
      agoraClient.current.on("user-joined", (user) => {
        console.log(`User ${user.uid} joined the room`);
        toast.info(`User joined`);
      });

      // Join channel
      await agoraClient.current.join(appId, room.agoraChannel, token, uid);
      console.log(`✅ Joined Agora channel: ${room.agoraChannel} with UID: ${uid}`);

      // Create and publish local audio track for speakers/hosts
      if (myRole !== "audience") {
        try {
          console.log(`🎤 Creating microphone audio track for ${myRole}...`);
          localAudioTrack.current = await AgoraRTC.createMicrophoneAudioTrack({
            encoderConfig: "music_standard",
          });
          console.log(`✅ Microphone track created successfully`);
          
          await agoraClient.current.publish([localAudioTrack.current]);
          console.log(`✅ Audio track published successfully - You can now be heard!`);
          
          setIsMuted(false);
          toast.success("🎤 You're on stage! Others can hear you.");
        } catch (audioError) {
          console.error("❌ Failed to create/publish audio track:", audioError);
          toast.error("Failed to enable microphone. Please check your device settings.");
          throw audioError;
        }
      } else {
        console.log(`👂 Joined as audience - listening only`);
        setIsMuted(true);
      }

      setIsConnected(true);
      toast.success("🎵 Connected to audio room!");
      console.log(`✅ Audio initialization complete. Role: ${myRole}, Muted: ${myRole === "audience"}`);
      
    } catch (error) {
      console.error("Failed to initialize Agora audio:", error);
      
      // Provide user-friendly error messages
      if (error.message?.includes("permission")) {
        toast.error("Microphone access denied. Please allow microphone in your browser settings.");
      } else if (error.message?.includes("NotFoundError")) {
        toast.error("No microphone found. Please connect a microphone device.");
      } else if (error.code === "INVALID_OPERATION") {
        toast.error("Failed to connect. Please try leaving and rejoining the room.");
      } else {
        toast.error(`Failed to connect to audio: ${error.message || 'Please try again'}`);
      }
    }
  };

  const cleanupAgoraResources = async () => {
    try {
      if (localAudioTrack.current) {
        localAudioTrack.current.close();
        localAudioTrack.current = null;
      }

      if (agoraClient.current) {
        await agoraClient.current.leave();
        agoraClient.current = null;
      }

      setIsConnected(false);
    } catch (error) {
      console.error("Error cleaning up Agora:", error);
    }
  };

  const handleLeaveRoom = async () => {
    try {
      await cleanupAgoraResources();
      await axios.post(`${API}/rooms/${roomId}/leave?userId=${currentUser.id}`);
      toast.success("Left VibeRoom");
      navigate("/viberooms");
    } catch (error) {
      toast.error("Failed to leave room");
    }
  };

  const toggleMute = async () => {
    if (!localAudioTrack.current) {
      const myRole = getCurrentUserRole();
      if (myRole === "audience") {
        toast.error("You need to be on stage to speak. Raise your hand to request!");
        return;
      }
      toast.error("Microphone not available");
      return;
    }

    const newMutedState = !isMuted;
    await localAudioTrack.current.setEnabled(!newMutedState);
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

  // Update audio permissions when role changes
  useEffect(() => {
    const updateAudioPermissions = async () => {
      if (!agoraClient.current || !isConnected) return;
      
      const myRole = getCurrentUserRole();
      const isNowSpeaker = myRole !== "audience";
      const hasAudioTrack = localAudioTrack.current !== null;

      // If promoted to speaker but don't have audio track
      if (isNowSpeaker && !hasAudioTrack) {
        try {
          // Request microphone permission first
          try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());
          } catch (permError) {
            console.error("Microphone permission denied:", permError);
            toast.error("Please allow microphone access to speak. Check browser permissions.");
            return;
          }
          
          // Change client role to host
          await agoraClient.current.setClientRole("host");
          
          // Create and publish audio track
          localAudioTrack.current = await AgoraRTC.createMicrophoneAudioTrack({
            encoderConfig: "music_standard",
          });
          await agoraClient.current.publish([localAudioTrack.current]);
          
          setIsMuted(false);
          toast.success("🎤 You're on stage! You can now speak.");
        } catch (error) {
          console.error("Failed to enable microphone:", error);
          if (error.message?.includes("permission")) {
            toast.error("Microphone access denied. Please allow microphone in browser settings.");
          } else {
            toast.error("Failed to enable microphone. Please try again.");
          }
        }
      }
      
      // If demoted to audience but have audio track
      if (!isNowSpeaker && hasAudioTrack) {
        try {
          // Unpublish and close audio track
          await agoraClient.current.unpublish([localAudioTrack.current]);
          localAudioTrack.current.close();
          localAudioTrack.current = null;
          
          // Change client role to audience
          await agoraClient.current.setClientRole("audience");
          
          setIsMuted(true);
          toast.info("Moved to audience");
        } catch (error) {
          console.error("Failed to disable microphone:", error);
        }
      }
    };

    updateAudioPermissions();
  }, [room?.participants, isConnected]);

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
            <button onClick={() => setShowShareModal(true)} className="text-gray-400 hover:text-cyan-400 transition">
              <Share2 size={20} />
            </button>
            <MoreVertical size={20} className="text-gray-400" />
          </div>
        </div>
        <div className="text-center">
          <h1 className="text-xl font-bold text-white">{room?.name}</h1>
          <p className="text-sm text-gray-400 mt-1">{room?.description}</p>
          {isConnected && (
            <p className="text-xs text-green-400 mt-1">🎙️ Connected • Powered by Agora</p>
          )}
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
                disabled={!isConnected}
                className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                  isMuted
                    ? "bg-gray-700 text-white"
                    : "bg-cyan-400 text-black shadow-lg shadow-cyan-400/50"
                } disabled:opacity-50`}
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

      {/* Share Modal */}
      {showShareModal && room && (
        <UniversalShareModal
          item={room}
          type="room"
          currentUser={currentUser}
          onClose={() => setShowShareModal(false)}
        />
      )}
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
