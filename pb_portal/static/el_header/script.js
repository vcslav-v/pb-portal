function logout(event) {
    event.preventDefault();
    const elem = document.getElementById('logout');
    axios.post(elem.getAttribute('data-logout-url'))
        .then(function (response){
            window.location.href = elem.getAttribute('data-login-url');
        })
        .catch(function (error){
            console.log('Error:', error);
        })
}