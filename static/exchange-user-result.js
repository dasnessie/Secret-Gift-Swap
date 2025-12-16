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
