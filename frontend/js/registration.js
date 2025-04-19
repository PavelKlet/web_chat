async function registerUser() {
  var form = document.getElementById("registration-form");
  var username = form.elements.username.value;
  var email = form.elements.email.value;
  var password = form.elements.password.value;
  var confirm_password = form.elements.confirm_password.value;

  var errorDiv = document.getElementById("error-message");
  var responseDiv = document.getElementById("response");
  errorDiv.innerHTML = "";
  responseDiv.innerHTML = "";

  var emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
  if (!emailRegex.test(email)) {
    appendErrorMessage("Введите корректный email");
    return;
  }

  if (username.trim() === "") {
    appendErrorMessage("Введите ваше имя пользователя");
    return;
  }
  
  var passwordRegex = /^(?=.*\d.*\d)[a-zA-Z0-9]{8,}$/;
  if (!passwordRegex.test(password)) {
    appendErrorMessage("Пароль должен содержать минимум 8 символов латинского алфавита и 2 цифры");
    return;
  }

  if (password !== confirm_password) {
    appendErrorMessage("Пароли не совпадают");
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
      responseDiv.innerHTML = "Регистрация прошла успешно!";
      responseDiv.style.color = "green";
      setTimeout(() => {
        window.location.href = "/login/";
      }, 200);
    } else {
      var errorData = await response.json();
      if (errorData.detail) {
        handleServerError(errorData.detail);
      } else {
        appendErrorMessage("Произошла ошибка при отправке запроса");
      }
    }
  } catch (error) {
    appendErrorMessage("Произошла ошибка при отправке запроса");
  }
}

function handleServerError(detail) {
  var errorDiv = document.getElementById("error-message");
  errorDiv.style.color = "red";

  if (detail.includes("Email already exists")) {
    errorDiv.innerHTML = "Этот email уже зарегистрирован.";
  } else if (detail.includes("Username already exists")) {
    errorDiv.innerHTML = "Это имя пользователя уже занято.";
  } else {
    errorDiv.innerHTML = "Произошла ошибка: " + detail;
  }
}

function appendErrorMessage(message) {
  var errorDiv = document.getElementById("error-message");
  errorDiv.style.color = "red";
  errorDiv.innerHTML = message;
}

