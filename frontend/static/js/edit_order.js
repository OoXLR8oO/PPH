//edit_order.js
import { apiFetch } from "/static/js/api.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("edit-form");
  const deleteBtn = document.getElementById("delete-btn");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const orderCode = form.dataset.orderCode;

      const payload = {
        status: document.querySelector("[name=order_status]").value,
        film_type: document.querySelector("[name=film_type]").value,
        needs_print: document.querySelector("[name=needs_print]").checked,
        notes: document.querySelector("[name=notes]").value || null,
      };

      const res = await apiFetch(`/api/orders/${orderCode}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        alert("Failed to update order");
        return;
      }

      window.location.href = "/?view=orders";
    });
  }

  if (deleteBtn) {
    deleteBtn.addEventListener("click", async () => {
      const confirmed = confirm("Delete this order permanently?");
      if (!confirmed) return;

      const orderCode = deleteBtn.dataset.orderCode;

      const res = await apiFetch(`/api/orders/${orderCode}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        alert("Failed to delete order");
        return;
      }

      window.location.href = "/?view=orders";
    });
  }
});