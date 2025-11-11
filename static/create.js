document.getElementById("add-participant").addEventListener("click", () => {
  const participants = document.getElementById("participants");
  const newParticipantLine = participants.lastElementChild.cloneNode(true);
  newParticipantLine.getElementsByTagName("input")[0].value = "";
  participants.appendChild(newParticipantLine);
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
