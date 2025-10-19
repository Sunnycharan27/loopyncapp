import React, { useState, useEffect } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useContext } from "react";
import BottomNav from "../components/BottomNav";
import CreateFAB from "../components/CreateFAB";
import TribeCard from "../components/TribeCard";
import CreateTribeModal from "../components/CreateTribeModal";
import { toast } from "sonner";

const Tribes = () => {
  const { currentUser } = useContext(AuthContext);
  const [tribes, setTribes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchTribes();
  }, []);

  const fetchTribes = async () => {
    try {
      const res = await axios.get(`${API}/tribes`);
      setTribes(res.data);
    } catch (error) {
      toast.error("Failed to load tribes");
    } finally {
      setLoading(false);
    }
  };

  const handleTribeCreated = (newTribe) => {
    setTribes([newTribe, ...tribes]);
    setShowCreateModal(false);
  };

  const handleJoinLeave = async (tribeId, isMember) => {
    try {
      const endpoint = isMember ? "leave" : "join";
      const res = await axios.post(`${API}/tribes/${tribeId}/${endpoint}?userId=${currentUser.id}`);
      
      setTribes(tribes.map(t => {
        if (t.id === tribeId) {
          const newMembers = isMember
            ? t.members.filter(m => m !== currentUser.id)
            : [...t.members, currentUser.id];
          return { ...t, members: newMembers, memberCount: res.data.memberCount };
        }
        return t;
      }));
      
      toast.success(isMember ? "Left tribe" : "Joined tribe!");
    } catch (error) {
      toast.error("Action failed");
    }
  };

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="sticky top-0 z-10 glass-surface p-4 mb-6">
          <h1 className="text-2xl font-bold neon-text">Tribes</h1>
          <p className="text-sm text-gray-400">Find your community</p>
        </div>

        {/* Tribes Grid */}
        <div className="px-4">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mx-auto"></div>
            </div>
          ) : tribes.length === 0 ? (
            <div className="text-center py-12 glass-card p-8">
              <p className="text-gray-400 mb-4">No tribes yet. Create one!</p>
              <button onClick={() => setShowCreateModal(true)} className="btn-primary">
                Create Tribe
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {tribes.map(tribe => (
                <TribeCard
                  key={tribe.id}
                  tribe={tribe}
                  currentUser={currentUser}
                  onJoinLeave={handleJoinLeave}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      <CreateFAB onClick={() => setShowCreateModal(true)} type="tribe" />
      <BottomNav active="tribes" />

      {showCreateModal && (
        <CreateTribeModal
          currentUser={currentUser}
          onClose={() => setShowCreateModal(false)}
          onTribeCreated={handleTribeCreated}
        />
      )}
    </div>
  );
};

export default Tribes;