import React, { useState } from "react";
import axios from "axios";
import { API } from "../App";
import { X, Video } from "lucide-react";
import { toast } from "sonner";

const ReelComposerModal = ({ currentUser, onClose, onReelCreated }) => {
  const [videoUrl, setVideoUrl] = useState("");
  const [thumb, setThumb] = useState("");
  const [caption, setCaption] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!videoUrl.trim()) {
      toast.error("Video URL is required");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post(`${API}/reels?authorId=${currentUser.id}`, {
        videoUrl,
        thumb: thumb || videoUrl,
        caption
      });
      toast.success("Reel created!");
      onReelCreated(res.data);
    } catch (error) {
      toast.error("Failed to create reel");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card p-6 w-full max-w-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold neon-text">Create Reel</h2>
          <button
            data-testid="reel-composer-close-btn"
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              <Video size={16} className="inline mr-2" />
              Video URL
            </label>
            <input
              data-testid="reel-video-input"
              type="url"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="https://example.com/video.mp4"
              className="w-full"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-400">
              Thumbnail URL (optional)
            </label>
            <input
              data-testid="reel-thumb-input"
              type="url"
              value={thumb}
              onChange={(e) => setThumb(e.target.value)}
              placeholder="https://example.com/thumbnail.jpg"
              className="w-full"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-400">
              Caption (optional)
            </label>
            <textarea
              data-testid="reel-caption-input"
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Add a caption..."
              className="w-full h-20 resize-none"
            />
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 rounded-full border border-gray-600 text-gray-300 hover:bg-gray-800"
            >
              Cancel
            </button>
            <button
              data-testid="reel-submit-btn"
              type="submit"
              disabled={loading || !videoUrl.trim()}
              className="flex-1 btn-primary"
            >
              {loading ? "Creating..." : "Create Reel"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReelComposerModal;