import { Link } from "react-router-dom";
import { useState } from "react";

function getRandomFoodImage(restaurant) {
  const IMAGES = [
    // Food Pexels
    "https://images.pexels.com/photos/70497/pexels-photo-70497.jpeg",
    "https://images.pexels.com/photos/461198/pexels-photo-461198.jpeg",
    "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg",
    "https://images.pexels.com/photos/958545/pexels-photo-958545.jpeg",
    "https://images.pexels.com/photos/109274/pexels-photo-109274.jpeg",
    "https://images.pexels.com/photos/1639561/pexels-photo-1639561.jpeg",
    "https://images.pexels.com/photos/70497/pexels-photo-70497.jpeg",
    "https://images.pexels.com/photos/277253/pexels-photo-277253.jpeg",
    "https://images.pexels.com/photos/616353/pexels-photo-616353.jpeg",
    "https://images.pexels.com/photos/675951/pexels-photo-675951.jpeg",
    "https://images.pexels.com/photos/1624487/pexels-photo-1624487.jpeg",
    "https://images.pexels.com/photos/958545/pexels-photo-958545.jpeg",

    // Restaurant interiors
    "https://images.pexels.com/photos/262978/pexels-photo-262978.jpeg",
    "https://images.pexels.com/photos/260922/pexels-photo-260922.jpeg",
    "https://images.pexels.com/photos/941861/pexels-photo-941861.jpeg",
    "https://images.pexels.com/photos/1128678/pexels-photo-1128678.jpeg",
    "https://images.pexels.com/photos/245535/pexels-photo-245535.jpeg",
    "https://images.pexels.com/photos/6267/menu-restaurant.jpg",
    "https://images.pexels.com/photos/262978/pexels-photo-262978.jpeg",
  ];

  // HASH the restaurant ID → get consistent image index
  const seed = restaurant.restaurant_id || restaurant.name;
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = (hash << 5) - hash + seed.charCodeAt(i);
    hash |= 0;
  }

  const index = Math.abs(hash) % IMAGES.length;
  return IMAGES[index] + "?auto=compress&cs=tinysrgb&w=600";
}


export default function RestaurantCard({ restaurant }) {
  const [isFavorite, setIsFavorite] = useState(false);


  const getRatingColor = (rating) => {
    if (rating >= 4.5) return "text-green-600";
    if (rating >= 4.0) return "text-green-500";
    if (rating >= 3.5) return "text-yellow-600";
    return "text-orange-500";
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
      <div className="absolute inset-0 bg-gradient-to-br from-orange-50 to-pink-50 opacity-0 group-hover:opacity-30 transition-opacity duration-300"></div>

      <div className="relative">
        <div className="flex gap-4">
          
          {/* Updated Restaurant Image */}
          <div className="w-28 h-28 rounded-lg overflow-hidden shadow-sm flex-shrink-0">
            <img
              src={getRandomFoodImage(restaurant)}
              alt={restaurant.name}
              className="w-full h-full object-cover"
            />
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
              >
                {isFavorite ? "❤️" : "🤍"}
              </button>
            </div>

            <div className="flex items-center gap-1.5 text-sm opacity-60 mb-3">
              <span className="text-base">📍</span>
              <span>{restaurant.city}</span>
            </div>

            <div className="flex flex-wrap gap-1.5 mb-3">
              {restaurant.cuisines?.slice(0, 3).map((cuisine, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-0.5 rounded-full bg-orange-50 text-orange-700"
                >
                  {cuisine}
                </span>
              ))}
              {restaurant.cuisines?.length > 3 && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                  +{restaurant.cuisines.length - 3}
                </span>
              )}
            </div>

            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1">
                <span className={`font-bold ${getRatingColor(restaurant.avg_rating)}`}>
                  ★ {restaurant.avg_rating?.toFixed(1) || "N/A"}
                </span>
                <span className="text-xs opacity-50">
                  ({restaurant.votes})
                </span>
              </div>

              <div className="flex items-center gap-0.5">
                {[...Array(4)].map((_, i) => (
                  <span
                    key={i}
                    className={`text-xs ${
                      i < getPriceLevel(restaurant.price_range)
                        ? "text-orange-500"
                        : "text-gray-300"
                    }`}
                  >
                    ●
                  </span>
                ))}
              </div>

              {restaurant.dining_type && (
                <span className="text-xs opacity-50 truncate">
                  {restaurant.dining_type}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="mt-4 flex gap-2">
          <Link
            to={`/restaurant/${restaurant.restaurant_id}`}
            className="flex-1 text-center py-2 rounded-lg bg-orange-500 text-white hover:bg-orange-600 transition-all duration-200 text-sm"
          >
            View Details
          </Link>

          {restaurant.website_url && (
            <a
              href={
                restaurant.website_url.startsWith("http")
                  ? restaurant.website_url
                  : `https://${restaurant.website_url}`
              }
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 rounded-lg border-2 border-gray-300 hover:border-orange-500 hover:bg-orange-50 transition-all duration-200 text-sm"
            >
              🌐
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
