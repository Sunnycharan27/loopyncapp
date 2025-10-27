import React, { useState, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useNavigate } from "react-router-dom";
import { Mail, Lock, User, Eye, EyeOff, CheckCircle, ArrowLeft } from "lucide-react";
import { toast } from "sonner";

const AuthComplete = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [mode, setMode] = useState("login"); // login, signup, verify, forgot, reset
  const [loading, setLoading] = useState(false);
  
  // Form states
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [handle, setHandle] = useState("");
  const [phone, setPhone] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  
  // Verification
  const [verificationCode, setVerificationCode] = useState("");
  const [serverCode, setServerCode] = useState(""); // For testing
  
  // Password reset
  const [resetCode, setResetCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Please fill in all fields");
      return;
    }

    setLoading(true);
    try {
      console.log("Attempting login with:", { email });
      const res = await axios.post(`${API}/auth/login`, { email, password });
      console.log("Login response:", res.data);
      login(res.data.token, res.data.user);
      toast.success(`Welcome back, ${res.data.user.name}!`);
      navigate("/");
    } catch (error) {
      console.error("Login error:", error.response?.data || error.message);
      const errorMsg = error.response?.data?.detail || "Invalid email or password";
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    
    if (!name || !handle || !email || !phone || !password) {
      toast.error("Please fill in all fields");
      return;
    }

    if (password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    if (!email.includes("@")) {
      toast.error("Please enter a valid email");
      return;
    }

    if (phone.length < 10) {
      toast.error("Please enter a valid 10-digit phone number");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post(`${API}/auth/signup`, {
        name,
        handle,
        email,
        phone,
        password
      });
      
      // Login immediately with returned token
      login(res.data.token, res.data.user);
      toast.success(`Welcome to Loopync, ${res.data.user.name}! 🎉`);
      navigate("/");
      
    } catch (error) {
      toast.error(error.response?.data?.detail || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyEmail = async (e) => {
    e.preventDefault();
    
    if (verificationCode.length !== 6) {
      toast.error("Please enter the 6-digit code");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/auth/verify-email`, {
        email,
        code: verificationCode
      });
      
      toast.success("Email verified! Logging you in...");
      
      // Auto-login after verification
      const loginRes = await axios.post(`${API}/auth/login`, { email, password });
      login(loginRes.data.token, loginRes.data.user);
      navigate("/");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Invalid code");
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/auth/resend-verification`, { email });
      setServerCode(res.data.code);
      toast.success("New code sent!");
      toast.info(`Code: ${res.data.code}`, { duration: 10000 });
    } catch (error) {
      toast.error("Failed to resend code");
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    
    if (!email) {
      toast.error("Please enter your email");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post(`${API}/auth/forgot-password`, { email });
      if (res.data.code) {
        toast.success("Reset code sent to your email!");
        toast.info(`Code: ${res.data.code}`, { duration: 10000 });
        setResetCode("");
        setMode("reset");
      }
    } catch (error) {
      toast.error("Failed to send reset code");
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    
    if (!resetCode || !newPassword || !confirmPassword) {
      toast.error("Please fill in all fields");
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error("Passwords don't match");
      return;
    }

    if (newPassword.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    setLoading(true);
    try {
      // Verify code first
      await axios.post(`${API}/auth/verify-reset-code`, {
        email,
        code: resetCode
      });

      // Reset password
      await axios.post(`${API}/auth/reset-password`, {
        email,
        code: resetCode,
        newPassword
      });
      
      toast.success("Password reset successfully!");
      setMode("login");
      setPassword("");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to reset password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold neon-text mb-2">Loopync</h1>
          <p className="text-gray-400">India's Social Superapp</p>
        </div>

        {/* Main Card */}
        <div className="glass-card p-8 mb-4">
          {/* Login Form */}
          {mode === "login" && (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <div className="relative">
                  <Mail size={20} className="absolute left-3 top-3 text-gray-400" />
                  <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>

              <div>
                <div className="relative">
                  <Lock size={20} className="absolute left-3 top-3 text-gray-400" />
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-12 pr-12 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold hover:opacity-90 transition-all disabled:opacity-50"
              >
                {loading ? "Logging in..." : "Log In"}
              </button>

              <button
                type="button"
                onClick={() => setMode("forgot")}
                className="w-full text-sm text-cyan-400 hover:text-cyan-300"
              >
                Forgot password?
              </button>
            </form>
          )}

          {/* Signup Form */}
          {mode === "signup" && (
            <form onSubmit={handleSignup} className="space-y-4">
              <div>
                <div className="relative">
                  <User size={20} className="absolute left-3 top-3 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Full Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>

              <div>
                <div className="relative">
                  <span className="absolute left-3 top-3 text-gray-400">@</span>
                  <input
                    type="text"
                    placeholder="username"
                    value={handle}
                    onChange={(e) => setHandle(e.target.value.replace(/[^a-zA-Z0-9_]/g, ''))}
                    className="w-full pl-12 pr-4 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>

              <div>
                <div className="relative">
                  <Mail size={20} className="absolute left-3 top-3 text-gray-400" />
                  <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>

              <div>
                <div className="relative">
                  <Lock size={20} className="absolute left-3 top-3 text-gray-400" />
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Password (min 8 characters)"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-12 pr-12 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold hover:opacity-90 transition-all disabled:opacity-50"
              >
                {loading ? "Creating Account..." : "Sign Up"}
              </button>
            </form>
          )}

          {/* Email Verification */}
          {mode === "verify" && (
            <form onSubmit={handleVerifyEmail} className="space-y-6">
              <div className="text-center mb-6">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-cyan-400/20 flex items-center justify-center">
                  <Mail size={32} className="text-cyan-400" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Check your email</h2>
                <p className="text-gray-400">We sent a code to</p>
                <p className="text-cyan-400 font-medium">{email}</p>
              </div>

              <div>
                <input
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/[^0-9]/g, '').slice(0, 6))}
                  className="w-full px-4 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white text-center text-2xl tracking-widest focus:outline-none focus:border-cyan-400"
                  maxLength={6}
                />
              </div>

              <button
                type="submit"
                disabled={loading || verificationCode.length !== 6}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold hover:opacity-90 transition-all disabled:opacity-50"
              >
                {loading ? "Verifying..." : "Verify Email"}
              </button>

              <button
                type="button"
                onClick={handleResendCode}
                disabled={loading}
                className="w-full text-sm text-cyan-400 hover:text-cyan-300"
              >
                Resend code
              </button>

              <button
                type="button"
                onClick={() => setMode("signup")}
                className="w-full text-sm text-gray-400 hover:text-white flex items-center justify-center gap-2"
              >
                <ArrowLeft size={16} />
                Back to signup
              </button>
            </form>
          )}

          {/* Forgot Password */}
          {mode === "forgot" && (
            <form onSubmit={handleForgotPassword} className="space-y-6">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-white mb-2">Reset Password</h2>
                <p className="text-gray-400">Enter your email to receive a reset code</p>
              </div>

              <div>
                <div className="relative">
                  <Mail size={20} className="absolute left-3 top-3 text-gray-400" />
                  <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold hover:opacity-90 transition-all disabled:opacity-50"
              >
                {loading ? "Sending..." : "Send Reset Code"}
              </button>

              <button
                type="button"
                onClick={() => setMode("login")}
                className="w-full text-sm text-gray-400 hover:text-white flex items-center justify-center gap-2"
              >
                <ArrowLeft size={16} />
                Back to login
              </button>
            </form>
          )}

          {/* Reset Password */}
          {mode === "reset" && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-white mb-2">Create New Password</h2>
                <p className="text-gray-400">Enter the code from your email</p>
              </div>

              <div>
                <input
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={resetCode}
                  onChange={(e) => setResetCode(e.target.value.replace(/[^0-9]/g, '').slice(0, 6))}
                  className="w-full px-4 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white text-center text-xl tracking-widest focus:outline-none focus:border-cyan-400"
                  maxLength={6}
                />
              </div>

              <div>
                <div className="relative">
                  <Lock size={20} className="absolute left-3 top-3 text-gray-400" />
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="New Password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full pl-12 pr-12 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <div>
                <div className="relative">
                  <Lock size={20} className="absolute left-3 top-3 text-gray-400" />
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Confirm Password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 rounded-xl bg-gray-900/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold hover:opacity-90 transition-all disabled:opacity-50"
              >
                {loading ? "Resetting..." : "Reset Password"}
              </button>
            </form>
          )}
        </div>

        {/* Toggle Login/Signup */}
        {(mode === "login" || mode === "signup") && (
          <div className="glass-card p-4 text-center">
            <span className="text-gray-400">
              {mode === "login" ? "Don't have an account?" : "Already have an account?"}
            </span>
            {" "}
            <button
              onClick={() => setMode(mode === "login" ? "signup" : "login")}
              className="text-cyan-400 font-semibold hover:text-cyan-300"
            >
              {mode === "login" ? "Sign Up" : "Log In"}
            </button>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>© 2025 Loopync. Made with ❤️ in India</p>
        </div>
      </div>
    </div>
  );
};

export default AuthComplete;
