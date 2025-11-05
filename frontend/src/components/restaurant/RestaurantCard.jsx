import { Link } from 'react-router-dom';
import { useState } from 'react';

export default function RestaurantCard({ restaurant }) {
  const [isFavorite, setIsFavorite] = useState(false);

  const getRatingColor = (rating) => {
    if (rating >= 4.5) return 'bg-green-500';
    if (rating >= 4.0) return 'bg-green-400';
    if (rating >= 3.5) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  const getPriceDisplay = (price) => {
    if (!price) return '₹₹';
    if (price < 500) return '₹';
    if (price < 1000) return '₹₹';
    if (price < 2000) return '₹₹₹';
    return '₹₹₹₹';
  };

  return (
    <div className="card group hover:shadow-2xl transition-all duration-300">
      <div className="flex gap-4">
        {/* Restaurant Image Placeholder */}
        <div className="w-32 h-32 rounded-lg bg-gradient-to-br from-orange-400 to-pink-600 flex-shrink-0 flex items-center justify-center text-5xl">
          🍽️
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <Link
              to={`/restaurant/${restaurant.restaurant_id}`}
              className="font-bold text-lg group-hover:text-orange-500 transition-colors line-clamp-1"
            >
              {restaurant.name}
            </Link>
            <button
              onClick={() => setIsFavorite(!isFavorite)}
              className="text-2xl hover:scale-110 transition-transform flex-shrink-0 ml-2"
              aria-label="Add to favorites"
            >
              {isFavorite ? '❤️' : '🤍'}
            </button>
          </div>

          {/* Location */}
          <div className="flex items-center gap-2 text-sm opacity-70 mb-2">
            <span>📍</span>
            <span className="line-clamp-1">{restaurant.city}</span>
          </div>

          {/* Cuisines */}
          <div className="flex flex-wrap gap-2 mb-3">
            {restaurant.cuisines?.slice(0, 3).map((cuisine, idx) => (
              <span key={idx} className="badge badge-primary text-xs">
                {cuisine}
              </span>
            ))}
            {restaurant.cuisines?.length > 3 && (
              <span className="badge badge-primary text-xs">
                +{restaurant.cuisines.length - 3}
              </span>
            )}
          </div>

          {/* Footer Info */}
          <div className="flex items-center gap-4 text-sm">
            {/* Rating */}
            <div className="flex items-center gap-1">
              <span className={`${getRatingColor(restaurant.avg_rating)} text-white px-2 py-1 rounded font-bold`}>
                ⭐ {restaurant.avg_rating?.toFixed(1) || 'N/A'}
              </span>
              <span className="opacity-70">({restaurant.votes} votes)</span>
            </div>

            {/* Price */}
            <div className="flex items-center gap-1">
              <span className="font-bold text-orange-500">
                {getPriceDisplay(restaurant.price_range)}
              </span>
            </div>

            {/* Dining Type */}
            {restaurant.dining_type && (
              <div className="opacity-70">
                {restaurant.dining_type}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* View Details Link */}
      <Link
        to={`/restaurant/${restaurant.restaurant_id}`}
        className="mt-4 text-center w-full py-2 rounded-lg border-2 border-orange-500 text-orange-500 font-medium hover:bg-orange-500 hover:text-white transition-all duration-300"
      >
        View Details →
      </Link>
    </div>
  );
}