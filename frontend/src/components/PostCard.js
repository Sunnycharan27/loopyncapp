import React, { useState } from "react";
import { Heart, MessageCircle, Repeat2, Share2, MoreHorizontal, Trash2, Bookmark, Flag, UserPlus, Copy, ExternalLink } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import ShareModal from "./ShareModal";

const PostCard = ({ post, currentUser, onLike, onRepost, onDelete }) => {
  const navigate = useNavigate();
  const [showQuickActions, setShowQuickActions] = useState(false);
  const [showReactions, setShowReactions] = useState(false);
  const [selectedReaction, setSelectedReaction] = useState(null);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");
  
  const isLiked = post.likedBy?.includes(currentUser?.id);
  const isReposted = post.repostedBy?.includes(currentUser?.id);
  const isOwnPost = post.authorId === currentUser?.id;

  const reactions = [
    { emoji: "❤️", label: "Love", color: "hover:bg-red-500/20" },
    { emoji: "😂", label: "Haha", color: "hover:bg-yellow-500/20" },
    { emoji: "😮", label: "Wow", color: "hover:bg-blue-500/20" },
    { emoji: "😢", label: "Sad", color: "hover:bg-gray-500/20" },
    { emoji: "🔥", label: "Fire", color: "hover:bg-orange-500/20" },
    { emoji: "👏", label: "Clap", color: "hover:bg-green-500/20" },
  ];

  const handleReaction = (reaction) => {
    setSelectedReaction(reaction);
    setShowReactions(false);
    toast.success(`Reacted with ${reaction.emoji}`);
  };

  const handleCopyLink = () => {
    const base = window?.location?.origin || '';
    navigator.clipboard.writeText(`${base}/post/${post.id}`);
    toast.success("Link copied to clipboard!");
    setShowQuickActions(false);
  };

  const handleSavePost = () => {
    toast.success("Post saved to Collections!");
    setShowQuickActions(false);
  };

  const handleReport = () => {
    toast.info("Post reported. We'll review it shortly.");
    setShowQuickActions(false);
  };

  return (
    <div className="glass-card p-4 mb-4 hover:bg-gray-800/30 transition-all relative" data-testid="post-card">
      {/* Reactions popup */}
      {showReactions && (
        <div className="absolute -top-14 left-12 z-50 glass-card p-2 rounded-full shadow-2xl flex gap-2 animate-slideUp">
          {reactions.map((reaction, idx) => (
            <button
              key={idx}
              onClick={() => handleReaction(reaction)}
              className={`w-10 h-10 rounded-full ${reaction.color} flex items-center justify-center text-2xl hover:scale-125 transition-transform`}
              title={reaction.label}
            >
              {reaction.emoji}
            </button>
          ))}
        </div>
      )}

      <div className="flex items-start gap-3">
        <img
          src={post.author?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${post.authorId}`}
          alt={post.author?.name || 'User'}
          className="w-12 h-12 rounded-full ring-2 ring-cyan-400/20 cursor-pointer hover:ring-cyan-400/50 transition-all"
          onClick={() => navigate(`/profile/${post.authorId}`)}
        />
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <div 
              className="cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => navigate(`/profile/${post.authorId}`)}
            >
              <h3 className="font-semibold text-white">{post.author?.name || 'User'}</h3>
              <p className="text-sm text-gray-400">@{post.author?.handle || post.authorId?.substring(0, 8)}</p>
            </div>
            <div className="relative">
              <button
                onClick={() => setShowQuickActions(!showQuickActions)}
                className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-700/50 text-gray-400 hover:text-white transition-all"
              >
                <MoreHorizontal size={18} />
              </button>

              {/* Quick Actions Menu */}
              {showQuickActions && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setShowQuickActions(false)}></div>
                  <div className="absolute right-0 top-full mt-2 w-48 glass-card rounded-xl shadow-2xl overflow-hidden z-50">
                    {!isOwnPost && (
                      <>
                        <button
                          onClick={handleSavePost}
                          className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-700/50 transition-all text-left"
                        >
                          <Bookmark size={16} className="text-cyan-400" />
                          <span className="text-sm text-white">Save Post</span>
                        </button>
                        <button
                          onClick={handleCopyLink}
                          className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-700/50 transition-all text-left"
                        >
                          <Copy size={16} className="text-blue-400" />
                          <span className="text-sm text-white">Copy Link</span>
                        </button>
                        <button
                          className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-700/50 transition-all text-left"
                        >
                          <UserPlus size={16} className="text-green-400" />
                          <span className="text-sm text-white">Follow {post.author?.name}</span>
                        </button>
                        <div className="border-t border-gray-700"></div>
                        <button
                          onClick={handleReport}
                          className="w-full flex items-center gap-3 px-4 py-3 hover:bg-red-500/20 transition-all text-left"
                        >
                          <Flag size={16} className="text-red-400" />
                          <span className="text-sm text-red-400">Report Post</span>
                        </button>
                      </>
                    )}
                    {isOwnPost && (
                      <>
                        <button
                          onClick={handleCopyLink}
                          className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-700/50 transition-all text-left"
                        >
                          <ExternalLink size={16} className="text-cyan-400" />
                          <span className="text-sm text-white">Share</span>
                        </button>
                        <button
                          onClick={() => {
                            onDelete(post.id);
                            setShowQuickActions(false);
                          }}
                          className="w-full flex items-center gap-3 px-4 py-3 hover:bg-red-500/20 transition-all text-left"
                        >
                          <Trash2 size={16} className="text-red-400" />
                          <span className="text-sm text-red-400">Delete Post</span>
                        </button>
                      </>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>

          <p className="text-gray-200 mb-3">{post.text}</p>

          {post.media && (
            /\.(mp4|webm|mov)$/i.test(post.media) ? (
              <video
                src={post.media.startsWith('/uploads') ? `${(import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL)}${post.media}` : post.media}
                controls
                className="rounded-2xl w-full mb-3"
                onClick={() => setShowReactions(true)}
              />
            ) : (
              <img
                src={post.media.startsWith('/uploads') ? `${(import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL)}${post.media}` : post.media}
                alt="Post media"
                className="rounded-2xl w-full mb-3 hover:scale-[1.01] transition-transform cursor-pointer"
                onClick={() => setShowReactions(true)}
              />
            )
          )}

          {/* Selected Reaction Display */}
          {selectedReaction && (
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gray-800/50 mb-3 animate-bounce-in">
              <span className="text-lg">{selectedReaction.emoji}</span>
              <span className="text-xs text-gray-400">You reacted</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-6 text-gray-400">
            <button
              data-testid="post-like-btn"
              onMouseEnter={() => setShowReactions(true)}
              onMouseLeave={() => setTimeout(() => setShowReactions(false), 1000)}
              onClick={() => onLike(post.id)}
              className={`flex items-center gap-2 hover:text-pink-400 transition-colors group ${
                isLiked ? 'text-pink-400' : ''
              }`}
            >
              <Heart size={18} className={`${isLiked ? 'fill-current' : ''} group-hover:scale-110 transition-transform`} />
              <span className="text-sm">{post.likeCount || 0}</span>
            </button>

            <button className="flex items-center gap-2 hover:text-cyan-400 transition-colors">
              <MessageCircle size={18} />
              <span className="text-sm">{post.stats?.replies || 0}</span>
            </button>

            <button
              data-testid="post-repost-btn"
              onClick={() => onRepost(post.id)}
              className={`flex items-center gap-2 hover:text-green-400 transition-colors ${
                isReposted ? 'text-green-400' : ''
              }`}
            >
              <Repeat2 size={18} />
              <span className="text-sm">{post.stats?.reposts || 0}</span>
            </button>

            <button 
              onClick={() => setShowShareModal(true)}
              className="flex items-center gap-2 hover:text-cyan-400 transition-colors"
            >
              <Share2 size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Share Modal */}
      <ShareModal
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
        item={post}
        type="post"
      />
    </div>
  );
};

export default PostCard;