document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("create-form");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      customer: {
        name: form.customer_name.value,
        email: form.customer_email.value,
        phone: form.customer_phone.value,
        notes: form.customer_notes.value || null,
      },
      film_type: form.film_type.value,
      needs_print: form.needs_print.checked,
      notes: form.notes.value || null,
    };

    const res = await fetch("/api/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      alert("Failed to create order");
      return;
    }

    window.location.href = "/?view=orders";
  });
});
