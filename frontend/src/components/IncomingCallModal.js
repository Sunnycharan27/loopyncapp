import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { Phone, Video, X } from 'lucide-react';
import { toast } from 'sonner';

const IncomingCallModal = ({ callData, onAccept, onReject }) => {
  const [ringing, setRinging] = useState(true);

  useEffect(() => {
    // Play ringing sound (optional - add audio file)
    const audio = new Audio('/ringtone.mp3');
    audio.loop = true;
    audio.play().catch(e => console.log('Audio play failed:', e));

    return () => {
      audio.pause();
      audio.currentTime = 0;
    };
  }, []);

  const handleAccept = () => {
    setRinging(false);
    onAccept();
  };

  const handleReject = () => {
    setRinging(false);
    onReject();
  };

  return ReactDOM.createPortal(
    <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center" style={{ zIndex: 10000 }}>
      <div className="relative w-full max-w-md mx-4">
        {/* Animated ripple effect */}
        <div className="absolute inset-0 flex items-center justify-center">
          {ringing && (
            <>
              <div className="absolute w-64 h-64 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full opacity-20 animate-ping" style={{ animationDuration: '2s' }}></div>
              <div className="absolute w-48 h-48 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full opacity-30 animate-ping" style={{ animationDuration: '2s', animationDelay: '0.5s' }}></div>
            </>
          )}
        </div>

        {/* Call info card */}
        <div className="relative bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl p-8 shadow-2xl border border-gray-700">
          {/* Caller avatar */}
          <div className="flex justify-center mb-6">
            <div className="relative">
              <img
                src={callData.callerAvatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${callData.callerId}`}
                alt={callData.callerName}
                className="w-32 h-32 rounded-full border-4 border-white shadow-xl"
              />
              {ringing && (
                <div className="absolute inset-0 rounded-full border-4 border-blue-500 animate-pulse"></div>
              )}
            </div>
          </div>

          {/* Caller info */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">
              {callData.callerName}
            </h2>
            <div className="flex items-center justify-center gap-2 text-gray-300">
              {callData.callType === 'video' ? (
                <Video className="w-5 h-5" />
              ) : (
                <Phone className="w-5 h-5" />
              )}
              <span className="text-lg">
                Incoming {callData.callType} call...
              </span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex justify-center gap-6">
            {/* Reject button */}
            <button
              onClick={handleReject}
              className="group relative w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition-all duration-300 transform hover:scale-110 shadow-lg"
            >
              <X className="w-8 h-8 text-white" />
              <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-white text-sm opacity-0 group-hover:opacity-100 transition-opacity">
                Decline
              </div>
            </button>

            {/* Accept button */}
            <button
              onClick={handleAccept}
              className="group relative w-20 h-20 rounded-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 flex items-center justify-center transition-all duration-300 transform hover:scale-110 shadow-2xl animate-pulse"
            >
              {callData.callType === 'video' ? (
                <Video className="w-10 h-10 text-white" />
              ) : (
                <Phone className="w-10 h-10 text-white" />
              )}
              <div className="absolute -bottom-10 left-1/2 transform -translate-x-1/2 text-white text-sm font-semibold opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                Accept Call
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default IncomingCallModal;
