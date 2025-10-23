import React, { useState, useContext, useEffect } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useNavigate } from "react-router-dom";
import { 
  ArrowLeft, User, Lock, Shield, Bell, EyeOff, UserX, 
  HelpCircle, Info, ChevronRight, Camera, Mail, Globe,
  Smartphone, Moon, LogOut
} from "lucide-react";
import { toast } from "sonner";

const Settings = () => {
  const { currentUser, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState("main");
  const [loading, setLoading] = useState(false);

  // Edit Profile State
  const [profile, setProfile] = useState({
    name: currentUser?.name || "",
    handle: currentUser?.handle || "",
    bio: currentUser?.bio || "",
    avatar: currentUser?.avatar || ""
  });

  // Settings State
  const [settings, setSettings] = useState({
    accountPrivate: false,
    showOnlineStatus: true,
    allowMessagesFrom: "everyone", // everyone, friends, none
    showActivity: true,
    allowTagging: true,
    showStories: true,
    emailNotifications: true,
    pushNotifications: true,
    likeNotifications: true,
    commentNotifications: true,
    followNotifications: true,
    messageNotifications: true,
    darkMode: false
  });

  const [blockedUsers, setBlockedUsers] = useState([]);
  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: ""
  });

  useEffect(() => {
    if (currentUser) {
      setProfile({
        name: currentUser.name || "",
        handle: currentUser.handle || "",
        bio: currentUser.bio || "",
        avatar: currentUser.avatar || ""
      });
      fetchSettings();
      fetchBlockedUsers();
    }
  }, [currentUser]);

  const fetchSettings = async () => {
    try {
      const res = await axios.get(`${API}/users/${currentUser.id}/settings`);
      setSettings({ ...settings, ...res.data });
    } catch (error) {
      console.error("Failed to load settings");
    }
  };

  const fetchBlockedUsers = async () => {
    try {
      const res = await axios.get(`${API}/users/${currentUser.id}/blocked`);
      setBlockedUsers(res.data);
    } catch (error) {
      console.error("Failed to load blocked users");
    }
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/${currentUser.id}`, profile);
      toast.success("Profile updated successfully!");
      setActiveSection("main");
    } catch (error) {
      toast.error("Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/${currentUser.id}/settings`, settings);
      toast.success("Settings saved!");
      setActiveSection("main");
    } catch (error) {
      toast.error("Failed to save settings");
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error("Passwords don't match");
      return;
    }
    if (passwordData.newPassword.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/auth/change-password`, {
        userId: currentUser.id,
        currentPassword: passwordData.currentPassword,
        newPassword: passwordData.newPassword
      });
      toast.success("Password changed successfully!");
      setPasswordData({ currentPassword: "", newPassword: "", confirmPassword: "" });
      setActiveSection("main");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to change password");
    } finally {
      setLoading(false);
    }
  };

  const handleUnblock = async (userId) => {
    try {
      await axios.delete(`${API}/users/${currentUser.id}/block/${userId}`);
      toast.success("User unblocked");
      fetchBlockedUsers();
    } catch (error) {
      toast.error("Failed to unblock user");
    }
  };

  const handleLogout = () => {
    if (window.confirm("Are you sure you want to log out?")) {
      logout();
      navigate("/auth");
    }
  };

  // Main Settings Menu
  const renderMainMenu = () => (
    <div className="space-y-2">
      <MenuItem
        icon={<User size={20} />}
        title="Edit Profile"
        onClick={() => setActiveSection("profile")}
      />
      <MenuItem
        icon={<Lock size={20} />}
        title="Account Settings"
        onClick={() => setActiveSection("account")}
      />
      <MenuItem
        icon={<Shield size={20} />}
        title="Security"
        onClick={() => setActiveSection("security")}
      />
      <MenuItem
        icon={<EyeOff size={20} />}
        title="Privacy"
        onClick={() => setActiveSection("privacy")}
      />
      <MenuItem
        icon={<Bell size={20} />}
        title="Notifications"
        onClick={() => setActiveSection("notifications")}
      />
      <MenuItem
        icon={<UserX size={20} />}
        title="Blocked Users"
        badge={blockedUsers.length > 0 ? blockedUsers.length : null}
        onClick={() => setActiveSection("blocked")}
      />
      <div className="border-t border-gray-700 my-4"></div>
      <MenuItem
        icon={<HelpCircle size={20} />}
        title="Help & Support"
        onClick={() => setActiveSection("help")}
      />
      <MenuItem
        icon={<Info size={20} />}
        title="About"
        onClick={() => setActiveSection("about")}
      />
      <div className="border-t border-gray-700 my-4"></div>
      <MenuItem
        icon={<LogOut size={20} />}
        title="Log Out"
        onClick={handleLogout}
        danger
      />
    </div>
  );

  // Edit Profile Section
  const renderProfile = () => (
    <div className="space-y-6">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <img
            src={profile.avatar}
            alt={profile.name}
            className="w-24 h-24 rounded-full ring-4 ring-cyan-400/20"
          />
          <button className="absolute bottom-0 right-0 w-8 h-8 bg-cyan-400 rounded-full flex items-center justify-center text-black hover:bg-cyan-500 transition-all">
            <Camera size={16} />
          </button>
        </div>
        <p className="text-sm text-cyan-400 cursor-pointer hover:text-cyan-300">
          Change Profile Photo
        </p>
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-2">Name</label>
        <input
          type="text"
          value={profile.name}
          onChange={(e) => setProfile({ ...profile, name: e.target.value })}
          className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
          placeholder="Your name"
        />
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-2">Username</label>
        <input
          type="text"
          value={profile.handle}
          onChange={(e) => setProfile({ ...profile, handle: e.target.value })}
          className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
          placeholder="@username"
        />
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-2">Bio</label>
        <textarea
          value={profile.bio}
          onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
          className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400 resize-none"
          rows="4"
          placeholder="Tell us about yourself..."
          maxLength="150"
        />
        <p className="text-xs text-gray-500 mt-1">{profile.bio.length}/150</p>
      </div>

      <button
        onClick={handleSaveProfile}
        disabled={loading}
        className="w-full py-3 rounded-xl bg-cyan-400 text-black font-semibold hover:bg-cyan-500 transition-all disabled:opacity-50"
      >
        {loading ? "Saving..." : "Save Changes"}
      </button>
    </div>
  );

  // Account Settings Section
  const renderAccount = () => (
    <div className="space-y-4">
      <ToggleItem
        title="Private Account"
        description="Only followers can see your posts"
        checked={settings.accountPrivate}
        onChange={(val) => setSettings({ ...settings, accountPrivate: val })}
      />
      <ToggleItem
        title="Show Online Status"
        description="Let friends see when you're active"
        checked={settings.showOnlineStatus}
        onChange={(val) => setSettings({ ...settings, showOnlineStatus: val })}
      />
      <ToggleItem
        title="Show Activity Status"
        description="Let others see your activity"
        checked={settings.showActivity}
        onChange={(val) => setSettings({ ...settings, showActivity: val })}
      />

      <div>
        <label className="block text-sm text-gray-400 mb-2">Allow Messages From</label>
        <select
          value={settings.allowMessagesFrom}
          onChange={(e) => setSettings({ ...settings, allowMessagesFrom: e.target.value })}
          className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
        >
          <option value="everyone">Everyone</option>
          <option value="friends">Friends Only</option>
          <option value="none">No One</option>
        </select>
      </div>

      <button
        onClick={handleSaveSettings}
        disabled={loading}
        className="w-full py-3 rounded-xl bg-cyan-400 text-black font-semibold hover:bg-cyan-500 transition-all disabled:opacity-50"
      >
        {loading ? "Saving..." : "Save Settings"}
      </button>
    </div>
  );

  // Security Section
  const renderSecurity = () => (
    <div className="space-y-6">
      <div className="glass-card p-4 rounded-xl">
        <h3 className="text-white font-semibold mb-2">Change Password</h3>
        <p className="text-sm text-gray-400 mb-4">Keep your account secure with a strong password</p>

        <div className="space-y-4">
          <input
            type="password"
            value={passwordData.currentPassword}
            onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
            className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
            placeholder="Current password"
          />
          <input
            type="password"
            value={passwordData.newPassword}
            onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
            className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
            placeholder="New password (min 8 characters)"
          />
          <input
            type="password"
            value={passwordData.confirmPassword}
            onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
            className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
            placeholder="Confirm new password"
          />

          <button
            onClick={handleChangePassword}
            disabled={loading}
            className="w-full py-3 rounded-xl bg-cyan-400 text-black font-semibold hover:bg-cyan-500 transition-all disabled:opacity-50"
          >
            {loading ? "Changing..." : "Change Password"}
          </button>
        </div>
      </div>

      <div className="glass-card p-4 rounded-xl">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold">Two-Factor Authentication</h3>
            <p className="text-sm text-gray-400 mt-1">Coming soon</p>
          </div>
          <div className="px-3 py-1 rounded-full bg-gray-700 text-xs text-gray-400">
            Soon
          </div>
        </div>
      </div>
    </div>
  );

  // Privacy Section
  const renderPrivacy = () => (
    <div className="space-y-4">
      <ToggleItem
        title="Allow Tagging"
        description="Let others tag you in posts"
        checked={settings.allowTagging}
        onChange={(val) => setSettings({ ...settings, allowTagging: val })}
      />
      <ToggleItem
        title="Show Stories"
        description="Let friends see your stories"
        checked={settings.showStories}
        onChange={(val) => setSettings({ ...settings, showStories: val })}
      />

      <button
        onClick={handleSaveSettings}
        disabled={loading}
        className="w-full py-3 rounded-xl bg-cyan-400 text-black font-semibold hover:bg-cyan-500 transition-all disabled:opacity-50"
      >
        {loading ? "Saving..." : "Save Settings"}
      </button>
    </div>
  );

  // Notifications Section
  const renderNotifications = () => (
    <div className="space-y-4">
      <div className="mb-6">
        <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
          <Mail size={18} className="text-cyan-400" />
          Email Notifications
        </h3>
        <ToggleItem
          title="Email Notifications"
          description="Receive notifications via email"
          checked={settings.emailNotifications}
          onChange={(val) => setSettings({ ...settings, emailNotifications: val })}
        />
      </div>

      <div className="mb-6">
        <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
          <Smartphone size={18} className="text-cyan-400" />
          Push Notifications
        </h3>
        <ToggleItem
          title="Push Notifications"
          description="Receive push notifications"
          checked={settings.pushNotifications}
          onChange={(val) => setSettings({ ...settings, pushNotifications: val })}
        />
      </div>

      <div className="glass-card p-4 rounded-xl space-y-3">
        <h4 className="text-white font-semibold">Activity Notifications</h4>
        <ToggleItem
          title="Likes"
          checked={settings.likeNotifications}
          onChange={(val) => setSettings({ ...settings, likeNotifications: val })}
          compact
        />
        <ToggleItem
          title="Comments"
          checked={settings.commentNotifications}
          onChange={(val) => setSettings({ ...settings, commentNotifications: val })}
          compact
        />
        <ToggleItem
          title="New Followers"
          checked={settings.followNotifications}
          onChange={(val) => setSettings({ ...settings, followNotifications: val })}
          compact
        />
        <ToggleItem
          title="Messages"
          checked={settings.messageNotifications}
          onChange={(val) => setSettings({ ...settings, messageNotifications: val })}
          compact
        />
      </div>

      <button
        onClick={handleSaveSettings}
        disabled={loading}
        className="w-full py-3 rounded-xl bg-cyan-400 text-black font-semibold hover:bg-cyan-500 transition-all disabled:opacity-50"
      >
        {loading ? "Saving..." : "Save Settings"}
      </button>
    </div>
  );

  // Blocked Users Section
  const renderBlocked = () => (
    <div className="space-y-4">
      {blockedUsers.length === 0 ? (
        <div className="text-center py-12">
          <UserX size={48} className="mx-auto text-gray-600 mb-4" />
          <p className="text-gray-400">No blocked users</p>
        </div>
      ) : (
        blockedUsers.map(user => (
          <div key={user.id} className="glass-card p-4 rounded-xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src={user.avatar} alt={user.name} className="w-12 h-12 rounded-full" />
              <div>
                <h3 className="text-white font-semibold">{user.name}</h3>
                <p className="text-sm text-gray-400">@{user.handle}</p>
              </div>
            </div>
            <button
              onClick={() => handleUnblock(user.id)}
              className="px-4 py-2 rounded-full bg-gray-700 text-white hover:bg-gray-600 transition-all text-sm"
            >
              Unblock
            </button>
          </div>
        ))
      )}
    </div>
  );

  // Help Section
  const renderHelp = () => (
    <div className="space-y-2">
      <MenuItem title="Help Center" onClick={() => toast.info("Opening help center...")} />
      <MenuItem title="Contact Support" onClick={() => toast.info("Contact: support@loopync.com")} />
      <MenuItem title="Report a Problem" onClick={() => toast.info("Report feature coming soon")} />
      <MenuItem title="Terms of Service" onClick={() => setActiveSection("terms")} />
      <MenuItem title="Privacy Policy" onClick={() => setActiveSection("privacy-policy")} />
    </div>
  );

  // About Section
  const renderAbout = () => (
    <div className="space-y-6">
      <div className="text-center">
        <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
          <Globe size={32} className="text-white" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Loopync</h2>
        <p className="text-gray-400">Version 1.0.0</p>
      </div>

      <div className="glass-card p-6 rounded-xl">
        <p className="text-gray-300 text-center mb-4">
          India's Free-Speech Social × Vibe Video × Venues × Fintech Superapp
        </p>
        <div className="text-sm text-gray-400 space-y-2">
          <p>© 2025 Loopync</p>
          <p>Made with ❤️ in India</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="sticky top-0 z-10 glass-surface p-4 flex items-center gap-3">
          <button 
            onClick={() => activeSection === "main" ? navigate(-1) : setActiveSection("main")}
            className="text-cyan-400"
          >
            <ArrowLeft size={24} />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white">
              {activeSection === "main" && "Settings"}
              {activeSection === "profile" && "Edit Profile"}
              {activeSection === "account" && "Account Settings"}
              {activeSection === "security" && "Security"}
              {activeSection === "privacy" && "Privacy"}
              {activeSection === "notifications" && "Notifications"}
              {activeSection === "blocked" && "Blocked Users"}
              {activeSection === "help" && "Help & Support"}
              {activeSection === "about" && "About"}
            </h1>
          </div>
        </div>

        {/* Content */}
        <div className="p-4">
          {activeSection === "main" && renderMainMenu()}
          {activeSection === "profile" && renderProfile()}
          {activeSection === "account" && renderAccount()}
          {activeSection === "security" && renderSecurity()}
          {activeSection === "privacy" && renderPrivacy()}
          {activeSection === "notifications" && renderNotifications()}
          {activeSection === "blocked" && renderBlocked()}
          {activeSection === "help" && renderHelp()}
          {activeSection === "about" && renderAbout()}
        </div>
      </div>
    </div>
  );
};

// Helper Components
const MenuItem = ({ icon, title, badge, onClick, danger }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center justify-between p-4 rounded-xl glass-card hover:bg-gray-800/50 transition-all ${
      danger ? 'text-red-400' : 'text-white'
    }`}
  >
    <div className="flex items-center gap-3">
      {icon}
      <span className="font-medium">{title}</span>
    </div>
    <div className="flex items-center gap-2">
      {badge && (
        <span className="px-2 py-1 rounded-full bg-cyan-400 text-black text-xs font-semibold">
          {badge}
        </span>
      )}
      <ChevronRight size={20} className="text-gray-400" />
    </div>
  </button>
);

const ToggleItem = ({ title, description, checked, onChange, compact }) => (
  <div className={`flex items-center justify-between ${compact ? 'py-2' : 'glass-card p-4 rounded-xl'}`}>
    <div className="flex-1">
      <h3 className="text-white font-medium">{title}</h3>
      {description && <p className="text-sm text-gray-400 mt-1">{description}</p>}
    </div>
    <button
      onClick={() => onChange(!checked)}
      className={`relative w-12 h-6 rounded-full transition-all ${
        checked ? 'bg-cyan-400' : 'bg-gray-700'
      }`}
    >
      <div
        className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${
          checked ? 'right-1' : 'left-1'
        }`}
      />
    </button>
  </div>
);

export default Settings;
