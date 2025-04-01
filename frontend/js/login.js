async function login() {
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;

    let formData = new URLSearchParams();
    formData.append('email', email);
    formData.append('password', password);

    let fetchResponse = await fetch('/auth/jwt/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
    });

    let responseDiv = document.getElementById("response");
    responseDiv.style.color = "white";
    responseDiv.classList.remove("hidden");

    if (fetchResponse.ok) {
        responseDiv.innerHTML = "Вход выполнен успешно";
        window.location.replace('/profile/');
    } else {
        responseDiv.innerHTML = "Неверный логин или пароль";
    }
}

