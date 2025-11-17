import { useState } from 'react';
import { reviewAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export function ReviewForm({ restaurantId, onSuccess, currentUserReview }) {
  const [reviewText, setReviewText] = useState(currentUserReview?.review_text || '');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const { isAuthenticated } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    
    if (!isAuthenticated) {
      setMessage('Please login to submit a review');
      return;
    }
    
    if (!reviewText.trim()) {
      setMessage('Please write a review');
      return;
    }

    setSubmitting(true);
    try {
      const response = await reviewAPI.create({
        restaurant_id: restaurantId,
        review_text: reviewText
      });
      
      setMessage(response.message || 'Review submitted successfully!');
      
      // Call success callback to refresh reviews list
      if (onSuccess) {
        // Small delay to ensure DB is updated
        setTimeout(() => {
          onSuccess();
        }, 500);
      }
      
      // If it's a new review (not update), clear the form
      if (!currentUserReview) {
        setTimeout(() => {
          setReviewText('');
        }, 2000);
      }
      
      // Clear message after 3 seconds
      setTimeout(() => {
        setMessage('');
      }, 3000);
      
    } catch (error) {
      setMessage(error.message || error.error || 'Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card mb-6">
      <h3 className="text-xl font-bold mb-4">
        {currentUserReview ? 'Update Your Review' : 'Write a Review'}
      </h3>
      
      {message && (
        <div className={`mb-4 p-3 rounded-lg ${
          message.includes('success') || message.includes('updated')
            ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-100'
            : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-100'
        }`}>
          {message}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <textarea
          value={reviewText}
          onChange={(e) => setReviewText(e.target.value)}
          placeholder="Share your experience at this restaurant... What did you like? What could be improved?"
          className="input min-h-32 mb-4"
          maxLength={500}
          disabled={submitting}
        />
        
        <div className="flex items-center justify-between">
          <span className="text-sm opacity-70">
            {reviewText.length}/500 characters
          </span>
          
          <div className="flex gap-3">
            {currentUserReview && reviewText !== currentUserReview.review_text && (
              <button
                type="button"
                onClick={() => setReviewText(currentUserReview.review_text)}
                className="btn btn-outline"
                disabled={submitting}
              >
                Reset
              </button>
            )}
            
            <button
              type="submit"
              disabled={submitting || !reviewText.trim()}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <>
                  <span className="spinner w-4 h-4 inline-block mr-2"></span>
                  Submitting...
                </>
              ) : currentUserReview ? (
                'Update Review'
              ) : (
                'Submit Review'
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}