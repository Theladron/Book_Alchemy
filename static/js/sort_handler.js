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