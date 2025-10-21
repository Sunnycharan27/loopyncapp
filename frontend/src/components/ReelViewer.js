import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { API } from "../App";
import { Heart, MessageCircle, Share, Volume2, VolumeX } from "lucide-react";

const ReelViewer = ({ reels, currentUser, onLike }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [muted, setMuted] = useState(false);
  const videoRefs = useRef([]);
  const containerRef = useRef(null);

  useEffect(() => {
    // Track view
    if (reels[currentIndex]) {
      axios.post(`${API}/reels/${reels[currentIndex].id}/view`);
    }
  }, [currentIndex, reels]);

  useEffect(() => {
    const handleScroll = () => {
      if (!containerRef.current) return;
      const scrollTop = containerRef.current.scrollTop;
      const newIndex = Math.round(scrollTop / window.innerHeight);
      if (newIndex !== currentIndex && newIndex >= 0 && newIndex < reels.length) {
        setCurrentIndex(newIndex);
      }
    };

    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [currentIndex, reels.length]);

  const currentReel = reels[currentIndex];
  if (!currentReel) return null;

  const isLiked = currentReel.likedBy?.includes(currentUser?.id);

  return (
    <div
      ref={containerRef}
      className="h-screen overflow-y-scroll snap-y snap-mandatory"
      style={{ scrollBehavior: 'smooth' }}
    >
      {reels.map((reel, idx) => (
        <div
          key={reel.id}
          data-testid="reel-viewer"
          className="h-screen snap-start relative flex items-center justify-center bg-black"
        >
          {/* Video */}
          <video
            ref={el => videoRefs.current[idx] = el}
            src={reel.videoUrl?.startsWith('/uploads') ? `${(import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL)}/api${reel.videoUrl}` : reel.videoUrl}
            className="w-full h-full object-cover"
            loop
            autoPlay={idx === currentIndex}
            muted={muted}
            playsInline
            poster={reel.thumb?.startsWith('/uploads') ? `${(import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL)}/api${reel.thumb}` : reel.thumb}
          />

          {/* Overlay Info */}
          <div className="absolute bottom-20 left-0 right-0 p-6 bg-gradient-to-t from-black/80 to-transparent">
            <div className="flex items-start gap-4">
              <img
                src={reel.author?.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'}
                alt={reel.author?.name}
                className="w-12 h-12 rounded-full"
              />
              <div className="flex-1">
                <h3 className="font-semibold">{reel.author?.name || 'Unknown'}</h3>
                <p className="text-sm text-gray-300">{reel.caption}</p>
                <div className="flex gap-1 mt-2 text-xs text-gray-400">
                  <span>{reel.stats?.views || 0} views</span>
                </div>
              </div>
            </div>
          </div>

          {/* Side Actions */}
          <div className="absolute right-4 bottom-32 flex flex-col gap-6">
            <button
              data-testid="reel-like-btn"
              onClick={() => onLike(reel.id)}
              className="flex flex-col items-center gap-1"
            >
              <div className={`w-14 h-14 rounded-full flex items-center justify-center ${
                isLiked ? 'bg-pink-500' : 'bg-white/20 backdrop-blur'
              }`}>
                <Heart size={24} fill={isLiked ? 'white' : 'none'} className="text-white" />
              </div>
              <span className="text-xs text-white font-semibold">{reel.stats?.likes || 0}</span>
            </button>

            <button
              data-testid="reel-comment-btn"
              className="flex flex-col items-center gap-1"
            >
              <div className="w-14 h-14 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
                <MessageCircle size={24} className="text-white" />
              </div>
              <span className="text-xs text-white font-semibold">{reel.stats?.comments || 0}</span>
            </button>

            <button
              data-testid="reel-share-btn"
              className="flex flex-col items-center gap-1"
            >
              <div className="w-14 h-14 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
                <Share size={24} className="text-white" />
              </div>
            </button>

            <button
              data-testid="reel-mute-btn"
              onClick={() => setMuted(!muted)}
              className="w-14 h-14 rounded-full bg-white/20 backdrop-blur flex items-center justify-center"
            >
              {muted ? <VolumeX size={24} className="text-white" /> : <Volume2 size={24} className="text-white" />}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ReelViewer;