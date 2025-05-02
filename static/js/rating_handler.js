document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('.rating-bar').forEach(ratingBar => {
    const bookId = ratingBar.getAttribute('data-book-id');
    const selectedRating = parseInt(ratingBar.getAttribute('data-selected-rating'), 10);
    const stars = ratingBar.querySelectorAll('.rating-star');

    // Highlight selected stars on page load
    stars.forEach(star => {
      const rating = parseInt(star.getAttribute('data-rating'), 10);
      if (rating <= selectedRating) {
        star.classList.add('selected');  // Make selected stars green
      }
    });

    // Attach event listeners to stars
    stars.forEach(star => {
      const starRating = parseInt(star.getAttribute('data-rating'), 10);

      // Handle click to set the rating
      star.addEventListener('click', function () {
        // Send the new rating to the backend
        fetch(`/book/${bookId}/update_rating`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ rating: starRating }),
        })
        .then(response => response.json())
        .then(data => {
          if (data.message === 'Rating updated successfully') {
            updateRatingStars(ratingBar, starRating);  // Update the stars visually
          }
        });
      });

      // Handle hover (gold stars)
      star.addEventListener('mouseover', function () {
        stars.forEach(s => {
          const sRating = parseInt(s.getAttribute('data-rating'), 10);
          s.classList.toggle('hovered', sRating <= starRating);  // Highlight hovered stars in gold
        });
      });

      // Handle mouseout (remove hover effect)
      star.addEventListener('mouseout', function () {
        stars.forEach(s => s.classList.remove('hovered'));  // Remove hover effect
      });
    });
  });
});

// Update the visual appearance of the stars after a click
function updateRatingStars(ratingBar, newRating) {
  const stars = ratingBar.querySelectorAll('.rating-star');
  stars.forEach(star => {
    const rating = parseInt(star.getAttribute('data-rating'), 10);
    // Add 'selected' class for green stars (clicked ones)
    star.classList.toggle('selected', rating <= newRating);
  });

  // Update the hidden attribute to persist the rating
  ratingBar.setAttribute('data-selected-rating', newRating);
}
