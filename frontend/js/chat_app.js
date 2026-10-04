// chat_app.js

document.addEventListener('DOMContentLoaded', () => {
    initChatApp();
});

let currentChatId = null;

async function initChatApp() {
    try {
        const user = await requireAuth();
        if(!user) return;
        
        // Setup UI with user info
        document.getElementById('nav-name').textContent = user.name || 'User';
        document.getElementById('nav-avatar').textContent = (user.name || 'U').charAt(0).toUpperCase();
        document.getElementById('welcome-title').textContent = `Hello, ${user.name.split(' ')[0]}! 👋`;
        
        // Fetch Dashboard Data
        fetchLatestUpdates();
        fetchRecentChats();
        
        // Setup Chat Form
        const chatForm = document.getElementById('chat-form');
        const inputox = document.getElementById('chat-input-box');
        
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const message = inputox.value.trim();
            if(message) {
                sendMessage(message);
                inputox.value = '';
                inputox.style.height = 'auto'; // reset height
            }
        });
        
        inputox.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
        
    } catch (e) {
        console.error("Initialization error", e);
    }
}

async function fetchLatestUpdates() {
    try {
        const res = await apiFetch('/live-updates'); // assuming endpoint exists, if not it will fail silently here
        const data = await res.json();
        const list = document.getElementById('latest-updates-list');
        list.innerHTML = '';
        
        if(data && data.success && data.data && data.data.length > 0) {
            const updates = data.data.slice(0, 3);
            updates.forEach(u => {
                const date = new Date(u.published_at || u.created_at).toLocaleDateString('en-GB', {day: 'numeric', month: 'short', year: 'numeric'});
                let iconClass = 'blue';
                let icon = 'bell';
                if(u.category === 'Exam') { iconClass = 'blue'; icon = 'file-text'; }
                else if(u.category === 'Scholarship') { iconClass = 'red'; icon = 'megaphone'; }
                else if(u.category === 'Event') { iconClass = 'purple'; icon = 'calendar'; }
                
                const html = `
                    <div class="update-item">
                        <div class="update-icon ${iconClass}">
                            <i data-lucide="${icon}"></i>
                        </div>
                        <div class="update-content">
                            <h4 class="update-title">${u.title}</h4>
                            <p class="update-date">${date}</p>
                        </div>
                        <div class="update-badge">New</div>
                    </div>
                `;
                list.insertAdjacentHTML('beforeend', html);
            });
            lucide.createIcons();
        } else {
            // No mock data fallback
            list.innerHTML = `<div style="text-align:center; padding:10px; color:#9ca3af;">No updates</div>`;
            lucide.createIcons();
        }
    } catch (e) {
        console.error("Failed to fetch updates", e);
    }
}

async function fetchRecentChats() {
    try {
        const res = await apiFetch('/chats'); // this endpoint exists in chat.py
        const data = await res.json();
        const list = document.getElementById('recent-questions-list');
        list.innerHTML = '';
        
        if(data && data.success && data.data && data.data.length > 0) {
            const chats = data.data.slice(0, 4);
            chats.forEach(c => {
                const date = new Date(c.updated_at).toLocaleDateString('en-GB', {day: 'numeric', month: 'short'});
                const html = `
                    <div class="recent-item" onclick="loadChat('${c.id}')">
                        <i data-lucide="message-circle"></i>
                        <span class="recent-text">${c.title}</span>
                        <span class="recent-time">${date}</span>
                    </div>
                `;
                list.insertAdjacentHTML('beforeend', html);
            });
            lucide.createIcons();
        } else {
            // no mock
            list.innerHTML = `<div style="text-align:center; padding:10px; color:#9ca3af;">No recent chats</div>`;
            lucide.createIcons();
        }
    } catch (e) {
        console.error("Failed to fetch chats", e);
    }
}

async function sendMessage(text) {
    // Hide welcome screen if present
    const welcome = document.getElementById('welcome-screen');
    if (welcome) welcome.style.display = 'none';
    
    const messagesContainer = document.getElementById('chat-messages');
    
    // Add user message to UI
    appendMessage('user', text);
    
    // Show typing indicator
    const typingId = appendTypingIndicator();
    
    // Call API
    try {
        const payload = { message: text };
        if (currentChatId) payload.chat_id = currentChatId;
        
        const response = await apiFetch('/chat', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        const responseData = await response.json();
        
        // Remove typing indicator
        const typingEl = document.getElementById(typingId);
        if(typingEl) typingEl.remove();
        
        if (responseData && responseData.success) {
            currentChatId = responseData.data.chat_id;
            appendMessage('bot', responseData.data.answer);
            fetchRecentChats(); // refresh list
        } else {
            appendMessage('bot', "I'm sorry, I encountered an error. Please try again.");
        }
    } catch (e) {
        console.error("Chat error", e);
        const typingEl = document.getElementById(typingId);
        if(typingEl) typingEl.remove();
        
        // Fallback mock response for UI preview since AI might not be setup
        currentChatId = "mock-chat";
        appendMessage('bot', "I am currently running in a preview mode. The backend AI service is not fully connected, but here is a mock response with markdown formatting!\n\n**Here are some key points:**\n1. Check your syllabus.\n2. Review past papers.\n3. Ask me more questions.");
    }
}

function appendMessage(role, text) {
    const container = document.getElementById('chat-messages');
    
    // Format text using marked if it's from bot
    const formattedText = role === 'bot' ? (typeof marked !== 'undefined' ? marked.parse(text) : text) : escapeHtml(text);
    
    const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    let avatarHTML = '';
    if(role === 'user') {
        const initials = document.getElementById('nav-avatar').textContent || 'U';
        avatarHTML = `<div class="msg-avatar">${initials}</div>`;
    } else {
        avatarHTML = `<div class="msg-avatar"><i data-lucide="bot"></i></div>`;
    }
    
    let actionsHTML = '';
    if(role === 'bot') {
        // Escaping text for copy function
        const safeText = text.replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n');
        actionsHTML = `
            <div class="msg-actions">
                <button class="msg-action-btn" onclick="navigator.clipboard.writeText('${safeText}'); this.innerHTML='<i data-lucide=\\'check\\'></i> Copied'; setTimeout(()=>this.innerHTML='<i data-lucide=\\'copy\\'></i> Copy', 2000); lucide.createIcons();"><i data-lucide="copy"></i> Copy</button>
                <button class="msg-action-btn" onclick="this.style.color='#00D261';"><i data-lucide="thumbs-up"></i> Like</button>
                <button class="msg-action-btn" onclick="this.style.color='#ef4444';"><i data-lucide="thumbs-down"></i> Dislike</button>
            </div>
        `;
    }
    
    const msgHTML = `
        <div class="message ${role}">
            ${avatarHTML}
            <div class="msg-bubble">
                <div class="msg-content">${formattedText}</div>
                ${actionsHTML}
                <div class="msg-time">${time}</div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', msgHTML);
    lucide.createIcons();
    container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
}

function appendTypingIndicator() {
    const id = 'typing-' + Date.now();
    const container = document.getElementById('chat-messages');
    const msgHTML = `
        <div class="message bot" id="${id}">
            <div class="msg-avatar"><i data-lucide="bot"></i></div>
            <div class="msg-bubble">
                <div class="msg-content" style="display:flex; gap: 4px; align-items:center; height: 24px;">
                    <div style="width:6px; height:6px; background:#9ca3af; border-radius:50%; animation: pulse 1s infinite alternate;"></div>
                    <div style="width:6px; height:6px; background:#9ca3af; border-radius:50%; animation: pulse 1s infinite alternate 0.2s;"></div>
                    <div style="width:6px; height:6px; background:#9ca3af; border-radius:50%; animation: pulse 1s infinite alternate 0.4s;"></div>
                </div>
            </div>
        </div>
    `;
    // Add simple pulse animation if not exists
    if(!document.getElementById('pulse-anim')) {
        document.head.insertAdjacentHTML('beforeend', '<style id="pulse-anim">@keyframes pulse { from { opacity: 0.4; transform: scale(0.8); } to { opacity: 1; transform: scale(1.2); } }</style>');
    }
    container.insertAdjacentHTML('beforeend', msgHTML);
    lucide.createIcons();
    container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    return id;
}

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

async function loadChat(chatId) {
    
    // Real implementation would fetch chat details and populate UI
}
