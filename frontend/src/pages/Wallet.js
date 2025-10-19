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
    <div className="min-h-screen pb-24" style={{ background: '#FFFFFF' }}>
      {/* Header - Starbucks Style */}
      <div className="sticky top-0 z-10 bg-white shadow-sm px-4 py-3 flex items-center justify-between border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">LoopPay</h1>
        <button
          data-testid="wallet-settings-btn"
          className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-900"
        >
          <Plus size={24} />
        </button>
      </div>

      <div className="max-w-2xl mx-auto">
        {/* Wallet Card - Starbucks Style */}
        <div 
          className="relative overflow-hidden mx-4 mt-6 rounded-2xl shadow-lg"
          style={{
            background: 'linear-gradient(135deg, #00704A 0%, #008248 50%, #00704A 100%)',
          }}
        >
          {/* Decorative Elements */}
          <div className="absolute top-0 right-0 w-48 h-48 opacity-10" style={{
            background: 'radial-gradient(circle, white 0%, transparent 70%)'
          }}></div>
          <div className="absolute bottom-0 left-0 w-32 h-32 opacity-10" style={{
            background: 'radial-gradient(circle, white 0%, transparent 70%)'
          }}></div>

          {/* White Card Content */}
          <div className="relative z-10 m-4 bg-white rounded-xl p-5 shadow-md">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-gray-900 font-semibold text-base">{currentUser.name} | *{currentUser.id.substring(0, 5).toUpperCase()}</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={fetchWalletData}
                  className="w-8 h-8 flex items-center justify-center text-gray-600 hover:bg-gray-100 rounded-full"
                >
                  <RefreshCw size={16} />
                </button>
                <button
                  data-testid="wallet-settings-btn"
                  className="w-8 h-8 flex items-center justify-center text-gray-600 hover:bg-gray-100 rounded-full"
                >
                  <Settings size={16} />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-4xl font-bold text-gray-900">₹{walletData?.balance?.toFixed(2) || '0.00'}</h2>
                <p className="text-xs text-gray-500 mt-1">
                  Updated at {new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })} on {new Date().toLocaleDateString('en-IN', { day: '2-digit', month: '2-digit', year: 'numeric' })}
                </p>
              </div>
              <button
                data-testid="wallet-topup-btn"
                onClick={() => setShowTopUp(true)}
                className="px-6 py-3 rounded-full font-semibold text-white text-sm"
                style={{ background: '#00704A' }}
              >
                Load Card
              </button>
            </div>
          </div>
        </div>

        {/* Tabs - Starbucks Style */}
        <div className="flex gap-0 mx-4 mt-6 bg-white rounded-full border-2 border-gray-300 overflow-hidden">
          <button
            onClick={() => setActiveTab("pay")}
            className={`flex-1 py-3 px-4 font-medium text-sm transition-all ${
              activeTab === "pay"
                ? 'text-white'
                : 'bg-white text-gray-700'
            }`}
            style={activeTab === "pay" ? { background: '#00704A' } : {}}
            data-testid="wallet-pay-tab"
          >
            Pay at Store
          </button>
          <button
            onClick={() => setActiveTab("transactions")}
            className={`flex-1 py-3 px-4 font-medium text-sm transition-all ${
              activeTab === "transactions"
                ? 'text-white'
                : 'bg-white text-gray-700'
            }`}
            style={activeTab === "transactions" ? { background: '#00704A' } : {}}
            data-testid="wallet-transactions-tab"
          >
            Past Transactions
          </button>
        </div>

        {/* Content */}
        {activeTab === "pay" ? (
          <div className="bg-white mx-4 mt-6 rounded-2xl p-6 shadow-sm">
            <h3 className="text-center text-gray-900 font-semibold text-base mb-6">
              Scan the barcode and pay at the store
            </h3>
            
            <div className="bg-white flex flex-col items-center justify-center py-8 px-4">
              <div className="bg-white p-4 rounded-lg">
                <Barcode
                  value={currentUser.id.toUpperCase().replace(/-/g, '').substring(0, 16)}
                  format="CODE128"
                  width={2.5}
                  height={80}
                  displayValue={true}
                  fontSize={16}
                  fontOptions="bold"
                  background="#ffffff"
                  lineColor="#000000"
                  margin={0}
                />
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center mb-4">Payment Methods</p>
              <div className="flex gap-3 justify-center">
                <div className="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 text-xs font-medium">
                  UPI Linked
                </div>
                <div className="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 text-xs font-medium">
                  RBI Compliant
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="mx-4 mt-6">
            {walletData?.transactions && walletData.transactions.length > 0 ? (
              <div className="space-y-3">
                {walletData.transactions.map((txn) => (
                  <div key={txn.id} className="bg-white rounded-2xl p-4 shadow-sm" data-testid="transaction-item">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          txn.type === 'topup' ? 'bg-green-100 text-green-600' :
                          txn.type === 'withdraw' ? 'bg-red-100 text-red-600' :
                          'bg-blue-100 text-blue-600'
                        }`}>
                          {txn.type === 'topup' ? <ArrowDownLeft size={18} /> :
                           txn.type === 'withdraw' ? <ArrowUpRight size={18} /> :
                           <ArrowUpRight size={18} />}
                        </div>
                        <div>
                          <p className="font-semibold text-sm text-gray-900">
                            {txn.type === 'topup' ? 'Money Added' :
                             txn.type === 'withdraw' ? 'Withdrawal' :
                             txn.description || 'Payment'}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(txn.createdAt).toLocaleDateString('en-IN')} • {txn.status}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-bold text-base ${
                          txn.type === 'topup' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {txn.type === 'topup' ? '+' : '-'}₹{txn.amount.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-2xl shadow-sm">
                <p className="text-gray-500">No transactions yet</p>
              </div>
            )}
          </div>
        )}

        {/* Bottom FAB - Starbucks Order Style */}
        <div className="fixed bottom-24 left-1/2 transform -translate-x-1/2 z-20">
          <button
            className="w-16 h-16 rounded-full shadow-2xl flex items-center justify-center text-white"
            style={{ background: '#00704A' }}
          >
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 8H20L20 21C20 21.5523 19.5523 22 19 22H5C4.44772 22 4 21.5523 4 21L4 8H7M17 8V5C17 3.89543 16.1046 3 15 3H9C7.89543 3 7 3.89543 7 5V8M17 8H7M7 8V21M17 8V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </div>

      <BottomNav active="wallet" />

      {/* Top-Up Modal - Starbucks Style */}
      {showTopUp && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Add Money to Wallet</h2>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Enter Amount</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-2xl text-gray-400">₹</span>
                <input
                  type="number"
                  value={topUpAmount}
                  onChange={(e) => setTopUpAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full pl-12 pr-4 py-4 text-3xl font-bold bg-gray-50 border-2 border-gray-300 rounded-xl focus:border-green-600 focus:outline-none text-gray-900"
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
                  className="py-3 rounded-xl bg-gray-100 hover:bg-gray-200 text-sm font-semibold text-gray-900"
                >
                  ₹{amt}
                </button>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowTopUp(false)}
                className="flex-1 py-3 rounded-full border-2 border-gray-300 text-gray-700 font-semibold hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleTopUp}
                className="flex-1 py-3 rounded-full text-white font-semibold"
                style={{ background: '#00704A' }}
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
