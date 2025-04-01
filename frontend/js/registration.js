async function registerUser() {
  var form = document.getElementById("registration-form");
  var username = form.elements.username.value;
  var email = form.elements.email.value;
  var password = form.elements.password.value;
  var confirm_password = form.elements.confirm_password.value;

  var errorDiv = document.getElementById("error-message");
  errorDiv.innerHTML = "";

  var emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
  if (!emailRegex.test(email)) {
    var errorMessage = "Введите корректный email";
    appendErrorMessage(errorMessage);
    return;
  }

  if (username.trim() === "") {
    var errorMessage = "Введите ваше имя пользователя";
    appendErrorMessage(errorMessage);
    return;
  }
  
  var passwordRegex = /^(?=.*\d.*\d)[a-zA-Z0-9]{8,}$/;
  if (!passwordRegex.test(password)) {
    var errorMessage = "Пароль должен содержать минимум 8 символов латинского алфавита и 2 цифры";
    appendErrorMessage(errorMessage);
    return;
  }

  if (password !== confirm_password) {
    var errorMessage = "Пароли не совпадают";
    appendErrorMessage(errorMessage);
    return;
  }

  var data = {
    "username": username,
    "email": email,
    "password": password,
    "confirm_password": confirm_password,
  };

  try {
    var response = await fetch("/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      var responseDiv = document.getElementById("response");
      responseDiv.innerHTML = "Успешно";
      window.location.href = "/login/";
    } else {
      var errorMessage = "Произошла ошибка при отправке запроса";
      appendErrorMessage(errorMessage);
    }
  } catch (error) {
    var errorMessage = "Произошла ошибка при отправке запроса";
    appendErrorMessage(errorMessage);
  }
}

function appendErrorMessage(message) {
  var errorDiv = document.getElementById("error-message");
  errorDiv.style.color = "white";
  errorDiv.innerHTML = message;
}

