import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { Send, Trash2, Heart } from "lucide-react";
import { toast } from "sonner";

const CommentsSection = ({ postId }) => {
  const { currentUser } = useContext(AuthContext);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [postId]);

  const fetchComments = async () => {
    try {
      const res = await axios.get(`${API}/posts/${postId}/comments`);
      setComments(res.data);
    } catch (error) {
      console.error("Failed to load comments");
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;

    setLoading(true);
    try {
      const res = await axios.post(
        `${API}/posts/${postId}/comments?authorId=${currentUser.id}`,
        { text: commentText }
      );
      setComments([res.data, ...comments]);
      setCommentText("");
      toast.success("Comment added!");
    } catch (error) {
      toast.error("Failed to add comment");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteComment = async (commentId) => {
    try {
      await axios.delete(`${API}/comments/${commentId}?userId=${currentUser.id}`);
      setComments(comments.filter(c => c.id !== commentId));
      toast.success("Comment deleted");
    } catch (error) {
      toast.error("Failed to delete comment");
    }
  };

  return (
    <div className="mt-4 space-y-4">
      {/* Comment Input */}
      <form onSubmit={handleAddComment} className="flex gap-2">
        <input
          type="text"
          placeholder="Add a comment..."
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
          className="flex-1 px-4 py-2 rounded-full bg-gray-800/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400 dark:bg-gray-800/50 dark:border-gray-700 light:bg-gray-100 light:border-gray-300 light:text-black"
        />
        <button
          type="submit"
          disabled={loading || !commentText.trim()}
          className="px-4 py-2 rounded-full bg-cyan-400 text-black hover:bg-cyan-500 transition-all disabled:opacity-50"
        >
          <Send size={18} />
        </button>
      </form>

      {/* Comments List */}
      <div className="space-y-3">
        {comments.map(comment => (
          <div key={comment.id} className="flex gap-3">
            <img
              src={comment.author?.avatar}
              alt={comment.author?.name}
              className="w-8 h-8 rounded-full"
            />
            <div className="flex-1">
              <div className="bg-gray-800/30 rounded-2xl px-4 py-2 dark:bg-gray-800/30 light:bg-gray-100">
                <p className="font-semibold text-sm text-white dark:text-white light:text-black">
                  {comment.author?.name}
                </p>
                <p className="text-gray-300 text-sm mt-1 dark:text-gray-300 light:text-gray-700">
                  {comment.text}
                </p>
              </div>
              <div className="flex items-center gap-4 mt-1 ml-4 text-xs text-gray-500">
                <span>{new Date(comment.createdAt).toLocaleDateString()}</span>
                {comment.authorId === currentUser.id && (
                  <button
                    onClick={() => handleDeleteComment(comment.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CommentsSection;