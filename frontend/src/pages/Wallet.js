import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { Plus, Settings, RefreshCw, ArrowUpRight, ArrowDownLeft, Shield } from "lucide-react";
import { toast } from "sonner";
import Barcode from "react-barcode";

const Wallet = () => {
  const { currentUser } = useContext(AuthContext);
  const [walletData, setWalletData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("pay");
  const [showTopUp, setShowTopUp] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState("");

  useEffect(() => {
    fetchWalletData();
  }, []);

  const fetchWalletData = async () => {
    try {
      const res = await axios.get(`${API}/wallet?userId=${currentUser.id}`);
      setWalletData(res.data);
    } catch (error) {
      toast.error("Failed to load wallet");
    } finally {
      setLoading(false);
    }
  };

  const handleTopUp = async () => {
    const amount = parseFloat(topUpAmount);
    if (!amount || amount <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    try {
      const res = await axios.post(`${API}/wallet/topup?userId=${currentUser.id}`, {
        amount
      });
      toast.success(`₹${amount} added to wallet!`);
      setWalletData({ ...walletData, balance: res.data.balance });
      setShowTopUp(false);
      setTopUpAmount("");
      fetchWalletData();
    } catch (error) {
      toast.error("Top-up failed");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  const kycTierBadge = walletData?.kycTier === 3 ? "Premium" : walletData?.kycTier === 2 ? "Verified" : "Basic";
  const kycColor = walletData?.kycTier === 3 ? "text-yellow-400" : walletData?.kycTier === 2 ? "text-green-400" : "text-gray-400";

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      {/* Header */}
      <div className="sticky top-0 z-10 glass-surface p-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold neon-text">LoopPay</h1>
          <p className="text-xs text-gray-400">Your digital wallet</p>
        </div>
        <button
          data-testid="wallet-settings-btn"
          className="w-10 h-10 rounded-full flex items-center justify-center bg-cyan-400/10 text-cyan-400 hover:bg-cyan-400/20"
        >
          <Settings size={20} />
        </button>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Wallet Card */}
        <div 
          className="relative overflow-hidden rounded-3xl p-6 mb-6 neon-glow"
          style={{
            background: 'linear-gradient(135deg, #00E0FF 0%, #0099cc 50%, #FF3DB3 100%)',
            minHeight: '280px'
          }}
        >
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-4 right-4 w-32 h-32 rounded-full border-2 border-white"></div>
            <div className="absolute bottom-4 left-4 w-24 h-24 rounded-full border-2 border-white"></div>
          </div>

          {/* Card Content */}
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">L</span>
                </div>
                <div>
                  <p className="text-white text-sm opacity-90">{currentUser.name}</p>
                  <p className="text-white text-xs opacity-70">@{currentUser.handle}</p>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-xs font-semibold px-3 py-1 rounded-full bg-white/20 backdrop-blur-sm ${kycColor}`}>
                  <Shield size={12} className="inline mr-1" />
                  {kycTierBadge}
                </div>
              </div>
            </div>

            <div className="mb-6">
              <p className="text-white text-sm opacity-80 mb-1">Available Balance</p>
              <h2 className="text-5xl font-bold text-white">₹{walletData?.balance?.toFixed(2) || '0.00'}</h2>
              <p className="text-white text-xs opacity-70 mt-2">
                Updated {new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>

            <div className="flex gap-3">
              <button
                data-testid="wallet-topup-btn"
                onClick={() => setShowTopUp(true)}
                className="flex-1 py-3 px-4 rounded-full bg-white text-cyan-600 font-semibold flex items-center justify-center gap-2 hover:bg-white/90 transition-all"
              >
                <Plus size={18} />
                Load Money
              </button>
              <button
                onClick={fetchWalletData}
                className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white hover:bg-white/30 transition-all"
              >
                <RefreshCw size={18} />
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab("pay")}
            className={`flex-1 py-3 rounded-full font-semibold transition-all ${
              activeTab === "pay"
                ? 'bg-cyan-400 text-black'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
            data-testid="wallet-pay-tab"
          >
            Pay at Venue
          </button>
          <button
            onClick={() => setActiveTab("transactions")}
            className={`flex-1 py-3 rounded-full font-semibold transition-all ${
              activeTab === "transactions"
                ? 'bg-cyan-400 text-black'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
            data-testid="wallet-transactions-tab"
          >
            Transactions
          </button>
        </div>

        {/* Content */}
        {activeTab === "pay" ? (
          <div className="glass-card p-8 text-center">
            <h3 className="text-lg font-bold mb-2">Scan to Pay at Venues</h3>
            <p className="text-sm text-gray-400 mb-6">Show this QR code to pay at Loopync partner venues</p>
            
            <div className="bg-white p-6 rounded-3xl inline-block mb-6">
              <QRCode
                value={`looppay://pay/${currentUser.id}`}
                size={200}
                level="H"
              />
            </div>

            <div className="mb-4">
              <div className="text-center font-mono text-xl tracking-wider text-gray-300">
                {currentUser.id.toUpperCase().substring(0, 16)}
              </div>
            </div>

            <div className="flex gap-3 justify-center">
              <div className="px-4 py-2 rounded-full bg-cyan-400/10 text-cyan-400 text-xs">
                <span className="font-semibold">UPI</span> Linked
              </div>
              <div className="px-4 py-2 rounded-full bg-green-400/10 text-green-400 text-xs">
                <span className="font-semibold">RBI</span> Compliant
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {walletData?.transactions && walletData.transactions.length > 0 ? (
              walletData.transactions.map((txn) => (
                <div key={txn.id} className="glass-card p-4" data-testid="transaction-item">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        txn.type === 'topup' ? 'bg-green-400/10 text-green-400' :
                        txn.type === 'withdraw' ? 'bg-red-400/10 text-red-400' :
                        'bg-cyan-400/10 text-cyan-400'
                      }`}>
                        {txn.type === 'topup' ? <ArrowDownLeft size={18} /> :
                         txn.type === 'withdraw' ? <ArrowUpRight size={18} /> :
                         <ArrowUpRight size={18} />}
                      </div>
                      <div>
                        <p className="font-semibold text-sm">
                          {txn.type === 'topup' ? 'Money Added' :
                           txn.type === 'withdraw' ? 'Withdrawal' :
                           txn.description || 'Payment'}
                        </p>
                        <p className="text-xs text-gray-400">
                          {new Date(txn.createdAt).toLocaleDateString('en-IN')} • {txn.status}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${
                        txn.type === 'topup' ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {txn.type === 'topup' ? '+' : '-'}₹{txn.amount.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12 glass-card">
                <p className="text-gray-400">No transactions yet</p>
              </div>
            )}
          </div>
        )}

        {/* Compliance Badges */}
        <div className="mt-8 glass-card p-4">
          <p className="text-xs text-gray-400 text-center mb-3">Powered by</p>
          <div className="flex flex-wrap gap-2 justify-center">
            <div className="px-3 py-1 rounded-full bg-cyan-400/10 text-cyan-400 text-xs">
              AWS Mumbai
            </div>
            <div className="px-3 py-1 rounded-full bg-green-400/10 text-green-400 text-xs">
              UPI • RBI PPI
            </div>
            <div className="px-3 py-1 rounded-full bg-purple-400/10 text-purple-400 text-xs">
              DPDP Compliant
            </div>
            <div className="px-3 py-1 rounded-full bg-pink-400/10 text-pink-400 text-xs">
              mTLS/KMS
            </div>
          </div>
        </div>
      </div>

      <BottomNav active="wallet" />

      {/* Top-Up Modal */}
      {showTopUp && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card p-6 w-full max-w-md">
            <h2 className="text-xl font-bold neon-text mb-4">Add Money to Wallet</h2>
            
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Enter Amount</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-2xl text-gray-400">₹</span>
                <input
                  type="number"
                  value={topUpAmount}
                  onChange={(e) => setTopUpAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full pl-12 pr-4 py-4 text-3xl font-bold bg-gray-900 border-2 border-cyan-400/30 rounded-2xl focus:border-cyan-400"
                  autoFocus
                  data-testid="topup-amount-input"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 mb-6">
              {[100, 500, 1000, 2000, 5000, 10000].map((amt) => (
                <button
                  key={amt}
                  onClick={() => setTopUpAmount(amt.toString())}
                  className="py-3 rounded-xl bg-gray-800 hover:bg-gray-700 text-sm font-semibold"
                >
                  ₹{amt}
                </button>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowTopUp(false)}
                className="flex-1 py-3 rounded-full border border-gray-600 text-gray-300 hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={handleTopUp}
                className="flex-1 btn-primary"
                data-testid="topup-confirm-btn"
              >
                Add Money
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Wallet;
