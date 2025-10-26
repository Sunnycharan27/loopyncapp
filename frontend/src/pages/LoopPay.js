import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { 
  ArrowLeft, Zap, Plus, Gift, Clock, TrendingUp, Award,
  ShoppingBag, Ticket, MessageCircle, Film, Users, X
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const LoopPay = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [walletBalance, setWalletBalance] = useState(0); // Money balance
  const [loopCredits, setLoopCredits] = useState(0); // Reward credits
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [vibeRank, setVibeRank] = useState("Bronze");
  const [showRedeemModal, setShowRedeemModal] = useState(false);
  const [showAddMoneyModal, setShowAddMoneyModal] = useState(false);
  const [showAddCreditsModal, setShowAddCreditsModal] = useState(false);
  const [addMoneyAmount, setAddMoneyAmount] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("upi"); // upi, card, netbanking
  const [earnedThisWeek, setEarnedThisWeek] = useState(0);
  const [spentThisWeek, setSpentThisWeek] = useState(0);

  useEffect(() => {
    fetchWalletData();
  }, []);

  const fetchWalletData = async () => {
    try {
      setLoading(true);
      const [creditsRes, walletRes] = await Promise.all([
        axios.get(`${API}/credits/${currentUser.id}`),
        axios.get(`${API}/wallet?userId=${currentUser.id}`)
      ]);
      
      setLoopCredits(creditsRes.data?.credits || 0);
      setWalletBalance(walletRes.data?.balance || 0);
      setTransactions(walletRes.data?.transactions || []);
      
      // Calculate weekly stats
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      
      let earned = 0;
      let spent = 0;
      
      (walletRes.data?.transactions || []).forEach(txn => {
        if (new Date(txn.createdAt) > weekAgo) {
          if (txn.type === 'topup') earned += txn.amount;
          else spent += txn.amount;
        }
      });
      
      setEarnedThisWeek(earned);
      setSpentThisWeek(spent);
      
      // Set rank based on credits
      const credits = creditsRes.data?.credits || 0;
      if (credits >= 1000) setVibeRank("Aurora");
      else if (credits >= 500) setVibeRank("Gold");
      else if (credits >= 200) setVibeRank("Silver");
      else setVibeRank("Bronze");
      
    } catch (error) {
      console.error('Failed to fetch wallet data:', error);
    } finally {
      setLoading(false);
    }
  };

  const redeemOptions = [
    { id: 1, icon: ShoppingBag, title: "₹50 Off Café", cost: 100, color: "from-cyan-400 to-blue-500" },
    { id: 2, icon: Ticket, title: "Event Pass", cost: 150, color: "from-purple-400 to-pink-500" },
    { id: 3, icon: Film, title: "Feature Post 24h", cost: 200, color: "from-yellow-400 to-orange-500" },
    { id: 4, icon: Users, title: "Tribe Boost", cost: 250, color: "from-green-400 to-emerald-500" }
  ];

  const handleRedeem = (option) => {
    if (loopCredits >= option.cost) {
      setLoopCredits(loopCredits - option.cost);
      toast.success(`${option.title} redeemed!`);
      setShowRedeemModal(false);
    } else {
      toast.error("Not enough credits");
    }
  };

  const handleAddMoney = async () => {
    if (!addMoneyAmount || parseFloat(addMoneyAmount) <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    try {
      toast.loading(`Processing via ${paymentMethod.toUpperCase()}...`);
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      await axios.post(`${API}/wallet/topup?userId=${currentUser.id}`, {
        amount: parseFloat(addMoneyAmount)
      });
      
      toast.dismiss();
      toast.success(`₹${addMoneyAmount} added to wallet!`);
      setShowAddMoneyModal(false);
      setAddMoneyAmount("");
      fetchWalletData();
    } catch (error) {
      toast.dismiss();
      toast.error("Payment failed");
    }
  };

  const handleAddCredits = () => {
    // Mock adding credits (normally earned through activities)
    setLoopCredits(loopCredits + 100);
    toast.success("100 credits added!");
    setShowAddCreditsModal(false);
    fetchWalletData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0F021E] to-[#121427] flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-[#00E0FF] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F021E] to-[#121427] pb-24">
      {/* Header */}
      <div className="sticky top-0 z-10 backdrop-blur-xl bg-[#0F021E]/80 border-b border-white/10 p-4">
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-white/5 rounded-lg transition-all"
          >
            <ArrowLeft size={24} className="text-white" />
          </button>
          <h1 className="text-xl font-bold text-white">Loop Credits</h1>
          <div className="w-10"></div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Balance Card */}
        <div className="relative overflow-hidden rounded-3xl p-6 backdrop-blur-xl bg-white/5 border border-white/10 shadow-2xl">
          {/* Animated particles background */}
          <div className="absolute inset-0 overflow-hidden">
            {[...Array(10)].map((_, i) => (
              <div
                key={i}
                className="absolute w-1 h-1 bg-[#00E0FF] rounded-full animate-pulse"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 3}s`,
                  animationDuration: `${2 + Math.random() * 3}s`
                }}
              />
            ))}
          </div>
          
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <img
                  src={currentUser.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser.name}`}
                  alt={currentUser.name}
                  className="w-12 h-12 rounded-full border-2 border-[#00E0FF]/50"
                />
                <div>
                  <p className="text-white font-semibold">{currentUser.name}</p>
                  <p className="text-white/60 text-sm">@{currentUser.handle}</p>
                </div>
              </div>
              <div className="px-4 py-1.5 rounded-full bg-gradient-to-r from-[#00E0FF]/20 to-[#5AFF9C]/20 border border-[#00E0FF]/30">
                <p className="text-[#00E0FF] text-xs font-bold">{vibeRank}</p>
              </div>
            </div>

            <div className="mb-2">
              <p className="text-white/60 text-sm mb-1">Your Balance</p>
              <div className="flex items-baseline gap-2">
                <h2 className="text-5xl font-bold text-white">{loopCredits}</h2>
                <Zap size={32} className="text-[#5AFF9C]" />
              </div>
            </div>

            <p className="text-white/40 text-xs">Loop Credits</p>
          </div>

          {/* Glow effect */}
          <div className="absolute -top-20 -right-20 w-40 h-40 bg-[#00E0FF]/20 rounded-full blur-3xl"></div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-3 gap-3">
          <button
            onClick={() => setShowAddModal(true)}
            className="p-4 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all group"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-r from-[#5AFF9C]/20 to-[#00E0FF]/20 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Plus size={24} className="text-[#5AFF9C]" />
            </div>
            <p className="text-white text-sm font-semibold">Add</p>
          </button>

          <button
            onClick={() => setShowRedeemModal(true)}
            className="p-4 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all group"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-r from-[#FF3DB3]/20 to-[#00E0FF]/20 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Gift size={24} className="text-[#FF3DB3]" />
            </div>
            <p className="text-white text-sm font-semibold">Redeem</p>
          </button>

          <button
            onClick={() => navigate('/wallet/history')}
            className="p-4 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all group"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-r from-[#00E0FF]/20 to-[#FF3DB3]/20 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Clock size={24} className="text-[#00E0FF]" />
            </div>
            <p className="text-white text-sm font-semibold">History</p>
          </button>
        </div>

        {/* Insights */}
        <div className="p-6 rounded-3xl backdrop-blur-xl bg-white/5 border border-white/10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-bold">This Week</h3>
            <TrendingUp size={20} className="text-[#00E0FF]" />
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#5AFF9C]"></div>
                <span className="text-white/60 text-sm">Earned</span>
              </div>
              <span className="text-[#5AFF9C] font-bold">+{earnedThisWeek}</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#FF3DB3]"></div>
                <span className="text-white/60 text-sm">Spent</span>
              </div>
              <span className="text-[#FF3DB3] font-bold">-{spentThisWeek}</span>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-4 h-2 bg-white/10 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-[#5AFF9C] to-[#00E0FF]"
              style={{ width: `${Math.min((earnedThisWeek / (earnedThisWeek + spentThisWeek)) * 100, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Recent Transactions */}
        <div>
          <h3 className="text-white font-bold mb-3 px-2">Recent Activity</h3>
          {transactions.length > 0 ? (
            <div className="space-y-2">
              {transactions.slice(0, 5).map((txn, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        txn.type === 'topup' ? 'bg-[#5AFF9C]/20' : 'bg-[#FF3DB3]/20'
                      }`}>
                        {txn.type === 'topup' ? (
                          <Plus size={20} className="text-[#5AFF9C]" />
                        ) : (
                          <Gift size={20} className="text-[#FF3DB3]" />
                        )}
                      </div>
                      <div>
                        <p className="text-white text-sm font-semibold">{txn.description}</p>
                        <p className="text-white/40 text-xs">
                          {new Date(txn.createdAt).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                    <span className={`font-bold ${
                      txn.type === 'topup' ? 'text-[#5AFF9C]' : 'text-[#FF3DB3]'
                    }`}>
                      {txn.type === 'topup' ? '+' : '-'}{txn.amount}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 text-center">
              <Clock size={48} className="mx-auto mb-3 text-white/20" />
              <p className="text-white/40 text-sm">No transactions yet</p>
            </div>
          )}
        </div>
      </div>

      {/* Add Credits Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md rounded-3xl backdrop-blur-xl bg-[#0F021E]/90 border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Add Credits</h3>
              <button onClick={() => setShowAddModal(false)} className="text-white/60 hover:text-white">
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              <div className="text-center p-8 rounded-2xl bg-white/5 border border-white/10">
                <Zap size={48} className="mx-auto mb-3 text-[#00E0FF]" />
                <p className="text-white/60 text-sm mb-2">Mock Transaction</p>
                <p className="text-white text-lg font-bold">+100 Credits</p>
              </div>

              <button
                onClick={handleAddCredits}
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-[#00E0FF] to-[#5AFF9C] text-black font-bold hover:opacity-90 transition-all"
              >
                Add Credits
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Redeem Modal */}
      {showRedeemModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md rounded-3xl backdrop-blur-xl bg-[#0F021E]/90 border border-white/10 p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Redeem Rewards</h3>
              <button onClick={() => setShowRedeemModal(false)} className="text-white/60 hover:text-white">
                <X size={24} />
              </button>
            </div>

            <div className="grid grid-cols-1 gap-3">
              {redeemOptions.map(option => (
                <button
                  key={option.id}
                  onClick={() => handleRedeem(option)}
                  disabled={loopCredits < option.cost}
                  className={`p-4 rounded-2xl backdrop-blur-xl border transition-all ${
                    loopCredits >= option.cost
                      ? 'bg-white/5 border-white/10 hover:bg-white/10'
                      : 'bg-white/5 border-white/5 opacity-50 cursor-not-allowed'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-full bg-gradient-to-r ${option.color} flex items-center justify-center`}>
                      <option.icon size={24} className="text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="text-white font-semibold">{option.title}</p>
                      <p className="text-white/60 text-sm">{option.cost} credits</p>
                    </div>
                    <div className="text-right">
                      <Award size={20} className="text-[#00E0FF]" />
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <BottomNav active="discover" />
    </div>
  );
};

export default LoopPay;
