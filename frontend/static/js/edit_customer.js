document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("edit-form");
  const deleteBtn = document.getElementById("delete-btn");

  const token = localStorage.getItem("access_token");

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
          "Authorization": token ? `Bearer ${token}` : ""
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
        headers: {
          "Authorization": token ? `Bearer ${token}` : ""
        }
      });

      if (!res.ok) {
        alert("Failed to delete customer");
        return;
      }

      window.location.href = "/?view=customers";
    });
  }
});