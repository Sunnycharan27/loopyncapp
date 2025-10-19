import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import Home from "./pages/Home";
import VibeZone from "./pages/VibeZone";
import Tribes from "./pages/Tribes";
import TribeDetail from "./pages/TribeDetail";
import Wallet from "./pages/Wallet";
import Profile from "./pages/Profile";
import Auth from "./pages/Auth";
import { Toaster } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const AuthContext = React.createContext();

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("loopync_token");
    const user = localStorage.getItem("loopync_user");
    if (token && user) {
      setCurrentUser(JSON.parse(user));
      setIsAuthenticated(true);
    }
  }, []);

  const login = (token, user) => {
    localStorage.setItem("loopync_token", token);
    localStorage.setItem("loopync_user", JSON.stringify(user));
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem("loopync_token");
    localStorage.removeItem("loopync_user");
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ currentUser, isAuthenticated, login, logout }}>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/auth" element={<Auth />} />
            <Route
              path="/"
              element={isAuthenticated ? <Home /> : <Navigate to="/auth" />}
            />
            <Route
              path="/vibezone"
              element={isAuthenticated ? <VibeZone /> : <Navigate to="/auth" />}
            />
            <Route
              path="/tribes"
              element={isAuthenticated ? <Tribes /> : <Navigate to="/auth" />}
            />
            <Route
              path="/tribes/:tribeId"
              element={isAuthenticated ? <TribeDetail /> : <Navigate to="/auth" />}
            />
            <Route
              path="/wallet"
              element={isAuthenticated ? <Wallet /> : <Navigate to="/auth" />}
            />
            <Route
              path="/profile"
              element={isAuthenticated ? <Profile /> : <Navigate to="/auth" />}
            />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-center" richColors />
      </div>
    </AuthContext.Provider>
  );
}

import React from "react";
export default App;