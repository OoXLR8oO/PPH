import { apiFetch } from "/static/js/api.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("edit-form");
  const deleteBtn = document.getElementById("delete-btn");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const batchId = form.dataset.batchId;

      const payload = {
        dropbox_link:
          document.querySelector("[name=dropbox_link]").value || null,
      };

      const res = await apiFetch(`/api/batches/${batchId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        alert("Failed to update batch");
        return;
      }

      window.location.href = "/?view=batches";
    });
  }

  if (deleteBtn) {
    deleteBtn.addEventListener("click", async () => {
      const confirmed = confirm("Delete this batch permanently?");
      if (!confirmed) return;

      const batchId = deleteBtn.dataset.batchId;

      const res = await apiFetch(`/api/batches/${batchId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        alert("Failed to delete batch");
        return;
      }

      window.location.href = "/?view=batches";
    });
  }
});