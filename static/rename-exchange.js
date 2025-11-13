const form = document.getElementById("rename_exchange");
const nameInput = document.getElementById("exchange_name");
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const res = await fetch(
    `/check_name?name=${encodeURIComponent(nameInput.value)}`
  );
  const data = await res.json();

  if (data.nameAvailable) {
    form.submit();
  } else {
    nameInput.setCustomValidity("This exchange name is already taken!");
    form.reportValidity();
  }
});

nameInput.addEventListener("change", (e) => {
  nameInput.setCustomValidity("");
});
