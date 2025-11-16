import { Link } from 'react-router-dom';
import { useState } from 'react';

export default function RestaurantCard({ restaurant }) {
  const [isFavorite, setIsFavorite] = useState(false);

  const getRatingColor = (rating) => {
    if (rating >= 4.5) return 'text-green-600';
    if (rating >= 4.0) return 'text-green-500';
    if (rating >= 3.5) return 'text-yellow-600';
    return 'text-orange-500';
  };

  const getPriceLevel = (price) => {
    if (!price) return 2;
    if (price < 500) return 1;
    if (price < 1000) return 2;
    if (price < 2000) return 3;
    return 4;
  };

  return (
    <div className="card group hover:shadow-xl transition-all duration-300 relative overflow-hidden">
      {/* Subtle gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-orange-50 to-pink-50 dark:from-orange-950 dark:to-pink-950 opacity-0 group-hover:opacity-30 transition-opacity duration-300"></div>
      
      <div className="relative">
        <div className="flex gap-4">
          {/* Restaurant Image */}
          <div className="w-28 h-28 rounded-lg bg-gradient-to-br from-orange-100 to-pink-100 dark:from-orange-900 dark:to-pink-900 flex-shrink-0 flex items-center justify-center text-4xl overflow-hidden">
            🍽️
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-2">
              <Link
                to={`/restaurant/${restaurant.restaurant_id}`}
                className="font-bold text-lg group-hover:text-orange-500 transition-colors line-clamp-2 flex-1 mr-2"
              >
                {restaurant.name}
              </Link>
              <button
                onClick={() => setIsFavorite(!isFavorite)}
                className="text-xl hover:scale-110 transition-transform flex-shrink-0"
                aria-label="Add to favorites"
              >
                {isFavorite ? '❤️' : '🤍'}
              </button>
            </div>

            {/* Location - More subtle */}
            <div className="flex items-center gap-1.5 text-sm opacity-60 mb-3">
              <span className="text-base">📍</span>
              <span>{restaurant.city}</span>
            </div>

            {/* Cuisines - More compact */}
            <div className="flex flex-wrap gap-1.5 mb-3">
              {restaurant.cuisines?.slice(0, 3).map((cuisine, idx) => (
                <span key={idx} className="text-xs px-2 py-0.5 rounded-full bg-orange-50 text-orange-700 dark:bg-orange-900 dark:text-orange-200">
                  {cuisine}
                </span>
              ))}
              {restaurant.cuisines?.length > 3 && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                  +{restaurant.cuisines.length - 3}
                </span>
              )}
            </div>

            {/* Footer Info - Cleaner layout */}
            <div className="flex items-center gap-4 text-sm">
              {/* Rating */}
              <div className="flex items-center gap-1">
                <span className={`font-bold ${getRatingColor(restaurant.avg_rating)}`}>
                  ★ {restaurant.avg_rating?.toFixed(1) || 'N/A'}
                </span>
                <span className="text-xs opacity-50">({restaurant.votes})</span>
              </div>

              {/* Price - Subtle dots instead of rupee signs */}
              <div className="flex items-center gap-0.5">
                {[...Array(4)].map((_, i) => (
                  <span 
                    key={i} 
                    className={`text-xs ${i < getPriceLevel(restaurant.price_range) ? 'text-orange-500' : 'text-gray-300 dark:text-gray-600'}`}
                  >
                    ●
                  </span>
                ))}
              </div>

              {/* Dining Type - More subtle */}
              {restaurant.dining_type && (
                <span className="text-xs opacity-50 truncate">
                  {restaurant.dining_type}
                </span>
              )}
            </div>
          </div>
        </div>

                  {/* Action buttons - Cleaner */}
        <div className="mt-4 flex gap-2">
          <Link
            to={`/restaurant/${restaurant.restaurant_id}`}
            className="flex-1 text-center py-2 rounded-lg bg-orange-500 text-white font-medium hover:bg-orange-600 transition-all duration-200 text-sm"
          >
            View Details
          </Link>
          
          {restaurant.website_url && restaurant.website_url.trim() !== '' && (
            <a
              href={restaurant.website_url.startsWith('http') ? restaurant.website_url : `https://${restaurant.website_url}`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 rounded-lg border-2 border-gray-300 dark:border-gray-600 hover:border-orange-500 hover:bg-orange-50 dark:hover:bg-orange-900 transition-all duration-200 text-sm flex items-center gap-1"
              title="Visit website"
            >
              <span className="text-base">🌐</span>
            </a>
          )}
        </div>
      </div>
    </div>
  );
}