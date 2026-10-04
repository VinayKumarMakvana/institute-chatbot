document.addEventListener('DOMContentLoaded', async () => {
    const user = await requireAuth();
    if (!user) return; // Will redirect

    // Display User info in Nav
    document.getElementById('nav-name').textContent = user.name;
    const initials = user.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
    document.getElementById('nav-avatar').textContent = initials;
    document.getElementById('nav-role').textContent = user.role;

    const chatContainer = document.getElementById('chat-messages');
    const inputBox = document.getElementById('chat-input-box');
    const sendBtn = document.querySelector('.send-btn');
    
    let currentChatId = null;

    // Check URL for existing chat
    const urlParams = new URLSearchParams(window.location.search);
    const queryChatId = urlParams.get('chat_id');

    if (queryChatId) {
        currentChatId = queryChatId;
        await loadChatHistory(queryChatId);
    } else {
        // Render initial greeting
        chatContainer.innerHTML = '';
        renderBotMessage("Hello! I am your AI Assistant. I can help you find answers from the uploaded PDFs, syllabus, and previous year papers. What do you want to learn today?", []);
    }

    // Input handlers
    sendBtn.addEventListener('click', handleSend);
    inputBox.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    async function handleSend() {
        const text = inputBox.value.trim();
        if (!text) return;

        // 1. Render User Message
        renderUserMessage(text);
        inputBox.value = '';

        // 2. Show Typing Indicator
        const typingId = showTypingIndicator();

        // 3. Call Backend API
        try {
            const payload = { message: text };
            if (currentChatId) payload.chat_id = currentChatId;

            const response = await apiFetch('/chat', {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            removeTypingIndicator(typingId);

            if (!response.ok) {
                renderBotMessage("I'm sorry, I encountered an error processing your request.", []);
                return;
            }

            const resData = await response.json();
            if (resData.success && resData.data) {
                const aiData = resData.data;
                currentChatId = aiData.chat_id; // Set current chat id for subsequent messages
                
                // Update URL without reloading so history is preserved
                if(!urlParams.has('chat_id')) {
                    const newUrl = window.location.pathname + '?chat_id=' + currentChatId;
                    window.history.replaceState({path:newUrl}, '', newUrl);
                }

                renderBotMessage(aiData.answer, aiData.sources);
            } else {
                renderBotMessage(resData.message || "An error occurred.", []);
            }
        } catch (err) {
            console.error("Chat API Error:", err);
            removeTypingIndicator(typingId);
            renderBotMessage("I'm unable to connect to the server right now. Please try again later.", []);
        }
    }

    function renderUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user';
        msgDiv.innerHTML = `
            <div class="msg-avatar">${initials}</div>
            <div class="msg-content">${escapeHTML(text)}</div>
        `;
        chatContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function renderBotMessage(text, sources) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot';
        
        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = '<div class="source-pills">';
            sources.forEach(src => {
                sourcesHtml += `<div class="source-pill" title="${escapeHTML(src.snippet || '')}"><i data-lucide="file-text" style="width:12px; height:12px;"></i> ${escapeHTML(src.document_title)} (Page ${src.page_number})</div>`;
            });
            sourcesHtml += '</div>';
        }

        // Extremely basic markdown to HTML for bolding (e.g. **text**)
        const formattedText = escapeHTML(text).replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>').replace(/\\n/g, '<br>');

        msgDiv.innerHTML = `
            <div class="msg-avatar"><i data-lucide="bot"></i></div>
            <div class="msg-content">
                ${formattedText}
                ${sourcesHtml}
            </div>
        `;
        chatContainer.appendChild(msgDiv);
        
        if (window.lucide) window.lucide.createIcons({root: msgDiv});
        scrollToBottom();
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot';
        msgDiv.id = id;
        msgDiv.innerHTML = `
            <div class="msg-avatar"><i data-lucide="bot"></i></div>
            <div class="msg-content" style="display:flex; align-items:center; gap:4px; padding: 12px 20px;">
                <div class="typing-dot" style="width:6px; height:6px; background:#00D261; border-radius:50%; animation: blink 1.4s infinite both;"></div>
                <div class="typing-dot" style="width:6px; height:6px; background:#00D261; border-radius:50%; animation: blink 1.4s infinite both; animation-delay: 0.2s;"></div>
                <div class="typing-dot" style="width:6px; height:6px; background:#00D261; border-radius:50%; animation: blink 1.4s infinite both; animation-delay: 0.4s;"></div>
            </div>
        `;
        // Inject keyframes if not present
        if(!document.getElementById('typing-keyframes')) {
            const style = document.createElement('style');
            style.id = 'typing-keyframes';
            style.innerHTML = `@keyframes blink { 0% { opacity: 0.2; } 20% { opacity: 1; } 100% { opacity: 0.2; } }`;
            document.head.appendChild(style);
        }

        chatContainer.appendChild(msgDiv);
        if (window.lucide) window.lucide.createIcons({root: msgDiv});
        scrollToBottom();
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    async function loadChatHistory(chatId) {
        try {
            const res = await apiFetch('/chats/' + chatId);
            if (!res.ok) {
                chatContainer.innerHTML = '<div style="text-align:center; color:#ef4444; margin-top:20px;">Failed to load chat history.</div>';
                return;
            }
            const resData = await res.json();
            if (resData.success && resData.data) {
                chatContainer.innerHTML = '';
                const messages = resData.data.messages || [];
                if(messages.length === 0) {
                     renderBotMessage("Hello! I am your AI Assistant. I can help you find answers from the uploaded PDFs, syllabus, and previous year papers. What do you want to learn today?", []);
                     return;
                }
                
                messages.forEach(m => {
                    if (m.role === 'USER') {
                        renderUserMessage(m.content);
                    } else {
                        renderBotMessage(m.content, m.sources);
                    }
                });
            }
        } catch (e) {
            console.error("Load Chat Error:", e);
        }
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
});
