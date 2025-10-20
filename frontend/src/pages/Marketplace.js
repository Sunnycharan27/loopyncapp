import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useNavigate } from "react-router-dom";
import BottomNav from "../components/BottomNav";
import TopHeader from "../components/TopHeader";
import { Star, Users, Download, Lock, Unlock, BookOpen, Video, Package, ShoppingBag } from "lucide-react";
import { toast } from "sonner";

const Marketplace = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [creators, setCreators] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [userCredits, setUserCredits] = useState(0);

  const categories = [
    { id: "all", name: "All", icon: <Package size={16} /> },
    { id: "courses", name: "Courses", icon: <BookOpen size={16} /> },
    { id: "ebooks", name: "eBooks", icon: <BookOpen size={16} /> },
    { id: "videos", name: "Videos", icon: <Video size={16} /> },
    { id: "merch", name: "Merch", icon: <ShoppingBag size={16} /> }
  ];

  useEffect(() => {
    fetchMarketplace();
    fetchUserCredits();
  }, []);

  const fetchMarketplace = async () => {
    try {
      const res = await axios.get(`${API}/creators`);
      setCreators(res.data);
      
      // Generate sample courses from creators
      const sampleCourses = res.data.flatMap(creator => [
        {
          id: `course-${creator.id}-1`,
          creatorId: creator.userId,
          creator: creator,
          title: `${creator.displayName}'s Masterclass`,
          description: `Learn the secrets of success from ${creator.displayName}`,
          price: 200,
          type: "courses",
          rating: (4 + Math.random()).toFixed(1),
          students: Math.floor(Math.random() * 500) + 50,
          thumbnail: creator.avatar,
          isPurchased: false
        },
        {
          id: `course-${creator.id}-2`,
          creatorId: creator.userId,
          creator: creator,
          title: `Advanced Guide by ${creator.displayName}`,
          description: `Deep dive into advanced techniques`,
          price: 350,
          type: "courses",
          rating: (4 + Math.random()).toFixed(1),
          students: Math.floor(Math.random() * 300) + 20,
          thumbnail: creator.avatar,
          isPurchased: false
        }
      ]);
      
      setCourses(sampleCourses);
    } catch (error) {
      toast.error("Failed to load marketplace");
    } finally {
      setLoading(false);
    }
  };

  const fetchUserCredits = async () => {
    try {
      const res = await axios.get(`${API}/credits/${currentUser.id}`);
      setUserCredits(res.data.balance);
    } catch (error) {
      console.error("Failed to fetch credits");
    }
  };

  const handlePurchase = async (course) => {
    if (userCredits < course.price) {
      toast.error(`Insufficient credits! You need ${course.price} credits but have ${userCredits}`);
      return;
    }

    try {
      // Deduct credits
      await axios.post(`${API}/credits/spend`, null, {
        params: {
          userId: currentUser.id,
          amount: course.price,
          source: 'marketplace',
          description: `Purchased: ${course.title}`
        }
      });

      toast.success(`🎉 Course unlocked! ${course.price} credits spent`);
      
      // Update local state
      setUserCredits(userCredits - course.price);
      setCourses(courses.map(c => 
        c.id === course.id ? { ...c, isPurchased: true } : c
      ));
    } catch (error) {
      toast.error("Purchase failed. Please try again.");
    }
  };

  const filteredCourses = selectedCategory === "all" 
    ? courses 
    : courses.filter(c => c.type === selectedCategory);

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <TopHeader title="Marketplace" subtitle="Courses, eBooks & More" />

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Credits Balance */}
        <div className="glass-card p-4 mb-6 flex items-center justify-between">
          <div>
            <p className="text-gray-400 text-sm">Your Loop Credits</p>
            <p className="text-3xl font-bold text-cyan-400">{userCredits}</p>
          </div>
          <button
            onClick={() => navigate('/wallet')}
            className="px-4 py-2 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white text-sm font-semibold"
          >
            Earn More
          </button>
        </div>

        {/* Categories */}
        <div className="flex gap-2 overflow-x-auto pb-4 mb-6 scrollbar-hide">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-full font-medium text-sm transition-all ${
                selectedCategory === cat.id
                  ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
              }`}
            >
              {cat.icon}
              {cat.name}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full mx-auto"></div>
          </div>
        ) : (
          <>
            {/* Courses Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredCourses.map((course) => (
                <div
                  key={course.id}
                  className="glass-card p-4 hover:scale-[1.02] transition-transform"
                >
                  {/* Course Thumbnail */}
                  <div className="relative h-40 rounded-xl overflow-hidden mb-4">
                    <img
                      src={course.thumbnail}
                      alt={course.title}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
                    <div className="absolute top-3 right-3">
                      {course.isPurchased ? (
                        <div className="px-3 py-1 rounded-full bg-green-500/20 border border-green-400 backdrop-blur-sm">
                          <Unlock size={16} className="inline text-green-400 mr-1" />
                          <span className="text-green-400 text-xs font-semibold">Owned</span>
                        </div>
                      ) : (
                        <div className="px-3 py-1 rounded-full bg-yellow-500/20 border border-yellow-400 backdrop-blur-sm">
                          <span className="text-yellow-400 text-sm font-bold">{course.price} 💰</span>
                        </div>
                      )}
                    </div>
                    <div className="absolute bottom-3 left-3 right-3">
                      <p className="text-white font-semibold line-clamp-1">{course.title}</p>
                    </div>
                  </div>

                  {/* Creator Info */}
                  <div className="flex items-center gap-2 mb-3">
                    <img
                      src={course.creator.avatar}
                      alt={course.creator.displayName}
                      className="w-8 h-8 rounded-full"
                    />
                    <div className="flex-1">
                      <p className="text-sm text-white font-medium">{course.creator.displayName}</p>
                      <p className="text-xs text-gray-400">{course.creator.followers} followers</p>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-gray-400 mb-3 line-clamp-2">{course.description}</p>

                  {/* Stats */}
                  <div className="flex items-center gap-4 mb-4 text-sm text-gray-400">
                    <div className="flex items-center gap-1">
                      <Star size={14} className="text-yellow-400" fill="currentColor" />
                      <span>{course.rating}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Users size={14} />
                      <span>{course.students}</span>
                    </div>
                  </div>

                  {/* Action Button */}
                  {course.isPurchased ? (
                    <button className="w-full py-2 rounded-full bg-gray-800 text-gray-400 font-semibold cursor-not-allowed">
                      Already Purchased
                    </button>
                  ) : (
                    <button
                      onClick={() => handlePurchase(course)}
                      className="w-full py-2 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold hover:opacity-90"
                    >
                      <Lock size={16} className="inline mr-2" />
                      Unlock for {course.price} Credits
                    </button>
                  )}
                </div>
              ))}
            </div>

            {filteredCourses.length === 0 && (
              <div className="text-center py-12 glass-card">
                <Package size={48} className="text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No items found in this category</p>
              </div>
            )}
          </>
        )}

        {/* Become a Creator CTA */}
        <div className="mt-8 glass-card p-6 text-center">
          <h3 className="text-xl font-bold text-white mb-2">Want to sell your content?</h3>
          <p className="text-gray-400 mb-4">Join as a creator and earn Loop Credits</p>
          <button className="px-6 py-3 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold">
            Become a Creator
          </button>
        </div>
      </div>

      <BottomNav active="discover" />
    </div>
  );
};

export default Marketplace;
