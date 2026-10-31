function getParticipantNameCounts() {
  const nameInputs = Array.from(
    document.querySelectorAll("#participant-list input.participant"),
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
    document.querySelectorAll("#participant-list input.participant"),
  );
  const nameCounts = getParticipantNameCounts();
  const duplicateNames = Object.keys(nameCounts).filter(
    (key) => nameCounts[key] > 1,
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
    document.querySelectorAll("#participant-list input.participant"),
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
          _("You need at least three participants to set up an exchange."),
        );
      }
    }
  }
}

function validateNames() {
  const nameInputs = Array.from(
    document.querySelectorAll("#participant-list input.participant"),
  );
  for (const nameInput of nameInputs) {
    if (nameInput.value.startsWith("/")) {
      nameInput.setCustomValidity(_("Names may not begin with a slash."));
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
  newParticipantLine.firstElementChild.addEventListener("keydown", (e) => {
    participantInputEnterEvent(e);
  });
  participants.appendChild(newParticipantLine);
  newParticipantLine.firstElementChild.focus();
  return newParticipantLine;
}

document
  .getElementById("add-participant")
  .addEventListener("click", addParticipantField);

function participantInputEnterEvent(e) {
  if (e.key != "Enter") {
    return;
  }
  e.preventDefault();
  const participants = document.getElementById("participant-list").children;
  for (let i = 0; i < participants.length; i++) {
    if (participants[i].firstElementChild == e.target) {
      if (i == participants.length - 1) {
        addParticipantField();
      } else {
        participants[i + 1].firstElementChild.focus();
      }
    }
  }
}

for (participantInput of document.getElementsByClassName("participant")) {
  participantInput.addEventListener("keydown", (e) => {
    participantInputEnterEvent(e);
  });
}

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
    validateNames();
  }
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
    const constraintDataElement = document.getElementById("constraint-data");
    const constraintData = constraintDataElement.textContent.trim()
      ? JSON.parse(constraintDataElement.textContent)
      : null;
    if (constraintData) {
      for (constraint of constraintData) {
        addConstraint(...constraint);
      }
    }
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

function setArrows(selectElement) {
  const rightArrow =
    selectElement.parentElement.getElementsByClassName("arrow-right")[0];
  const bothArrow =
    selectElement.parentElement.getElementsByClassName("arrow-both")[0];
  const fromLabel =
    selectElement.parentElement.getElementsByClassName("from-label")[0];
  if (selectElement.value == "never") {
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
    setArrows(e.target);
  });
}

function addConstraint(giver, giftee, level) {
  const constraints = document.getElementById("constraint-list");
  const participantOptions = Array.from(
    constraints.getElementsByClassName("giver")[0].options,
    (option) => option.value,
  );
  const levelOptions = Array.from(
    constraints.getElementsByClassName("probability-level")[0].options,
    (option) => option.value,
  );
  if (
    giver &&
    giftee &&
    level &&
    (!participantOptions.includes(giver) ||
      !participantOptions.includes(giftee) ||
      !levelOptions.includes(level))
  ) {
    console.warn(
      "Got instruction to add constraint with unavailable options, skipping this constraint!",
    );
  } else {
    const newConstraintLine = constraints.lastElementChild.cloneNode(true);
    for (const el of newConstraintLine.getElementsByTagName("select")) {
      el.value = "";
      el.required = true;
      el.disabled = false;
    }
    newConstraintLine
      .getElementsByClassName("probability-level")[0]
      .addEventListener("change", (e) => {
        setArrows(e.target);
      });
    const giverInput = newConstraintLine.getElementsByClassName("giver")[0];
    const gifteeInput = newConstraintLine.getElementsByClassName("giftee")[0];
    const levelInput =
      newConstraintLine.getElementsByClassName("probability-level")[0];
    if (giver && giftee && level) {
      giverInput.value = giver;
      gifteeInput.value = giftee;
      levelInput.value = level;
    }
    setArrows(levelInput);
    newConstraintLine.hidden = false;
    constraints.appendChild(newConstraintLine);
    if (!(giver && giftee && level)) {
      newConstraintLine.getElementsByClassName("giver")[0].focus();
    }
  }
}

document
  .getElementById("add-constraint")
  .addEventListener("click", addConstraint);

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
