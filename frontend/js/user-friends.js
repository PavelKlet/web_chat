
let currentPage = 1;
let hasMoreFriends = true;

window.addEventListener('scroll', async () => {
  if (window.scrollY >= document.documentElement.scrollHeight - window.innerHeight - 100 && hasMoreFriends) {
    currentPage += 1;
    await getFUserFriends(currentPage);
  }
});


async function getFUserFriends(page) {
  let friendsResponse = await fetch(`/friends/?pagination=true&page=${page}`);
  if (friendsResponse.status === 200) {
    let friendsData = await friendsResponse.json();

    let friendsList = document.getElementById("friends_list");
    friendsData.forEach(function(friend) {
      let profileLink = document.createElement("a");
      profileLink.href = `/user-profile/${friend.id}`;
      profileLink.classList.add("friend-link");

      let listItem = document.createElement("li");
      listItem.classList.add("friend-item");

      let friendContainer = document.createElement("div");
      friendContainer.classList.add("friend-container");

      let avatarImage = document.createElement("img");
      avatarImage.src = friend.avatar;
      avatarImage.alt = "Аватар";
      avatarImage.width = 50;
      avatarImage.height = 50;
      avatarImage.style.borderRadius = "50%";

      friendContainer.appendChild(avatarImage);

      let friendInfo = document.createElement("div");
      friendInfo.classList.add("friend-info");

      let username = document.createElement("p");
      username.classList.add("friend-username");
      username.textContent = friend.username;

      friendInfo.appendChild(username);
      friendContainer.appendChild(friendInfo);
      listItem.appendChild(friendContainer);

      profileLink.appendChild(listItem);
      
      friendsList.appendChild(profileLink);
    });

    if (friendsData.length === 0) {
      hasMoreFriends = false;
    }
  }
}


async function searchFriends() {
  let searchValue = document.getElementById("search_input").value;

  let searchResponse = await fetch(`/search/?query=${searchValue}`);
  if (searchResponse.status === 200) {
    let searchData = await searchResponse.json();

    let friendsList = document.getElementById("friends_list");
    friendsList.innerHTML = "";

    if (searchData.length === 0) {
      let noResultsMessage = document.createElement("li");
      noResultsMessage.textContent = "Нет результатов";
      friendsList.appendChild(noResultsMessage);
    } else {
      searchData.forEach(function (friend) {
        let profileLink = document.createElement("a");
        profileLink.href = `/user-profile/${friend.id}`;
        profileLink.classList.add("friend-link");

        let listItem = document.createElement("li");
        listItem.classList.add("friend-item");

        let friendContainer = document.createElement("div");
        friendContainer.classList.add("friend-container");

        let avatarImage = document.createElement("img");
        avatarImage.src = friend.avatar;
        avatarImage.alt = "Аватар";
        avatarImage.width = 50;
        avatarImage.height = 50;
        avatarImage.style.borderRadius = "50%";

        friendContainer.appendChild(avatarImage);

        let friendInfo = document.createElement("div");
        friendInfo.classList.add("friend-info");

        let username = document.createElement("p");
        username.classList.add("friend-username");
        username.textContent = friend.username;

        friendInfo.appendChild(username);
        friendContainer.appendChild(friendInfo);
        listItem.appendChild(friendContainer);

        profileLink.appendChild(listItem);

        friendsList.appendChild(profileLink);
      });
    }
  }
}




getFUserFriends(currentPage);

