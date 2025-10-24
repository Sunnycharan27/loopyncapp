import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import PostCard from "../components/PostCard";
import TopHeader from "../components/TopHeader";
import BottomNav from "../components/BottomNav";
import { Bookmark } from "lucide-react";

const BookmarksPage = () => {
  const { currentUser } = useContext(AuthContext);
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBookmarks();
  }, []);

  const fetchBookmarks = async () => {
    try {
      const res = await axios.get(`${API}/bookmarks/${currentUser.id}`);
      setBookmarks(res.data);
    } catch (error) {
      console.error("Failed to load bookmarks");
    } finally {
      setLoading(false);
    }
  };

  const handleUnbookmark = async (postId) => {
    try {
      await axios.post(`${API}/posts/${postId}/bookmark?userId=${currentUser.id}`);
      setBookmarks(bookmarks.filter(post => post.id !== postId));
    } catch (error) {
      console.error("Failed to unbookmark");
    }
  };

  return (
    <div className="min-h-screen pb-24 dark:bg-gradient-to-b dark:from-gray-900 dark:to-black light:bg-gray-50">
      <TopHeader title="Bookmarks" subtitle="Saved posts" />

      <div className="p-4">
        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading bookmarks...</div>
        ) : bookmarks.length === 0 ? (
          <div className="text-center py-12">
            <Bookmark size={48} className="mx-auto text-gray-600 mb-4" />
            <p className="text-gray-400">No bookmarks yet</p>
            <p className="text-sm text-gray-500 mt-2">Save posts to view them here</p>
          </div>
        ) : (
          <div className="space-y-4">
            {bookmarks.map(post => (
              <PostCard
                key={post.id}
                post={post}
                currentUser={currentUser}
                onLike={async () => {}}
                onRepost={async () => {}}
                onDelete={async () => {}}
              />
            ))}
          </div>
        )}
      </div>

      <BottomNav active="profile" />
    </div>
  );
};

export default BookmarksPage;