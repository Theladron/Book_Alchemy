// Function to open modal with either book details or author details
function openDetailModal(details, type, id) {
  const modal = document.getElementById('detailModal');
  const text = document.getElementById('detailText');
  const recommendationsContainer = document.getElementById('recommendations');

  // Reset content
  text.classList.add('hidden');
  text.textContent = 'Loading...';
  recommendationsContainer.innerHTML = '';
  recommendationsContainer.classList.add('hidden');

  modal.classList.remove('hidden');

  if (type === 'book') {
    fetch(`/book_details/${id}`)
      .then(response => response.json())
      .then(data => {
        text.textContent = data.details || 'No book details available.';
        text.classList.remove('hidden');

        // Show loading message for recommendations
        recommendationsContainer.innerHTML = 'Loading recommendations...';
        recommendationsContainer.classList.remove('hidden');

        // Fetch book recommendations
        fetch(`/book/${id}/recommendations`)
          .then(response => response.json())
          .then(recommendationsData => {
            if (recommendationsData.recommendations && recommendationsData.recommendations.length > 0) {
              recommendationsContainer.innerHTML = '<strong>Recommended Books:</strong><ul>';
              recommendationsData.recommendations.forEach((recommendation) => {
                recommendationsContainer.innerHTML += `<li>${recommendation}</li>`;
              });
              recommendationsContainer.innerHTML += '</ul>';
            } else {
              recommendationsContainer.innerHTML = 'No recommendations available.';
            }
          })
          .catch(() => {
            recommendationsContainer.innerHTML = 'Failed to fetch recommendations.';
          });
      })
      .catch(() => {
        text.textContent = 'Failed to fetch book details.';
        text.classList.remove('hidden');
      });
  } else if (type === 'author') {
    fetch(`/author_details/${id}`)
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          text.textContent = 'No author details available.';
        } else {
          text.textContent =
            `Top Subject: ${data.top_subject}\n` +
            `Top Work: ${data.top_work}\n` +
            `Work Count: ${data.work_count}`;
        }
        text.classList.remove('hidden');

        // Show loading message for recommendations
        recommendationsContainer.innerHTML = 'Loading recommendations...';
        recommendationsContainer.classList.remove('hidden');

        // Fetch author recommendations
        fetch(`/author/${id}/recommendations`)
          .then(response => response.json())
          .then(recommendationsData => {
            if (recommendationsData.recommendations && recommendationsData.recommendations.length > 0) {
              recommendationsContainer.innerHTML = '<strong>Recommended Books:</strong><ul>';
              recommendationsData.recommendations.forEach((recommendation) => {
                recommendationsContainer.innerHTML += `<li>${recommendation}</li>`;
              });
              recommendationsContainer.innerHTML += '</ul>';
            } else {
              recommendationsContainer.innerHTML = 'No recommendations available.';
            }
          })
          .catch(() => {
            recommendationsContainer.innerHTML = 'Failed to fetch recommendations.';
          });
      })
      .catch(() => {
        text.textContent = 'Failed to fetch author details.';
        text.classList.remove('hidden');
      });
  }
}

// Close the modal
function closeDetailModal() {
  const modal = document.getElementById('detailModal');
  modal.classList.add('hidden');
}

// Fetch and display homepage book recommendations (only once)
function fetchBookRecommendations() {
  const recommendationsContainer = document.getElementById('bookRecommendationsContainer');
  if (!recommendationsContainer) return;

  recommendationsContainer.innerHTML = 'Loading recommendations...';

  fetch('/book_recommendations')
    .then(response => response.json())
    .then(data => {
      const recommendations = data.recommendations;
      recommendationsContainer.innerHTML = '';

      if (recommendations.length > 0) {
        recommendationsContainer.innerHTML = '<strong>Recommended Books:</strong><ul>';
        recommendations.forEach((recommendation) => {
          recommendationsContainer.innerHTML += `<li>${recommendation}</li>`;
        });
        recommendationsContainer.innerHTML += '</ul>';
      } else {
        recommendationsContainer.innerHTML = 'No recommendations available.';
      }
    })
    .catch(() => {
      recommendationsContainer.innerHTML = 'Failed to fetch recommendations.';
    });
}

// DOM ready event
document.addEventListener('DOMContentLoaded', () => {
  // Attach click handlers for books and authors
  document.querySelectorAll('.book-title, .poster').forEach(element => {
    element.addEventListener('click', (e) => {
      e.stopPropagation();
      const bookId = element.dataset.bookId;
      openDetailModal(null, 'book', bookId);
    });
  });

  document.querySelectorAll('.author-name').forEach(element => {
    element.addEventListener('click', (e) => {
      e.stopPropagation();
      const authorId = element.dataset.authorId;
      openDetailModal(null, 'author', authorId);
    });
  });

  // Load homepage recommendations once
  fetchBookRecommendations();
});
