import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ratingAPI, restaurantAPI,reviewAPI} from '../services/api';
import RestaurantCard from '../components/restaurant/RestaurantCard';
import LoadingSpinner from '../components/common/LoadingSpinner';

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

// Fetch user's reviews (correct API)
       const reviewResponse = await reviewAPI.getUserReviews();
    const reviews = Array.isArray(reviewResponse) ? reviewResponse : [];
      
      // Get most common city from ratings
      let favoriteCity = 'Dehradun';
      if (ratings.length > 0) {
        const cityCount = {};
        ratings.forEach(r => {
          // We'll get city from recommendations or default
        });
      }
      
      setRecentRatings(ratings.slice(0, 5));
      
      // Fetch recommendations based on user's ratings
      const recsResponse = await restaurantAPI.getAll({ 
        limit: 4,
        min_rating: ratings.length > 0 ? 3.5 : 0
      });
      const restaurants = recsResponse.restaurants || recsResponse || [];
      setRecommendations(Array.isArray(restaurants) ? restaurants : []);

      setStats({
        ratingsCount: ratings.length,
        reviewsCount: reviews.length, // Can be updated if we add review count API
        favoriteCity: favoriteCity
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setRecentRatings([]);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

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
          <div className="card text-center hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-3">⭐</div>
            <div className="text-3xl font-bold text-gradient mb-2">{stats.ratingsCount}</div>
            <div className="opacity-70">Ratings Given</div>
          </div>
          <div className="card text-center hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-3">💬</div>
            <div className="text-3xl font-bold text-gradient mb-2">{stats.reviewsCount}</div>
            <div className="opacity-70">Reviews Written</div>
          </div>
          <div className="card text-center hover:shadow-lg transition-shadow">
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
                  <div key={rating.rating_id} className="card flex items-center justify-between hover:shadow-lg transition-shadow">
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
                    <div className="flex items-center gap-1">
                      <span className="text-2xl text-orange-500">★</span>
                      <span className="text-xl font-bold">{rating.rating_value.toFixed(1)}</span>
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
              <Link to="/discover" className="card flex items-center gap-4 hover:border-orange-500 hover:shadow-lg transition-all">
                <div className="text-4xl">🔍</div>
                <div>
                  <h3 className="font-semibold text-lg">Discover Restaurants</h3>
                  <p className="text-sm opacity-70">Find new places to eat</p>
                </div>
              </Link>
              <Link to="/analytics" className="card flex items-center gap-4 hover:border-orange-500 hover:shadow-lg transition-all">
                <div className="text-4xl">📊</div>
                <div>
                  <h3 className="font-semibold text-lg">View Analytics</h3>
                  <p className="text-sm opacity-70">Explore food trends</p>
                </div>
              </Link>
              <Link to="/profile" className="card flex items-center gap-4 hover:border-orange-500 hover:shadow-lg transition-all">
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
        {recommendations.length > 0 && (
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
        )}
      </div>
    </div>
  );
}