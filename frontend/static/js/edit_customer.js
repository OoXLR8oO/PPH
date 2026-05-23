document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("edit-form");
  const deleteBtn = document.getElementById("delete-btn");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const customerId = form.dataset.customerId;

      const payload = {
        name: document.querySelector("[name=name]").value,
        email: document.querySelector("[name=email]").value,
        phone: document.querySelector("[name=phone]").value,
        notes: document.querySelector("[name=notes]").value || null,
      };

      const res = await fetch(`/api/customers/${customerId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        alert("Failed to update customer");
        return;
      }

      window.location.href = "/?view=customers";
    });
  }

  if (deleteBtn) {
    deleteBtn.addEventListener("click", async () => {
      const confirmed = confirm("Delete this customer permanently?");
      if (!confirmed) return;

      const customerId = deleteBtn.dataset.customerId;

      const res = await fetch(`/api/customers/${customerId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        alert("Failed to delete customer");
        return;
      }

      window.location.href = "/?view=customers";
    });
  }
});