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

function submitForm(event) {
    event.preventDefault();
    const form = document.getElementById('loginForm');
    const formData = new FormData(form);
    axios.post(form.getAttribute('data-auth-url'), form)
        .then(function (response){
            window.location.href = form.getAttribute('data-success-url');
        })
        .catch(function (error){
            console.log('Error:', error);
        })
}
