import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiInstance } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function Profile() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [profileData, setProfileData] = useState(null);
  const [activity, setActivity] = useState({ ratings: [], reviews: [] });
  
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || ''
  });

  const [preferences, setPreferences] = useState({
    favoriteCuisines: ['North Indian', 'Chinese'],
    dietaryPrefs: [],
    priceRange: '2'
  });

  useEffect(() => {
    fetchProfileData();
  }, []);

  useEffect(() => {
    if (activeTab === 'activity') {
      fetchActivity();
    }
  }, [activeTab]);

  const fetchProfileData = async () => {
    try {
      const data = await apiInstance.get('/profile');
      setProfileData(data);
      setFormData({
        username: data.username,
        email: data.email
      });
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchActivity = async () => {
    try {
      const data = await apiInstance.get('/profile/activity');
      setActivity(data);
    } catch (error) {
      console.error('Error fetching activity:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    
    try {
      const response = await apiInstance.post('/profile', formData);
      setMessage(response.message || 'Profile updated successfully!');
      setEditing(false);
      
      // Update local user data
      if (response.user) {
        localStorage.setItem('user', JSON.stringify(response.user));
      }
      
      // Refresh profile data
      fetchProfileData();
      
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(error.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCuisineToggle = (cuisine) => {
    setPreferences(prev => ({
      ...prev,
      favoriteCuisines: prev.favoriteCuisines.includes(cuisine)
        ? prev.favoriteCuisines.filter(c => c !== cuisine)
        : [...prev.favoriteCuisines, cuisine]
    }));
  };

  const handleDietaryPrefToggle = (pref) => {
    setPreferences(prev => ({
      ...prev,
      dietaryPrefs: prev.dietaryPrefs.includes(pref)
        ? prev.dietaryPrefs.filter(p => p !== pref)
        : [...prev.dietaryPrefs, pref]
    }));
  };

  const savePreferences = () => {
    // Save to localStorage for now (could be moved to backend)
    localStorage.setItem('userPreferences', JSON.stringify(preferences));
    setMessage('Preferences saved successfully!');
    setTimeout(() => setMessage(''), 3000);
  };

  // Load preferences from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('userPreferences');
    if (saved) {
      try {
        setPreferences(JSON.parse(saved));
      } catch (e) {
        console.error('Error loading preferences:', e);
      }
    }
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="profile-page py-8 px-4">
      <div className="container-custom max-w-4xl">
        {/* Profile Header */}
        <div className="card mb-8">
          <div className="flex flex-col md:flex-row items-center gap-6">
            <div className="w-32 h-32 rounded-full bg-gradient-to-r from-orange-400 to-pink-600 flex items-center justify-center text-white font-bold text-5xl">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-3xl font-bold mb-2">{user?.username}</h1>
              <p className="opacity-70 mb-4">{user?.email}</p>
              {profileData && (
                <div className="flex flex-wrap gap-4 justify-center md:justify-start">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gradient">
                      {profileData.stats?.ratings_count || 0}
                    </div>
                    <div className="text-sm opacity-70">Ratings</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gradient">
                      {profileData.stats?.reviews_count || 0}
                    </div>
                    <div className="text-sm opacity-70">Reviews</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gradient">
                      {profileData.stats?.favorite_city || 'N/A'}
                    </div>
                    <div className="text-sm opacity-70">Favorite City</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Global Success/Error Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.includes('success') 
              ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-100'
              : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-100'
          }`}>
            {message}
          </div>
        )}

        {/* Tabs */}
        <div className="mb-8">
          <div className="flex gap-4 border-b overflow-x-auto" style={{ borderColor: 'var(--border)' }}>
            {['profile', 'activity', 'preferences'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-4 px-6 font-medium transition-colors whitespace-nowrap ${
                  activeTab === tab
                    ? 'border-b-2 border-orange-500 text-orange-500'
                    : 'opacity-70 hover:opacity-100'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'profile' && (
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Profile Information</h2>
              {!editing ? (
                <button onClick={() => setEditing(true)} className="btn btn-outline">
                  ✏️ Edit
                </button>
              ) : (
                <div className="flex gap-2">
                  <button 
                    onClick={handleSave} 
                    disabled={saving}
                    className="btn btn-primary disabled:opacity-50"
                  >
                    {saving ? 'Saving...' : 'Save'}
                  </button>
                  <button 
                    onClick={() => {
                      setEditing(false);
                      setFormData({
                        username: profileData.username,
                        email: profileData.email
                      });
                    }} 
                    className="btn btn-outline"
                    disabled={saving}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">Username</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  disabled={!editing}
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  disabled={!editing}
                  className="input"
                />
              </div>

              {profileData && (
                <div>
                  <label className="block text-sm font-medium mb-2">Member Since</label>
                  <input
                    type="text"
                    value={new Date(profileData.registration_date).toLocaleDateString('en-IN', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                    disabled
                    className="input opacity-70"
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'activity' && (
          <div className="space-y-6">
            {/* Recent Ratings */}
            <div className="card">
              <h3 className="text-xl font-bold mb-4">Recent Ratings</h3>
              {activity.ratings.length > 0 ? (
                <div className="space-y-3">
                  {activity.ratings.slice(0, 5).map((rating) => (
                    <div key={rating.rating_id} className="flex items-center justify-between py-3 border-b last:border-b-0" style={{ borderColor: 'var(--border)' }}>
                      <div>
                        <p className="font-medium">{rating.restaurant_name}</p>
                        <p className="text-sm opacity-70">
                          {new Date(rating.rating_date).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-2xl text-orange-500">★</span>
                        <span className="text-xl font-bold">{rating.rating_value.toFixed(1)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center py-8 opacity-70">No ratings yet</p>
              )}
            </div>

            {/* Recent Reviews */}
            <div className="card">
              <h3 className="text-xl font-bold mb-4">Recent Reviews</h3>
              {activity.reviews.length > 0 ? (
                <div className="space-y-4">
                  {activity.reviews.slice(0, 3).map((review) => (
                    <div key={review.review_id} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <p className="font-medium mb-2">{review.restaurant_name}</p>
                      <p className="text-sm opacity-80 mb-2">{review.review_text}</p>
                      <p className="text-xs opacity-60">
                        {new Date(review.review_date).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center py-8 opacity-70">No reviews yet</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'preferences' && (
          <div className="card">
            <h2 className="text-2xl font-bold mb-6">Food Preferences</h2>
            <div className="space-y-6">
              {/* Favorite Cuisines */}
              <div>
                <label className="block text-sm font-medium mb-3">Favorite Cuisines</label>
                <div className="flex flex-wrap gap-2">
                  {['North Indian', 'South Indian', 'Chinese', 'Italian', 'Mexican', 'Thai', 'Continental', 'Fast Food'].map((cuisine) => (
                    <button
                      key={cuisine}
                      onClick={() => handleCuisineToggle(cuisine)}
                      className={`badge ${
                        preferences.favoriteCuisines.includes(cuisine)
                          ? 'bg-orange-500 text-white'
                          : 'badge-primary'
                      } hover:bg-orange-500 hover:text-white transition-colors cursor-pointer`}
                    >
                      {preferences.favoriteCuisines.includes(cuisine) && '✓ '}
                      {cuisine}
                    </button>
                  ))}
                </div>
              </div>

              {/* Dietary Preferences */}
              <div>
                <label className="block text-sm font-medium mb-3">Dietary Preferences</label>
                <div className="space-y-2">
                  {['Vegetarian', 'Non-Vegetarian', 'Vegan', 'Gluten-Free', 'Jain'].map((pref) => (
                    <label key={pref} className="flex items-center gap-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 p-2 rounded">
                      <input
                        type="checkbox"
                        checked={preferences.dietaryPrefs.includes(pref)}
                        onChange={() => handleDietaryPrefToggle(pref)}
                        className="w-5 h-5"
                      />
                      <span>{pref}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Price Range Preference */}
              <div>
                <label className="block text-sm font-medium mb-3">Price Range Preference</label>
                <select 
                  className="input"
                  value={preferences.priceRange}
                  onChange={(e) => setPreferences({...preferences, priceRange: e.target.value})}
                >
                  <option value="1">Budget (₹)</option>
                  <option value="2">Moderate (₹₹)</option>
                  <option value="3">Premium (₹₹₹)</option>
                  <option value="4">Luxury (₹₹₹₹)</option>
                </select>
              </div>

              <button onClick={savePreferences} className="btn btn-primary w-full">
                Save Preferences
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}