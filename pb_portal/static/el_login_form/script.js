function showPassword() {
    var passwordInput = document.getElementById("password");
    var img = document.getElementById("password-eye");
    passwordInput.type = "text";
    img.src = img.getAttribute("data-closed-eye-src");
}

function hidePassword() {
    var passwordInput = document.getElementById("password");
    var img = document.getElementById("password-eye");
    passwordInput.type = "password";
    img.src = img.getAttribute("data-open-eye-src");
}