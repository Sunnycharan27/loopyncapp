import React, { useState } from "react";
import axios from "axios";
import { API } from "../App";
import { X, Image as ImageIcon } from "lucide-react";
import { toast } from "sonner";

const ComposerModal = ({ currentUser, onClose, onPostCreated }) => {
  const [text, setText] = useState("");
  const [media, setMedia] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) {
      toast.error("Post text cannot be empty");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post(`${API}/posts?authorId=${currentUser.id}`, {
        text,
        media: media || null,
        audience: "public"
      });
      toast.success("Posted!");
      onPostCreated(res.data);
    } catch (error) {
      toast.error("Failed to create post");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card p-6 w-full max-w-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold neon-text">Create Post</h2>
          <button
            data-testid="composer-close-btn"
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <textarea
            data-testid="composer-text-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="What's on your mind?"
            className="w-full h-32 resize-none mb-4"
            autoFocus
          />

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-400">
              <ImageIcon size={16} className="inline mr-2" />
              Image URL (optional)
            </label>
            <input
              data-testid="composer-media-input"
              type="url"
              value={media}
              onChange={(e) => setMedia(e.target.value)}
              placeholder="https://example.com/image.jpg"
              className="w-full"
            />
          </div>

          {media && (
            <div className="mb-4">
              <img src={media} alt="Preview" className="rounded-2xl w-full max-h-64 object-cover" onError={() => setMedia("")} />
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 rounded-full border border-gray-600 text-gray-300 hover:bg-gray-800"
            >
              Cancel
            </button>
            <button
              data-testid="composer-submit-btn"
              type="submit"
              disabled={loading || !text.trim()}
              className="flex-1 btn-primary"
            >
              {loading ? "Posting..." : "Post"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ComposerModal;