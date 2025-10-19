import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import CreateFAB from "../components/CreateFAB";
import ReelViewer from "../components/ReelViewer";
import ReelComposerModal from "../components/ReelComposerModal";
import { toast } from "sonner";

const VibeZone = () => {
  const { currentUser } = useContext(AuthContext);
  const [reels, setReels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showComposer, setShowComposer] = useState(false);

  useEffect(() => {
    fetchReels();
  }, []);

  const fetchReels = async () => {
    try {
      const res = await axios.get(`${API}/reels`);
      setReels(res.data);
    } catch (error) {
      toast.error("Failed to load reels");
    } finally {
      setLoading(false);
    }
  };

  const handleReelCreated = (newReel) => {
    setReels([newReel, ...reels]);
    setShowComposer(false);
  };

  const handleLike = async (reelId) => {
    try {
      const res = await axios.post(`${API}/reels/${reelId}/like?userId=${currentUser.id}`);
      setReels(reels.map(r => {
        if (r.id === reelId) {
          const liked = res.data.action === "liked";
          return {
            ...r,
            stats: { ...r.stats, likes: res.data.likes },
            likedBy: liked
              ? [...(r.likedBy || []), currentUser.id]
              : (r.likedBy || []).filter(id => id !== currentUser.id)
          };
        }
        return r;
      }));
    } catch (error) {
      toast.error("Failed to like reel");
    }
  };

  return (
    <div className="min-h-screen" style={{ background: '#0f021e' }}>
      {loading ? (
        <div className="flex items-center justify-center h-screen">
          <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
        </div>
      ) : reels.length === 0 ? (
        <div className="flex items-center justify-center h-screen">
          <div className="text-center glass-card p-8">
            <p className="text-gray-400 mb-4">No reels yet. Create the first one!</p>
            <button onClick={() => setShowComposer(true)} className="btn-primary">
              Create Reel
            </button>
          </div>
        </div>
      ) : (
        <ReelViewer reels={reels} currentUser={currentUser} onLike={handleLike} />
      )}

      <CreateFAB onClick={() => setShowComposer(true)} type="reel" />
      <BottomNav active="vibezone" />

      {showComposer && (
        <ReelComposerModal
          currentUser={currentUser}
          onClose={() => setShowComposer(false)}
          onReelCreated={handleReelCreated}
        />
      )}
    </div>
  );
};

export default VibeZone;