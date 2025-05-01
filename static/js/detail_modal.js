// static/js/detail_modal.js

// Open modal with either an iframe (if URL) or fallback text
function openDetailModal(details) {
  const modal = document.getElementById('detailModal');
  const frame = document.getElementById('detailFrame');
  const text = document.getElementById('detailText');

  // Reset
  frame.classList.add('hidden');
  text.classList.add('hidden');
  frame.src = '';

  // Heuristic: if it starts with http, show iframe; else show text
  if (details.startsWith('http://') || details.startsWith('https://')) {
    frame.src = details;
    frame.classList.remove('hidden');
  } else {
    text.textContent = details;
    text.classList.remove('hidden');
  }

  modal.classList.remove('hidden');
}

function closeDetailModal() {
  const modal = document.getElementById('detailModal');
  const frame = document.getElementById('detailFrame');
  frame.src = '';
  modal.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.book-card').forEach(card => {
    card.addEventListener('click', () => {
      const details = card.dataset.details;
      openDetailModal(details);
    });
  });
});
