import React, { useState, useContext, useEffect } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { CheckCircle, XCircle, Loader } from "lucide-react";

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [handle, setHandle] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [checkingHandle, setCheckingHandle] = useState(false);
  const [handleAvailable, setHandleAvailable] = useState(null);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  // Debounced handle check
  useEffect(() => {
    if (!isLogin && handle.length >= 3) {
      const timer = setTimeout(() => {
        checkHandleAvailability(handle);
      }, 500);
      return () => clearTimeout(timer);
    } else {
      setHandleAvailable(null);
    }
  }, [handle, isLogin]);

  // Debounced handle check
  useEffect(() => {
    if (!isLogin && handle.length >= 3) {
      const timer = setTimeout(() => {
        checkHandleAvailability(handle);
      }, 500);
      return () => clearTimeout(timer);
    } else {
      setHandleAvailable(null);
    }
  }, [handle, isLogin]);

  const checkHandleAvailability = async (handleToCheck) => {
    setCheckingHandle(true);
    try {
      const res = await axios.get(`${API}/auth/check-handle/${handleToCheck}`);
      setHandleAvailable(res.data.available);
    } catch (error) {
      console.error("Failed to check handle");
    } finally {
      setCheckingHandle(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!isLogin) {
      if (handle.length < 3) {
        toast.error("Username must be at least 3 characters");
        return;
      }
      if (!handleAvailable) {
        toast.error("Please choose an available username");
        return;
      }
      if (password.length < 8) {
        toast.error("Password must be at least 8 characters");
        return;
      }
    }
    
    setLoading(true);

    try {
      if (isLogin) {
        const res = await axios.post(`${API}/auth/login`, { email, password });
        login(res.data.token, res.data.user);
        toast.success("Welcome back!");
        navigate("/");
      } else {
        const res = await axios.post(`${API}/auth/signup`, { handle, name, email, password });
        login(res.data.token, res.data.user);
        toast.success("Account created successfully!");
        navigate("/");
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="glass-card p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <img 
            src="/loopync-logo.jpg" 
            alt="Loopync" 
            className="w-32 h-32 mx-auto mb-4 rounded-3xl"
          />
          <h1 className="text-5xl font-bold neon-text mb-2">Loopync</h1>
          <p className="text-gray-400 text-sm">Where your vibes find their tribes</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium mb-2 text-white">Username</label>
              <div className="relative">
                <input
                  data-testid="auth-handle-input"
                  type="text"
                  value={handle}
                  onChange={(e) => setHandle(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                  placeholder="yourhandle"
                  className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border-2 border-gray-700 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none pr-10"
                  required
                  minLength={3}
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  {checkingHandle && (
                    <Loader size={20} className="text-gray-400 animate-spin" />
                  )}
                  {!checkingHandle && handleAvailable === true && handle.length >= 3 && (
                    <CheckCircle size={20} className="text-green-400" />
                  )}
                  {!checkingHandle && handleAvailable === false && (
                    <XCircle size={20} className="text-red-400" />
                  )}
                </div>
              </div>
              {handle.length >= 3 && handleAvailable === false && (
                <p className="text-red-400 text-xs mt-1">@{handle} is already taken</p>
              )}
              {handle.length >= 3 && handleAvailable === true && (
                <p className="text-green-400 text-xs mt-1">@{handle} is available!</p>
              )}
              {handle.length > 0 && handle.length < 3 && (
                <p className="text-gray-400 text-xs mt-1">Username must be at least 3 characters</p>
              )}
            </div>
          )}

          {!isLogin && (
            <div>
              <label className="block text-sm font-medium mb-2 text-white">Name</label>
              <input
                data-testid="auth-name-input"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your full name"
                className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border-2 border-gray-700 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2 text-white">Email</label>
            <input
              data-testid="auth-email-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border-2 border-gray-700 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-white">Password</label>
            <input
              data-testid="auth-password-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border-2 border-gray-700 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none"
              required
              minLength={8}
            />
            {!isLogin && password.length > 0 && password.length < 8 && (
              <p className="text-red-400 text-xs mt-1">Password must be at least 8 characters</p>
            )}
          </div>

          <button
            data-testid="auth-submit-btn"
            type="submit"
            className="w-full py-3 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold text-lg hover:opacity-90 transition-all disabled:opacity-50"
            disabled={loading || (!isLogin && (!handleAvailable || checkingHandle))}
          >
            {loading ? (
              <div className="flex items-center justify-center gap-2">
                <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
                {isLogin ? "Logging in..." : "Creating account..."}
              </div>
            ) : (
              isLogin ? "Login" : "Sign Up"
            )}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button
            data-testid="auth-toggle-btn"
            onClick={() => setIsLogin(!isLogin)}
            className="text-sm text-cyan-400 hover:text-cyan-300"
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Login"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Auth;