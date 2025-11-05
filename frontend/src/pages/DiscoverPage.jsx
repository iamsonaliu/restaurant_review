import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { restaurantAPI } from '../services/api';
import RestaurantCard from '../components/restaurant/RestaurantCard';
import FilterSidebar from '../components/restaurant/FilterSidebar';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function DiscoverPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    city: searchParams.get('city') || '',
    cuisine: searchParams.get('cuisine') || '',
    min_rating: searchParams.get('min_rating') || '',
    price_range: searchParams.get('price_range') || '',
    search: searchParams.get('search') || ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [categories, setCategories] = useState([]);
  const [cities, setCities] = useState([]);

  useEffect(() => {
    fetchRestaurants();
    fetchCategories();
    fetchCities();
  }, [filters]);

  const fetchRestaurants = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.city) params.city = filters.city;
      if (filters.cuisine) params.cuisine = filters.cuisine;
      if (filters.min_rating) params.min_rating = filters.min_rating;
      if (filters.search) params.search = filters.search;
      
      const response = await restaurantAPI.getAll(params);
      setRestaurants(response.data);
    } catch (error) {
      console.error('Error fetching restaurants:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await restaurantAPI.getCategories();
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchCities = async () => {
    try {
      const response = await restaurantAPI.getCities();
      setCities(response.data);
    } catch (error) {
      console.error('Error fetching cities:', error);
    }
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    
    // Update URL params
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v) params.set(k, v);
    });
    setSearchParams(params);
  };

  const clearFilters = () => {
    setFilters({
      city: '',
      cuisine: '',
      min_rating: '',
      price_range: '',
      search: ''
    });
    setSearchParams({});
  };

  return (
    <div className="discover-page py-8 px-4">
      <div className="container-custom">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">
            Discover Restaurants
            {filters.city && <span className="text-gradient"> in {filters.city}</span>}
          </h1>
          <p className="text-lg opacity-70">
            Browse {restaurants.length}+ restaurants across Uttarakhand
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <div className="relative max-w-2xl">
            <input
              type="text"
              placeholder="Search restaurants by name..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="input pr-12"
            />
            <button className="absolute right-3 top-1/2 transform -translate-y-1/2 text-2xl">
              🔍
            </button>
          </div>
        </div>

        <div className="flex gap-8">
          {/* Filter Sidebar - Desktop */}
          <aside className="hidden lg:block w-80 flex-shrink-0">
            <div className="sticky top-24">
              <FilterSidebar
                filters={filters}
                categories={categories}
                cities={cities}
                onFilterChange={handleFilterChange}
                onClearFilters={clearFilters}
              />
            </div>
          </aside>

          {/* Mobile Filter Button */}
          <button
            className="lg:hidden fixed bottom-6 right-6 btn btn-primary shadow-lg z-10"
            onClick={() => setShowFilters(!showFilters)}
          >
            🎛️ Filters
          </button>

          {/* Mobile Filter Modal */}
          {showFilters && (
            <div className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end">
              <div className="w-full max-h-[80vh] overflow-y-auto bg-white dark:bg-gray-800 rounded-t-3xl p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-2xl font-bold">Filters</h3>
                  <button onClick={() => setShowFilters(false)} className="text-3xl">×</button>
                </div>
                <FilterSidebar
                  filters={filters}
                  categories={categories}
                  cities={cities}
                  onFilterChange={handleFilterChange}
                  onClearFilters={clearFilters}
                />
                <button
                  className="btn btn-primary w-full mt-6"
                  onClick={() => setShowFilters(false)}
                >
                  Apply Filters
                </button>
              </div>
            </div>
          )}

          {/* Main Content */}
          <main className="flex-1">
            {/* Active Filters */}
            {(filters.city || filters.cuisine || filters.min_rating) && (
              <div className="mb-6 flex flex-wrap gap-3">
                <span className="text-sm opacity-70">Active Filters:</span>
                {filters.city && (
                  <span className="badge badge-primary flex items-center gap-2">
                    📍 {filters.city}
                    <button onClick={() => handleFilterChange('city', '')}>×</button>
                  </span>
                )}
                {filters.cuisine && (
                  <span className="badge badge-primary flex items-center gap-2">
                    🍽️ {filters.cuisine}
                    <button onClick={() => handleFilterChange('cuisine', '')}>×</button>
                  </span>
                )}
                {filters.min_rating && (
                  <span className="badge badge-primary flex items-center gap-2">
                    ⭐ {filters.min_rating}+
                    <button onClick={() => handleFilterChange('min_rating', '')}>×</button>
                  </span>
                )}
                <button
                  onClick={clearFilters}
                  className="text-sm text-red-600 hover:underline"
                >
                  Clear All
                </button>
              </div>
            )}

            {/* Results */}
            {loading ? (
              <div className="flex justify-center py-20">
                <LoadingSpinner size="large" />
              </div>
            ) : restaurants.length > 0 ? (
              <div className="grid md:grid-cols-2 gap-6">
                {restaurants.map((restaurant) => (
                  <RestaurantCard key={restaurant.restaurant_id} restaurant={restaurant} />
                ))}
              </div>
            ) : (
              <div className="text-center py-20">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-2xl font-bold mb-2">No restaurants found</h3>
                <p className="opacity-70 mb-6">
                  Try adjusting your filters or search terms
                </p>
                <button onClick={clearFilters} className="btn btn-primary">
                  Clear Filters
                </button>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}