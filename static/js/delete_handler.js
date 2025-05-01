document.addEventListener("DOMContentLoaded", () => {
  const deleteBookButtons = document.querySelectorAll(".delete-btn");
  const deleteAuthorButtons = document.querySelectorAll(".delete-author-btn");

  // === DELETE BOOK LOGIC ===
  deleteBookButtons.forEach(button => {
    button.addEventListener("click", async (event) => {
      // 1. Prevent any default or other handlers
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();

      // 2. Disable the button so you can’t re-click
      button.disabled = true;

      const card = button.closest(".book-card");
      const bookId = card.dataset.bookId;

      // 3. Single confirm for book deletion
      const deleteBookConfirmed = confirm("Willst du dieses Buch wirklich löschen?");
      if (!deleteBookConfirmed) {
        button.disabled = false;
        return;
      }

      // 4. Delete the book
      let response, result;
      try {
        response = await fetch(`/book/${bookId}/delete`, { method: "DELETE" });
        result = await response.json();
      } catch (err) {
        alert("Netzwerkfehler beim Löschen des Buches.");
        button.disabled = false;
        return;
      }

      if (!response.ok) {
        alert("Fehler beim Löschen: " + result.error);
        button.disabled = false;
        return;
      }

      // 5. Remove the card from the UI
      card.remove();

      // 6. If this was the last book, ask one more time, but for the author only
      if (result.author_id) {
        const deleteAuthor = confirm(
          "Das war das letzte Buch dieses Autors. Möchtest du den Autor ebenfalls löschen?"
        );
        if (deleteAuthor) {
          try {
            const authorResp = await fetch(`/author/${result.author_id}/delete`, { method: "DELETE" });
            const authorResult = await authorResp.json();
            if (!authorResp.ok) {
              throw new Error(authorResult.error);
            }
            alert("Autor gelöscht.");
          } catch (err) {
            alert("Fehler beim Löschen des Autors: " + err.message);
          }
        }
      }

      // Done — no further confirmations
    }, { once: true });  // ensure this handler only fires once per button
  });


  // === DELETE AUTHOR LOGIC ===
  deleteAuthorButtons.forEach(button => {
    button.addEventListener("click", async (event) => {
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();
      button.disabled = true;

      const authorId = button.dataset.authorId;
      const confirmed = confirm(
        "Willst du diesen Autor und alle seine Bücher wirklich löschen?"
      );
      if (!confirmed) {
        button.disabled = false;
        return;
      }

      try {
        const resp = await fetch(`/author/${authorId}/delete`, { method: "DELETE" });
        const result = await resp.json();
        if (!resp.ok) throw new Error(result.error);
        alert("Autor und seine Bücher wurden gelöscht.");
        window.location.reload();
      } catch (err) {
        alert("Fehler beim Löschen des Autors: " + err.message);
        button.disabled = false;
      }
    }, { once: true });
  });
});
