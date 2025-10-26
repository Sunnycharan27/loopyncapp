import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { API } from "../App";
import { Heart, MessageCircle, Share, Volume2, VolumeX, Music, Bookmark, MoreHorizontal, AlertCircle } from "lucide-react";
import ReelCommentsModal from "./ReelCommentsModal";
import UniversalShareModal from "./UniversalShareModal";

const ReelViewer = ({ reels, currentUser, onLike }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [muted, setMuted] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const [bookmarked, setBookmarked] = useState({});
  const [videoErrors, setVideoErrors] = useState({});
  const videoRefs = useRef([]);
  const containerRef = useRef(null);

  // Filter out reels with broken videos
  const validReels = reels.filter(reel => !videoErrors[reel.id]);

  useEffect(() => {
    // Track view
    if (validReels[currentIndex]) {
      axios.post(`${API}/reels/${validReels[currentIndex].id}/view`).catch(() => {});
    }
  }, [currentIndex, validReels]);

  useEffect(() => {
    const handleScroll = () => {
      if (!containerRef.current) return;
      const scrollTop = containerRef.current.scrollTop;
      const newIndex = Math.round(scrollTop / window.innerHeight);
      if (newIndex !== currentIndex && newIndex >= 0 && newIndex < validReels.length) {
        setCurrentIndex(newIndex);
        
        // Pause all videos except current
        videoRefs.current.forEach((video, idx) => {
          if (video) {
            if (idx === newIndex) {
              video.play().catch(() => {});
            } else {
              video.pause();
            }
          }
        });
      }
    };

    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [currentIndex, validReels.length]);

  const handleVideoError = (reelId) => {
    console.error(`Video failed to load for reel: ${reelId}`);
    setVideoErrors(prev => ({ ...prev, [reelId]: true }));
  };

  if (validReels.length === 0) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-gradient-to-b from-gray-900 to-black p-8 text-center">
        <div className="glass-card p-8 max-w-md">
          <AlertCircle size={64} className="text-cyan-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-3">No Reels Available</h2>
          <p className="text-gray-400 mb-6">
            Be the first to create amazing content! Click the + button below to start creating your first reel.
          </p>
          <div className="text-sm text-gray-500">
            {videoErrors && Object.keys(videoErrors).length > 0 && (
              <p>Some videos failed to load. They have been filtered out.</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  const currentReel = validReels[currentIndex];
  if (!currentReel) return null;

  const isLiked = currentReel.likedBy?.includes(currentUser?.id);
  const isBookmarked = bookmarked[currentReel.id];

  const handleBookmark = async () => {
    try {
      await axios.post(`${API}/posts/${currentReel.id}/bookmark?userId=${currentUser.id}`);
      setBookmarked(prev => ({ ...prev, [currentReel.id]: !prev[currentReel.id] }));
    } catch (error) {
      console.error("Failed to bookmark:", error);
    }
  };

  const handleDoubleTap = (e) => {
    // Double tap to like
    if (e.detail === 2 && !isLiked) {
      onLike(currentReel.id);
      // Show heart animation
      const heart = document.createElement('div');
      heart.innerHTML = '❤️';
      heart.style.cssText = 'position:absolute;font-size:100px;animation:heartPop 0.8s;pointer-events:none;z-index:10;';
      heart.style.left = e.clientX - 50 + 'px';
      heart.style.top = e.clientY - 50 + 'px';
      e.currentTarget.appendChild(heart);
      setTimeout(() => heart.remove(), 800);
    }
  };

  const getVideoSource = (reel) => {
    let videoUrl = reel.videoUrl;
    
    // If it's a relative path, prepend the API base
    if (videoUrl?.startsWith('/uploads')) {
      return `${API}${videoUrl}`;
    }
    
    // Return as-is for external URLs
    return videoUrl;
  };

  return (
    <>
      <div
        ref={containerRef}
        className="h-screen overflow-y-scroll snap-y snap-mandatory"
        style={{ scrollBehavior: 'smooth' }}
      >
        {validReels.map((reel, idx) => (
          <div
            key={reel.id}
            data-testid="reel-viewer"
            className="h-screen snap-start relative flex items-center justify-center bg-black"
            onClick={handleDoubleTap}
          >
            {/* Video */}
            <video
              ref={el => videoRefs.current[idx] = el}
              src={getVideoSource(reel)}
              className="w-full h-full object-cover"
              loop
              autoPlay={idx === currentIndex}
              muted={muted}
              playsInline
              poster={reel.thumb}
              onError={() => handleVideoError(reel.id)}
              crossOrigin="anonymous"
            />

            {/* Top Bar */}
            <div className="absolute top-0 left-0 right-0 p-4 bg-gradient-to-b from-black/60 to-transparent z-10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Music size={18} className="text-white" />
                  <span className="text-white text-sm">Original Audio</span>
                </div>
                <button className="text-white">
                  <MoreHorizontal size={24} />
                </button>
              </div>
            </div>

            {/* Overlay Info */}
            <div className="absolute bottom-20 left-0 right-0 p-6 bg-gradient-to-t from-black/80 to-transparent z-10">
              <div className="flex items-start gap-4">
                <img
                  src={reel.author?.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'}
                  alt={reel.author?.name}
                  className="w-12 h-12 rounded-full border-2 border-white"
                />
                <div className="flex-1">
                  <h3 className="font-bold text-white text-lg">{reel.author?.name || 'Unknown'}</h3>
                  <p className="text-sm text-white mt-1">{reel.caption}</p>
                  <div className="flex gap-2 mt-2 text-xs text-gray-300">
                    <span>👁️ {reel.stats?.views || 0} views</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Side Actions */}
            <div className="absolute right-4 bottom-32 flex flex-col gap-5 z-10">
              {/* Like */}
              <button
                data-testid="reel-like-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onLike(reel.id);
                }}
                className="flex flex-col items-center gap-1"
              >
                <div className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${
                  isLiked ? 'bg-pink-500 scale-110' : 'bg-white/20 backdrop-blur'
                }`}>
                  <Heart size={28} fill={isLiked ? 'white' : 'none'} className="text-white" />
                </div>
                <span className="text-xs text-white font-bold">{reel.stats?.likes || 0}</span>
              </button>

              {/* Comments */}
              <button
                data-testid="reel-comment-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowComments(true);
                }}
                className="flex flex-col items-center gap-1"
              >
                <div className="w-14 h-14 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
                  <MessageCircle size={28} className="text-white" />
                </div>
                <span className="text-xs text-white font-bold">{reel.stats?.comments || 0}</span>
              </button>

              {/* Share */}
              <button
                data-testid="reel-share-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowShare(true);
                }}
                className="flex flex-col items-center gap-1"
              >
                <div className="w-14 h-14 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
                  <Share size={28} className="text-white" />
                </div>
                <span className="text-xs text-white font-bold">Share</span>
              </button>

              {/* Bookmark */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleBookmark();
                }}
                className="flex flex-col items-center gap-1"
              >
                <div className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${
                  isBookmarked ? 'bg-yellow-500' : 'bg-white/20 backdrop-blur'
                }`}>
                  <Bookmark size={28} fill={isBookmarked ? 'white' : 'none'} className="text-white" />
                </div>
              </button>

              {/* Mute */}
              <button
                data-testid="reel-mute-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setMuted(!muted);
                }}
                className="w-14 h-14 rounded-full bg-white/20 backdrop-blur flex items-center justify-center"
              >
                {muted ? <VolumeX size={28} className="text-white" /> : <Volume2 size={28} className="text-white" />}
              </button>
            </div>

            {/* Music Track */}
            <div className="absolute bottom-20 right-4 z-10">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 animate-spin-slow flex items-center justify-center">
                <Music size={20} className="text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Comments Modal */}
      {showComments && (
        <ReelCommentsModal
          reel={currentReel}
          currentUser={currentUser}
          onClose={() => setShowComments(false)}
        />
      )}

      {/* Share Modal */}
      {showShare && (
        <UniversalShareModal
          item={currentReel}
          type="reel"
          currentUser={currentUser}
          onClose={() => setShowShare(false)}
        />
      )}

      <style jsx>{`
        @keyframes heartPop {
          0% { opacity: 0; transform: scale(0); }
          50% { opacity: 1; transform: scale(1.2); }
          100% { opacity: 0; transform: scale(1) translateY(-50px); }
        }
        
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        .animate-spin-slow {
          animation: spin-slow 3s linear infinite;
        }
      `}</style>
    </>
  );
};

export default ReelViewer;