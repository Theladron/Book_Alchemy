document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form[action$="/add_author"]');
  if (!form) return;

  let messageEl = document.getElementById('authorMessage');
  if (!messageEl) {
    messageEl = document.createElement('p');
    messageEl.id = 'authorMessage';
    messageEl.style.marginTop = '1rem';
    form.parentNode.insertBefore(messageEl, form.nextSibling);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    messageEl.textContent = 'Submitting...';
    messageEl.classList.remove('error', 'success');

    const formData = new FormData(form);

    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new URLSearchParams(formData)
      });

      let data;
      try {
        data = await res.json();
      } catch {
        data = {};
      }

      if (!res.ok) {
        messageEl.textContent = data.error || 'Failed to add author.';
        messageEl.classList.add('error');
      } else {
        messageEl.textContent = data.message || 'Author created successfully.';
        messageEl.classList.add('success');
        form.reset();

        setTimeout(() => {
          messageEl.textContent = '';
          messageEl.classList.remove('success');
        }, 3000);
      }
    } catch (err) {
      messageEl.textContent = 'Network error. Please try again.';
      messageEl.classList.add('error');
    }
  });
});
