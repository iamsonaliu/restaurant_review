import { useState } from 'react';
import { ratingAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export function RatingForm({ restaurantId, onSuccess }) {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const { isAuthenticated } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      alert('Please login to submit a rating');
      return;
    }
    if (rating === 0) {
      alert('Please select a rating');
      return;
    }

    setSubmitting(true);
    try {
      await ratingAPI.create({
        restaurant_id: restaurantId,
        rating_value: rating
      });
      alert('Rating submitted successfully!');
      if (onSuccess) onSuccess();
      setRating(0);
    } catch (error) {
      alert(error.message || error.error || 'Failed to submit rating');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card mb-6">
      <h3 className="text-xl font-bold mb-4">Rate this Restaurant</h3>
      <form onSubmit={handleSubmit}>
        <div className="flex items-center gap-3 mb-4 select-none rating-stars">
          {[1, 2, 3, 4, 5].map((star) => (
            <span
              key={star}
              onClick={() => setRating(star)}
              onMouseEnter={() => setHover(star)}
              onMouseLeave={() => setHover(0)}
              className="text-4xl cursor-pointer"
              style={{ userSelect: 'none' }}
            >
              {star <= (hover || rating) ? '⭐' : '☆'}
            </span>
          ))}
          {rating > 0 && (
            <span className="ml-2 font-semibold text-lg">{rating}.0</span>
          )}
        </div>

        <button
          type="submit"
          disabled={submitting || rating === 0}
          className="btn btn-primary disabled:opacity-50"
        >
          {submitting ? 'Submitting...' : 'Submit Rating'}
        </button>
      </form>
    </div>
  );
}
