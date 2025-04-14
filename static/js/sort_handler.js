document.addEventListener('DOMContentLoaded', function () {
  const sortForm = document.getElementById('sortForm');
  const sortBySelect = document.getElementById('sort_by');
  const orderSelect = document.getElementById('order');

  if (sortBySelect && orderSelect && sortForm) {
    sortBySelect.addEventListener('change', function () {
      sortForm.submit();
    });

    orderSelect.addEventListener('change', function () {
      sortForm.submit();
    });
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const deleteButtons = document.querySelectorAll(".delete-btn");

  deleteButtons.forEach(button => {
    button.addEventListener("click", async () => {
      const card = button.closest(".book-card");
      const bookId = card.dataset.bookId;

      const confirmed = confirm("Willst du dieses Buch wirklich löschen?");
      if (!confirmed) return;

      const response = await fetch(`/book/${bookId}/delete`, {
        method: "DELETE",
      });

      if (response.ok) {
        card.remove();
      } else {
        const error = await response.json();
        alert("Fehler beim Löschen: " + error.error);
      }
    });
  });
});