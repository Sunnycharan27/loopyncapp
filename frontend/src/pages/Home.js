import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import TopHeader from "../components/TopHeader";
import CreateFAB from "../components/CreateFAB";
import PostCard from "../components/PostCard";
import ComposerModal from "../components/ComposerModal";
import LiveActivityFeed from "../components/LiveActivityFeed";
import StreakCounter from "../components/StreakCounter";
import MoodSelector from "../components/MoodSelector";
import { toast } from "sonner";
import { emergentApi } from "../services/emergentApi";
// import GuidedTours from "../components/GuidedTours";

const Home = () => {
  const { currentUser } = useContext(AuthContext);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showComposer, setShowComposer] = useState(false);
  const [userMood, setUserMood] = useState("happy");

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const res = await axios.get(`${API}/posts`);
      setPosts(res.data);
    } catch (error) {
      toast.error("Failed to load posts");
    } finally {
      setLoading(false);
    }
  };

  const handlePostCreated = (newPost) => {
    setPosts([newPost, ...posts]);
    setShowComposer(false);
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

  const handleDelete = async (postId) => {
    if (!window.confirm("Are you sure you want to delete this post?")) {
      return;
    }

    try {
      await axios.delete(`${API}/posts/${postId}`);
      setPosts(posts.filter(p => p.id !== postId));
      toast.success("Post deleted successfully");
    } catch (error) {
      toast.error("Failed to delete post");
    }
  };

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="max-w-2xl mx-auto">
        <TopHeader title="Timeline" subtitle="What's happening now" />

        {/* User Status Bar */}
        <div className="px-4 py-3 flex items-center justify-between gap-3">
          <MoodSelector currentMood={userMood} onMoodChange={setUserMood} />
          <StreakCounter />
        </div>

        {/* Live Activity Feed */}
        <LiveActivityFeed />

        {/* AI Quick Actions */}
        <div className="px-4 mt-2">
          <div className="glass-card p-4 rounded-2xl">
            <p className="text-sm text-gray-300 mb-2">AI Quick Actions</p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={async () => {
                  const text = prompt('Enter text to check for safety');
                  if (!text) return;
                  const res = await emergentApi.safety(text);
                  toast.info(res.safe ? 'Looks safe ✅' : `Flagged ❗ Categories: ${res.categories?.join(', ')}`);
                }}
                className="px-3 py-2 rounded-full bg-red-400/20 text-red-300 border border-red-500/30 text-xs"
               data-testid="btn-ai-safety">Safety Check</button>
              <button
                onClick={async () => {
                  const text = prompt('Enter text to translate');
                  if (!text) return;
                  const target = prompt('Target language code (e.g., hi, en, es)') || 'en';
                  const res = await emergentApi.translate(text, target);
                  toast.success(res.translated_text || 'No result');
                }}
                className="px-3 py-2 rounded-full bg-cyan-400/20 text-cyan-300 border border-cyan-500/30 text-xs"
               data-testid="btn-ai-translate">Translate</button>
              <button
                onClick={async () => {
                  const query = prompt('Enter ranking query');
                  const docsRaw = prompt('Enter documents (comma separated)');
                  if (!query || !docsRaw) return;
                  const docs = docsRaw.split(',').map(s => s.trim());
                  const res = await emergentApi.rank(query, docs);
                  toast.message('Ranking Done', { description: JSON.stringify(res.items).slice(0, 160) + '…' });
                }}
                className="px-3 py-2 rounded-full bg-purple-400/20 text-purple-300 border border-purple-500/30 text-xs"
               data-testid="btn-ai-rank">Rank</button>
              <button
                onClick={async () => {
                  const text = prompt('Enter text for insights or summary');
                  if (!text) return;
                  const res = await emergentApi.insight(text, 'summarize');
                  toast.message('Insights', { description: (res.result || '').slice(0, 180) + '…' });
                }}
                className="px-3 py-2 rounded-full bg-yellow-400/20 text-yellow-300 border border-yellow-500/30 text-xs"
               data-testid="btn-ai-insights">Insights</button>
            </div>
          </div>
        </div>
        {/* Guided Tours Launcher */}
        <div className="px-4 mt-2">
          <p className="text-xs text-gray-500 mb-1">Need a quick walkthrough?</p>
        </div>

        {/* Guided Tours Widget */}
        <GuidedTours />

        {/* Posts Feed */}
        <div className="space-y-4 px-4 mt-4">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mx-auto"></div>
            </div>
          ) : posts.length === 0 ? (
            <div className="text-center py-12 glass-card p-8">
              <p className="text-gray-400">No posts yet. Be the first to post!</p>
            </div>
          ) : (
            posts.map(post => (
              <PostCard
                key={post.id}
                post={post}
                currentUser={currentUser}
                onLike={handleLike}
                onRepost={handleRepost}
                onDelete={handleDelete}
              />
            ))
          )}
        </div>
      </div>

      <CreateFAB onClick={() => setShowComposer(true)} />
      <BottomNav active="home" />

      {showComposer && (
        <ComposerModal
          currentUser={currentUser}
          onClose={() => setShowComposer(false)}
          onPostCreated={handlePostCreated}
        />
      )}
    </div>
  );
};

export default Home;