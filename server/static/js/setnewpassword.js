const showPasswordToggle = document.querySelector(".showPasswordToggle");
const passwordField = document.querySelector("#passwordField");
const passwordField2 = document.querySelector("#passwordField2");

const handlePasswordToggle = (e) => {
  if (showPasswordToggle.textContent === "SHOW") {
    showPasswordToggle.textContent = "HIDE";
    passwordField.setAttribute("type", "text");
    passwordField2.setAttribute("type", "text");
  } else {
    showPasswordToggle.textContent = "SHOW";
    passwordField.setAttribute("type", "password");
    passwordField2.setAttribute("type", "password");
  }
};

if (showPasswordToggle) {
  showPasswordToggle.addEventListener("click", handlePasswordToggle);
}
