import React from "react";
import { Heart, MessageCircle, Repeat2, Share2, MoreHorizontal, Trash2 } from "lucide-react";

const PostCard = ({ post, currentUser, onLike, onRepost, onDelete }) => {
  const isLiked = post.likedBy?.includes(currentUser?.id);
  const isReposted = post.repostedBy?.includes(currentUser?.id);
  const isOwnPost = post.authorId === currentUser?.id;

  return (
    <div data-testid="post-card" className="glass-card p-5">
      {/* Author */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <img
            src={post.author?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${post.authorId}`}
            alt={post.author?.name || 'User'}
            className="w-12 h-12 rounded-full"
          />
          <div>
            <h3 className="font-semibold text-white">{post.author?.name || 'User'}</h3>
            <p className="text-sm text-gray-400">@{post.author?.handle || post.authorId?.substring(0, 8)}</p>
          </div>
        </div>
        {isOwnPost && (
          <button
            onClick={() => onDelete(post.id)}
            className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-all"
            title="Delete post"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>

      {/* Content */}
      <p className="text-gray-200 mb-3">{post.text}</p>
      {post.media && (
        <img
          src={post.media}
          alt="Post media"
          className="rounded-2xl w-full mb-3 hover:scale-[1.02] transition-transform"
        />
      )}

      {/* Actions */}
      <div className="flex items-center gap-6 text-gray-400">
        <button
          data-testid="post-like-btn"
          onClick={() => onLike(post.id)}
          className={`flex items-center gap-2 hover:text-pink-400 transition-colors ${
            isLiked ? 'text-pink-400' : ''
          }`}
        >
          <Heart size={18} fill={isLiked ? 'currentColor' : 'none'} />
          <span className="text-xs">{post.stats?.likes || 0}</span>
        </button>

        <button
          data-testid="post-comment-btn"
          className="flex items-center gap-2 hover:text-cyan-400 transition-colors"
        >
          <MessageCircle size={18} />
          <span className="text-xs">{post.stats?.replies || 0}</span>
        </button>

        <button
          data-testid="post-repost-btn"
          onClick={() => onRepost(post.id)}
          className={`flex items-center gap-2 hover:text-green-400 transition-colors ${
            isReposted ? 'text-green-400' : ''
          }`}
        >
          <Repeat2 size={18} />
          <span className="text-xs">{post.stats?.reposts || 0}</span>
        </button>

        <button
          data-testid="post-share-btn"
          className="flex items-center gap-2 hover:text-cyan-400 transition-colors"
        >
          <Share size={18} />
        </button>
      </div>
    </div>
  );
};

export default PostCard;