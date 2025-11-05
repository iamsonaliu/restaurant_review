export function ReviewForm({ restaurantId, onSuccess }) {
  const [reviewText, setReviewText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { isAuthenticated } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      alert('Please login to submit a review');
      return;
    }
    if (!reviewText.trim()) {
      alert('Please write a review');
      return;
    }

    setSubmitting(true);
    try {
      await reviewAPI.create({
        restaurant_id: restaurantId,
        review_text: reviewText
      });
      alert('Review submitted successfully!');
      if (onSuccess) onSuccess();
      setReviewText('');
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card mb-6">
      <h3 className="text-xl font-bold mb-4">Write a Review</h3>
      <form onSubmit={handleSubmit}>
        <textarea
          value={reviewText}
          onChange={(e) => setReviewText(e.target.value)}
          placeholder="Share your experience at this restaurant..."
          className="input min-h-32 mb-4"
          maxLength={500}
        />
        <div className="flex items-center justify-between">
          <span className="text-sm opacity-70">
            {reviewText.length}/500 characters
          </span>
          <button
            type="submit"
            disabled={submitting || !reviewText.trim()}
            className="btn btn-primary disabled:opacity-50"
          >
            {submitting ? 'Submitting...' : 'Submit Review'}
          </button>
        </div>
      </form>
    </div>
  );
}