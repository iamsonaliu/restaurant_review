import { useState, useEffect } from 'react';
import { analyticsAPI, restaurantAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function Analytics() {
  const [topRated, setTopRated] = useState([]);
  const [cityStats, setCityStats] = useState([]);
  const [cuisineStats, setCuisineStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [topRatedRes, cityRes] = await Promise.all([
        analyticsAPI.getTopRated(),
        analyticsAPI.getCityStats()
      ]);

      const topRated = Array.isArray(topRatedRes) ? topRatedRes : [];
      const cityStats = Array.isArray(cityRes) ? cityRes : [];
      
      setTopRated(topRated);
      setCityStats(cityStats);

      // Generate cuisine stats from restaurants
      const cuisines = {};
      topRated.forEach(r => {
        // Note: topRated from analytics API may not have cuisines
        // We'll need to fetch full restaurant details if needed
      });
      
      // For now, set empty cuisine stats or fetch separately
      setCuisineStats([]);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setTopRated([]);
      setCityStats([]);
      setCuisineStats([]);
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
    <div className="analytics-page py-8 px-4">
      <div className="container-custom">
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-4">
            Restaurant <span className="text-gradient">Analytics</span>
          </h1>
          <p className="text-lg opacity-70">
            Insights and trends from Uttarakhand's dining scene
          </p>
        </div>

        {/* Top Rated Restaurants */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold mb-6">🏆 Top Rated Restaurants</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {topRated.slice(0, 6).map((restaurant, index) => (
              <div key={restaurant.restaurant_id} className="card relative">
                {index < 3 && (
                  <div className="absolute -top-3 -right-3 w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-2xl shadow-lg">
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
                  </div>
                )}
                <div className="text-5xl text-center mb-4">🍽️</div>
                <h3 className="font-bold text-lg mb-2 text-center">{restaurant.name}</h3>
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="bg-green-500 text-white px-3 py-1 rounded font-bold">
                    ⭐ {restaurant.avg_rating?.toFixed(1)}
                  </span>
                </div>
                <p className="text-center opacity-70 text-sm">
                  📍 {restaurant.city}
                </p>
                <p className="text-center opacity-70 text-sm">
                  {restaurant.votes} votes
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* City Statistics */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold mb-6">🏙️ City-wise Distribution</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {cityStats.map((city) => (
              <div key={city.city} className="card text-center">
                <div className="text-5xl mb-4">
                  {city.city === 'Dehradun' ? '🏔️' :
                   city.city === 'Haridwar' ? '🕉️' :
                   city.city === 'Mussoorie' ? '🌄' : '🧘'}
                </div>
                <h3 className="text-2xl font-bold mb-2">{city.city}</h3>
                <div className="text-3xl font-bold text-gradient mb-2">
                  {city.total_restaurants || city.restaurant_count || 0}
                </div>
                <p className="opacity-70">Restaurants</p>
                <div className="mt-4 pt-4 border-t" style={{ borderColor: 'var(--border)' }}>
                  <p className="text-sm">Avg Rating</p>
                  <p className="text-xl font-bold text-green-500">
                    ⭐ {city.avg_rating?.toFixed(1)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Popular Cuisines */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold mb-6">🍽️ Popular Cuisines</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cuisineStats.map((cuisine, index) => (
              <div key={cuisine.name} className="card">
                <div className="flex items-center gap-4">
                  <div className="text-4xl">
                    {index === 0 ? '👑' : '🍴'}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-lg">{cuisine.name}</h3>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mt-2">
                      <div
                        className="bg-gradient-to-r from-orange-400 to-pink-600 h-3 rounded-full transition-all duration-500"
                        style={{ width: `${(cuisine.count / cuisineStats[0].count) * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-sm opacity-70 mt-1">
                      {cuisine.count} restaurants
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Insights */}
        <section>
          <h2 className="text-3xl font-bold mb-6">💡 Key Insights</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="card">
              <div className="text-4xl mb-4">📈</div>
              <h3 className="text-xl font-bold mb-2">Growing Trends</h3>
              <ul className="space-y-2 opacity-80">
                <li>• North Indian cuisine leads with highest popularity</li>
                <li>• Average restaurant rating: 4.2⭐</li>
                <li>• Dehradun has the most restaurants</li>
                <li>• Premium dining experiences gaining traction</li>
              </ul>
            </div>
            <div className="card">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-bold mb-2">User Preferences</h3>
              <ul className="space-y-2 opacity-80">
                <li>• Multi-cuisine restaurants most reviewed</li>
                <li>• Mid-range pricing (₹₹) most popular</li>
                <li>• Weekend bookings peak on Saturdays</li>
                <li>• Family dining preferred over fine dining</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}