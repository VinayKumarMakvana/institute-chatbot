document.addEventListener('DOMContentLoaded', async () => {
    const user = await requireAuth();
    if (!user) return;

    // Display User info in Nav
    document.getElementById('nav-name').textContent = user.name;
    const initials = user.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
    document.getElementById('nav-avatar').textContent = initials;

    const container = document.getElementById('updates-container');
    if (!container) return;

    async function loadUpdates() {
        try {
            const res = await apiFetch('/live-updates');
            if (!res.ok) {
                container.innerHTML = '<div style="color:#ef4444;">Failed to load live updates.</div>';
                return;
            }
            
            const resData = await res.json();
            if (resData.success && resData.data) {
                const updates = resData.data;
                if(updates.length === 0) {
                    container.innerHTML = '<div style="color:#9ca3af;">No live updates available.</div>';
                    return;
                }
                
                container.innerHTML = updates.map(update => {
                    const dateStr = new Date(update.created_at).toLocaleString([], {
                        month: 'short', day: 'numeric', year: 'numeric', 
                        hour: '2-digit', minute: '2-digit'
                    });
                    
                    let color = '#3b82f6'; // INFO
                    let bg = 'rgba(59, 130, 246, 0.15)';
                    if(update.priority === 'URGENT') {
                        color = '#ef4444';
                        bg = 'rgba(239, 68, 68, 0.15)';
                    } else if(update.priority === 'WARNING') {
                        color = '#f59e0b';
                        bg = 'rgba(245, 158, 11, 0.15)';
                    }

                    return `
                        <div style="position: relative;">
                            <div style="position: absolute; left: -39px; top: 0; width: 16px; height: 16px; border-radius: 50%; background: ${color}; border: 4px solid #041209;"></div>
                            <span style="color: #9ca3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">${dateStr}</span>
                            <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin-top: 10px;">
                                <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
                                    <span style="background: ${bg}; color: ${color}; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600;">${update.priority || 'INFO'}</span>
                                    <h3 style="color: #fff; margin: 0; font-size: 1.1rem;">${escapeHTML(update.title)}</h3>
                                </div>
                                <p style="color: #d1d5db; font-size: 0.9rem; line-height: 1.5; margin: 0;">${escapeHTML(update.content)}</p>
                            </div>
                        </div>
                    `;
                }).join('');
                
                if (window.lucide) window.lucide.createIcons();
            }
        } catch(e) {
            console.error(e);
            container.innerHTML = '<div style="color:#ef4444;">An error occurred while loading updates.</div>';
        }
    }

    loadUpdates();

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
