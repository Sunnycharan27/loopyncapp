import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import PostCard from "../components/PostCard";
import { toast } from "sonner";
import { ArrowLeft, Users } from "lucide-react";
import { useNavigate } from "react-router-dom";

const TribeDetail = () => {
  const { tribeId } = useParams();
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [tribe, setTribe] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTribeData();
  }, [tribeId]);

  const fetchTribeData = async () => {
    try {
      const [tribeRes, postsRes] = await Promise.all([
        axios.get(`${API}/tribes/${tribeId}`),
        axios.get(`${API}/tribes/${tribeId}/posts`)
      ]);
      setTribe(tribeRes.data);
      setPosts(postsRes.data);
    } catch (error) {
      toast.error("Failed to load tribe");
    } finally {
      setLoading(false);
    }
  };

  const handleJoinLeave = async () => {
    const isMember = tribe.members.includes(currentUser.id);
    try {
      const endpoint = isMember ? "leave" : "join";
      const res = await axios.post(`${API}/tribes/${tribeId}/${endpoint}?userId=${currentUser.id}`);
      
      setTribe({
        ...tribe,
        members: isMember
          ? tribe.members.filter(m => m !== currentUser.id)
          : [...tribe.members, currentUser.id],
        memberCount: res.data.memberCount
      });
      
      toast.success(isMember ? "Left tribe" : "Joined tribe!");
    } catch (error) {
      toast.error("Action failed");
    }
  };

  const handleLike = async (postId) => {
    try {
      const res = await axios.post(`${API}/posts/${postId}/like?userId=${currentUser.id}`);
      setPosts(posts.map(p => {
        if (p.id === postId) {
          const liked = res.data.action === "liked";
          return {
            ...p,
            stats: { ...p.stats, likes: res.data.likes },
            likedBy: liked
              ? [...(p.likedBy || []), currentUser.id]
              : (p.likedBy || []).filter(id => id !== currentUser.id)
          };
        }
        return p;
      }));
    } catch (error) {
      toast.error("Failed to like post");
    }
  };

  const handleRepost = async (postId) => {
    try {
      const res = await axios.post(`${API}/posts/${postId}/repost?userId=${currentUser.id}`);
      setPosts(posts.map(p => {
        if (p.id === postId) {
          const reposted = res.data.action === "reposted";
          return {
            ...p,
            stats: { ...p.stats, reposts: res.data.reposts },
            repostedBy: reposted
              ? [...(p.repostedBy || []), currentUser.id]
              : (p.repostedBy || []).filter(id => id !== currentUser.id)
          };
        }
        return p;
      }));
      toast.success(res.data.action === "reposted" ? "Reposted!" : "Unreposted");
    } catch (error) {
      toast.error("Failed to repost");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0f021e' }}>
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!tribe) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0f021e' }}>
        <p className="text-gray-400">Tribe not found</p>
      </div>
    );
  }

  const isMember = tribe.members.includes(currentUser.id);

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="glass-surface p-4 mb-6">
          <button
            data-testid="tribe-back-btn"
            onClick={() => navigate('/tribes')}
            className="flex items-center gap-2 text-cyan-400 mb-4 hover:text-cyan-300"
          >
            <ArrowLeft size={20} />
            Back to Tribes
          </button>

          <div className="flex items-start gap-4">
            <img src={tribe.avatar} alt={tribe.name} className="w-20 h-20 rounded-3xl" />
            <div className="flex-1">
              <h1 className="text-2xl font-bold neon-text">{tribe.name}</h1>
              <p className="text-sm text-gray-400 mb-2">{tribe.description}</p>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Users size={16} />
                <span>{tribe.memberCount} members</span>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {tribe.tags.map((tag, idx) => (
                  <span key={idx} className="px-3 py-1 rounded-full text-xs bg-cyan-400/10 text-cyan-400">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <button
            data-testid="tribe-join-leave-btn"
            onClick={handleJoinLeave}
            className={`w-full mt-4 py-3 rounded-full font-semibold ${
              isMember
                ? 'bg-gray-700 text-white hover:bg-gray-600'
                : 'btn-primary'
            }`}
          >
            {isMember ? 'Leave Tribe' : 'Join Tribe'}
          </button>
        </div>

        {/* Tribe Posts */}
        <div className="px-4">
          <h2 className="text-xl font-bold mb-4">Tribe Posts</h2>
          {posts.length === 0 ? (
            <div className="text-center py-12 glass-card p-8">
              <p className="text-gray-400">No posts in this tribe yet</p>
            </div>
          ) : (
            <div className="space-y-4">
              {posts.map(post => (
                <PostCard
                  key={post.id}
                  post={post}
                  currentUser={currentUser}
                  onLike={handleLike}
                  onRepost={handleRepost}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      <BottomNav active="tribes" />
    </div>
  );
};

export default TribeDetail;