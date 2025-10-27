import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import { Phone, PhoneOff, Video, VideoOff, Mic, MicOff, X, Maximize2, Minimize2 } from 'lucide-react';
import AgoraRTC from 'agora-rtc-sdk-ng';
import { toast } from 'sonner';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const AgoraCallModal = ({ 
  callData, 
  currentUserId,
  onClose,
  isIncoming = false
}) => {
  const [callState, setCallState] = useState(isIncoming ? 'ringing' : 'connecting');
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isVideoEnabled, setIsVideoEnabled] = useState(callData?.callType === 'video');
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [remoteUserJoined, setRemoteUserJoined] = useState(false);
  
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const clientRef = useRef(null);
  const localTracksRef = useRef({ audio: null, video: null });
  const timerRef = useRef(null);

  useEffect(() => {
    initializeCall();
    
    return () => {
      cleanupCall();
    };
  }, []);

  const initializeCall = async () => {
    try {
      setCallState('connecting');
      
      // Create Agora client
      const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
      clientRef.current = client;

      // Set up event listeners
      client.on('user-published', async (user, mediaType) => {
        console.log('User published:', user.uid, mediaType);
        await client.subscribe(user, mediaType);
        
        if (mediaType === 'video') {
          const remoteVideoTrack = user.videoTrack;
          if (remoteVideoRef.current && remoteVideoTrack) {
            remoteVideoTrack.play(remoteVideoRef.current);
            setRemoteUserJoined(true);
          }
        }
        
        if (mediaType === 'audio') {
          const remoteAudioTrack = user.audioTrack;
          if (remoteAudioTrack) {
            remoteAudioTrack.play();
          }
        }

        if (callState !== 'connected') {
          setCallState('connected');
          startTimer();
          toast.success('Call connected');
        }
      });

      client.on('user-unpublished', (user, mediaType) => {
        console.log(`User ${user.uid} unpublished ${mediaType}`);
      });

      client.on('user-left', (user) => {
        console.log(`User ${user.uid} left the channel`);
        toast.info('Call ended');
        handleEndCall();
      });

      // Join the channel with token from backend
      const { channelName, appId, callerToken, callerUid } = callData;
      
      await client.join(appId, channelName, callerToken, callerUid);
      console.log('Joined Agora channel:', channelName);
      
      // Create and publish local tracks
      const audioTrack = await AgoraRTC.createMicrophoneAudioTrack();
      localTracksRef.current.audio = audioTrack;
      
      if (callData.callType === 'video') {
        const videoTrack = await AgoraRTC.createCameraVideoTrack();
        localTracksRef.current.video = videoTrack;
        
        // Play local video
        if (localVideoRef.current) {
          videoTrack.play(localVideoRef.current);
        }
        
        await client.publish([audioTrack, videoTrack]);
      } else {
        await client.publish([audioTrack]);
      }

      console.log('Published local tracks');
      
      if (!isIncoming) {
        setCallState('ringing');
      }
      
    } catch (error) {
      console.error('Failed to initialize call:', error);
      toast.error('Failed to connect call');
      onClose();
    }
  };

  const startTimer = () => {
    timerRef.current = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);
  };

  const toggleAudio = async () => {
    if (localTracksRef.current.audio) {
      await localTracksRef.current.audio.setEnabled(!isAudioEnabled);
      setIsAudioEnabled(!isAudioEnabled);
      toast.success(isAudioEnabled ? 'Microphone muted' : 'Microphone unmuted');
    }
  };

  const toggleVideo = async () => {
    if (localTracksRef.current.video) {
      await localTracksRef.current.video.setEnabled(!isVideoEnabled);
      setIsVideoEnabled(!isVideoEnabled);
      toast.success(isVideoEnabled ? 'Camera off' : 'Camera on');
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleEndCall = async () => {
    try {
      await cleanupCall();
      
      // Notify backend
      if (callData?.callId) {
        await axios.post(`${API}/api/calls/${callData.callId}/end`);
      }
      
      onClose();
    } catch (error) {
      console.error('Error ending call:', error);
      onClose();
    }
  };

  const cleanupCall = async () => {
    // Stop timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    // Close local tracks
    if (localTracksRef.current.audio) {
      localTracksRef.current.audio.close();
    }
    if (localTracksRef.current.video) {
      localTracksRef.current.video.close();
    }

    // Leave channel
    if (clientRef.current) {
      await clientRef.current.leave();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return ReactDOM.createPortal(
    <div className="fixed inset-0 bg-black flex items-center justify-center" style={{ zIndex: 9999 }}>
      <div className="relative w-full h-full overflow-hidden">
        {/* Remote Video (Full Screen) */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-black">
          {callData.callType === 'video' ? (
            <div 
              ref={remoteVideoRef}
              className="w-full h-full bg-gray-900 flex items-center justify-center"
            >
              {!remoteUserJoined && (
                <div className="text-center">
                  <div className="mb-6 relative">
                    <div className="w-40 h-40 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mx-auto flex items-center justify-center shadow-2xl">
                      <span className="text-5xl font-bold text-white">
                        {callData.peerName?.[0]?.toUpperCase() || 'U'}
                      </span>
                    </div>
                    {callState === 'connecting' && (
                      <div className="absolute inset-0 rounded-full border-4 border-blue-500 animate-ping"></div>
                    )}
                  </div>
                  <h2 className="text-3xl font-semibold text-white mb-3">
                    {callData.peerName || 'Unknown User'}
                  </h2>
                  <p className="text-gray-300 text-lg">
                    {callState === 'connecting' && 'Connecting...'}
                    {callState === 'ringing' && 'Ringing...'}
                    {callState === 'connected' && 'Waiting for video...'}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
              <div className="text-center">
                <div className="mb-8 relative">
                  <div className="w-48 h-48 bg-white/10 backdrop-blur-lg rounded-full mx-auto flex items-center justify-center shadow-2xl border-4 border-white/20">
                    <span className="text-6xl font-bold text-white">
                      {callData.peerName?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  {callState === 'connecting' && (
                    <div className="absolute inset-0 rounded-full border-4 border-white/50 animate-ping"></div>
                  )}
                </div>
                <h2 className="text-4xl font-semibold text-white mb-4">
                  {callData.peerName || 'Unknown User'}
                </h2>
                <p className="text-white/80 text-xl mb-2">
                  {callState === 'connecting' && 'Connecting...'}
                  {callState === 'ringing' && 'Calling...'}
                  {callState === 'connected' && (
                    <span className="flex items-center justify-center gap-2">
                      <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
                      {formatTime(elapsedTime)}
                    </span>
                  )}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Local Video (Picture-in-Picture) */}
        {callData.callType === 'video' && (
          <div className={`absolute ${isFullscreen ? 'top-4 right-4 w-40 h-56' : 'bottom-24 right-6 w-48 h-64'} bg-gray-900 rounded-2xl overflow-hidden shadow-2xl border-2 border-white/20 transition-all duration-300 cursor-pointer hover:border-white/40`} style={{ zIndex: 10001 }} onClick={toggleFullscreen}>
            <div 
              ref={localVideoRef}
              className="w-full h-full relative"
            >
              {!isVideoEnabled && (
                <div className="absolute inset-0 bg-gray-800 flex items-center justify-center">
                  <VideoOff className="w-12 h-12 text-gray-400" />
                </div>
              )}
            </div>
            <div className="absolute bottom-2 left-2 bg-black/60 backdrop-blur-sm px-2 py-1 rounded-lg text-xs text-white">
              You
            </div>
          </div>
        )}

        {/* Top Bar - Call Info */}
        <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/60 to-transparent p-6" style={{ zIndex: 10001 }}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white">{callData.peerName || 'Unknown'}</h3>
              {callState === 'connected' && (
                <p className="text-sm text-white/80 flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  {formatTime(elapsedTime)}
                </p>
              )}
              {callState !== 'connected' && (
                <p className="text-sm text-white/80">
                  {callState === 'connecting' && 'Connecting...'}
                  {callState === 'ringing' && 'Ringing...'}
                </p>
              )}
            </div>
            {callData.callType === 'video' && (
              <button
                onClick={toggleFullscreen}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-colors"
              >
                {isFullscreen ? (
                  <Minimize2 className="w-5 h-5 text-white" />
                ) : (
                  <Maximize2 className="w-5 h-5 text-white" />
                )}
              </button>
            )}
          </div>
        </div>

        {/* Bottom Bar - Controls */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-8" style={{ zIndex: 10001 }}>
          <div className="flex items-center justify-center gap-6">
            {/* Mute/Unmute */}
            <button
              onClick={toggleAudio}
              className={`w-16 h-16 rounded-full flex items-center justify-center transition-all transform hover:scale-110 ${
                isAudioEnabled 
                  ? 'bg-white/20 hover:bg-white/30 backdrop-blur-md' 
                  : 'bg-red-500 hover:bg-red-600'
              } shadow-lg`}
            >
              {isAudioEnabled ? (
                <Mic className="w-7 h-7 text-white" />
              ) : (
                <MicOff className="w-7 h-7 text-white" />
              )}
            </button>

            {/* End Call */}
            <button
              onClick={handleEndCall}
              className="w-20 h-20 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition-all transform hover:scale-110 shadow-2xl"
            >
              <PhoneOff className="w-9 h-9 text-white" />
            </button>

            {/* Video On/Off */}
            {callData.callType === 'video' && (
              <button
                onClick={toggleVideo}
                className={`w-16 h-16 rounded-full flex items-center justify-center transition-all transform hover:scale-110 ${
                  isVideoEnabled 
                    ? 'bg-white/20 hover:bg-white/30 backdrop-blur-md' 
                    : 'bg-red-500 hover:bg-red-600'
                } shadow-lg`}
              >
                {isVideoEnabled ? (
                  <Video className="w-7 h-7 text-white" />
                ) : (
                  <VideoOff className="w-7 h-7 text-white" />
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>,
    document.body
  );

export default AgoraCallModal;
