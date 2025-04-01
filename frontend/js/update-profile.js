async function submitForm(event) {
    event.preventDefault();

    let form = document.querySelector('form');
    let formData = new FormData(form);

    try {
      let response = await fetch('/update-profile/', {
          method: 'POST',
          body: formData
      });

      if (response.status === 200) {
          handleSuccess();
      } else if (response.status === 401) {
          redirectToLogin();
      } else if (response.status === 400) {
        console.log(response.text)
          displayErrorMessage("Что-то пошло не так, максимальная длина имени и фамилии 60 символов");
      }
    } catch(error) {
      displayErrorMessage("Что-то пошло не так");
    }
}

function displayErrorMessage(message) {
  let errorMessageElement = document.getElementById("error-message");
  errorMessageElement.textContent = message;
  errorMessageElement.classList.remove("hidden");
}

function handleSuccess() {
    window.location.href = '/profile/';
}

function redirectToLogin() {
    window.location.href = '/login/';
}

