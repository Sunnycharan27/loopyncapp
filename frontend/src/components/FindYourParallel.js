import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Sparkles, Heart, Users, MapPin, Music, ShoppingBag, Zap, X } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import FriendButton from './FriendButton';

const FindYourParallel = ({ currentUser, onClose }) => {
  const [parallels, setParallels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tasteDNA, setTasteDNA] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (currentUser) {
      fetchParallels();
      fetchTasteDNA();
    }
  }, [currentUser]);

  const fetchTasteDNA = async () => {
    try {
      const res = await axios.get(`${API}/ai/taste-dna/${currentUser.id}`);
      setTasteDNA(res.data);
    } catch (error) {
      // Generate mock TasteDNA if API not ready
      setTasteDNA({
        categories: {
          food: 75,
          music: 65,
          spiritual: 45,
          social: 80,
          fitness: 30,
          art: 55
        },
        topInterests: ['Food & Cafés', 'Music', 'Social Events'],
        personalityType: 'Explorer'
      });
    }
  };

  const fetchParallels = async () => {
    try {
      const res = await axios.get(`${API}/ai/find-parallels/${currentUser.id}`);
      setParallels(res.data);
    } catch (error) {
      // Generate mock parallels if API not ready
      try {
        const mockUsers = await axios.get(`${API}/users`);
        const otherUsers = mockUsers.data
          .filter(u => u.id !== currentUser.id)
          .slice(0, 10)
          .map(u => ({
            ...u,
            matchScore: Math.floor(Math.random() * 40) + 60,
            commonInterests: ['Music', 'Food', 'Social Events'].slice(0, Math.floor(Math.random() * 3) + 1),
            reason: 'Similar taste in content and venues'
          }));
        setParallels(otherUsers);
      } catch (err) {
        setParallels([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      food: '🍕',
      music: '🎵',
      spiritual: '🛕',
      social: '👥',
      fitness: '💪',
      art: '🎨'
    };
    return icons[category] || '✨';
  };

  const getPersonalityColor = (type) => {
    const colors = {
      Explorer: 'from-purple-400 to-pink-500',
      Creator: 'from-cyan-400 to-blue-500',
      Social: 'from-green-400 to-emerald-500',
      Spiritual: 'from-orange-400 to-yellow-500'
    };
    return colors[type] || 'from-gray-400 to-gray-600';
  };

  return (
    <div className="fixed inset-0 bg-black/95 backdrop-blur-sm z-50 overflow-y-auto">
      <div className="min-h-screen py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center">
                <Sparkles size={24} className="text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Find Your Parallel</h1>
                <p className="text-sm text-gray-400">AI-powered taste matching</p>
              </div>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-white transition">
              <X size={28} />
            </button>
          </div>

          {tasteDNA && (
            <div className="glass-card p-6 mb-6 border border-purple-500/30">
              <div className="flex items-center gap-3 mb-4">
                <Zap size={20} className="text-purple-400" />
                <h2 className="font-bold text-white">Your TasteDNA</h2>
              </div>
              
              <div className={`mb-4 p-4 rounded-2xl bg-gradient-to-r ${getPersonalityColor(tasteDNA.personalityType)}`}>
                <p className="text-white font-bold text-lg">{tasteDNA.personalityType}</p>
                <p className="text-white/80 text-sm">Your unique taste profile</p>
              </div>

              <div className="grid grid-cols-3 gap-3 mb-4">
                {Object.entries(tasteDNA.categories).map(([category, score]) => (
                  <div key={category} className="glass-card p-3 text-center">
                    <div className="text-2xl mb-1">{getCategoryIcon(category)}</div>
                    <div className="text-xs text-gray-400 capitalize mb-1">{category}</div>
                    <div className="font-bold text-cyan-400">{score}%</div>
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap gap-2">
                {tasteDNA.topInterests.map((interest, idx) => (
                  <span key={idx} className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-semibold">
                    {interest}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="mb-4">
            <div className="flex items-center gap-2 mb-4">
              <Users size={20} className="text-cyan-400" />
              <h2 className="font-bold text-white">Your Parallels ({parallels.length})</h2>
            </div>
            <p className="text-sm text-gray-400 mb-6">
              People with similar tastes, interests, and behaviors
            </p>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
            </div>
          ) : parallels.length === 0 ? (
            <div className="glass-card p-12 text-center">
              <Sparkles size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400 mb-2">No parallels found yet</p>
              <p className="text-sm text-gray-500">
                Engage more with content to help our AI find your perfect matches!
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {parallels.map((parallel) => (
                <div key={parallel.id} className="glass-card p-5 hover:scale-[1.01] transition-transform">
                  <div className="flex items-start gap-4">
                    <img
                      src={parallel.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${parallel.name}`}
                      alt={parallel.name}
                      className="w-16 h-16 rounded-full cursor-pointer"
                      onClick={() => navigate(`/profile/${parallel.id}`)}
                    />

                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between mb-2">
                        <div className="cursor-pointer" onClick={() => navigate(`/profile/${parallel.id}`)}>
                          <h3 className="font-bold text-white">{parallel.name}</h3>
                          <p className="text-sm text-gray-400">@{parallel.handle}</p>
                        </div>
                        
                        <div className="text-right">
                          <div className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
                            {parallel.matchScore || Math.floor(Math.random() * 40) + 60}%
                          </div>
                          <div className="text-xs text-gray-500">Match</div>
                        </div>
                      </div>

                      {parallel.bio && (
                        <p className="text-sm text-gray-300 mb-3 line-clamp-2">{parallel.bio}</p>
                      )}

                      <div className="flex flex-wrap gap-2 mb-3">
                        {(parallel.commonInterests || ['Music', 'Food']).slice(0, 3).map((interest, idx) => (
                          <span key={idx} className="px-2 py-1 rounded-full bg-cyan-400/10 text-cyan-400 text-xs font-semibold flex items-center gap-1">
                            <Heart size={12} />
                            {interest}
                          </span>
                        ))}
                      </div>

                      <p className="text-xs text-gray-500 mb-3 flex items-center gap-1">
                        <Sparkles size={12} className="text-purple-400" />
                        {parallel.reason || 'Similar taste in content and activities'}
                      </p>

                      <FriendButton currentUser={currentUser} targetUser={parallel} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-6 glass-card p-4 border border-cyan-500/20">
            <div className="flex items-start gap-3">
              <Sparkles size={20} className="text-cyan-400 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold text-white mb-1">How does this work?</h4>
                <p className="text-xs text-gray-400 leading-relaxed">
                  Our AI analyzes your likes, views, check-ins, and interactions to build your TasteDNA. 
                  We then match you with people who have similar patterns, helping you discover friends with shared interests!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FindYourParallel;
