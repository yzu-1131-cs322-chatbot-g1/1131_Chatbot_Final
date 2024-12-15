const chatModeNames = {
    'GEMINI': '聊天',
    'SEARCH_MOVIE': '查詢資料庫',
    'GUESS_MOVIE': '以圖搜尋',
    'SUB_TRANSLATE': '字幕翻譯'
};

function setChatMode(mode) {
    fetch(`/set_chat_mode/${mode}`, { method: 'POST' })
        .then(response => response.text())
        .then(data => {
            document.getElementById('current-mode').textContent = `目前模式: ${chatModeNames[mode]}`;
            document.getElementById('chat-box').innerHTML = ''; // 清空對話框
        })
        .catch(error => console.error('Error:', error));
}

function sendMessage() {
    const inputElement = document.getElementById('chat-input');
    const message = inputElement.value;
    if (message.trim() === '') return;

    const chatBox = document.getElementById('chat-box');
    const userMessage = document.createElement('div');
    userMessage.textContent = `你：${message}`;
    userMessage.className = 'chat-message user';
    chatBox.appendChild(userMessage);

    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(data => {
        const botMessage = document.createElement('div');
        botMessage.textContent = `機器人：${data.reply}`;
        botMessage.className = 'chat-message bot';
        chatBox.appendChild(botMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => console.error('Error:', error));

    inputElement.value = '';
}

function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    if (!file) return;

    const chatBox = document.getElementById('chat-box');
    const userMessage = document.createElement('div');
    userMessage.className = 'chat-message user';

    if (file.type.startsWith('image/')) {
        // 如果是圖片類型，顯示圖片預覽
        const reader = new FileReader();
        reader.onload = function (e) {
            userMessage.innerHTML = `<img src="${e.target.result}" alt="${file.name}" style="max-width: 100%;">`;
            chatBox.appendChild(userMessage);
            chatBox.scrollTop = chatBox.scrollHeight; // 滾動到聊天框底部
        };
        reader.readAsDataURL(file); // 將檔案讀取為 Base64 資料 URI
    } else {
        // 如果不是圖片類型，顯示文字訊息
        userMessage.textContent = `你上傳了檔案：${file.name}`;
        chatBox.appendChild(userMessage);
        chatBox.scrollTop = chatBox.scrollHeight; // 滾動到聊天框底部
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload_file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const botMessage = document.createElement('div');
        botMessage.textContent = `機器人：${data.reply}`;
        //格式化回覆訊息 /n就可以換行
        if(data.reply.includes("\n")){
            botMessage.innerHTML = data.reply.replace(/\n/g, "<br>");
        } else {
            botMessage.textContent = `機器人：${data.reply}`;
        }
        botMessage.className = 'chat-message bot';
        chatBox.appendChild(botMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => console.error('Error:', error));
}
