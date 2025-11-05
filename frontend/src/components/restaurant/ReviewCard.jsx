export function ReviewCard({ review }) {
  const [helpful, setHelpful] = useState(false);

  return (
    <div className="card mb-4">
      <div className="flex items-start gap-4">
        {/* User Avatar */}
        <div className="w-12 h-12 rounded-full bg-gradient-to-r from-orange-400 to-pink-600 flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
          {review.username?.charAt(0).toUpperCase()}
        </div>

        <div className="flex-1">
          {/* Header */}
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
          </div>

          {/* Review Text */}
          <p className="mb-3 leading-relaxed">{review.review_text}</p>

          {/* Actions */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => setHelpful(!helpful)}
              className={`text-sm flex items-center gap-1 ${helpful ? 'text-orange-500' : 'opacity-70'} hover:opacity-100 transition-opacity`}
            >
              👍 Helpful ({review.helpful_count + (helpful ? 1 : 0)})
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}