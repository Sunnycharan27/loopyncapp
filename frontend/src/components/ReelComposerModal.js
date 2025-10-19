import React, { useState, useRef } from "react";
import axios from "axios";
import { API } from "../App";
import { X, Video, Upload } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ReelComposerModal = ({ currentUser, onClose, onReelCreated }) => {
  const [videoUrl, setVideoUrl] = useState("");
  const [thumb, setThumb] = useState("");
  const [caption, setCaption] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (max 50MB for videos)
    if (file.size > 50 * 1024 * 1024) {
      toast.error("Video size must be less than 50MB");
      return;
    }

    // Validate file type
    const allowedTypes = ['video/mp4', 'video/quicktime', 'video/webm'];
    if (!allowedTypes.includes(file.type)) {
      toast.error("Only videos (MP4, MOV, WebM) are supported");
      return;
    }

    setSelectedFile(file);
    
    // Create preview
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleUpload = async () => {
    if (!selectedFile) return null;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await axios.post(`${API}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      return `${BACKEND_URL}${res.data.url}`;
    } catch (error) {
      toast.error("Failed to upload video");
      return null;
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!videoUrl.trim() && !selectedFile) {
      toast.error("Video is required");
      return;
    }

    setLoading(true);
    try {
      let uploadedVideoUrl = videoUrl;
      
      // Upload file if selected
      if (selectedFile) {
        const url = await handleUpload();
        if (url) {
          uploadedVideoUrl = url;
        }
      }

      const res = await axios.post(`${API}/reels?authorId=${currentUser.id}`, {
        videoUrl: uploadedVideoUrl,
        thumb: thumb || uploadedVideoUrl,
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