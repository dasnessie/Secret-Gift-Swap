function returnToOverview(event) {
  event.preventDefault();
  window.location.href = "../";
}

document.getElementById("no-button").addEventListener("click", (e) => {
  returnToOverview(e);
});

document.getElementById("name-confirmation").addEventListener("cancel", (e) => {
  returnToOverview(e);
});

window.addEventListener("pageshow", (event) => {
  document.getElementById("name-confirmation").showModal();
});

document.getElementById("spoiler-cover").addEventListener("click", (e) => {
  e.target.style.display = "none";
  document.getElementById("spoiler-content").style.display = "inline";
});

const changeNameForm = document.getElementById("rename_participant");
const nameInput = document.getElementById("participant_name");
changeNameForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (oldname == nameInput.value) {
    nameInput.setCustomValidity(_("That's already your name."));
  } else if (nameInput.value.startsWith("/")) {
    nameInput.setCustomValidity(_("Names may not begin with a slash."));
  } else {
    const res = await fetch(
      `/check_participant_name?exchangeslug=${encodeURIComponent(
        exchangeslug
      )}&newname=${encodeURIComponent(
        nameInput.value
      )}&oldname=${encodeURIComponent(oldname)}`
    );
    const data = await res.json();

    if (data.nameAvailable) {
      changeNameForm.submit();
    } else {
      nameInput.setCustomValidity(
        _("This name is already used by someone else.")
      );
      changeNameForm.reportValidity();
    }
  }
});

nameInput.addEventListener("change", (e) => {
  nameInput.setCustomValidity("");
});
