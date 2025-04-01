async function handleRequest() {
  let body = document.querySelector("body");

  let response = await fetch("/protect/profile/");

  if (response.status === 200) {
    let data = await response.json();

    body.classList.remove("hidden");
    let avatarImage = document.getElementById("avatar_image");
    avatarImage.src = data.avatar;
    let firstNameValue = document.getElementById("first_name_value");
    let lastNameValue = document.getElementById("last_name_value");
    firstNameValue.textContent = data.first_name;
    lastNameValue.textContent = data.last_name;
    let usernameElement = document.querySelector(".shifting-h1");
    usernameElement.textContent = data.username;
  } 
  else if (response.status === 401) {
    window.location.replace("/login/");
  }
}

async function getUserFriends() {
  let page = 1;
  let limit = 10;
  let friendsResponse = await fetch(`/friends/?page=${page}&limit=${limit}`);

  if (friendsResponse.status === 200) {
    let friendsData = await friendsResponse.json();
    let friendsListContainer = document.querySelector(".friends-container");

    if (friendsData.length === 0) {
      let emptyMessage = document.createElement("p");
      emptyMessage.textContent = "У вас еще нет друзей";
      emptyMessage.style.margin = "0 auto";
      friendsListContainer.appendChild(emptyMessage);
    } else {
      friendsData.forEach(function (friend) {
        let friendItemContainer = document.createElement("div");
        friendItemContainer.classList.add("friend-item");

        let friendAvatarContainer = document.createElement("div");
        friendAvatarContainer.classList.add("friend-avatar-container");

        let friendAvatar = document.createElement("img");
        friendAvatar.classList.add("friend-avatar");
        friendAvatar.src = friend.avatar;
        friendAvatar.alt = "Аватар";
        friendAvatar.width = 50;
        friendAvatar.height = 50;
        friendAvatar.style.borderRadius = "50%";
        friendAvatarContainer.appendChild(friendAvatar);

        let friendUsername = document.createElement("p");
        friendUsername.classList.add("friend-username");
        friendUsername.textContent =
          friend.username.length > 10
            ? friend.username.substring(0, 10) + "..."
            : friend.username;

        friendItemContainer.appendChild(friendAvatarContainer);
        friendItemContainer.appendChild(friendUsername);

        friendsListContainer.appendChild(friendItemContainer);
      });
    }
  }
}



document.addEventListener("DOMContentLoaded", handleRequest);




