function getParticipantNameCounts() {
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
  return nameCounts;
}

function validateUserNames(e) {
  const nameInputs = Array.from(
    document.querySelectorAll("#participant-list input.participant")
  );
  const nameCounts = getParticipantNameCounts();
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

function validateSufficientParticipants() {
  const nameInputs = Array.from(
    document.querySelectorAll("#participant-list input.participant")
  );
  const nameCounts = getParticipantNameCounts();
  if (Object.keys(nameCounts).length < 3) {
    const missing_inputs = Math.max(3 - nameInputs.length, 0);
    for (let i = 0; i < missing_inputs; i++) {
      nameInputs.push(addParticipantField().firstElementChild);
    }
    for (const nameInput of nameInputs) {
      if (nameInput.value == "") {
        nameInput.setCustomValidity(
          _("You need at least three participants to set up an exchange.")
        );
      }
    }
  }
}

for (const participantNameInput of document.getElementsByName("participant")) {
  participantNameInput.addEventListener("blur", (e) => {
    validateUserNames(e);
  });
}

function addParticipantField() {
  const participants = document.getElementById("participant-list");
  const newParticipantLine = participants.lastElementChild.cloneNode(true);
  newParticipantLine.getElementsByTagName("input")[0].value = "";
  newParticipantLine.firstElementChild.addEventListener("blur", (e) => {
    validateUserNames(e);
  });
  participants.appendChild(newParticipantLine);
  newParticipantLine.firstElementChild.focus();
  return newParticipantLine;
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
    validateSufficientParticipants();
  }
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
    document.getElementById("add-constraint").focus();
  } else {
    form.reportValidity();
  }
});

function setArrows(e) {
  const rightArrow =
    e.target.parentElement.getElementsByClassName("arrow-right")[0];
  const bothArrow =
    e.target.parentElement.getElementsByClassName("arrow-both")[0];
  const fromLabel =
    e.target.parentElement.getElementsByClassName("from-label")[0];
  if (e.target.value == "never") {
    rightArrow.hidden = true;
    fromLabel.hidden = true;
    bothArrow.hidden = false;
  } else {
    bothArrow.hidden = true;
    rightArrow.hidden = false;
    fromLabel.hidden = false;
  }
}

for (const probabilitySelect of document
  .getElementById("constraint-list")
  .getElementsByClassName("probability-level")) {
  probabilitySelect.addEventListener("change", (e) => {
    setArrows(e);
  });
}

document.getElementById("add-constraint").addEventListener("click", () => {
  const constraints = document.getElementById("constraint-list");
  const newConstraintLine = constraints.lastElementChild.cloneNode(true);
  for (const el of newConstraintLine.getElementsByTagName("select")) {
    el.value = "";
    el.required = true;
    el.disabled = false;
  }
  newConstraintLine
    .getElementsByClassName("probability-level")[0]
    .addEventListener("change", (e) => {
      setArrows(e);
    });
  newConstraintLine.getElementsByClassName("arrow-both")[0].hidden = true;
  newConstraintLine.getElementsByClassName("arrow-right")[0].hidden = false;
  newConstraintLine.getElementsByClassName("from-label")[0].hidden = false;
  newConstraintLine.hidden = false;
  constraints.appendChild(newConstraintLine);
  newConstraintLine.getElementsByClassName("giver")[0].focus();
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
