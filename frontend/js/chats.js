async function getAccessToken() {
  try {
    let response = await fetch('/getcookies/', {
      credentials: 'same-origin'
    });
    if (response.ok) {
      let token = await response.text(); 
      if (token) {
        token = token.replace(/"/g, '');
        return token;
      } else {
        console.log('Ошибка получения токена');
      }
    } else {
      console.log('Ошибка получения токена:', response.status);
    }
  } catch (error) {
    console.log('Ошибка получения токена:');
  }
  return '';
}

async function loadChats() {
      try {
        const response = await fetch("/api/chats", { credentials: "include" });
        if (!response.ok) throw new Error("Ошибка загрузки чатов");
        const chats = await response.json();

        const chatList = document.getElementById("chatList");
        chatList.innerHTML = "";

        chats.forEach(chat => {
          const li = document.createElement("li");
          li.className = "chat-item";
          li.onclick = () => window.location.href = `/get/chat/?recipient_id=${chat.recipient.id}`;

          const avatar = document.createElement("img");
          avatar.className = "chat-avatar";
          avatar.src = chat.recipient.profile?.avatar || "/static/img/default-avatar.png";

          const info = document.createElement("div");
          info.className = "chat-info";

          const name = document.createElement("p");
          name.className = "chat-name";
          name.textContent = chat.recipient.username;

          const message = document.createElement("p");
          message.className = "chat-message";
          message.textContent = chat.last_message || "Нет сообщений";

          info.appendChild(name);
          info.appendChild(message);

          const time = document.createElement("span");
          time.className = "chat-time";
          if (chat.last_message_time) {
            const date = new Date(chat.last_message_time);
            time.textContent = date.toLocaleDateString("ru-RU", {
                day: "2-digit",
                month: "2-digit"
            });
        }

          li.appendChild(avatar);
          li.appendChild(info);
          li.appendChild(time);

          chatList.appendChild(li);
        });
      } catch (error) {
        console.error(error);
        document.getElementById("chatList").innerHTML = "<p>Ошибка загрузки чатов</p>";
      }
    }

loadChats();


async function initializeChatListWebSocket() {
  console.log("initializeChatListWebSocket() called");
  let jwtToken = await getAccessToken();

  if (!jwtToken) {
    window.location.href = '/login/';
    return;
  }

  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = window.location.host;
  let socket = new WebSocket(`${wsProtocol}//${wsHost}/ws/chat-list`);

  socket.onopen = () => {
    console.log('WebSocket connection for chat list established');
    socket.send(jwtToken);
  };

  socket.onmessage = (event) => {
    try {
      let data = JSON.parse(event.data);

      if (data.type === "chat_update") {
        loadChats();

      }
    } catch (err) {
      console.error("Ошибка обработки сообщения чата:", err);
    }
  };

  socket.onclose = (event) => {
    if (event.code === 1008) {
      window.location.href = '/profile/';
    } else {
      console.log('Chat list socket closed, reconnecting in 5s...', event);
      setTimeout(initializeChatListWebSocket, 5000);
    }
  };

  socket.onerror = (error) => {
    console.error('Chat list WebSocket error:', error);
    socket.close();
  };
}

initializeChatListWebSocket();
