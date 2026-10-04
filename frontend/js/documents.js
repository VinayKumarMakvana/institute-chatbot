document.addEventListener('DOMContentLoaded', async () => {
    const user = await requireAuth();
    if (!user) return;

    // Display User info in Nav
    document.getElementById('nav-name').textContent = user.name;
    const initials = user.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
    document.getElementById('nav-avatar').textContent = initials;

    const container = document.getElementById('documents-container');
    if (!container) return;

    async function loadDocuments() {
        try {
            const res = await apiFetch('/documents/library');
            if (!res.ok) {
                container.innerHTML = '<div style="color:#ef4444; width:100%; grid-column: 1 / -1; text-align: center;">Failed to load document library.</div>';
                return;
            }
            
            const resData = await res.json();
            if (resData.success && resData.data) {
                const docs = resData.data;
                if(docs.length === 0) {
                    container.innerHTML = '<div style="color:#9ca3af; width:100%; grid-column: 1 / -1; text-align: center;">No documents available in the library yet.</div>';
                    return;
                }
                
                container.innerHTML = docs.map(doc => {
                    const sizeMB = (doc.size_bytes / (1024 * 1024)).toFixed(2);
                    // Generate random page count mock (since not in DB standard schema)
                    const pages = Math.floor(Math.random() * 50) + 5; 
                    
                    return `
                        <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; text-align: center; transition: transform 0.2s; cursor: pointer;">
                            <div style="width: 60px; height: 60px; background: rgba(239, 68, 68, 0.1); color: #ef4444; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto;">
                                <i data-lucide="file-type-2" style="width: 30px; height: 30px;"></i>
                            </div>
                            <h4 style="color: #fff; margin: 0 0 5px 0; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHTML(doc.title)}">${escapeHTML(doc.title)}</h4>
                            <p style="color: #9ca3af; font-size: 0.75rem; margin: 0 0 15px 0;">${sizeMB} MB • ${doc.category || 'General'} • Sem ${doc.semester || 'All'}</p>
                            <button class="btn-outline-small" style="width: 100%;" onclick="window.location.href='document_viewer.html?id=${doc.id}'">Open PDF</button>
                        </div>
                    `;
                }).join('');
                
                if (window.lucide) window.lucide.createIcons();
            }
        } catch(e) {
            console.error(e);
            container.innerHTML = '<div style="color:#ef4444; width:100%; grid-column: 1 / -1; text-align: center;">An error occurred while loading documents.</div>';
        }
    }

    loadDocuments();

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
