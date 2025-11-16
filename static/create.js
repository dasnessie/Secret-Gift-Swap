function validateUserNames(e) {
  const nameInputs = Array.from(
    document.querySelectorAll("#participant-list input.participant")
  );
  const names = nameInputs
    .map((input) => input.value)
    .filter((value) => value !== "");

  const nameCounts = {};
  for (value of names) {
    nameCounts[value] = (nameCounts[value] || 0) + 1;
  }
  const duplicateNames = Object.keys(nameCounts).filter(
    (key) => nameCounts[key] > 1
  );
  for (const input of nameInputs) {
    if (duplicateNames.includes(input.value)) {
      input.setCustomValidity(_("Can't have the same name twice!"));
    } else {
      input.setCustomValidity("");
    }
  }
}

document.getElementsByName("participant")[0].addEventListener("blur", (e) => {
  validateUserNames(e);
});

function addParticipantField() {
  const participants = document.getElementById("participant-list");
  const newParticipantLine = participants.lastElementChild.cloneNode(true);
  newParticipantLine.getElementsByTagName("input")[0].value = "";
  newParticipantLine.firstElementChild.addEventListener("blur", (e) => {
    validateUserNames(e);
  });
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
  const form = document.getElementById("participant-form");
  if (form.checkValidity()) {
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
    document.getElementById("constraints").disabled = false;
    document.getElementById("next-button").hidden = true;
    document.getElementById("generate-button").hidden = false;
  } else {
    form.reportValidity();
  }
});

document.getElementById("add-constraint").addEventListener("click", () => {
  const constraints = document.getElementById("constraint-list");
  const newConstraintLine = constraints.lastElementChild.cloneNode(true);
  for (const el of newConstraintLine.getElementsByTagName("select")) {
    el.value = "";
    el.required = true;
    el.disabled = false;
  }
  newConstraintLine.hidden = false;
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
  for (el of form.querySelectorAll("fieldset, input, select, textarea")) {
    el.disabled = false;
  }
});
