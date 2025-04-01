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

    let socket = new WebSocket(`ws://localhost:8000/ws/${recipient_id}`);
    let messagesContainer = document.getElementById('messagesContainer');
    let sendMessageForm = document.getElementById('sendMessageForm');
    let messageInput = document.getElementById('messageInput');
    
    socket.onopen = () => {
      console.log('WebSocket connection established');
      socket.send(jwtToken); 
    };
    
    socket.onmessage = (event) => {
      let messageData = JSON.parse(event.data);
      let messageText = messageData.text;
      let avatarUrl = messageData.avatarUrl;
      addMessageToContainer(messageText, avatarUrl);
    };

    socket.onclose = () => {
      // window.location.href = '/profile/';
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
    
    function sendMessage(text) {
      socket.send(text);
    }
    
    sendMessageForm.addEventListener('submit', (event) => {
      event.preventDefault();
      let inputText = messageInput.value;
      if (inputText) {
        sendMessage(inputText);
        messageInput.value = '';
      }
    });
  }
}
}

initializeWebSocket();
