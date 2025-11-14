import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ratingAPI, reviewAPI, restaurantAPI } from '../services/api';
import RestaurantCard from '../components/restaurant/RestaurantCard';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    ratingsCount: 0,
    reviewsCount: 0,
    favoriteCity: 'N/A'
  });
  const [recentRatings, setRecentRatings] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch user's ratings
      const ratingsResponse = await ratingAPI.getUserRatings();
      const ratings = Array.isArray(ratingsResponse) ? ratingsResponse : [];
      setRecentRatings(ratings.slice(0, 5));
      
      // Fetch recommendations
      const recsResponse = await restaurantAPI.getAll({ limit: 4 });
      const restaurants = recsResponse.restaurants || recsResponse || [];
      setRecommendations(Array.isArray(restaurants) ? restaurants : []);

      setStats({
        ratingsCount: ratings.length,
        reviewsCount: 0,
        favoriteCity: 'Dehradun'
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setRecentRatings([]);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard py-8 px-4">
      <div className="container-custom">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">
            Welcome back, <span className="text-gradient">{user?.username}!</span>
          </h1>
          <p className="text-lg opacity-70">Here's what's happening with your food journey</p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="card text-center">
            <div className="text-4xl mb-3">⭐</div>
            <div className="text-3xl font-bold text-gradient mb-2">{stats.ratingsCount}</div>
            <div className="opacity-70">Ratings Given</div>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-3">💬</div>
            <div className="text-3xl font-bold text-gradient mb-2">{stats.reviewsCount}</div>
            <div className="opacity-70">Reviews Written</div>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-3">🏙️</div>
            <div className="text-3xl font-bold text-gradient mb-2">{stats.favoriteCity}</div>
            <div className="opacity-70">Favorite City</div>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Recent Activity */}
          <div>
            <h2 className="text-2xl font-bold mb-6">Recent Ratings</h2>
            {recentRatings.length > 0 ? (
              <div className="space-y-4">
                {recentRatings.map((rating) => (
                  <div key={rating.rating_id} className="card flex items-center justify-between">
                    <div className="flex-1">
                      <Link 
                        to={`/restaurant/${rating.restaurant_id}`}
                        className="font-semibold hover:text-orange-500 transition-colors"
                      >
                        {rating.restaurant_name}
                      </Link>
                      <p className="text-sm opacity-70">
                        {new Date(rating.rating_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-2xl">
                      {'⭐'.repeat(rating.rating_value)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="card text-center py-12">
                <div className="text-5xl mb-4">⭐</div>
                <p className="text-lg opacity-70 mb-4">No ratings yet</p>
                <Link to="/discover" className="btn btn-primary">
                  Start Exploring
                </Link>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div>
            <h2 className="text-2xl font-bold mb-6">Quick Actions</h2>
            <div className="space-y-4">
              <Link to="/discover" className="card flex items-center gap-4 hover:border-orange-500 transition-all">
                <div className="text-4xl">🔍</div>
                <div>
                  <h3 className="font-semibold text-lg">Discover Restaurants</h3>
                  <p className="text-sm opacity-70">Find new places to eat</p>
                </div>
              </Link>
              <Link to="/analytics" className="card flex items-center gap-4 hover:border-orange-500 transition-all">
                <div className="text-4xl">📊</div>
                <div>
                  <h3 className="font-semibold text-lg">View Analytics</h3>
                  <p className="text-sm opacity-70">Explore food trends</p>
                </div>
              </Link>
              <Link to="/profile" className="card flex items-center gap-4 hover:border-orange-500 transition-all">
                <div className="text-4xl">👤</div>
                <div>
                  <h3 className="font-semibold text-lg">My Profile</h3>
                  <p className="text-sm opacity-70">Manage your account</p>
                </div>
              </Link>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="mt-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Recommended for You</h2>
            <Link to="/discover" className="text-orange-500 hover:underline">
              View All →
            </Link>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {recommendations.map((restaurant) => (
              <RestaurantCard key={restaurant.restaurant_id} restaurant={restaurant} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}