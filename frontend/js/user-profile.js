async function CheckProtectUserId() {
  let path = window.location.pathname;
  let parts = path.split("/");
  let user_id = parseInt(parts[parts.length - 2]);

  let protectResponse = await fetch("/protect/profile/");
  if (!protectResponse.ok) {
    return;
  }

  let protectData = await protectResponse.json();
  let protectUserId = protectData.user_id; 

  let isFriendResponse = await fetch(`/friends/is-friend/${user_id}`);
  if (!isFriendResponse.ok) {
    return;
  }

  let { is_friend } = await isFriendResponse.json();
  let addFriendLink = document.querySelector("div > button");

  if (is_friend) {
    let parentDiv = addFriendLink.parentElement;
    let textElement = document.createElement("p");
    textElement.textContent = "Пользователь уже добавлен в друзья";
    parentDiv.removeChild(addFriendLink); 
    parentDiv.appendChild(textElement); 
  } else if (protectUserId !== user_id) {
    addFriendLink.classList.remove("hidden");
    addFriendLink.setAttribute("data-friend-id", user_id); 
    addFriendLink.addEventListener("click", addFriend);
  } else {
    window.location.href = '/profile/';
  }

  let userProfileResponse = await fetch(`/get/user-profile/${user_id}`);
  if (!userProfileResponse.ok) {
    if (userProfileResponse.status === 404) {
      window.location.href = '/not-found/';
    }
    return;
  }

  let userProfile = await userProfileResponse.json();
  let usernameElement = document.querySelector("h1");
  usernameElement.textContent = userProfile.username;
  document.getElementById("avatar_image").src = userProfile.avatar;
  document.getElementById("first_name_value").textContent = userProfile.first_name;
  document.getElementById("last_name_value").textContent = userProfile.last_name;
}

async function addFriend() {
  const friend_id = this.getAttribute("data-friend-id");

  const response = await fetch(`/add/friend/${friend_id}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (response.ok) {
    alert("Пользователь добавлен в друзья");
    location.reload();
  } else {
    alert("Ошибка при добавлении пользователя в друзья");
  }
}





  