document.getElementById("yes-button").addEventListener("click", () => {
  document.getElementById("result-content").hidden = false;
});

document.getElementById("no-button").addEventListener("click", () => {
  window.location.href = "../../";
});

window.addEventListener("pageshow", (event) => {
  document.getElementById("result-content").hidden = true;
  document.getElementById("name-confirmation").showModal();
});
