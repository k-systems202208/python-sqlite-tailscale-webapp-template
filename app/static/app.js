document.addEventListener("submit", (event) => {
  const form = event.target;
  const message = form.dataset.confirm;
  if (message && !window.confirm(message)) {
    event.preventDefault();
  }
});

window.appCsrfToken = () =>
  document.querySelector('meta[name="csrf-token"]')?.content || "";
