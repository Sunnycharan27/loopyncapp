import React, { useState, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [handle, setHandle] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const res = await axios.post(`${API}/auth/login`, { handle, password });
        login(res.data.token, res.data.user);
        toast.success("Welcome back!");
        navigate("/");
      } else {
        const res = await axios.post(`${API}/auth/signup`, { handle, name, password });
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

  // Quick demo login
  const demoLogin = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/auth/login`, { handle: "demo", password: "demo" });
      login(res.data.token, res.data.user);
      toast.success("Logged in as Demo User!");
      navigate("/");
    } catch (error) {
      toast.error("Demo login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="glass-card p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold neon-text mb-2">Loopync</h1>
          <p className="text-gray-400 text-sm">Where your vibes find their tribes</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Handle</label>
            <input
              data-testid="auth-handle-input"
              type="text"
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              placeholder="@yourhandle"
              className="w-full"
              required
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-sm font-medium mb-2">Name</label>
              <input
                data-testid="auth-name-input"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                className="w-full"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">Password</label>
            <input
              data-testid="auth-password-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full"
              required
            />
          </div>

          <button
            data-testid="auth-submit-btn"
            type="submit"
            className="btn-primary w-full"
            disabled={loading}
          >
            {loading ? "Loading..." : isLogin ? "Login" : "Sign Up"}
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

        <div className="mt-6 pt-6 border-t border-gray-700">
          <button
            data-testid="demo-login-btn"
            onClick={demoLogin}
            className="w-full py-3 rounded-full border border-cyan-400 text-cyan-400 hover:bg-cyan-400/10"
            disabled={loading}
          >
            Quick Demo Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default Auth;