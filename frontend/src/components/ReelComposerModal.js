import React, { useState, useRef } from "react";
import MusicPicker from "./MusicPicker";

import axios from "axios";
import { API } from "../App";
import { X, Video, Upload, Music, Mic } from "lucide-react";
import { toast } from "sonner";

const ReelComposerModal = ({ currentUser, onClose, onReelCreated }) => {
  const [videoUrl, setVideoUrl] = useState("");
  const [thumb, setThumb] = useState("");
  const [caption, setCaption] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedMusic, setSelectedMusic] = useState(null);
  const fileInputRef = useRef(null);
  const audioInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (max 100MB for videos)
    if (file.size > 100 * 1024 * 1024) {
      toast.error("Video size must be less than 100MB");
      return;
    }

    // Validate file type
    const allowedTypes = ['video/mp4', 'video/quicktime', 'video/webm', 'video/avi'];
    if (!allowedTypes.includes(file.type)) {
      toast.error("Only videos (MP4, MOV, WebM, AVI) are supported");
      return;
    }

    setSelectedFile(file);
    
    // Create preview
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    
    toast.success("Video selected!");
  };

  const handleAudioSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (max 10MB for audio)
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Audio size must be less than 10MB");
      return;
    }

    // Validate file type
    const allowedTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg'];
    if (!allowedTypes.includes(file.type)) {
      toast.error("Only audio files (MP3, WAV, OGG) are supported");
      return;
    }

    setAudioFile(file);
    toast.success(`Audio selected: ${file.name}`);
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
      return `${API}${res.data.url}`;
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

      // Add music info to caption if selected
      let finalCaption = caption;
      if (selectedMusic) {
        finalCaption = `${caption}\n\n🎵 ${selectedMusic.title} - ${selectedMusic.artists?.[0] || ''}`.trim();
      } else if (audioFile) {
        finalCaption = `${caption}\n\n🎵 Custom Audio: ${audioFile.name}`.trim();
      }

      const res = await axios.post(`${API}/reels?authorId=${currentUser.id}`, {
        videoUrl: uploadedVideoUrl,
        thumb: thumb || uploadedVideoUrl,
        caption: finalCaption
      });
      
      toast.success("Reel created successfully! 🎉");
      onReelCreated(res.data);
    } catch (error) {
      toast.error("Failed to create reel");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="glass-card p-6 w-full max-w-2xl my-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold neon-text">Create Reel</h2>
          <button
            data-testid="reel-composer-close-btn"
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {/* File Upload Section */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-300">
              <Video size={16} className="inline mr-2" />
              Upload Video
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/quicktime,video/webm,video/avi"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-cyan-400/20 to-purple-400/20 text-white hover:from-cyan-400/30 hover:to-purple-400/30 w-full justify-center border border-cyan-400/30"
              data-testid="reel-file-btn"
            >
              <Upload size={20} />
              {selectedFile ? `✓ ${selectedFile.name.substring(0, 30)}...` : "Choose Video (MP4, MOV, WebM)"}
            </button>
          </div>

          {/* Preview */}
          {previewUrl && (
            <div className="mb-4 relative rounded-xl overflow-hidden">
              <video src={previewUrl} className="w-full max-h-96 object-cover" controls />
              <button
                type="button"
                onClick={() => {
                  setSelectedFile(null);
                  setPreviewUrl("");
                  URL.revokeObjectURL(previewUrl);
                }}
                className="absolute top-2 right-2 w-10 h-10 rounded-full bg-black/70 flex items-center justify-center text-white hover:bg-black/90 backdrop-blur"
              >
                <X size={20} />
              </button>
            </div>
          )}

          {/* URL Input (optional fallback) */}
          {!selectedFile && (
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2 text-gray-400">
                Or paste video URL
              </label>
              <input
                data-testid="reel-video-input"
                type="url"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="https://example.com/video.mp4"
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white"
              />
            </div>
          )}

          {/* Caption */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-300">
              Caption
            </label>
            <textarea
              data-testid="reel-caption-input"
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Write a caption... (use hashtags!)"
              className="w-full h-24 resize-none bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white"
              maxLength={500}
            />
            <p className="text-xs text-gray-500 mt-1">{caption.length}/500</p>
          </div>

          {/* Audio Options */}
          <div className="mb-4 space-y-3">
            <label className="block text-sm font-medium text-gray-300">
              <Music size={16} className="inline mr-2" />
              Add Audio
            </label>
            
            {/* Custom Audio Upload */}
            <div>
              <input
                ref={audioInputRef}
                type="file"
                accept="audio/mpeg,audio/mp3,audio/wav,audio/ogg"
                onChange={handleAudioSelect}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => audioInputRef.current?.click()}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-400/20 text-purple-300 hover:bg-purple-400/30 w-full justify-center border border-purple-400/30"
              >
                <Mic size={18} />
                {audioFile ? `✓ ${audioFile.name}` : "Upload Custom Audio"}
              </button>
            </div>

            {/* Music Library */}
            <MusicPicker 
              onSelect={(track) => {
                setSelectedMusic(track);
                toast.success(`Selected: ${track.title}`);
              }} 
            />
            {selectedMusic && (
              <div className="p-3 rounded-xl bg-cyan-400/10 border border-cyan-400/30">
                <p className="text-sm text-cyan-300">
                  🎵 Selected: {selectedMusic.title} - {selectedMusic.artists?.[0]}
                </p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 rounded-full border-2 border-gray-600 text-gray-300 hover:bg-gray-800 font-semibold"
            >
              Cancel
            </button>
            <button
              data-testid="reel-submit-btn"
              type="submit"
              disabled={loading || uploading || (!videoUrl.trim() && !selectedFile)}
              className="flex-1 py-3 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90"
            >
              {uploading ? "Uploading..." : loading ? "Creating..." : "🎬 Post Reel"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReelComposerModal;