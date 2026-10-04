let chatsData = [];
let activeChatId = null;

const colors = [
    { bg: 'rgba(16, 185, 129, 0.1)', color: '#10b981', icon: 'book' },
    { bg: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6', icon: 'file-text' },
    { bg: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', icon: 'info' },
    { bg: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', icon: 'calendar' },
    { bg: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', icon: 'help-circle' }
];

document.addEventListener('DOMContentLoaded', () => {
    fetchHistoryList();
});

async function fetchHistoryList() {
    try {
        const response = await apiFetch('/chats');
        const data = await response.json();
        
        if (data.success && data.data) {
            chatsData = data.data;
            renderHistoryList(chatsData);
            
            // Auto select first chat if available
            if(chatsData.length > 0) {
                selectChat(chatsData[0].id);
            }
        }
    } catch (err) {
        console.error("Failed to load chat history", err);
        document.getElementById('history-list-container').innerHTML = '<div style="text-align:center; padding:2rem; color:#ef4444;">Failed to load history</div>';
    }
}

function renderHistoryList(chats) {
    const container = document.getElementById('history-list-container');
    if(!chats || chats.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: #9ca3af; padding: 2rem;">No chat history found.</div>';
        return;
    }
    
    container.innerHTML = chats.map((chat, idx) => {
        const style = colors[idx % colors.length];
        const dateStr = new Date(chat.updated_at).toLocaleString('en-US', { day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: '2-digit' });
        
        // Generate pseudo-tags from title for the UI look
        const words = chat.title.split(' ').filter(w => w.length > 3).slice(0, 3);
        const tagsHtml = words.map(w => `<span class="history-tag">${w}</span>`).join('');
        
        return `
            <div class="history-item ${activeChatId === chat.id ? 'active' : ''}" onclick="selectChat('${chat.id}')" id="chat-item-${chat.id}">
                <div class="history-icon-box" style="background: ${style.bg}; color: ${style.color};">
                    <i data-lucide="${style.icon}" style="width: 20px; height: 20px;"></i>
                </div>
                <div style="flex: 1; min-width: 0;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                        <div style="color: #fff; font-weight: 500; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 70%;">${chat.title}</div>
                        <div style="color: #9ca3af; font-size: 0.65rem; white-space: nowrap;">${dateStr}</div>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; gap: 6px;">
                            ${tagsHtml}
                        </div>
                        <i data-lucide="chevron-right" style="width: 14px; height: 14px; color: #9ca3af;"></i>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    if(window.lucide) { lucide.createIcons(); }
}

function filterHistory() {
    const q = document.getElementById('history-search').value.toLowerCase();
    const filtered = chatsData.filter(c => c.title.toLowerCase().includes(q));
    renderHistoryList(filtered);
}

async function selectChat(chatId) {
    activeChatId = chatId;
    // Update active class
    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
    const activeEl = document.getElementById(`chat-item-${chatId}`);
    if(activeEl) activeEl.classList.add('active');
    
    const placeholder = document.getElementById('detail-placeholder');
    const content = document.getElementById('detail-content');
    
    placeholder.style.display = 'none';
    content.style.display = 'flex';
    content.innerHTML = '<div style="padding: 2rem; text-align: center; color: #9ca3af;">Loading chat details...</div>';
    
    try {
        const response = await apiFetch(`/chats/${chatId}`);
        const data = await response.json();
        
        if (data.success && data.data) {
            renderChatDetail(data.data);
        }
    } catch (err) {
        console.error("Failed to load chat detail", err);
        content.innerHTML = '<div style="padding: 2rem; text-align: center; color: #ef4444;">Failed to load details</div>';
    }
}

function renderChatDetail(detail) {
    const content = document.getElementById('detail-content');
    const msgs = detail.messages || [];
    
    const dateStr = new Date(detail.chat.updated_at).toLocaleString('en-US', { day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: '2-digit' });
    
    // Find the first user message for the header title, if any
    const firstUserMsg = msgs.find(m => m.role === 'USER')?.content || detail.chat.title;
    
    // Build chat bubbles
    let bubblesHtml = msgs.map(m => {
        if (m.role === 'USER') {
            return `
            <div style="align-self: flex-end; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 12px 16px; border-radius: 12px 12px 0 12px; color: #fff; font-size: 0.85rem; max-width: 85%;">
                ${m.content}
            </div>`;
        } else {
            let htmlContent = window.marked ? marked.parse(m.content) : m.content;
            
            // Build sources if available
            let sourcesHtml = '';
            if (m.sources && m.sources.length > 0) {
                const srcCards = m.sources.map(src => `
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 10px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="background: rgba(239, 68, 68, 0.2); color: #ef4444; width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                            <i data-lucide="file-text" style="width:16px; height:16px;"></i>
                        </div>
                        <div>
                            <div style="color: #fff; font-size: 0.75rem; font-weight: 500;">${src.original_filename || src.title || 'Document'}</div>
                            <div style="color: #9ca3af; font-size: 0.65rem;">Page ${src.page_number || 1} &bull; ${(src.score * 100).toFixed(1)}% Match</div>
                        </div>
                    </div>
                    <button class="nav-btn" style="background:none; border:none; color:#00D261; cursor:pointer;" onclick="window.open('/document_viewer.html?doc_id=${src.document_id}', '_blank')">
                        <i data-lucide="external-link" style="width:14px; height:14px;"></i>
                    </button>
                </div>
                `).join('');
                
                sourcesHtml = `
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                        <div style="color: #fff; font-size: 0.75rem; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                            <i data-lucide="file-text" style="width:12px; height:12px;"></i> Source Documents
                        </div>
                    </div>
                    ${srcCards}
                </div>`;
            }
            
            return `
            <div style="display: flex; gap: 12px; align-self: flex-start; max-width: 90%;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: #00D261; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <i data-lucide="bot" style="width:18px; height:18px; color:#000;"></i>
                </div>
                <div style="flex: 1;">
                    <div style="background: rgba(0, 210, 97, 0.05); border: 1px solid rgba(0, 210, 97, 0.1); padding: 16px; border-radius: 0 12px 12px 12px;">
                        <div class="markdown-body">${htmlContent}</div>
                        ${sourcesHtml}
                    </div>
                </div>
            </div>`;
        }
    }).join('');
    
    content.innerHTML = `
        <!-- Header -->
        <div style="padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: flex-start; background: rgba(0,0,0,0.2);">
            <div style="display: flex; gap: 12px;">
                <div style="background: rgba(16, 185, 129, 0.2); color: #10b981; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <i data-lucide="layers" style="width: 20px; height: 20px;"></i>
                </div>
                <div>
                    <h2 style="margin: 0 0 4px 0; font-size: 1rem; color: #fff;">${firstUserMsg}</h2>
                    <div style="color: #9ca3af; font-size: 0.7rem;">${dateStr}</div>
                </div>
            </div>
            <button class="nav-btn" style="background:none; border:none; color:#ef4444; cursor:pointer;" onclick="deleteChat('${detail.chat.id}')" title="Delete Chat">
                <i data-lucide="trash-2" style="width:16px; height:16px;"></i>
            </button>
        </div>
        
        <!-- Messages Area -->
        <div style="flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem;">
            ${bubblesHtml}
        </div>
        
        <!-- Footer Actions -->
        <div style="padding: 1rem 1.5rem; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2);">
            <div style="display: flex; gap: 10px;">
                <button style="background: #00D261; color: #000; border: none; padding: 8px 16px; border-radius: 8px; font-size: 0.75rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                    <i data-lucide="thumbs-up" style="width:14px; height:14px;"></i> Helpful
                </button>
                <button style="background: transparent; color: #9ca3af; border: 1px solid rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 8px; font-size: 0.75rem; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                    <i data-lucide="thumbs-down" style="width:14px; height:14px;"></i> Not Helpful
                </button>
            </div>
            <button style="background: transparent; color: #fff; border: 1px solid rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 8px; font-size: 0.75rem; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                <i data-lucide="bookmark" style="width:14px; height:14px;"></i> Save Answer
            </button>
        </div>
    `;
    
    if(window.lucide) { lucide.createIcons(); }
}

async function deleteChat(chatId) {
    if(!confirm('Are you sure you want to delete this chat history?')) return;
    
    try {
        const response = await apiFetch(`/chats/${chatId}`, { method: 'DELETE' });
        const data = await response.json();
        if(data.success) {
            // Refresh list
            activeChatId = null;
            document.getElementById('detail-placeholder').style.display = 'flex';
            document.getElementById('detail-content').style.display = 'none';
            fetchHistoryList();
        }
    } catch(err) {
        console.error(err);
        alert('Failed to delete chat.');
    }
}
