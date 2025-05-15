function switchMode(mode) {
  const manualFields = document.getElementById("manualFields");
  const modeInput = document.getElementById("mode");
  const isbnField = document.getElementById("isbn");

  if (mode === "manual") {
    manualFields.style.display = "block";
    modeInput.value = "manual";
    isbnField.removeAttribute("required");
  } else if (mode === "isbn_lookup") {
    manualFields.style.display = "none";
    modeInput.value = "isbn_lookup";
    isbnField.setAttribute("required", "required");
  }
}

function submitForm() {
  const form = document.getElementById("bookForm");
  const messageDiv = document.getElementById("message");
  const formData = new FormData(form);

  fetch("/add_book", {
    method: "POST",
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        messageDiv.textContent = data.error;
        messageDiv.style.color = "red";
      } else {
        messageDiv.textContent = data.message;
        messageDiv.style.color = "green";
        form.reset();
        switchMode("manual");

        setTimeout(() => {
          messageDiv.textContent = "";
        }, 3000);
      }
    })
    .catch((err) => {
      console.error("Form submission error:", err);
      messageDiv.textContent = "An error occurred while submitting the form.";
      messageDiv.style.color = "red";
    });
}

document.addEventListener("DOMContentLoaded", () => {
  switchMode("manual");

  const form = document.getElementById("bookForm");
  form.addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent default form submission
    submitForm();
  });
});
