import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { API } from "../App";
import { X, Send, Heart } from "lucide-react";
import { toast } from "sonner";

const ReelCommentsModal = ({ reel, currentUser, onClose }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);
  const commentsEndRef = useRef(null);

  useEffect(() => {
    fetchComments();
  }, [reel.id]);

  useEffect(() => {
    scrollToBottom();
  }, [comments]);

  const fetchComments = async () => {
    try {
      const res = await axios.get(`${API}/reels/${reel.id}/comments`);
      setComments(res.data);
    } catch (error) {
      console.error("Failed to load comments:", error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    commentsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setPosting(true);
    try {
      const res = await axios.post(
        `${API}/reels/${reel.id}/comments?userId=${currentUser.id}&comment=${encodeURIComponent(newComment)}`
      );
      setComments([...comments, res.data]);
      setNewComment("");
      toast.success("Comment posted!");
    } catch (error) {
      toast.error("Failed to post comment");
    } finally {
      setPosting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/90 z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white">
          Comments ({comments.length})
        </h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition"
        >
          <X size={24} />
        </button>
      </div>

      {/* Comments List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
          </div>
        ) : comments.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <Heart size={48} className="mb-4 opacity-30" />
            <p>No comments yet</p>
            <p className="text-sm">Be the first to comment!</p>
          </div>
        ) : (
          comments.map((comment, idx) => (
            <div key={idx} className="flex gap-3">
              <img
                src={comment.author?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${comment.author?.name}`}
                alt={comment.author?.name}
                className="w-10 h-10 rounded-full flex-shrink-0"
              />
              <div className="flex-1">
                <div className="bg-gray-800/50 rounded-2xl px-4 py-2">
                  <p className="font-semibold text-sm text-white">
                    {comment.author?.name || "Unknown"}
                  </p>
                  <p className="text-white text-sm mt-1">{comment.comment}</p>
                </div>
                <div className="flex items-center gap-4 mt-1 px-4">
                  <span className="text-xs text-gray-400">
                    {new Date(comment.timestamp).toLocaleDateString()}
                  </span>
                  {/* <button className="text-xs text-gray-400 hover:text-white">
                    Like
                  </button>
                  <button className="text-xs text-gray-400 hover:text-white">
                    Reply
                  </button> */}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={commentsEndRef} />
      </div>

      {/* Comment Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800 bg-gray-900">
        <div className="flex items-center gap-3">
          <img
            src={currentUser?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser?.name}`}
            alt={currentUser?.name}
            className="w-10 h-10 rounded-full"
          />
          <input
            type="text"
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a comment..."
            className="flex-1 bg-gray-800 border border-gray-700 rounded-full px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400"
            disabled={posting}
          />
          <button
            type="submit"
            disabled={!newComment.trim() || posting}
            className="p-2 rounded-full bg-cyan-400 text-black disabled:opacity-30 disabled:cursor-not-allowed hover:bg-cyan-300 transition"
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ReelCommentsModal;
