import React, { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { 
  Settings, Grid, Users, Ticket, Edit3, Camera, X, Check, Phone, Video, MessageCircle, ShoppingBag
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const ProfileVibe = () => {
  const { currentUser, setCurrentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState("posts");
  const [userPosts, setUserPosts] = useState([]);
  const [userTribes, setUserTribes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userTickets, setUserTickets] = useState([]);
  const [marketplaceItems, setMarketplaceItems] = useState([]);
  const [loopCredits, setLoopCredits] = useState(0);
  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState("");
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const avatarInputRef = useRef(null);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      const [postsRes, tribesRes, creditsRes, ticketsRes] = await Promise.all([
        axios.get(`${API}/posts`),
        axios.get(`${API}/tribes`),
        axios.get(`${API}/credits/${currentUser.id}`),
        axios.get(`${API}/tickets/${currentUser.id}`)
      ]);

      const myPosts = postsRes.data.filter(p => p.authorId === currentUser.id);
      const myTribes = tribesRes.data.filter(t => t.members?.includes(currentUser.id) || t.creatorId === currentUser.id);
      setUserPosts(myPosts);
      setUserTribes(myTribes);
      setLoopCredits(creditsRes.data?.credits || 0);
      setUserTickets(ticketsRes.data || []);
    } catch (error) {
      console.error("Failed to fetch profile data:", error);
      toast.error("Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !file.type.startsWith('image/')) {
      toast.error("Please upload an image file");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error("Image size should be less than 5MB");
      return;
    }
    setUploadingAvatar(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const uploadRes = await axios.post(`${API}/upload`, formData, { headers: { "Content-Type": "multipart/form-data" } });
      const avatarUrl = `${API}${uploadRes.data.url}`;
      await axios.patch(`${API}/users/${currentUser.id}/profile`, { avatar: avatarUrl });
      setCurrentUser({ ...currentUser, avatar: avatarUrl });
      toast.success("Profile picture updated!");
    } catch (error) {
      toast.error("Failed to upload profile picture");
    } finally {
      setUploadingAvatar(false);
    }
  };

  const handleNameEdit = async () => {
    if (!editedName.trim()) {
      toast.error("Name cannot be empty");
      return;
    }
    try {
      await axios.patch(`${API}/users/${currentUser.id}/profile`, { name: editedName });
      setCurrentUser({ ...currentUser, name: editedName });
      setIsEditingName(false);
      toast.success("Name updated!");
    } catch (error) {
      toast.error("Failed to update name");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen text-white pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="sticky top-0 z-10 glass-surface backdrop-blur-xl">
        <div className="max-w-2xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-white">Profile</h1>
          <button onClick={() => navigate("/settings")} className="p-2 rounded-xl hover:bg-white/10 transition-all">
            <Settings size={20} />
          </button>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-6 py-8 space-y-8">
        <div className="relative">
          <div className="flex items-center gap-6">
            <div className="relative group">
              <div className="w-24 h-24 rounded-full border-4 border-cyan-400/30 overflow-hidden bg-gray-800 shadow-lg shadow-cyan-400/20">
                <img src={currentUser.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser.name}`} alt={currentUser.name} className="w-full h-full object-cover" />
                <input type="file" ref={avatarInputRef} onChange={handleAvatarUpload} accept="image/*" className="hidden" />
                <button onClick={() => avatarInputRef.current?.click()} disabled={uploadingAvatar} className="absolute inset-0 bg-black/0 group-hover:bg-black/60 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                  {uploadingAvatar ? <div className="animate-spin w-6 h-6 border-4 border-white border-t-transparent rounded-full"></div> : <Camera size={20} className="text-white" />}
                </button>
              </div>
            </div>

            <div className="flex-1">
              {isEditingName ? (
                <div className="flex items-center gap-2 mb-2">
                  <input type="text" value={editedName} onChange={(e) => setEditedName(e.target.value)} className="text-2xl font-bold text-white bg-transparent border-b-2 border-cyan-400 focus:outline-none" autoFocus />
                  <button onClick={handleNameEdit} className="p-1 rounded bg-green-500/20 hover:bg-green-500/30"><Check size={16} className="text-green-400" /></button>
                  <button onClick={() => setIsEditingName(false)} className="p-1 rounded bg-red-500/20 hover:bg-red-500/30"><X size={16} className="text-red-400" /></button>
                </div>
              ) : (
                <div className="flex items-center gap-2 mb-2">
                  <h2 className="text-2xl font-bold text-white">{currentUser.name}</h2>
                  <button onClick={() => { setEditedName(currentUser.name); setIsEditingName(true); }} className="p-1 hover:bg-cyan-400/10 rounded transition-all">
                    <Edit3 size={16} className="text-cyan-400" />
                  </button>
                </div>
              )}
              <p className="text-cyan-400 text-sm mb-3">@{currentUser.handle}</p>
              <div className="flex items-center gap-6">
                <div className="text-center"><div className="text-lg font-bold text-white">{userPosts.length}</div><div className="text-xs text-gray-500">Posts</div></div>
                <div className="text-center"><div className="text-lg font-bold text-white">{currentUser.friends?.length || 0}</div><div className="text-xs text-gray-500">Friends</div></div>
                <div className="text-center"><div className="text-lg font-bold text-white">{userTribes.length}</div><div className="text-xs text-gray-500">Tribes</div></div>
              </div>
            </div>
          </div>

          {currentUser.bio && <p className="mt-4 text-gray-400 text-sm leading-relaxed">{currentUser.bio}</p>}

          <div className="flex items-center gap-2 mt-6">
            <button onClick={() => navigate("/messenger")} className="flex-1 py-2.5 rounded-xl bg-cyan-400/10 border border-cyan-400/30 text-cyan-400 font-semibold hover:bg-cyan-400/20 transition-all flex items-center justify-center gap-2">
              <MessageCircle size={18} />Message
            </button>
            <button className="flex-1 py-2.5 rounded-xl bg-purple-400/10 border border-purple-400/30 text-purple-400 font-semibold hover:bg-purple-400/20 transition-all flex items-center justify-center gap-2">
              <Phone size={18} />Call
            </button>
          </div>
        </div>

        <div className="flex gap-2 border-b border-gray-800">
          {[{ id: "posts", label: "Posts", icon: Grid }, { id: "tribes", label: "Tribes", icon: Users }, { id: "tickets", label: "Tickets", icon: Ticket }].map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center gap-2 px-4 py-3 font-semibold transition-all ${activeTab === tab.id ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-500 hover:text-gray-300'}`}>
              <tab.icon size={18} />{tab.label}
            </button>
          ))}
        </div>

        <div>
          {activeTab === "posts" && (
            <div className="grid grid-cols-3 gap-2">
              {userPosts.length > 0 ? userPosts.map((post) => (
                <div key={post.id} className="aspect-square rounded-xl overflow-hidden cursor-pointer hover:opacity-80 transition-all border border-gray-800 hover:border-cyan-400" onClick={() => navigate(`/post/${post.id}`)}>
                  {post.mediaUrl ? <img src={post.mediaUrl} alt="Post" className="w-full h-full object-cover" /> : <div className="w-full h-full bg-gray-900/50 flex items-center justify-center p-3"><p className="text-xs text-center text-gray-500 line-clamp-4">{post.text}</p></div>}
                </div>
              )) : (
                <div className="col-span-3 py-16 text-center">
                  <Grid size={48} className="mx-auto mb-4 text-gray-700" />
                  <p className="text-gray-500 mb-4">No posts yet</p>
                  <button onClick={() => navigate("/")} className="px-6 py-2.5 bg-cyan-400 hover:bg-cyan-500 text-black rounded-xl font-semibold transition-all">Create Post</button>
                </div>
              )}
            </div>
          )}

          {activeTab === "tribes" && (
            <div className="space-y-3">
              {userTribes.length > 0 ? userTribes.map(tribe => (
                <div key={tribe.id} className="p-4 rounded-xl bg-gray-900/30 border border-gray-800 hover:border-cyan-400/30 transition-all cursor-pointer" onClick={() => navigate(`/tribe/${tribe.id}`)}>
                  <div className="flex items-center justify-between">
                    <div><h3 className="font-semibold text-white mb-1">{tribe.name}</h3><p className="text-sm text-gray-500">{tribe.members?.length || 0} members</p></div>
                    <Users size={20} className="text-cyan-400" />
                  </div>
                </div>
              )) : <div className="py-16 text-center"><Users size={48} className="mx-auto mb-4 text-gray-700" /><p className="text-gray-500">No tribes joined yet</p></div>}
            </div>
          )}

          {activeTab === "tickets" && (
            <div className="space-y-3">
              {userTickets.length > 0 ? userTickets.map(ticket => (
                <div key={ticket.id} className="p-4 rounded-xl bg-gray-900/30 border border-gray-800">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex-1"><h3 className="font-semibold text-white mb-1">{ticket.event?.name || 'Event'}</h3><p className="text-sm text-gray-500">{ticket.event?.date || 'Date TBD'}</p></div>
                    {ticket.qrCodeImage && <div className="w-16 h-16 bg-white rounded-lg p-1"><img src={ticket.qrCodeImage} alt="QR" className="w-full h-full" /></div>}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 rounded-full bg-cyan-400/20 text-cyan-400 text-xs font-semibold">{ticket.tier}</span>
                    <span className="px-2 py-1 rounded-full bg-green-400/20 text-green-400 text-xs font-semibold">{ticket.status}</span>
                  </div>
                </div>
              )) : (
                <div className="py-16 text-center">
                  <Ticket size={48} className="mx-auto mb-4 text-gray-700" />
                  <p className="text-gray-500 mb-4">No tickets yet</p>
                  <button onClick={() => navigate('/discover')} className="px-6 py-2.5 bg-cyan-400 hover:bg-cyan-500 text-black rounded-xl font-semibold transition-all">Browse Events</button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <BottomNav active="profile" />
    </div>
  );
};

export default ProfileVibe;