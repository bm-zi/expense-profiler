console.log("register connected!");

const usernameField = document.querySelector("#usernameField");
const usernameFeedback = document.querySelector(".invalid-feedback");
const emailField = document.querySelector("#emailField");
const emailFeedback = document.querySelector(".email-feedback");
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");
const showPasswordToggle = document.querySelector(".showPasswordToggle");
const passwordField = document.querySelector("#passwordField");
const submitBtn = document.querySelector(".submit-btn");

if (usernameField) {
  usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
    usernameSuccessOutput.style.display = "block";
    usernameSuccessOutput.textContent = `Checking ${usernameVal}`;
    usernameField.classList.remove("is-invalid");
    usernameFeedback.style.display = "none";

    if (usernameVal.length > 0) {
      fetch("/auth/validate-username", {
        body: JSON.stringify({ username: usernameVal }),
        method: "POST",
      })
        .then((res) => res.json())
        .then((data) => {
          usernameSuccessOutput.style.display = "none";
          if (data.username_error) {
            submitBtn.disabled = true;
            usernameField.classList.add("is-invalid");
            usernameFeedback.style.display = "block";
            usernameFeedback.innerHTML = `<p>${data.username_error}</p>`;
          } else {
            submitBtn.removeAttribute("disabled");
          }
        });
    }
  });
}

if (emailField) {
  emailField.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;

    emailField.classList.remove("is-invalid");
    emailFeedback.style.display = "none";

    if (emailVal.length > 0) {
      fetch("/auth/validate-email", {
        body: JSON.stringify({ email: emailVal }),
        method: "POST",
      })
        .then((res) => res.json())
        .then((data) => {
          console.log(data);
          if (data.email_error) {
            submitBtn.disabled = true;
            emailField.classList.add("is-invalid");
            emailFeedback.style.display = "block";
            emailFeedback.innerHTML = `<p>${data.email_error}</p>`;
          } else {
            submitBtn.removeAttribute("disabled");
          }
        });
    }
  });
}

const handlePasswordToggle = (e) => {
  if (showPasswordToggle.textContent === "SHOW") {
    showPasswordToggle.textContent = "HIDE";
    passwordField.setAttribute("type", "text");
  } else {
    showPasswordToggle.textContent = "SHOW";
    passwordField.setAttribute("type", "password");
  }
};

if (showPasswordToggle) {
  showPasswordToggle.addEventListener("click", handlePasswordToggle);
}
