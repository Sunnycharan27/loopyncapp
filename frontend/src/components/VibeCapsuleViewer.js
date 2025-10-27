import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { X, Heart, MessageCircle, Eye, ChevronLeft, ChevronRight } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import { API } from "../App";

const VibeCapsuleViewer = ({ stories, currentUserId, onClose }) => {
  const [currentStoryIndex, setCurrentStoryIndex] = useState(0);
  const [currentCapsuleIndex, setCurrentCapsuleIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  const currentStory = stories[currentStoryIndex];
  const currentCapsule = currentStory?.capsules[currentCapsuleIndex];

  useEffect(() => {
    if (!currentCapsule || isPaused) return;

    // Mark as viewed
    markAsViewed();

    // Progress bar animation
    const duration = currentCapsule.mediaType === "video" ? currentCapsule.duration * 1000 : 5000;
    const interval = 50;
    let elapsed = 0;

    const timer = setInterval(() => {
      elapsed += interval;
      const progressPercent = (elapsed / duration) * 100;
      setProgress(progressPercent);

      if (elapsed >= duration) {
        goToNext();
      }
    }, interval);

    return () => clearInterval(timer);
  }, [currentStoryIndex, currentCapsuleIndex, isPaused]);

  const markAsViewed = async () => {
    try {
      await axios.post(
        `${API}/capsules/${currentCapsule.id}/view?userId=${currentUserId}`
      );
    } catch (error) {
      console.error("Failed to mark as viewed:", error);
    }
  };

  const goToNext = () => {
    if (currentCapsuleIndex < currentStory.capsules.length - 1) {
      setCurrentCapsuleIndex(currentCapsuleIndex + 1);
      setProgress(0);
    } else if (currentStoryIndex < stories.length - 1) {
      setCurrentStoryIndex(currentStoryIndex + 1);
      setCurrentCapsuleIndex(0);
      setProgress(0);
    } else {
      onClose();
    }
  };

  const goToPrevious = () => {
    if (currentCapsuleIndex > 0) {
      setCurrentCapsuleIndex(currentCapsuleIndex - 1);
      setProgress(0);
    } else if (currentStoryIndex > 0) {
      setCurrentStoryIndex(currentStoryIndex - 1);
      const prevStory = stories[currentStoryIndex - 1];
      setCurrentCapsuleIndex(prevStory.capsules.length - 1);
      setProgress(0);
    }
  };

  const handleReaction = async (emoji) => {
    try {
      await axios.post(
        `${API}/capsules/${currentCapsule.id}/react?userId=${currentUserId}&reaction=${emoji}`
      );
      toast.success(`Reacted with ${emoji}`);
    } catch (error) {
      toast.error("Failed to add reaction");
    }
  };

  if (!currentStory || !currentCapsule) return null;

  // Render using portal to ensure it's on top of everything
  return ReactDOM.createPortal(
    <div className="fixed inset-0 bg-black flex items-center justify-center" style={{ zIndex: 9999 }}>
      {/* Progress Bars */}
      <div className="absolute top-4 left-4 right-4 flex gap-1 z-10">
        {currentStory.capsules.map((_, idx) => (
          <div
            key={idx}
            className="flex-1 h-1 bg-gray-700 rounded-full overflow-hidden"
          >
            <div
              className="h-full bg-white transition-all"
              style={{
                width: idx === currentCapsuleIndex ? `${progress}%` : idx < currentCapsuleIndex ? "100%" : "0%"
              }}
            />
          </div>
        ))}
      </div>

      {/* Header */}
      <div className="absolute top-8 left-4 right-4 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <img
            src={currentStory.author.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${currentStory.author.name}`}
            alt={currentStory.author.name}
            className="w-10 h-10 rounded-full border-2 border-white"
          />
          <div>
            <p className="text-white font-semibold">{currentStory.author.name}</p>
            <p className="text-white/80 text-xs">@{currentStory.author.handle}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 bg-black/50 rounded-full hover:bg-black/70 transition-colors"
        >
          <X size={24} className="text-white" />
        </button>
      </div>

      {/* Navigation Areas */}
      <div className="absolute inset-0 flex">
        <button
          onClick={goToPrevious}
          className="flex-1 cursor-pointer"
          onMouseEnter={() => setIsPaused(true)}
          onMouseLeave={() => setIsPaused(false)}
        />
        <button
          onClick={goToNext}
          className="flex-1 cursor-pointer"
          onMouseEnter={() => setIsPaused(true)}
          onMouseLeave={() => setIsPaused(false)}
        />
      </div>

      {/* Content */}
      <div className="relative w-full max-w-lg h-full flex items-center justify-center">
        {currentCapsule.mediaType === "image" ? (
          <img
            src={currentCapsule.mediaUrl}
            alt="Story"
            className="w-full h-full object-contain"
          />
        ) : (
          <video
            src={currentCapsule.mediaUrl}
            autoPlay
            muted
            className="w-full h-full object-contain"
          />
        )}

        {/* Caption */}
        {currentCapsule.caption && (
          <div className="absolute bottom-24 left-4 right-4">
            <p className="text-white text-lg font-medium bg-black/50 backdrop-blur-sm rounded-xl p-4">
              {currentCapsule.caption}
            </p>
          </div>
        )}
      </div>

      {/* Reactions Bar */}
      <div className="absolute bottom-8 left-4 right-4 z-10">
        <div className="flex items-center justify-center gap-4 bg-black/50 backdrop-blur-sm rounded-full p-3">
          {["❤️", "🔥", "😂", "😮", "👏"].map((emoji) => (
            <button
              key={emoji}
              onClick={() => handleReaction(emoji)}
              className="text-2xl hover:scale-125 transition-transform"
            >
              {emoji}
            </button>
          ))}
        </div>

        {/* View Count */}
        <div className="flex items-center justify-center gap-2 mt-3 text-white text-sm">
          <Eye size={16} />
          <span>{currentCapsule.views?.length || 0} views</span>
        </div>
      </div>

      {/* Navigation Arrows (Desktop) */}
      <div className="hidden md:block">
        {currentCapsuleIndex > 0 || currentStoryIndex > 0 ? (
          <button
            onClick={goToPrevious}
            className="absolute left-4 top-1/2 -translate-y-1/2 p-3 bg-black/50 rounded-full hover:bg-black/70 transition-colors"
          >
            <ChevronLeft size={32} className="text-white" />
          </button>
        ) : null}

        {currentCapsuleIndex < currentStory.capsules.length - 1 || currentStoryIndex < stories.length - 1 ? (
          <button
            onClick={goToNext}
            className="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-black/50 rounded-full hover:bg-black/70 transition-colors"
          >
            <ChevronRight size={32} className="text-white" />
          </button>
        ) : null}
      </div>
    </div>,
    document.body
  );
};

export default VibeCapsuleViewer;
