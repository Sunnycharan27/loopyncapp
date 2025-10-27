import React, { useState } from "react";
import ReactDOM from "react-dom";
import { Plus, X, Upload, Image as ImageIcon, Video } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import { API } from "../App";

const VibeCapsuleUpload = ({ currentUser, onUploadComplete }) => {
  const [showModal, setShowModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [mediaType, setMediaType] = useState("image");
  const [mediaUrl, setMediaUrl] = useState("");
  const [caption, setCaption] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const isImage = file.type.startsWith("image/");
    const isVideo = file.type.startsWith("video/");

    if (!isImage && !isVideo) {
      toast.error("Please upload an image or video file");
      return;
    }

    // Validate file size (max 50MB for video, 10MB for image)
    const maxSize = isVideo ? 50 * 1024 * 1024 : 10 * 1024 * 1024;
    if (file.size > maxSize) {
      toast.error(`File too large. Max ${isVideo ? '50MB for video' : '10MB for image'}`);
      return;
    }

    setUploading(true);
    setMediaType(isImage ? "image" : "video");

    try {
      // Upload to backend
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await axios.post(`${API}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });

      const uploadedUrl = `${API}${uploadRes.data.url}`;
      setMediaUrl(uploadedUrl);
      
      toast.success("Media uploaded successfully!");
    } catch (error) {
      console.error("Upload failed:", error);
      toast.error("Failed to upload media");
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleCreateCapsule = async () => {
    if (!mediaUrl) {
      toast.error("Please upload media first");
      return;
    }

    try {
      setUploading(true);
      
      const capsuleData = {
        mediaType,
        mediaUrl,
        caption,
        duration: mediaType === "video" ? 15 : 5
      };

      await axios.post(
        `${API}/capsules?authorId=${currentUser.id}`,
        capsuleData
      );

      toast.success("🎉 Vibe Capsule created!");
      setShowModal(false);
      setMediaUrl("");
      setCaption("");
      
      if (onUploadComplete) {
        onUploadComplete();
      }
    } catch (error) {
      console.error("Failed to create capsule:", error);
      toast.error("Failed to create Vibe Capsule");
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      {/* Add Story Button */}
      <button
        onClick={() => setShowModal(true)}
        className="flex flex-col items-center gap-2 flex-shrink-0"
      >
        <div className="w-16 h-16 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 flex items-center justify-center border-4 border-gray-900 relative">
          <Plus size={24} className="text-white" />
        </div>
        <span className="text-xs text-white font-medium">Your Story</span>
      </button>

      {/* Upload Modal */}
      {showModal && ReactDOM.createPortal(
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4" style={{ zIndex: 9999 }}>
          <div className="bg-gray-800 rounded-2xl max-w-lg w-full border border-gray-700" style={{ zIndex: 10000 }}>
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h2 className="text-xl font-bold text-white">Create Vibe Capsule</h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X size={24} className="text-gray-400" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4">
              {/* Media Upload */}
              {!mediaUrl ? (
                <div className="border-2 border-dashed border-gray-600 rounded-xl p-8 text-center">
                  <input
                    type="file"
                    id="media-upload"
                    accept="image/*,video/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <label
                    htmlFor="media-upload"
                    className="cursor-pointer flex flex-col items-center gap-4"
                  >
                    <div className="w-16 h-16 rounded-full bg-gray-700 flex items-center justify-center">
                      <Upload size={32} className="text-cyan-400" />
                    </div>
                    <div>
                      <p className="text-white font-semibold mb-1">
                        Upload Photo or Video
                      </p>
                      <p className="text-sm text-gray-400">
                        Video must be 15-30 seconds
                      </p>
                    </div>
                  </label>
                </div>
              ) : (
                <div className="relative rounded-xl overflow-hidden bg-gray-900">
                  {mediaType === "image" ? (
                    <img
                      src={mediaUrl}
                      alt="Preview"
                      className="w-full h-64 object-cover"
                    />
                  ) : (
                    <video
                      src={mediaUrl}
                      controls
                      className="w-full h-64 object-cover"
                    />
                  )}
                  <button
                    onClick={() => setMediaUrl("")}
                    className="absolute top-2 right-2 p-2 bg-black/50 rounded-full hover:bg-black/70 transition-colors"
                  >
                    <X size={20} className="text-white" />
                  </button>
                </div>
              )}

              {/* Caption */}
              <div>
                <label className="text-sm text-gray-400 mb-2 block">
                  Caption (Optional)
                </label>
                <textarea
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  placeholder="Add a caption..."
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none resize-none"
                  rows="3"
                  maxLength={200}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {caption.length}/200 characters
                </p>
              </div>

              {/* Create Button */}
              <button
                onClick={handleCreateCapsule}
                disabled={!mediaUrl || uploading}
                className="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-cyan-500 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all"
              >
                {uploading ? "Creating..." : "Share Vibe Capsule"}
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
};

export default VibeCapsuleUpload;
