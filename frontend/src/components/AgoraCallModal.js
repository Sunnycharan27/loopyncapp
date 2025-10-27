import React, { useState, useEffect, useRef } from 'react';
import { Phone, PhoneOff, Video, VideoOff, Mic, MicOff, X } from 'lucide-react';
import AgoraRTC from 'agora-rtc-sdk-ng';
import { toast } from 'sonner';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const AgoraCallModal = ({ 
  callData, 
  currentUserId,
  onClose 
}) => {
  const [callState, setCallState] = useState('initializing'); // initializing, ringing, connected, ended
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isVideoEnabled, setIsVideoEnabled] = useState(callData?.callType === 'video');
  const [elapsedTime, setElapsedTime] = useState(0);
  
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
      setCallState('initializing');
      
      // Create Agora client
      const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
      clientRef.current = client;

      // Set up event listeners
      client.on('user-published', async (user, mediaType) => {
        await client.subscribe(user, mediaType);
        
        if (mediaType === 'video') {
          const remoteVideoTrack = user.videoTrack;
          if (remoteVideoRef.current && remoteVideoTrack) {
            remoteVideoTrack.play(remoteVideoRef.current);
          }
        }
        
        if (mediaType === 'audio') {
          const remoteAudioTrack = user.audioTrack;
          if (remoteAudioTrack) {
            remoteAudioTrack.play();
          }
        }

        setCallState('connected');
        startTimer();
        toast.success('Call connected');
      });

      client.on('user-unpublished', (user, mediaType) => {
        console.log(`User ${user.uid} unpublished ${mediaType}`);
      });

      client.on('user-left', (user) => {
        console.log(`User ${user.uid} left the channel`);
        toast.info('Call ended by other user');
        handleEndCall();
      });

      // Join the channel with token from backend
      const { channelName, appId, callerToken, callerUid } = callData;
      
      await client.join(appId, channelName, callerToken, callerUid);
      
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

      setCallState('ringing');
      
    } catch (error) {
      console.error('Failed to initialize call:', error);
      toast.error('Failed to initialize call');
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
    }
  };

  const toggleVideo = async () => {
    if (localTracksRef.current.video) {
      await localTracksRef.current.video.setEnabled(!isVideoEnabled);
      setIsVideoEnabled(!isVideoEnabled);
    }
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

  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center" style={{ zIndex: 9999 }}>
      <div className="relative w-full h-full">
        {/* Remote Video (Full Screen) */}
        <div className="absolute inset-0">
          {callData.callType === 'video' ? (
            <div 
              ref={remoteVideoRef}
              className="w-full h-full bg-gray-900 flex items-center justify-center"
            >
              {callState !== 'connected' && (
                <div className="text-white text-center">
                  <div className="mb-4">
                    <div className="w-32 h-32 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full mx-auto flex items-center justify-center">
                      <span className="text-4xl font-bold">
                        {callData.peerName?.[0]?.toUpperCase() || 'U'}
                      </span>
                    </div>
                  </div>
                  <h2 className="text-2xl font-semibold mb-2">
                    {callData.peerName || 'Unknown User'}
                  </h2>
                  <p className="text-gray-400">
                    {callState === 'initializing' && 'Initializing...'}
                    {callState === 'ringing' && 'Ringing...'}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-purple-900 to-pink-900 flex items-center justify-center">
              <div className="text-white text-center">
                <div className="mb-4">
                  <div className="w-32 h-32 bg-white/20 backdrop-blur-lg rounded-full mx-auto flex items-center justify-center">
                    <span className="text-4xl font-bold">
                      {callData.peerName?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                </div>
                <h2 className="text-2xl font-semibold mb-2">
                  {callData.peerName || 'Unknown User'}
                </h2>
                <p className="text-gray-300">
                  {callState === 'initializing' && 'Initializing...'}
                  {callState === 'ringing' && 'Calling...'}
                  {callState === 'connected' && formatTime(elapsedTime)}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Local Video (Picture-in-Picture) */}
        {callData.callType === 'video' && (
          <div className="absolute top-4 right-4 w-32 h-48 bg-gray-800 rounded-lg overflow-hidden shadow-xl" style={{ zIndex: 10001 }}>
            <div 
              ref={localVideoRef}
              className="w-full h-full"
            />
          </div>
        )}

        {/* Call Info */}
        <div className="absolute top-4 left-4 text-white" style={{ zIndex: 10001 }}>
          <h3 className="text-lg font-semibold">{callData.peerName || 'Unknown'}</h3>
          {callState === 'connected' && (
            <p className="text-sm text-gray-300">{formatTime(elapsedTime)}</p>
          )}
        </div>

        {/* Controls */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex items-center gap-4" style={{ zIndex: 10001 }}>
          {/* Mute/Unmute */}
          <button
            onClick={toggleAudio}
            className={`w-14 h-14 rounded-full flex items-center justify-center ${
              isAudioEnabled ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-500 hover:bg-red-600'
            } transition-colors`}
          >
            {isAudioEnabled ? (
              <Mic className="w-6 h-6 text-white" />
            ) : (
              <MicOff className="w-6 h-6 text-white" />
            )}
          </button>

          {/* End Call */}
          <button
            onClick={handleEndCall}
            className="w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition-colors"
          >
            <PhoneOff className="w-8 h-8 text-white" />
          </button>

          {/* Video On/Off */}
          {callData.callType === 'video' && (
            <button
              onClick={toggleVideo}
              className={`w-14 h-14 rounded-full flex items-center justify-center ${
                isVideoEnabled ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-500 hover:bg-red-600'
              } transition-colors`}
            >
              {isVideoEnabled ? (
                <Video className="w-6 h-6 text-white" />
              ) : (
                <VideoOff className="w-6 h-6 text-white" />
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgoraCallModal;
