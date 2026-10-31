const form = document.getElementsByClassName("exchange_name_form")[0];
const nameInput = document.getElementsByClassName("exchange_name")[0];
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const res = await fetch(
    `/check_exchange_name?name=${encodeURIComponent(nameInput.value)}`,
  );
  const data = await res.json();

  if (data.nameAvailable) {
    form.submit();
  } else {
    nameInput.setCustomValidity(_("This exchange name is not available."));
    form.reportValidity();
  }
});

nameInput.addEventListener("change", (e) => {
  nameInput.setCustomValidity("");
});
