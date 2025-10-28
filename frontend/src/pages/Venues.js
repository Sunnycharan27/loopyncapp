import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useNavigate } from "react-router-dom";
import BottomNav from "../components/BottomNav";
import TopHeader from "../components/TopHeader";
import { MapPin, Star, Clock, Search, Filter } from "lucide-react";
import { toast } from "sonner";

const Venues = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const categories = [
    { id: "all", name: "All", icon: "🏪" },
    { id: "cafe", name: "Cafés", icon: "☕" },
    { id: "restaurant", name: "Restaurants", icon: "🍽️" },
    { id: "pub", name: "Pubs & Bars", icon: "🍺" },
    { id: "temple", name: "Temples", icon: "🛕" },
    { id: "mosque", name: "Mosques", icon: "🕌" },
    { id: "spiritual", name: "Spiritual", icon: "🙏" },
    { id: "park", name: "Parks", icon: "🌳" },
  ];

  // Check if venue is a spiritual/religious place (no menu)
  const isSpiritualPlace = (venue) => {
    const spiritualKeywords = ['temple', 'mosque', 'church', 'gurudwara', 'monastery', 'shrine', 'mandir', 'masjid'];
    const venueName = venue.name.toLowerCase();
    const venueCategory = venue.category?.toLowerCase() || '';
    
    return spiritualKeywords.some(keyword => 
      venueName.includes(keyword) || venueCategory.includes(keyword)
    );
  };

  useEffect(() => {
    fetchVenues();
  }, []);

  const fetchVenues = async () => {
    try {
      const res = await axios.get(`${API}/venues`);
      setVenues(res.data);
    } catch (error) {
      toast.error("Failed to load venues");
    } finally {
      setLoading(false);
    }
  };

  const filteredVenues = venues.filter((venue) => {
    const matchesSearch = venue.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         venue.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "all" || 
                           venue.name.toLowerCase().includes(selectedCategory);
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <TopHeader title="Nearby Venues" subtitle="Discover amazing places" />

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Search Bar */}
        <div className="relative mb-6">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search venues, locations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-gray-900/50 border border-cyan-400/30 rounded-full focus:border-cyan-400 focus:outline-none text-white"
          />
        </div>

        {/* Categories */}
        <div className="flex gap-2 overflow-x-auto pb-4 mb-6 scrollbar-hide">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`flex-shrink-0 px-4 py-2 rounded-full font-medium text-sm transition-all ${
                selectedCategory === cat.id
                  ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
              }`}
            >
              <span className="mr-2">{cat.icon}</span>
              {cat.name}
            </button>
          ))}
        </div>

        {/* Venues Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full mx-auto"></div>
          </div>
        ) : filteredVenues.length === 0 ? (
          <div className="text-center py-12 glass-card">
            <p className="text-gray-400">No venues found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredVenues.map((venue) => (
              <div
                key={venue.id}
                onClick={() => navigate(`/venues/${venue.id}`)}
                className="glass-card p-4 cursor-pointer hover:scale-[1.02] transition-transform"
              >
                {/* Venue Image */}
                <div className="relative h-48 rounded-2xl overflow-hidden mb-4">
                  <img
                    src={venue.avatar || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400'}
                    alt={venue.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-3 right-3 px-3 py-1 rounded-full bg-black/50 backdrop-blur-sm flex items-center gap-1">
                    <Star size={14} className="text-yellow-400" fill="currentColor" />
                    <span className="text-white text-sm font-semibold">{venue.rating || 4.5}</span>
                  </div>
                </div>

                {/* Venue Info */}
                <h3 className="font-bold text-lg text-white mb-2 neon-text">{venue.name}</h3>
                
                <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
                  <MapPin size={14} />
                  <span>{venue.location}</span>
                </div>

                {venue.description && (
                  <p className="text-gray-400 text-sm line-clamp-2 mb-3">
                    {venue.description}
                  </p>
                )}

                {/* Opening Hours/Timings */}
                {venue.timings && (
                  <div className="flex items-center gap-2 text-gray-400 text-sm mb-3">
                    <Clock size={14} />
                    <span>{venue.timings}</span>
                  </div>
                )}

                {/* Quick Actions - All venues show More Information */}
                <div className="flex gap-2">
                  <button className="flex-1 py-2 px-3 rounded-full bg-cyan-400/10 text-cyan-400 text-sm font-medium hover:bg-cyan-400/20">
                    More Information
                  </button>
                  <button className="flex-1 py-2 px-3 rounded-full bg-purple-400/10 text-purple-400 text-sm font-medium hover:bg-purple-400/20">
                    Get Directions
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <BottomNav active="discover" />
    </div>
  );
};

export default Venues;
