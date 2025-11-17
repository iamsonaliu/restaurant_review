import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { restaurantAPI, reviewAPI, ratingAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { RatingForm } from '../components/restaurant/RatingForm';
import { ReviewForm } from '../components/restaurant/ReviewForm';
import LoadingSpinner from '../components/common/LoadingSpinner';

function getRandomFoodImage(restaurant) {
  const IMAGES = [
    "https://images.pexels.com/photos/70497/pexels-photo-70497.jpeg",
    "https://images.pexels.com/photos/461198/pexels-photo-461198.jpeg",
    "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg",
    "https://images.pexels.com/photos/958545/pexels-photo-958545.jpeg",
    "https://images.pexels.com/photos/109274/pexels-photo-109274.jpeg",
    "https://images.pexels.com/photos/1639561/pexels-photo-1639561.jpeg",
    "https://images.pexels.com/photos/277253/pexels-photo-277253.jpeg",
    "https://images.pexels.com/photos/616353/pexels-photo-616353.jpeg",
    "https://images.pexels.com/photos/675951/pexels-photo-675951.jpeg",
    "https://images.pexels.com/photos/1624487/pexels-photo-1624487.jpeg",
    "https://images.pexels.com/photos/262978/pexels-photo-262978.jpeg",
    "https://images.pexels.com/photos/260922/pexels-photo-260922.jpeg",
    "https://images.pexels.com/photos/941861/pexels-photo-941861.jpeg",
    "https://images.pexels.com/photos/1128678/pexels-photo-1128678.jpeg",
    "https://images.pexels.com/photos/245535/pexels-photo-245535.jpeg",
    "https://images.pexels.com/photos/6267/menu-restaurant.jpg"
  ];

  const seed = restaurant.restaurant_id || restaurant.name || "default";
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = (hash << 5) - hash + seed.charCodeAt(i);
    hash |= 0;
  }

  const index = Math.abs(hash) % IMAGES.length;
  return IMAGES[index] + "?auto=compress&cs=tinysrgb&w=600";
}

export default function RestaurantDetail() {
  const { id } = useParams();
  const { isAuthenticated, user } = useAuth();
  const [restaurant, setRestaurant] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [userRating, setUserRating] = useState(null);
  const [userReview, setUserReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    fetchAllData();
  }, [id, refreshKey]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchUserData();
    }
  }, [id, isAuthenticated]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchRestaurantDetails(),
        fetchReviews()
      ]);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRestaurantDetails = async () => {
    try {
      const response = await restaurantAPI.getById(id);
      setRestaurant(response || null);
    } catch (error) {
      console.error('Error fetching restaurant:', error);
      setRestaurant(null);
    }
  };

  const fetchReviews = async () => {
    try {
      const response = await reviewAPI.getByRestaurant(id);
      setReviews(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error fetching reviews:', error);
      setReviews([]);
    }
  };

  const fetchUserData = async () => {
    if (!isAuthenticated) return;
    
    try {
      // Fetch user's ratings to find if they rated this restaurant
      const userRatings = await ratingAPI.getUserRatings();
      const thisRating = userRatings.find(r => r.restaurant_id === id);
      setUserRating(thisRating || null);

      // Find user's review in the reviews list
      const thisReview = reviews.find(r => r.user_id === user?.user_id);
      setUserReview(thisReview || null);
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  const handleRatingSuccess = () => {
    // Refresh restaurant details to get updated average
    fetchRestaurantDetails();
    // Refresh user data
    if (isAuthenticated) {
      fetchUserData();
    }
    // Force re-render
    setRefreshKey(prev => prev + 1);
  };

  const handleReviewSuccess = () => {
    // Refresh reviews list
    fetchReviews();
    // Refresh user data
    if (isAuthenticated) {
      fetchUserData();
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!restaurant) {
    return (
      <div className="container-custom py-12 text-center">
        <div className="text-6xl mb-4">🍽️</div>
        <h2 className="text-2xl font-bold mb-4">Restaurant not found</h2>
        <Link to="/discover" className="btn btn-primary">
          Back to Discover
        </Link>
      </div>
    );
  }

  const getRatingColor = (rating) => {
    if (rating >= 4.5) return 'bg-green-500';
    if (rating >= 4.0) return 'bg-green-400';
    if (rating >= 3.5) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  const getPriceDisplay = (price) => {
    if (!price) return 2;
    if (price < 500) return 1;
    if (price < 1000) return 2;
    if (price < 2000) return 3;
    return 4;
  };

  return (
    <div className="restaurant-detail py-8 px-4">
      <div className="container-custom">
        {/* Breadcrumb */}
        <div className="mb-6 flex items-center gap-2 text-sm opacity-70">
          <Link to="/" className="hover:text-orange-500">Home</Link>
          <span>→</span>
          <Link to="/discover" className="hover:text-orange-500">Discover</Link>
          <span>→</span>
          <span>{restaurant.name}</span>
        </div>

        {/* Header */}
        <div className="card mb-8">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="w-full md:w-48 h-48 rounded-lg overflow-hidden shadow-sm">
              <img
                src={getRandomFoodImage(restaurant)}
                alt={restaurant.name}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>

            <div className="flex-1">
              <h1 className="text-4xl font-bold mb-4">{restaurant.name}</h1>
              
              <div className="flex flex-wrap gap-3 mb-4">
                <div className={`${getRatingColor(restaurant.avg_rating)} text-white px-4 py-2 rounded-lg font-bold text-lg flex items-center gap-1`}>
                  <span>★</span>
                  <span>{restaurant.avg_rating?.toFixed(1) || 'N/A'}</span>
                </div>
                <div className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center gap-2">
                  <span>📊</span>
                  <span>{restaurant.votes} ratings</span>
                </div>
                <div className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center gap-2">
                  <span>💬</span>
                  <span>{reviews.length} reviews</span>
                </div>
              </div>

              <div className="flex items-center gap-3 mb-4">
                <div className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center gap-2">
                  <span>📍</span>
                  <span>{restaurant.city}</span>
                </div>
                {restaurant.dining_type && (
                  <div className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                    {restaurant.dining_type}
                  </div>
                )}
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                {restaurant.cuisines?.map((cuisine, idx) => (
                  <span key={idx} className="badge badge-primary">
                    {cuisine}
                  </span>
                ))}
              </div>

              <div className="space-y-2 mb-4 text-sm opacity-80">
                <div className="flex items-center gap-2">
                  <span>💰</span>
                  <span>Price Level:</span>
                  <div className="flex items-center gap-0.5">
                    {[...Array(4)].map((_, i) => (
                      <span 
                        key={i} 
                        className={`${i < getPriceDisplay(restaurant.price_range) ? 'text-orange-500' : 'text-gray-300 dark:text-gray-600'}`}
                      >
                        ●
                      </span>
                    ))}
                  </div>
                  <span className="text-xs opacity-60">(₹{restaurant.price_range || 500} for two)</span>
                </div>
              </div>

              {restaurant.address && (
                <p className="opacity-70 mb-4 text-sm">
                  📍 {restaurant.address}
                </p>
              )}

              {/* Action buttons */}
              <div className="flex flex-wrap gap-3">
                {restaurant.website_url && restaurant.website_url.trim() !== '' && (
                  <a
                    href={restaurant.website_url.startsWith('http') ? restaurant.website_url : `https://${restaurant.website_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-primary flex items-center gap-2"
                  >
                    <span>🌐</span>
                    <span>Visit Website</span>
                  </a>
                )}
                {restaurant.phone_number && (
                  <a
                    href={`tel:${restaurant.phone_number}`}
                    className="btn btn-outline flex items-center gap-2"
                  >
                    <span>📞</span>
                    <span>Call</span>
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="flex gap-4 border-b overflow-x-auto" style={{ borderColor: 'var(--border)' }}>
            <button
              onClick={() => setActiveTab('overview')}
              className={`pb-4 px-6 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'overview'
                  ? 'border-b-2 border-orange-500 text-orange-500'
                  : 'opacity-70 hover:opacity-100'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('reviews')}
              className={`pb-4 px-6 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'reviews'
                  ? 'border-b-2 border-orange-500 text-orange-500'
                  : 'opacity-70 hover:opacity-100'
              }`}
            >
              Reviews ({reviews.length})
            </button>
            {isAuthenticated && (
              <button
                onClick={() => setActiveTab('rate')}
                className={`pb-4 px-6 font-medium transition-colors whitespace-nowrap ${
                  activeTab === 'rate'
                    ? 'border-b-2 border-orange-500 text-orange-500'
                    : 'opacity-70 hover:opacity-100'
                }`}
              >
                {userRating || userReview ? 'My Rating & Review' : 'Rate & Review'}
              </button>
            )}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid md:grid-cols-2 gap-8">
            <div className="card">
              <h3 className="text-2xl font-bold mb-4">About</h3>
              <p className="opacity-80 leading-relaxed">
                {restaurant.name} is a popular dining destination in {restaurant.city}, 
                known for its exceptional {restaurant.cuisines?.[0]} cuisine. 
                With an average rating of {restaurant.avg_rating?.toFixed(1)}, 
                it has become a favorite among food lovers.
              </p>
            </div>

            <div className="card">
              <h3 className="text-2xl font-bold mb-4">Quick Info</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">🍽️</span>
                  <div>
                    <p className="font-medium">Cuisines</p>
                    <p className="opacity-70 text-sm">{restaurant.cuisines?.join(', ')}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-2xl">📍</span>
                  <div>
                    <p className="font-medium">Location</p>
                    <p className="opacity-70 text-sm">{restaurant.city}, {restaurant.region || 'Uttarakhand'}</p>
                  </div>
                </div>
                {restaurant.timings && (
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">🕐</span>
                    <div>
                      <p className="font-medium">Timings</p>
                      <p className="opacity-70 text-sm">{restaurant.timings}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reviews' && (
          <div>
            {reviews.length > 0 ? (
              <div className="space-y-4">
                {reviews.map((review) => (
                  <div key={review.review_id} className="card">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-r from-orange-400 to-pink-600 flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                        {review.username?.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <h4 className="font-semibold">{review.username}</h4>
                            <p className="text-sm opacity-70">
                              {new Date(review.review_date).toLocaleDateString('en-IN', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                              })}
                            </p>
                          </div>
                          {review.user_id === user?.user_id && (
                            <span className="badge badge-primary text-xs">Your Review</span>
                          )}
                        </div>
                        <p className="leading-relaxed">{review.review_text}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="card text-center py-12">
                <div className="text-5xl mb-4">💬</div>
                <p className="text-xl opacity-70 mb-4">No reviews yet</p>
                {isAuthenticated ? (
                  <button 
                    onClick={() => setActiveTab('rate')}
                    className="btn btn-primary"
                  >
                    Be the first to review!
                  </button>
                ) : (
                  <Link to="/login" className="btn btn-primary">
                    Login to write a review
                  </Link>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'rate' && isAuthenticated && (
          <div className="max-w-2xl mx-auto">
            <RatingForm 
              restaurantId={id} 
              onSuccess={handleRatingSuccess}
              currentUserRating={userRating?.rating_value}
            />
            <ReviewForm 
              restaurantId={id}
              onSuccess={handleReviewSuccess}
              currentUserReview={userReview}
            />
          </div>
        )}
      </div>
    </div>
  );
}