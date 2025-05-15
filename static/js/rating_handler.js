document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('.rating-bar').forEach(ratingBar => {
    const bookId = ratingBar.getAttribute('data-book-id');
    const selectedRating = parseInt(ratingBar.getAttribute('data-selected-rating'), 10);
    const stars = ratingBar.querySelectorAll('.rating-star');

    stars.forEach(star => {
      const rating = parseInt(star.getAttribute('data-rating'), 10);
      if (rating <= selectedRating) {
        star.classList.add('selected');
      }
    });

    stars.forEach(star => {
      const starRating = parseInt(star.getAttribute('data-rating'), 10);

      star.addEventListener('click', function () {
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
            updateRatingStars(ratingBar, starRating);
          }
        });
      });

      star.addEventListener('mouseover', function () {
        stars.forEach(s => {
          const sRating = parseInt(s.getAttribute('data-rating'), 10);
          s.classList.toggle('hovered', sRating <= starRating);
        });
      });

      star.addEventListener('mouseout', function () {
        stars.forEach(s => s.classList.remove('hovered'));
      });
    });
  });
});

function updateRatingStars(ratingBar, newRating) {
  const stars = ratingBar.querySelectorAll('.rating-star');
  stars.forEach(star => {
    const rating = parseInt(star.getAttribute('data-rating'), 10);
    star.classList.toggle('selected', rating <= newRating);
  });

  ratingBar.setAttribute('data-selected-rating', newRating);
}
