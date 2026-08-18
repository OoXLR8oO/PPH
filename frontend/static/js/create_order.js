// create_order.js
import { apiFetch } from "/static/js/api.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("create-form");

  if (!form) return;

  const emailInput = form.customer_email;
  const customerEmails = document.getElementById("customer-emails");

  emailInput.addEventListener("input", () => {
    const email = emailInput.value.toLowerCase();

    const option = [...customerEmails.options].find(
      (option) => option.value.toLowerCase() === email
    );

    if (!option) return;

    form.customer_name.value = option.dataset.name;
    form.customer_phone.value = option.dataset.phone;
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      customer: {
        name: form.customer_name.value,
        email: form.customer_email.value,
        phone: form.customer_phone.value,
      },
      film_type: form.film_type.value,
      quantity: Number(form.quantity.value),
      needs_print: form.needs_print.checked,
      notes: null,
    };

    const res = await apiFetch("/api/orders", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      alert("Failed to create order");
      return;
    }

    window.location.href = "/?view=orders";
  });
});