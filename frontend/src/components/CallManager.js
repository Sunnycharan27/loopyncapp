import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import IncomingCallModal from './IncomingCallModal';
import AgoraCallModal from './AgoraCallModal';
import { toast } from 'sonner';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const CallManager = ({ currentUser }) => {
  const [incomingCall, setIncomingCall] = useState(null);
  const [activeCall, setActiveCall] = useState(null);
  const { socket } = useWebSocket();

  useEffect(() => {
    if (!socket || !currentUser) return;

    console.log('🎧 CallManager: Setting up incoming call listener for user:', currentUser.id);

    // Listen for incoming call events
    const handleIncomingCall = (data) => {
      console.log('📞 Incoming call received:', data);
      setIncomingCall(data);
      toast.info(`Incoming ${data.callType} call from ${data.callerName}`, {
        duration: 10000
      });
    };

    socket.on('incoming_call', handleIncomingCall);

    return () => {
      socket.off('incoming_call', handleIncomingCall);
    };
  }, [socket, currentUser]);

  const handleAcceptCall = async () => {
    if (!incomingCall) return;

    console.log('✅ Accepting call:', incomingCall);

    // Notify backend that call was answered
    try {
      await axios.post(`${API}/api/calls/${incomingCall.callId}/answer`);
    } catch (error) {
      console.error('Failed to notify backend of answer:', error);
    }

    // Join the call with recipient token
    const callData = {
      callId: incomingCall.callId,
      channelName: incomingCall.channelName,
      appId: incomingCall.appId,
      callerToken: incomingCall.token, // Use recipient token
      callerUid: incomingCall.uid, // Use recipient UID
      callType: incomingCall.callType,
      peerName: incomingCall.callerName,
      peerAvatar: incomingCall.callerAvatar,
      isInitiator: false
    };

    setActiveCall(callData);
    setIncomingCall(null);
  };

  const handleRejectCall = async () => {
    if (!incomingCall) return;

    console.log('❌ Rejecting call:', incomingCall.callId);
    
    // Notify backend that call was rejected
    try {
      await axios.post(`${API}/api/calls/${incomingCall.callId}/reject`);
    } catch (error) {
      console.error('Failed to notify backend of rejection:', error);
    }

    toast.info('Call declined');
    setIncomingCall(null);
  };

  const handleCloseCall = () => {
    console.log('🔚 Closing call');
    setActiveCall(null);
  };

  return (
    <>
      {incomingCall && (
        <IncomingCallModal
          callData={incomingCall}
          onAccept={handleAcceptCall}
          onReject={handleRejectCall}
        />
      )}

      {activeCall && (
        <AgoraCallModal
          callData={activeCall}
          currentUserId={currentUser?.id}
          onClose={handleCloseCall}
          isIncoming={!activeCall.isInitiator}
        />
      )}
    </>
  );
};

export default CallManager;
