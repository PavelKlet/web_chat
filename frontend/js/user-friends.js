let currentFriendsPage = 1;
let currentSearchPage = 1;
let isSearching = false;
let hasMoreFriends = true;
let hasMoreSearchResults = true;
let currentSearchQuery = ""; 

window.addEventListener("scroll", async () => {
    if (window.scrollY >= document.documentElement.scrollHeight - window.innerHeight - 100) {
        if (isSearching && hasMoreSearchResults) {
            currentSearchPage += 1;
            await searchFriendsPaginated(currentSearchPage, currentSearchQuery);
        } else if (!isSearching && hasMoreFriends) {
            currentFriendsPage += 1;
            await getFUserFriends(currentFriendsPage);
        }
    }
});

async function getFUserFriends(page) {
    let friendsResponse = await fetch(`/friends/?pagination=true&page=${page}`);
    if (friendsResponse.status === 200) {
        let friendsData = await friendsResponse.json();

        let friendsList = document.getElementById("friends_list");
        if (page === 1) {
            friendsList.innerHTML = ""; 
        }

        if (friendsData.length === 0 && page === 1) {
            
            friendsList.innerHTML = "<p>Список друзей пуст.</p>";
            hasMoreFriends = false;
        } else {
            friendsData.forEach(friend => appendFriendToList(friendsList, friend));
            if (friendsData.length === 0) {
                hasMoreFriends = false;
            }
        }
    }
}


async function searchFriends() {
    isSearching = true;
    currentSearchPage = 1;
    hasMoreSearchResults = true;

    currentSearchQuery = document.getElementById("search_input").value;

    
    document.getElementById("friends_section").style.display = "none";
    document.getElementById("search_section").style.display = "block";

    let searchList = document.getElementById("search_list");
    searchList.innerHTML = ""; 
    await searchFriendsPaginated(currentSearchPage, currentSearchQuery);
}

async function searchFriendsPaginated(page, query) {
    if (!query) return;

    let searchResponse = await fetch(`/search/?query=${query}&pagination=true&page=${page}`);
    if (searchResponse.status === 200) {
        let searchData = await searchResponse.json();

        let searchList = document.getElementById("search_list");
        if (page === 1) {
            searchList.innerHTML = ""; 
        }

        if (searchData.length === 0 && page === 1) {
            
            searchList.innerHTML = "<p>По вашему запросу ничего не найдено.</p>";
            hasMoreSearchResults = false;
        } else {
            searchData.forEach(friend => appendFriendToList(searchList, friend));
            if (searchData.length === 0) {
                hasMoreSearchResults = false;
            }
        }
    }
}


function appendFriendToList(listElement, friend) {
    let profileLink = document.createElement("a");
    profileLink.href = `/user-profile/${friend.id}`;
    profileLink.classList.add("friend-link");

    let listItem = document.createElement("li");
    listItem.classList.add("friend-item");

    let friendContainer = document.createElement("div");
    friendContainer.classList.add("friend-container");

    let avatarImage = document.createElement("img");
    avatarImage.src = friend.avatar || "/static/images/default-avatar.png";
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

    listElement.appendChild(profileLink);
}

function resetFriendsView() {
    isSearching = false;
    currentFriendsPage = 1;
    hasMoreFriends = true;

    document.getElementById("search_section").style.display = "none";
    document.getElementById("friends_section").style.display = "block";

    let friendsList = document.getElementById("friends_list");
    friendsList.innerHTML = "";
    getFUserFriends(currentFriendsPage);
}

getFUserFriends(currentFriendsPage);
