function addParticipantField() {
  const participants = document.getElementById("participants");
  const newParticipantLine = participants.lastElementChild.cloneNode(true);
  newParticipantLine.getElementsByTagName("input")[0].value = "";
  participants.appendChild(newParticipantLine);
  newParticipantLine.firstElementChild.focus();
}

document
  .getElementById("add-participant")
  .addEventListener("click", addParticipantField);

document.getElementById("participants").addEventListener("keydown", (e) => {
  if (e.key != "Enter") {
    return;
  }
  if (!e.target.classList.contains("participant")) {
    return;
  }
  e.preventDefault();
  addParticipantField();
});

document.getElementById("participants").addEventListener("click", (e) => {
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
