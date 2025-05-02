// static/js/detail_modal.js

// Function to open modal with either book details or author details
function openDetailModal(details, type, id) {
  const modal = document.getElementById('detailModal');
  const text = document.getElementById('detailText');

  // Reset
  text.classList.add('hidden');
  text.textContent = 'Loading...';

  modal.classList.remove('hidden');

  // Fetch details based on type
  if (type === 'book') {
    fetch(`/book_details/${id}`)
      .then(response => response.json())
      .then(data => {
        text.textContent = data.details || 'No book details available.';
        text.classList.remove('hidden');
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

document.addEventListener('DOMContentLoaded', () => {
  // Event listeners for book details (clicking on poster or title)
  document.querySelectorAll('.book-title, .poster').forEach(element => {
    element.addEventListener('click', (e) => {
      e.stopPropagation(); // Prevent closing modal on click
      const bookId = element.dataset.bookId;
      openDetailModal(null, 'book', bookId);
    });
  });

  // Event listener for author details (clicking on author name)
  document.querySelectorAll('.author-name').forEach(element => {
    element.addEventListener('click', (e) => {
      e.stopPropagation(); // Prevent closing modal on click
      const authorId = element.dataset.authorId;
      openDetailModal(null, 'author', authorId);
    });
  });
});
