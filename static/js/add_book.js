document.addEventListener("DOMContentLoaded", () => {
  switchMode("manual");  // Ensure default mode is shown on load
});

function switchMode(mode) {
  // Set the mode value in the hidden input field
  document.getElementById("mode").value = mode;

  const manualFields = document.getElementById("manualFields");

  // Show or hide manual entry fields based on the selected mode
  if (mode === "manual") {
    manualFields.style.display = "block";
  } else {
    manualFields.style.display = "none";
  }
}

function submitForm() {
  // Get the form element
  const form = document.getElementById("bookForm");

  // Create FormData object to collect form values
  const formData = new FormData(form);

  // Fetch request to submit the form data
  fetch("/add_book", {
    method: "POST",
    body: formData,
  })
    .then(res => res.json())
    .then(data => {
      // If there's an error from the server, display it
      if (data.error) {
        document.getElementById("message").textContent = data.error;
      } else {
        // If successful, show the success message
        document.getElementById("message").textContent = data.message;
        form.reset();
        // Optionally reset the mode to 'manual' after submission
        switchMode("manual");
      }
    })
    .catch(err => {
      // In case of a network error or any other error, show a generic error message
      document.getElementById("message").textContent = "Fehler beim Senden des Formulars.";
      console.error(err);
    });
}
