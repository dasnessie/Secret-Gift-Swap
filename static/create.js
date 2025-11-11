function addParticipantField() {
  const participants = document.getElementById("participant-list");
  const newParticipantLine = participants.lastElementChild.cloneNode(true);
  newParticipantLine.getElementsByTagName("input")[0].value = "";
  participants.appendChild(newParticipantLine);
  newParticipantLine.firstElementChild.focus();
}

document
  .getElementById("add-participant")
  .addEventListener("click", addParticipantField);

document.getElementById("participant-list").addEventListener("keydown", (e) => {
  if (e.key != "Enter") {
    return;
  }
  if (!e.target.classList.contains("participant")) {
    return;
  }
  e.preventDefault();
  addParticipantField();
});

document.getElementById("participant-list").addEventListener("click", (e) => {
  if (!e.target.classList.contains("delete-participant")) {
    return;
  }
  const elementToDelete = e.target.parentElement;
  if (
    elementToDelete.parentElement.firstElementChild ==
    elementToDelete.parentElement.lastElementChild
  ) {
    elementToDelete.getElementsByTagName("input")[0].value = "";
  } else {
    elementToDelete.remove();
  }
});

document.getElementById("next-button").addEventListener("click", () => {
  const participants = document.getElementById("participant-list").children;
  const giverSelect = document.getElementsByClassName("giver")[0];
  const gifteeSelect = document.getElementsByClassName("giftee")[0];
  for (const el of participants) {
    const participantName = el.getElementsByTagName("input")[0].value;
    if (participantName != "") {
      const optionGiver = new Option(participantName, participantName);
      giverSelect.appendChild(optionGiver);
      const optionGiftee = new Option(participantName, participantName);
      gifteeSelect.appendChild(optionGiftee);
    }
  }
  giverSelect.value = "";
  gifteeSelect.value = "";
  document.getElementById("participants").disabled = true;
  document.getElementById("constraints").hidden = false;
});

document.getElementById("add-constraint").addEventListener("click", () => {
  const constraints = document.getElementById("constraint-list");
  const newConstraintLine = constraints.lastElementChild.cloneNode(true);
  for (const el of newConstraintLine.getElementsByTagName("select")) {
    el.value = "";
  }
  constraints.appendChild(newConstraintLine);
});

document.getElementById("constraint-list").addEventListener("click", (e) => {
  if (!e.target.classList.contains("delete-constraint")) {
    return;
  }
  const elementToDelete = e.target.parentElement;
  if (
    elementToDelete.parentElement.firstElementChild ==
    elementToDelete.parentElement.lastElementChild
  ) {
    for (const el of elementToDelete.getElementsByTagName("select")) {
      el.value = "";
    }
  } else {
    elementToDelete.remove();
  }
});

const form = document.getElementById("participant-form");
form.addEventListener("submit", () => {
  form.querySelectorAll("fieldset, input, select, textarea").forEach((el) => {
    el.disabled = false;
  });
});
