import React, { useState, useEffect, useRef } from 'react';
import AgoraRTC from 'agora-rtc-sdk-ng';
import { Phone, Video, Mic, MicOff, VideoOff, PhoneOff, Maximize2 } from 'lucide-react';
import { toast } from 'sonner';

const AGORA_APP_ID = process.env.REACT_APP_AGORA_APP_ID || '';

const CallModal = ({ callData, onClose }) => {
  const [localAudioTrack, setLocalAudioTrack] = useState(null);
  const [localVideoTrack, setLocalVideoTrack] = useState(null);
  const [remoteUsers, setRemoteUsers] = useState({});
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [callStatus, setCallStatus] = useState('connecting'); // connecting, connected, ended
  const [callDuration, setCallDuration] = useState(0);
  
  const clientRef = useRef(null);
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const callStartTimeRef = useRef(null);
  const durationIntervalRef = useRef(null);

  const { recipientUser, myToken, channelName, callType, callId } = callData;

  useEffect(() => {
    initializeCall();
    
    return () => {
      endCall();
    };
  }, []);

  const initializeCall = async () => {
    try {
      // Create Agora client
      const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
      clientRef.current = client;

      // Set up event listeners
      client.on('user-published', handleUserPublished);
      client.on('user-unpublished', handleUserUnpublished);
      client.on('user-left', handleUserLeft);

      // Join the channel
      const uid = await client.join(
        AGORA_APP_ID,
        channelName,
        agoraToken,
        currentUser.id
      );

      // Create local tracks
      const audioTrack = await AgoraRTC.createMicrophoneAudioTrack();
      setLocalAudioTrack(audioTrack);

      if (callType === 'video') {
        const videoTrack = await AgoraRTC.createCameraVideoTrack();
        setLocalVideoTrack(videoTrack);
        
        // Play local video
        if (localVideoRef.current) {
          videoTrack.play(localVideoRef.current);
        }
      }

      // Publish local tracks
      const tracksToPublish = callType === 'video' 
        ? [audioTrack, localVideoTrack] 
        : [audioTrack];
      
      await client.publish(tracksToPublish.filter(Boolean));

      setCallStatus('connected');
      callStartTimeRef.current = Date.now();
      
      // Start duration timer
      durationIntervalRef.current = setInterval(() => {
        if (callStartTimeRef.current) {
          setCallDuration(Math.floor((Date.now() - callStartTimeRef.current) / 1000));
        }
      }, 1000);

      toast.success(`${callType === 'video' ? 'Video' : 'Voice'} call started`);
    } catch (error) {
      console.error('Error initializing call:', error);
      toast.error('Failed to start call');
      onClose();
    }
  };

  const handleUserPublished = async (user, mediaType) => {
    try {
      await clientRef.current.subscribe(user, mediaType);

      if (mediaType === 'video') {
        setRemoteUsers(prev => ({ ...prev, [user.uid]: user }));
        
        // Play remote video
        if (remoteVideoRef.current) {
          user.videoTrack.play(remoteVideoRef.current);
        }
      }

      if (mediaType === 'audio') {
        user.audioTrack.play();
      }
    } catch (error) {
      console.error('Error subscribing to user:', error);
    }
  };

  const handleUserUnpublished = (user, mediaType) => {
    if (mediaType === 'video') {
      setRemoteUsers(prev => {
        const newUsers = { ...prev };
        delete newUsers[user.uid];
        return newUsers;
      });
    }
  };

  const handleUserLeft = (user) => {
    setRemoteUsers(prev => {
      const newUsers = { ...prev };
      delete newUsers[user.uid];
      return newUsers;
    });
    toast.info(`${recipientUser.name} left the call`);
  };

  const toggleMute = () => {
    if (localAudioTrack) {
      localAudioTrack.setEnabled(isMuted);
      setIsMuted(!isMuted);
    }
  };

  const toggleVideo = () => {
    if (localVideoTrack) {
      localVideoTrack.setEnabled(isVideoOff);
      setIsVideoOff(!isVideoOff);
    }
  };

  const endCall = async () => {
    try {
      // Clear duration timer
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }

      // Close local tracks
      if (localAudioTrack) {
        localAudioTrack.close();
      }
      if (localVideoTrack) {
        localVideoTrack.close();
      }

      // Leave channel
      if (clientRef.current) {
        await clientRef.current.leave();
      }

      setCallStatus('ended');
      toast.success('Call ended');
      onClose();
    } catch (error) {
      console.error('Error ending call:', error);
      onClose();
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* Call Header */}
      <div className="p-6 bg-gradient-to-b from-black/60 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src={recipientUser.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${recipientUser.name}`}
              alt={recipientUser.name}
              className="w-12 h-12 rounded-full"
            />
            <div>
              <h3 className="text-white font-semibold">{recipientUser.name}</h3>
              <p className="text-white/60 text-sm">
                {callStatus === 'connecting' && 'Connecting...'}
                {callStatus === 'connected' && formatDuration(callDuration)}
                {callStatus === 'ended' && 'Call ended'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Video Container */}
      <div className="flex-1 relative">
        {callType === 'video' ? (
          <>
            {/* Remote Video (Full Screen) */}
            <div 
              ref={remoteVideoRef}
              className="absolute inset-0 bg-gray-900"
            >
              {Object.keys(remoteUsers).length === 0 && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-32 h-32 mx-auto mb-4 rounded-full bg-cyan-400/20 flex items-center justify-center">
                      <Video size={64} className="text-cyan-400" />
                    </div>
                    <p className="text-white/60">Waiting for {recipientUser.name} to join...</p>
                  </div>
                </div>
              )}
            </div>

            {/* Local Video (Picture-in-Picture) */}
            <div className="absolute top-4 right-4 w-32 h-40 rounded-xl overflow-hidden shadow-2xl border-2 border-white/20">
              <div 
                ref={localVideoRef}
                className="w-full h-full bg-gray-800"
              />
              {isVideoOff && (
                <div className="absolute inset-0 bg-gray-900 flex items-center justify-center">
                  <VideoOff className="text-white/60" />
                </div>
              )}
            </div>
          </>
        ) : (
          // Audio Call UI
          <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/20 to-purple-500/20 flex items-center justify-center">
            <div className="text-center">
              <div className="w-40 h-40 mx-auto mb-6 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 p-1">
                <div className="w-full h-full rounded-full bg-black flex items-center justify-center">
                  <img
                    src={recipientUser.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${recipientUser.name}`}
                    alt={recipientUser.name}
                    className="w-full h-full rounded-full"
                  />
                </div>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">{recipientUser.name}</h2>
              <p className="text-white/60">
                {callStatus === 'connecting' && 'Calling...'}
                {callStatus === 'connected' && formatDuration(callDuration)}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Call Controls */}
      <div className="p-6 bg-gradient-to-t from-black/80 to-transparent">
        <div className="flex items-center justify-center gap-6">
          {/* Mute Button */}
          <button
            onClick={toggleMute}
            className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${
              isMuted 
                ? 'bg-red-500 text-white' 
                : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            {isMuted ? <MicOff size={24} /> : <Mic size={24} />}
          </button>

          {/* Video Toggle (only for video calls) */}
          {callType === 'video' && (
            <button
              onClick={toggleVideo}
              className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${
                isVideoOff 
                  ? 'bg-red-500 text-white' 
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
            >
              {isVideoOff ? <VideoOff size={24} /> : <Video size={24} />}
            </button>
          )}

          {/* End Call Button */}
          <button
            onClick={endCall}
            className="w-16 h-16 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-all shadow-lg"
          >
            <PhoneOff size={28} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default CallModal;
