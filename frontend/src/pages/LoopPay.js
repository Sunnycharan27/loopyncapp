import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { 
  ArrowLeft, Zap, Plus, Gift, Clock, TrendingUp, Award,
  ShoppingBag, Ticket, Film, Users, X, CreditCard, Smartphone, Building
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
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      {/* Header */}
      <div className="sticky top-0 z-10 glass-surface p-4">
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-cyan-400/10 rounded-lg transition-all"
          >
            <ArrowLeft size={24} className="text-white" />
          </button>
          <h1 className="text-xl font-bold text-white">LoopPay Wallet</h1>
          <div className="w-10"></div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Money Balance Card */}
        <div className="relative overflow-hidden rounded-3xl p-6 glass-card">
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <img
                  src={currentUser.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser.name}`}
                  alt={currentUser.name}
                  className="w-12 h-12 rounded-full border-2 border-cyan-400/50"
                />
                <div>
                  <p className="text-white font-semibold">{currentUser.name}</p>
                  <p className="text-gray-400 text-sm">@{currentUser.handle}</p>
                </div>
              </div>
              <div className="px-4 py-1.5 rounded-full bg-cyan-400/20 border border-cyan-400/30">
                <p className="text-cyan-400 text-xs font-bold">{vibeRank}</p>
              </div>
            </div>

            <div className="mb-2">
              <p className="text-gray-400 text-sm mb-1">Wallet Balance</p>
              <div className="flex items-baseline gap-2">
                <h2 className="text-5xl font-bold text-white">₹{walletBalance.toFixed(2)}</h2>
              </div>
            </div>

            <button
              onClick={() => setShowAddMoneyModal(true)}
              className="mt-4 px-6 py-2.5 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 text-white font-bold hover:opacity-90 transition-all"
            >
              + Add Money
            </button>
          </div>

          <div className="absolute -top-20 -right-20 w-40 h-40 bg-cyan-400/20 rounded-full blur-3xl"></div>
        </div>

        {/* Loop Credits Card */}
        <div className="p-6 rounded-3xl glass-card">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                <Zap size={28} className="text-white" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Loop Credits</p>
                <h3 className="text-3xl font-bold text-white">{loopCredits}</h3>
              </div>
            </div>
            <button
              onClick={() => setShowAddCreditsModal(true)}
              className="px-4 py-2 rounded-full glass-surface border border-gray-700 text-white text-sm font-semibold hover:bg-cyan-400/10 transition-all"
            >
              Earn More
            </button>
          </div>
          <p className="text-gray-500 text-xs mt-4">Earn credits through activities and redeem for rewards</p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => setShowRedeemModal(true)}
            className="p-4 rounded-2xl glass-card hover:bg-cyan-400/5 transition-all group"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-r from-pink-400/20 to-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Gift size={24} className="text-pink-400" />
            </div>
            <p className="text-white text-sm font-semibold">Redeem Credits</p>
          </button>

          <button
            onClick={() => navigate('/wallet/history')}
            className="p-4 rounded-2xl glass-card hover:bg-cyan-400/5 transition-all group"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-r from-cyan-400/20 to-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Clock size={24} className="text-cyan-400" />
            </div>
            <p className="text-white text-sm font-semibold">Transactions</p>
          </button>
        </div>

        {/* Insights */}
        <div className="p-6 rounded-3xl glass-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-bold">This Week</h3>
            <TrendingUp size={20} className="text-cyan-400" />
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-400"></div>
                <span className="text-gray-400 text-sm">Earned</span>
              </div>
              <span className="text-green-400 font-bold">+{earnedThisWeek}</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-pink-400"></div>
                <span className="text-gray-400 text-sm">Spent</span>
              </div>
              <span className="text-pink-400 font-bold">-{spentThisWeek}</span>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-4 h-2 bg-gray-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-green-400 to-cyan-400"
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
                  className="p-4 rounded-2xl glass-card hover:bg-cyan-400/5 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        txn.type === 'topup' ? 'bg-green-400/20' : 'bg-pink-400/20'
                      }`}>
                        {txn.type === 'topup' ? (
                          <Plus size={20} className="text-green-400" />
                        ) : (
                          <Gift size={20} className="text-pink-400" />
                        )}
                      </div>
                      <div>
                        <p className="text-white text-sm font-semibold">{txn.description}</p>
                        <p className="text-gray-500 text-xs">
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
                      txn.type === 'topup' ? 'text-green-400' : 'text-pink-400'
                    }`}>
                      {txn.type === 'topup' ? '+' : '-'}{txn.amount}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 rounded-2xl glass-card text-center">
              <Clock size={48} className="mx-auto mb-3 text-gray-600" />
              <p className="text-gray-500 text-sm">No transactions yet</p>
            </div>
          )}
        </div>
      </div>

      {/* Add Money Modal */}
      {showAddMoneyModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md rounded-3xl glass-surface border border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Add Money to Wallet</h3>
              <button onClick={() => setShowAddMoneyModal(false)} className="text-gray-400 hover:text-white">
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              {/* Amount Input */}
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Enter Amount</label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-xl text-white">₹</span>
                  <input
                    type="number"
                    value={addMoneyAmount}
                    onChange={(e) => setAddMoneyAmount(e.target.value)}
                    placeholder="0.00"
                    className="w-full pl-10 pr-4 py-4 glass-card border border-gray-700 rounded-2xl text-white text-xl focus:border-cyan-400 focus:outline-none"
                  />
                </div>
              </div>

              {/* Quick Amount Buttons */}
              <div className="grid grid-cols-3 gap-2">
                {[100, 500, 1000, 2000, 5000, 10000].map(amount => (
                  <button
                    key={amount}
                    onClick={() => setAddMoneyAmount(amount.toString())}
                    className="py-3 glass-card hover:bg-cyan-400 hover:text-black rounded-xl font-semibold text-white transition-all border border-gray-700"
                  >
                    ₹{amount}
                  </button>
                ))}
              </div>

              {/* Payment Method Selection */}
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Payment Method</label>
                <div className="space-y-2">
                  {[
                    { id: 'upi', label: 'UPI (PhonePe, GPay, Paytm)' },
                    { id: 'card', label: 'Debit/Credit Card' },
                    { id: 'netbanking', label: 'Net Banking' }
                  ].map(method => (
                    <button
                      key={method.id}
                      onClick={() => setPaymentMethod(method.id)}
                      className={`w-full p-4 rounded-2xl border flex items-center justify-between transition-all ${
                        paymentMethod === method.id
                          ? 'border-cyan-400 bg-cyan-400/10'
                          : 'border-gray-700 glass-card'
                      }`}
                    >
                      <span className="text-white text-sm font-semibold">{method.label}</span>
                      {paymentMethod === method.id && (
                        <div className="w-5 h-5 rounded-full bg-cyan-400 flex items-center justify-center">
                          <div className="w-2 h-2 bg-white rounded-full"></div>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleAddMoney}
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-cyan-400 to-blue-500 text-white font-bold hover:opacity-90 transition-all"
              >
                Add ₹{addMoneyAmount || '0'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Credits Modal */}
      {showAddCreditsModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md rounded-3xl glass-surface border border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Earn Loop Credits</h3>
              <button onClick={() => setShowAddCreditsModal(false)} className="text-gray-400 hover:text-white">
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              <div className="text-center p-8 rounded-2xl glass-card border border-gray-700">
                <Zap size={48} className="mx-auto mb-3 text-cyan-400" />
                <p className="text-gray-400 text-sm mb-4">Earn credits by:</p>
                <div className="space-y-2 text-left">
                  <p className="text-white text-sm">• Creating posts & reels</p>
                  <p className="text-white text-sm">• Engaging with community</p>
                  <p className="text-white text-sm">• Completing tribe challenges</p>
                  <p className="text-white text-sm">• Attending events</p>
                </div>
              </div>

              <button
                onClick={handleAddCredits}
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-yellow-400 to-orange-500 text-white font-bold hover:opacity-90 transition-all"
              >
                Get Free 100 Credits (Demo)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Redeem Modal */}
      {showRedeemModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md rounded-3xl glass-surface border border-gray-700 p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Redeem Rewards</h3>
              <button onClick={() => setShowRedeemModal(false)} className="text-gray-400 hover:text-white">
                <X size={24} />
              </button>
            </div>

            <div className="grid grid-cols-1 gap-3">
              {redeemOptions.map(option => (
                <button
                  key={option.id}
                  onClick={() => handleRedeem(option)}
                  disabled={loopCredits < option.cost}
                  className={`p-4 rounded-2xl border transition-all ${
                    loopCredits >= option.cost
                      ? 'glass-card border-gray-700 hover:bg-cyan-400/5'
                      : 'glass-card border-gray-800 opacity-50 cursor-not-allowed'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-full bg-gradient-to-r ${option.color} flex items-center justify-center`}>
                      <option.icon size={24} className="text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="text-white font-semibold">{option.title}</p>
                      <p className="text-gray-400 text-sm">{option.cost} credits</p>
                    </div>
                    <div className="text-right">
                      <Award size={20} className="text-cyan-400" />
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