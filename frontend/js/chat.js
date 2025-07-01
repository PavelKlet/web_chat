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


async function initializeWebSocket() {
  console.log("initializeWebSocket() called");
  let jwtToken = await getAccessToken();
  
  if (!jwtToken) {
    window.location.href = '/login/';
    return;
  }
  else {
    let urlParams = new URLSearchParams(window.location.search);
    let recipient_id = urlParams.get('recipient_id');

    if (recipient_id) {
      recipient_id = parseInt(recipient_id);

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.host;
    let socket = new WebSocket(`${wsProtocol}//${wsHost}/ws/${recipient_id}`);
    let messagesContainer = document.getElementById('messagesContainer');
    let sendMessageForm = document.getElementById('sendMessageForm');
    let messageInput = document.getElementById('messageInput');
    
    socket.onopen = () => {
      console.log('WebSocket connection established');
      socket.send(jwtToken); 
    };

    
    socket.onmessage = (event) => {
      let messageData = JSON.parse(event.data);
    
      if (Array.isArray(messageData)) {
        messageData.forEach((msg) => {
          if (msg && msg.text && msg.text.trim() !== "") {
            addMessageToContainer(msg.text, msg.avatarUrl);
          }
        });
      } 
      else if (messageData && messageData.text && messageData.text.trim() !== "") {
        addMessageToContainer(messageData.text, messageData.avatarUrl);
      } else {
        console.warn("Неизвестный формат сообщения:", messageData);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    

    socket.onclose = (event) => {
      if (event.code === 1008) {
        window.location.href = '/profile/';
      } else {
        console.log('Соединение закрыто:', event);
      }
    };
    
    function addMessageToContainer(messageText, avatarUrl) {
      let messageElement = document.createElement('div');
      messageElement.classList.add('message');
      messageElement.style.marginBottom = '10px';
    
      let avatarElement = document.createElement('img');
      avatarElement.classList.add('avatar');
      avatarElement.src = avatarUrl;
      avatarElement.style.width = '50px';
      avatarElement.style.height = '50px';
      avatarElement.style.borderRadius = '50%';
      messageElement.appendChild(avatarElement);
    
      let messageTextElement = document.createElement('div');
      messageTextElement.classList.add('message-text');
      messageTextElement.textContent = messageText;
      messageElement.appendChild(messageTextElement);
    
      messagesContainer.appendChild(messageElement);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    sendMessageForm.addEventListener('submit', (event) => {
    event.preventDefault();
    let inputText = messageInput.value.trim();
    if (inputText) {
      try {
        socket.send(inputText); 
        messageInput.value = '';
      } catch (error) {
      console.error("Ошибка при отправке сообщения:", error);
    }
  } else {
    console.warn("Сообщение не может быть пустым.");
  }
  });
  }
}
}

initializeWebSocket();
