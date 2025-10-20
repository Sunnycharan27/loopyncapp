import React, { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import Home from "./pages/Home";
import VibeZone from "./pages/VibeZone";
import Tribes from "./pages/Tribes";
import TribeDetail from "./pages/TribeDetail";
import Wallet from "./pages/Wallet";
import Discover from "./pages/Discover";
import Venues from "./pages/Venues";
import VenueDetail from "./pages/VenueDetail";
import Events from "./pages/Events";
import EventDetail from "./pages/EventDetail";
import Payment from "./pages/Payment";
import Marketplace from "./pages/Marketplace";
import Onboarding from "./pages/Onboarding";
import Messenger from "./pages/Messenger";
import Notifications from "./pages/Notifications";
import Profile from "./pages/Profile";
import Auth from "./pages/Auth";
import { Toaster } from "sonner";
import { WebSocketProvider } from "./context/WebSocketContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const AuthContext = React.createContext();

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [needsOnboarding, setNeedsOnboarding] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("loopync_token");
    const user = localStorage.getItem("loopync_user");
    if (token && user) {
      setCurrentUser(JSON.parse(user));
      setIsAuthenticated(true);
      checkOnboardingStatus(JSON.parse(user).id);
    }
  }, []);

  const checkOnboardingStatus = async (userId) => {
    try {
      const res = await axios.get(`${API}/users/${userId}/interests`);
      if (!res.data.onboardingComplete) {
        setNeedsOnboarding(true);
      }
    } catch (error) {
      // If interests not found, user needs onboarding
      setNeedsOnboarding(true);
    }
  };

  const login = (token, user) => {
    localStorage.setItem("loopync_token", token);
    localStorage.setItem("loopync_user", JSON.stringify(user));
    setCurrentUser(user);
    setIsAuthenticated(true);
    checkOnboardingStatus(user.id);
  };

  const logout = () => {
    localStorage.removeItem("loopync_token");
    localStorage.removeItem("loopync_user");
    setCurrentUser(null);
    setIsAuthenticated(false);
    setNeedsOnboarding(false);
  };

  return (
    <AuthContext.Provider value={{ currentUser, isAuthenticated, needsOnboarding, setNeedsOnboarding, login, logout }}>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/auth" element={<Auth />} />
            <Route
              path="/onboarding"
              element={isAuthenticated ? <Onboarding /> : <Navigate to="/auth" />}
            />
            <Route
              path="/"
              element={
                isAuthenticated ? (
                  needsOnboarding ? <Navigate to="/onboarding" /> : <Home />
                ) : (
                  <Navigate to="/auth" />
                )
              }
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
              path="/discover"
              element={isAuthenticated ? <Discover /> : <Navigate to="/auth" />}
            />
            <Route
              path="/marketplace"
              element={isAuthenticated ? <Marketplace /> : <Navigate to="/auth" />}
            />
            <Route
              path="/venues"
              element={isAuthenticated ? <Venues /> : <Navigate to="/auth" />}
            />
            <Route
              path="/venues/:venueId"
              element={isAuthenticated ? <VenueDetail /> : <Navigate to="/auth" />}
            />
            <Route
              path="/events"
              element={isAuthenticated ? <Events /> : <Navigate to="/auth" />}
            />
            <Route
              path="/events/:eventId"
              element={isAuthenticated ? <EventDetail /> : <Navigate to="/auth" />}
            />
            <Route
              path="/payment"
              element={isAuthenticated ? <Payment /> : <Navigate to="/auth" />}
            />
            <Route
              path="/messenger"
              element={isAuthenticated ? <Messenger /> : <Navigate to="/auth" />}
            />
            <Route
              path="/notifications"
              element={isAuthenticated ? <Notifications /> : <Navigate to="/auth" />}
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

export default App;