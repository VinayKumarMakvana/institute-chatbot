document.addEventListener('DOMContentLoaded', async () => {
    const user = await requireAuth();
    if (!user) return;

    // Display User info in Nav
    document.getElementById('nav-name').textContent = user.name;
    const initials = user.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
    document.getElementById('nav-avatar').textContent = initials;
    document.getElementById('nav-role').textContent = user.role;

    const container = document.getElementById('history-container');
    if (!container) return;

    async function loadHistory() {
        try {
            const res = await apiFetch('/chats');
            if (!res.ok) {
                container.innerHTML = '<div style="color:#ef4444; width:100%; grid-column: 1 / -1;">Failed to load chat history.</div>';
                return;
            }
            
            const resData = await res.json();
            if (resData.success && resData.data) {
                const chats = resData.data;
                if(chats.length === 0) {
                    container.innerHTML = '<div style="color:#9ca3af; width:100%; grid-column: 1 / -1;">No chat history found. Start a new chat!</div>';
                    return;
                }
                
                container.innerHTML = chats.map(chat => {
                    const dateStr = new Date(chat.created_at).toLocaleString();
                    return `
                        <div class="category-card" style="padding: 20px; flex-direction: column; align-items: flex-start; gap: 10px; cursor: pointer; position:relative;" onclick="window.location.href='index.html?chat_id=${chat.id}'">
                            <div style="display: flex; justify-content: space-between; width: 100%;">
                                <h3 style="color: #fff; font-size: 1rem; margin:0; width: 75%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${escapeHTML(chat.title)}</h3>
                                <span style="color: #00D261; background: rgba(0, 210, 97, 0.1); padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; white-space:nowrap;">${chat.message_count} msgs</span>
                            </div>
                            <span style="color: #6b7280; font-size: 0.7rem;"><i data-lucide="clock" style="width:12px; height:12px; vertical-align:middle;"></i> ${dateStr}</span>
                            <button onclick="event.stopPropagation(); deleteChat('${chat.id}')" style="position:absolute; bottom:15px; right:20px; background:none; border:none; color:#ef4444; cursor:pointer;" title="Delete Chat"><i data-lucide="trash-2" style="width:16px; height:16px;"></i></button>
                        </div>
                    `;
                }).join('');
                
                if (window.lucide) window.lucide.createIcons();
            }
        } catch(e) {
            console.error(e);
            container.innerHTML = '<div style="color:#ef4444; width:100%; grid-column: 1 / -1;">An error occurred.</div>';
        }
    }
    
    window.deleteChat = async function(id) {
        if(!confirm("Are you sure you want to delete this chat history?")) return;
        try {
            const res = await apiFetch('/chats/' + id, { method: 'DELETE' });
            if (res.ok) {
                loadHistory();
            } else {
                alert("Failed to delete chat.");
            }
        } catch (e) {
            console.error(e);
            alert("Error deleting chat.");
        }
    }

    loadHistory();

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
