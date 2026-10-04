let savedData = [];

const colors = [
    { bg: 'rgba(0, 210, 97, 0.1)', color: '#00D261', icon: 'file-text' },
    { bg: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', icon: 'list' },
    { bg: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6', icon: 'book' },
    { bg: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', icon: 'graduation-cap' },
    { bg: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', icon: 'calendar' }
];

document.addEventListener('DOMContentLoaded', () => {
    fetchSavedAnswers();
});

async function fetchSavedAnswers() {
    try {
        const response = await apiFetch('/chats/saved-answers'); // we'll route it here to avoid naming conflict
        const data = await response.json();
        
        if (data.success && data.data) {
            savedData = data.data;
            renderSavedAnswers(savedData);
        }
    } catch (err) {
        console.error("Failed to load saved answers", err);
        document.getElementById('saved-list-container').innerHTML = '<div style="text-align:center; padding:3rem; color:#ef4444;">Failed to load saved answers</div>';
    }
}

function renderSavedAnswers(items) {
    const container = document.getElementById('saved-list-container');
    if(!items || items.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; color: #9ca3af; padding: 4rem; background: rgba(2, 12, 6, 0.5); border: 1px dashed rgba(255,255,255,0.1); border-radius: 12px;">
                <i data-lucide="bookmark" style="width: 48px; height: 48px; margin-bottom: 1rem; opacity: 0.5;"></i>
                <h3 style="color: #fff; margin-bottom: 8px;">No saved answers yet</h3>
                <p style="font-size: 0.9rem;">Click the "Save Answer" button on any chat to save it here for quick reference.</p>
            </div>
        `;
        if(window.lucide) { lucide.createIcons(); }
        return;
    }
    
    container.innerHTML = items.map((item, idx) => {
        const style = colors[idx % colors.length];
        const dateStr = new Date(item.created_at).toLocaleString('en-US', { day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: '2-digit' });
        
        // Generate pseudo-tags
        const words = item.question.split(' ').filter(w => w.length > 3).slice(0, 2);
        const tagsHtml = words.map(w => `<span class="saved-tag">${w}</span>`).join('');
        
        let answerSnippet = item.answer.replace(/<[^>]*>?/gm, '').substring(0, 150);
        if(item.answer.length > 150) answerSnippet += '...';
        
        let sourceHtml = '';
        if(item.sources && item.sources.length > 0) {
            const src = item.sources[0];
            sourceHtml = `
                <div class="saved-source">
                    <div class="source-doc">
                        <div class="source-doc-info">
                            <div style="background: rgba(239, 68, 68, 0.2); color: #ef4444; width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                <i data-lucide="file-text" style="width:16px; height:16px;"></i>
                            </div>
                            <div style="min-width: 0;">
                                <div style="color: #fff; font-size: 0.75rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${src.original_filename || src.title || 'Document'}</div>
                                <div style="color: #9ca3af; font-size: 0.65rem;">Page ${src.page_number || 1}</div>
                            </div>
                        </div>
                        <i data-lucide="external-link" style="width:14px; height:14px; color:#9ca3af; cursor:pointer;" onclick="window.open('/document_viewer.html?doc_id=${src.document_id}', '_blank')"></i>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn-action" style="flex:1; justify-content:center;" onclick="window.location.href='chat_history.html'"><i data-lucide="eye" style="width:14px; height:14px;"></i> Open</button>
                        <button class="btn-action" style="flex:1; justify-content:center;"><i data-lucide="share-2" style="width:14px; height:14px;"></i> Share</button>
                        <button class="btn-action delete" style="flex:1; justify-content:center;" onclick="deleteSaved('${item.id}')"><i data-lucide="trash-2" style="width:14px; height:14px;"></i> Delete</button>
                    </div>
                </div>
            `;
        } else {
            sourceHtml = `
                <div class="saved-source" style="justify-content: flex-end;">
                    <div style="display: flex; gap: 8px;">
                        <button class="btn-action" style="flex:1; justify-content:center;" onclick="window.location.href='chat_history.html'"><i data-lucide="eye" style="width:14px; height:14px;"></i> Open</button>
                        <button class="btn-action delete" style="flex:1; justify-content:center;" onclick="deleteSaved('${item.id}')"><i data-lucide="trash-2" style="width:14px; height:14px;"></i> Delete</button>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="saved-item">
                <div class="saved-icon" style="background: ${style.bg}; color: ${style.color};">
                    <i data-lucide="${style.icon}" style="width: 24px; height: 24px;"></i>
                </div>
                <div class="saved-content">
                    <div style="color: #fff; font-weight: 600; font-size: 1rem; margin-bottom: 6px;">${item.question}</div>
                    <div style="color: #9ca3af; font-size: 0.85rem; line-height: 1.5; margin-bottom: 15px;">
                        ${answerSnippet}
                    </div>
                    <div class="saved-meta">
                        ${tagsHtml}
                        <div class="saved-date" style="margin-left: 10px;">
                            <i data-lucide="calendar" style="width: 12px; height: 12px;"></i> ${dateStr}
                        </div>
                    </div>
                </div>
                ${sourceHtml}
            </div>
        `;
    }).join('');
    
    if(window.lucide) { lucide.createIcons(); }
}

function filterSaved() {
    const q = document.getElementById('saved-search').value.toLowerCase();
    const filtered = savedData.filter(c => c.question.toLowerCase().includes(q) || c.answer.toLowerCase().includes(q));
    renderSavedAnswers(filtered);
}

async function deleteSaved(id) {
    if(!confirm('Are you sure you want to delete this saved answer?')) return;
    
    try {
        const response = await apiFetch(`/chats/saved-answers/${id}`, { method: 'DELETE' });
        const data = await response.json();
        if(data.success) {
            fetchSavedAnswers();
        }
    } catch(err) {
        console.error(err);
        alert('Failed to delete saved answer.');
    }
}
