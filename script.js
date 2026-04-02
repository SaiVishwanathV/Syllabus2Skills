document.getElementById("registrationForm").addEventListener("submit", function(e) {
  e.preventDefault();

  let fullname = document.getElementById("fullname").value.trim();
  let email = document.getElementById("email").value.trim();
  let phone = document.getElementById("phone").value.trim();
  let password = document.getElementById("password").value.trim();
  let confirmPassword = document.getElementById("confirmPassword").value.trim();
  let message = document.getElementById("message");

  // Basic validation
  if (fullname === "" || email === "" || phone === "" || password === "" || confirmPassword === "") {
    message.textContent = "⚠️ Please fill in all fields.";
    return;
  }

  if (password !== confirmPassword) {
    message.textContent = "⚠️ Passwords do not match!";
    return;
  }

  if (password.length < 6) {
    message.textContent = "⚠️ Password must be at least 6 characters.";
    return;
  }

  message.style.color = "green";
  message.textContent = "✅ Registration successful!";
  
  // Clear form
  document.getElementById("registrationForm").reset();
});
