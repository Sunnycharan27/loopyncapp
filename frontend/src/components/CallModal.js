import React, { useState, useEffect, useRef } from 'react';
import { Phone, PhoneOff, Video, VideoOff, Mic, MicOff, X } from 'lucide-react';
import WebRTCManager from '../utils/webrtc';
import { toast } from 'sonner';

const CallModal = ({ 
  callData, 
  socket, 
  currentUser,
  onClose 
}) => {
  const [callState, setCallState] = useState('ringing'); // ringing, connecting, connected, ended
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isVideoEnabled, setIsVideoEnabled] = useState(callData?.isVideo || false);
  const [elapsedTime, setElapsedTime] = useState(0);
  
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const webrtcRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!socket || !callData) return;

    // Initialize WebRTC manager
    webrtcRef.current = new WebRTCManager(socket);

    // Set up event handlers
    webrtcRef.current.onRemoteStream = (stream) => {
      if (remoteVideoRef.current) {
        remoteVideoRef.current.srcObject = stream;
      }
    };

    webrtcRef.current.onConnected = () => {
      setCallState('connected');
      startTimer();
      toast.success('Call connected');
    };

    webrtcRef.current.onDisconnected = () => {
      handleEndCall();
    };

    // Set up Socket.IO listeners
    const handleCallAnswered = async () => {
      setCallState('connecting');
      
      if (callData.isInitiator) {
        // Initiator creates offer after call is answered
        try {
          const offer = await webrtcRef.current.createOffer();
          socket.emit('webrtc_offer', {
            callId: callData.callId,
            sdp: offer.sdp
          });
        } catch (error) {
          console.error('Failed to create offer:', error);
          toast.error('Failed to establish connection');
          handleEndCall();
        }
      }
    };

    const handleWebRTCOffer = async (data) => {
      if (data.callId !== callData.callId) return;
      
      try {
        await webrtcRef.current.handleOffer(data.sdp);
        const answer = await webrtcRef.current.createAnswer();
        socket.emit('webrtc_answer', {
          callId: callData.callId,
          sdp: answer.sdp
        });
      } catch (error) {
        console.error('Failed to handle offer:', error);
        toast.error('Failed to establish connection');
        handleEndCall();
      }
    };

    const handleWebRTCAnswer = async (data) => {
      if (data.callId !== callData.callId) return;
      
      try {
        await webrtcRef.current.handleAnswer(data.sdp);
      } catch (error) {
        console.error('Failed to handle answer:', error);
      }
    };

    const handleIceCandidate = async (data) => {
      if (data.callId !== callData.callId) return;
      
      try {
        await webrtcRef.current.handleIceCandidate(data.candidate);
      } catch (error) {
        console.error('Failed to handle ICE candidate:', error);
      }
    };

    const handleCallEnded = () => {
      toast.info('Call ended');
      handleEndCall();
    };

    const handleCallRejected = () => {
      toast.error('Call was rejected');
      handleEndCall();
    };

    socket.on('call_answered', handleCallAnswered);
    socket.on('webrtc_offer', handleWebRTCOffer);
    socket.on('webrtc_answer', handleWebRTCAnswer);
    socket.on('webrtc_ice_candidate', handleIceCandidate);
    socket.on('call_ended', handleCallEnded);
    socket.on('call_rejected', handleCallRejected);

    // Initialize call
    initializeCall();

    return () => {
      socket.off('call_answered', handleCallAnswered);
      socket.off('webrtc_offer', handleWebRTCOffer);
      socket.off('webrtc_answer', handleWebRTCAnswer);
      socket.off('webrtc_ice_candidate', handleIceCandidate);
      socket.off('call_ended', handleCallEnded);
      socket.off('call_rejected', handleCallRejected);
      
      if (webrtcRef.current) {
        webrtcRef.current.cleanup();
      }
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [socket, callData]);

  const initializeCall = async () => {
    try {
      const localStream = await webrtcRef.current.initializeCall(
        callData.callId,
        callData.isVideo,
        callData.isInitiator
      );

      if (localVideoRef.current) {
        localVideoRef.current.srcObject = localStream;
      }

      // If answering a call, send answer immediately
      if (!callData.isInitiator) {
        socket.emit('call_answer', { callId: callData.callId });
      }
    } catch (error) {
      console.error('Failed to initialize call:', error);
      toast.error('Failed to access camera/microphone');
      handleEndCall();
    }
  };

  const startTimer = () => {
    timerRef.current = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);
  };

  const handleEndCall = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    if (webrtcRef.current) {
      webrtcRef.current.cleanup();
    }

    socket.emit('call_end', { callId: callData.callId });
    
    setCallState('ended');
    onClose();
  };

  const handleRejectCall = () => {
    socket.emit('call_reject', { callId: callData.callId });
    handleEndCall();
  };

  const toggleAudio = () => {
    if (webrtcRef.current) {
      webrtcRef.current.toggleAudio(!isAudioEnabled);
      setIsAudioEnabled(!isAudioEnabled);
    }
  };

  const toggleVideo = () => {
    if (webrtcRef.current) {
      webrtcRef.current.toggleVideo(!isVideoEnabled);
      setIsVideoEnabled(!isVideoEnabled);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed inset-0 bg-black/95 z-50 flex flex-col">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 p-6 flex items-center justify-between z-10">
        <div>
          <h2 className="text-white text-xl font-bold">{callData.peerName}</h2>
          <p className="text-gray-400 text-sm">
            {callState === 'ringing' && 'Ringing...'}
            {callState === 'connecting' && 'Connecting...'}
            {callState === 'connected' && formatTime(elapsedTime)}
          </p>
        </div>
        <button
          onClick={handleEndCall}
          className="p-2 rounded-full hover:bg-white/10 transition-all"
        >
          <X size={24} className="text-white" />
        </button>
      </div>

      {/* Video Area */}
      <div className="flex-1 relative">
        {/* Remote Video (full screen) */}
        <video
          ref={remoteVideoRef}
          autoPlay
          playsInline
          className="w-full h-full object-cover"
        />

        {/* Local Video (picture-in-picture) */}
        {callData.isVideo && (
          <div className="absolute top-24 right-6 w-32 h-40 rounded-xl overflow-hidden border-2 border-white/20 shadow-lg">
            <video
              ref={localVideoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover mirror"
            />
          </div>
        )}

        {/* Avatar fallback if no video */}
        {!callData.isVideo && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <img
                src={callData.peerAvatar}
                alt={callData.peerName}
                className="w-32 h-32 rounded-full mx-auto mb-4 border-4 border-white/20"
              />
              <h3 className="text-white text-2xl font-bold">{callData.peerName}</h3>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="absolute bottom-0 left-0 right-0 p-8">
        <div className="flex items-center justify-center gap-4">
          {/* Answer button (only show when ringing and not initiator) */}
          {callState === 'ringing' && !callData.isInitiator && (
            <button
              onClick={() => socket.emit('call_answer', { callId: callData.callId })}
              className="w-16 h-16 rounded-full bg-green-500 hover:bg-green-600 transition-all flex items-center justify-center shadow-lg"
            >
              <Phone size={28} className="text-white" />
            </button>
          )}

          {/* Reject button (only show when ringing and not initiator) */}
          {callState === 'ringing' && !callData.isInitiator && (
            <button
              onClick={handleRejectCall}
              className="w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 transition-all flex items-center justify-center shadow-lg"
            >
              <PhoneOff size={28} className="text-white" />
            </button>
          )}

          {/* Audio toggle */}
          {(callState === 'connecting' || callState === 'connected') && (
            <button
              onClick={toggleAudio}
              className={`w-14 h-14 rounded-full transition-all flex items-center justify-center shadow-lg ${
                isAudioEnabled 
                  ? 'bg-gray-700 hover:bg-gray-600' 
                  : 'bg-red-500 hover:bg-red-600'
              }`}
            >
              {isAudioEnabled ? (
                <Mic size={24} className="text-white" />
              ) : (
                <MicOff size={24} className="text-white" />
              )}
            </button>
          )}

          {/* Video toggle (only for video calls) */}
          {callData.isVideo && (callState === 'connecting' || callState === 'connected') && (
            <button
              onClick={toggleVideo}
              className={`w-14 h-14 rounded-full transition-all flex items-center justify-center shadow-lg ${
                isVideoEnabled 
                  ? 'bg-gray-700 hover:bg-gray-600' 
                  : 'bg-red-500 hover:bg-red-600'
              }`}
            >
              {isVideoEnabled ? (
                <Video size={24} className="text-white" />
              ) : (
                <VideoOff size={24} className="text-white" />
              )}
            </button>
          )}

          {/* End call button */}
          {(callState === 'connecting' || callState === 'connected') && (
            <button
              onClick={handleEndCall}
              className="w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 transition-all flex items-center justify-center shadow-lg"
            >
              <PhoneOff size={28} className="text-white" />
            </button>
          )}
        </div>
      </div>

      <style jsx>{`
        .mirror {
          transform: scaleX(-1);
        }
      `}</style>
    </div>
  );
};

export default CallModal;
