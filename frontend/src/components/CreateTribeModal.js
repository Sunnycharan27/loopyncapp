import React, { useState } from "react";
import axios from "axios";
import { API } from "../App";
import { X } from "lucide-react";
import { toast } from "sonner";

const CreateTribeModal = ({ currentUser, onClose, onTribeCreated }) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState("");
  const [type, setType] = useState("public");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      toast.error("Tribe name is required");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post(`${API}/tribes?ownerId=${currentUser.id}`, {
        name,
        description,
        tags: tags.split(',').map(t => t.trim()).filter(t => t),
        type
      });
      toast.success("Tribe created!");
      onTribeCreated(res.data);
    } catch (error) {
      toast.error("Failed to create tribe");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card p-6 w-full max-w-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold neon-text">Create Tribe</h2>
          <button
            data-testid="tribe-modal-close-btn"
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Tribe Name</label>
            <input
              data-testid="tribe-name-input"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Tech Builders India"
              className="w-full"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              data-testid="tribe-desc-input"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What's your tribe about?"
              className="w-full h-24 resize-none"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-400">
              Tags (comma-separated)
            </label>
            <input
              data-testid="tribe-tags-input"
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="tech, startups, coding"
              className="w-full"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Type</label>
            <select
              data-testid="tribe-type-select"
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full"
            >
              <option value="public">Public</option>
              <option value="private">Private</option>
            </select>
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
              data-testid="tribe-submit-btn"
              type="submit"
              disabled={loading || !name.trim()}
              className="flex-1 btn-primary"
            >
              {loading ? "Creating..." : "Create Tribe"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateTribeModal;