export function FilterSidebar({ filters, categories, cities, onFilterChange, onClearFilters }) {
  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold">Filters</h3>
        <button
          onClick={onClearFilters}
          className="text-sm text-orange-500 hover:underline"
        >
          Clear All
        </button>
      </div>

      {/* City Filter */}
      <div className="mb-6">
        <label className="block font-semibold mb-3">📍 City</label>
        <select
          value={filters.city}
          onChange={(e) => onFilterChange('city', e.target.value)}
          className="input"
        >
          <option value="">All Cities</option>
          {cities.map((city) => (
            <option key={city.city} value={city.city}>
              {city.city} ({city.count})
            </option>
          ))}
        </select>
      </div>

      {/* Cuisine Filter */}
      <div className="mb-6">
        <label className="block font-semibold mb-3">🍽️ Cuisine</label>
        <select
          value={filters.cuisine}
          onChange={(e) => onFilterChange('cuisine', e.target.value)}
          className="input"
        >
          <option value="">All Cuisines</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.name}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      {/* Rating Filter */}
      <div className="mb-6">
        <label className="block font-semibold mb-3">⭐ Minimum Rating</label>
        <div className="space-y-2">
          {[4.5, 4.0, 3.5, 3.0].map((rating) => (
            <label key={rating} className="flex items-center gap-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 p-2 rounded">
              <input
                type="radio"
                name="rating"
                checked={filters.min_rating === rating.toString()}
                onChange={() => onFilterChange('min_rating', rating.toString())}
                className="w-4 h-4"
              />
              <span>⭐ {rating} & above</span>
            </label>
          ))}
          <label className="flex items-center gap-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 p-2 rounded">
            <input
              type="radio"
              name="rating"
              checked={filters.min_rating === ''}
              onChange={() => onFilterChange('min_rating', '')}
              className="w-4 h-4"
            />
            <span>All Ratings</span>
          </label>
        </div>
      </div>
    </div>
  );
}

export default FilterSidebar;