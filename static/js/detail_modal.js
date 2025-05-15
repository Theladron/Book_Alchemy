function openDetailModal(details, type, id) {
  const modal = document.getElementById('detailModal');
  const text = document.getElementById('detailText');
  const recommendationsContainer = document.getElementById('recommendations');

  text.classList.add('hidden');
  text.innerHTML = 'Loading...';
  recommendationsContainer.innerHTML = '';
  recommendationsContainer.classList.add('hidden');

  modal.classList.remove('hidden');

  function renderLines(raw, container) {
    container.innerHTML = '';
    raw.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (!trimmed) return;
      const idx = trimmed.indexOf(':');
      let key, value;
      if (idx > -1) {
        key = trimmed.slice(0, idx);
        value = trimmed.slice(idx + 1).trim();
      } else {
        key = '';
        value = trimmed;
      }
      const item = document.createElement('div');
      item.classList.add('detail-item');
      if (key) {
        item.innerHTML = `<strong>${key}:</strong> ${value}`;
      } else {
        item.textContent = value;
      }
      container.appendChild(item);
    });
  }

  if (type === 'book') {
    fetch(`/book_details/${id}`)
      .then(r => r.json())
      .then(data => {
        renderLines(data.details || 'No book details available.', text);
        text.classList.remove('hidden');

        recommendationsContainer.innerHTML = 'Loading recommendations...';
        recommendationsContainer.classList.remove('hidden');
        fetch(`/book/${id}/recommendations`)
          .then(r => r.json())
          .then(recData => {
            if (recData.recommendations?.length) {
              recommendationsContainer.innerHTML = '<strong>Recommended Books:</strong><ul>';
              recData.recommendations.forEach(r => {
                recommendationsContainer.innerHTML += `<li>${r}</li>`;
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
        text.innerHTML = '';
        renderLines('Failed to fetch book details.', text);
        text.classList.remove('hidden');
      });
  } else if (type === 'author') {
    fetch(`/author_details/${id}`)
      .then(r => r.json())
      .then(data => {
        let raw;
        if (data.error) {
          raw = 'No author details available.';
        } else {
          raw = `Top Subject: ${data.top_subject}\nTop Work: ${data.top_work}\nWork Count: ${data.work_count}`;
        }
        renderLines(raw, text);
        text.classList.remove('hidden');

        recommendationsContainer.innerHTML = 'Loading recommendations...';
        recommendationsContainer.classList.remove('hidden');
        fetch(`/author/${id}/recommendations`)
          .then(r => r.json())
          .then(recData => {
            if (recData.recommendations?.length) {
              recommendationsContainer.innerHTML = '<strong>Recommended Books:</strong><ul>';
              recData.recommendations.forEach(r => {
                recommendationsContainer.innerHTML += `<li>${r}</li>`;
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
        text.innerHTML = '';
        renderLines('Failed to fetch author details.', text);
        text.classList.remove('hidden');
      });
  }
}

function closeDetailModal() {
  document.getElementById('detailModal').classList.add('hidden');
}

function fetchFilteredBookRecommendations() {
  const recC = document.getElementById('bookRecommendationsContainer');
  if (!recC) return;

  recC.innerHTML = 'Loading recommendations...';

  const form = document.getElementById('sortForm');
  const params = new URLSearchParams(new FormData(form)).toString();

  fetch(`/book_recommendations?${params}`)
    .then(r => r.json())
    .then(data => {
      recC.innerHTML = '';
      if (data.recommendations?.length) {
        recC.innerHTML = '<strong>Recommended Books:</strong><ul>';
        data.recommendations.forEach(r => {
          recC.innerHTML += `<li>${r}</li>`;
        });
        recC.innerHTML += '</ul>';
      } else {
        recC.innerHTML = 'No recommendations available.';
      }
    })
    .catch(() => {
      recC.innerHTML = 'Failed to fetch recommendations.';
    });
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.book-title, .poster').forEach(el => {
    el.addEventListener('click', e => {
      e.stopPropagation();
      openDetailModal(null, 'book', el.dataset.bookId);
    });
  });

  document.querySelectorAll('.author-name').forEach(el => {
    el.addEventListener('click', e => {
      e.stopPropagation();
      openDetailModal(null, 'author', el.dataset.authorId);
    });
  });

  const loadRecBtn = document.getElementById('loadRecommendationsBtn');
  if (loadRecBtn) {
    loadRecBtn.addEventListener('click', () => {
      fetchFilteredBookRecommendations();
    });
  }

});
