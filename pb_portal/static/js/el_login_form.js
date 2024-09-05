function switchVisiblePassword() {
    var passwordInput = document.getElementById("password");
    var img = document.getElementById("password-eye");
    if (img.src === img.getAttribute("data-open-eye-src")) {
        img.src = img.getAttribute("data-closed-eye-src");
        passwordInput.type = "text";
    } else {
        img.src = img.getAttribute("data-open-eye-src");
        passwordInput.type = "password";
    }
}


function submitForm(event) {
    event.preventDefault();
    const form = document.getElementById('loginForm');
    axios.post(form.getAttribute('data-auth-url'), form)
        .then(function (response){
            window.location.href = form.getAttribute('data-success-url');
        })
        .catch(function (error){
            if (error.response.status === 400 && error.response.data.message === 'LOGIN_BAD_CREDENTIALS') {
                const inputs = document.getElementsByTagName('input');
                const error_msg = document.getElementById('errorMsg');
                for (let i = 0; i < inputs.length; i++) {
                    inputs[i].classList.add('bad-credentials');
                }
                error_msg.classList.remove('hidden');
            }
        })
}

function toDefault(event) {
    if (event.target.classList.contains('bad-credentials')){
        event.target.classList.remove('bad-credentials');
    };
}
