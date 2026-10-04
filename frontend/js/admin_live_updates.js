let updatesData = [];
let currentUser = null;

document.addEventListener('DOMContentLoaded', async () => {
    currentUser = await requireAuth();
    if(!currentUser) return;

    // Set default datetime to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('form-publish').value = now.toISOString().slice(0,16);

    await fetchUpdates();
    updatePreview();
});

function focusCreateForm() {
    resetForm();
    document.getElementById('form-title').focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updatePreview() {
    const title = document.getElementById('form-title').value || 'Announcement Title';
    const content = document.getElementById('form-content').value || 'Announcement content will appear here...';
    const cat = document.getElementById('form-category').value;
    const aud = document.getElementById('form-audience').value;
    
    document.getElementById('preview-title').textContent = title;
    document.getElementById('preview-content').textContent = content;
    document.getElementById('preview-category').textContent = cat;
    document.getElementById('preview-audience').textContent = aud;
}

function resetForm() {
    document.getElementById('edit-id').value = '';
    document.getElementById('form-title').value = '';
    document.getElementById('form-content').value = '';
    document.getElementById('form-category').value = 'Syllabus';
    document.getElementById('form-audience').value = 'All Students';
    document.getElementById('form-priority').value = 'NORMAL';
    document.getElementById('form-expiry').value = '';
    
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('form-publish').value = now.toISOString().slice(0,16);
    
    document.getElementById('btn-cancel').style.display = 'none';
    document.getElementById('btn-save').textContent = 'Save as Draft';
    updatePreview();
}

async function fetchUpdates() {
    try {
        const res = await apiFetch('/live_updates/admin');
        const data = await res.json();
        if(data.success) {
            updatesData = data.data;
            renderKPIs();
            filterTable();
        }
    } catch (e) {
        console.error(e);
    }
}

function renderKPIs() {
    const total = updatesData.length;
    const published = updatesData.filter(d => d.status === 'PUBLISHED').length;
    const drafts = updatesData.filter(d => d.status === 'DRAFT').length;
    
    document.getElementById('kpi-total').textContent = total;
    document.getElementById('kpi-published').textContent = published;
    document.getElementById('kpi-drafts').textContent = drafts;
    document.getElementById('kpi-scheduled').textContent = "0"; // Mock for now
    
    document.getElementById('pag-total').textContent = total;
}

function filterTable() {
    const query = document.getElementById('search-input').value.toLowerCase();
    const cat = document.getElementById('filter-category').value;
    const stat = document.getElementById('filter-status').value;
    
    let filtered = updatesData.filter(d => {
        const mq = d.title.toLowerCase().includes(query) || (d.content && d.content.toLowerCase().includes(query));
        const mc = cat === 'all' || d.category === cat;
        const ms = stat === 'all' || d.status === stat;
        return mq && mc && ms;
    });
    
    renderTable(filtered);
}

function renderTable(data) {
    const tbody = document.getElementById('updates-table-body');
    if(data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:20px; color:#9ca3af;">No announcements found</td></tr>`;
        document.getElementById('pag-end').textContent = 0;
        return;
    }
    
    document.getElementById('pag-end').textContent = data.length;
    
    tbody.innerHTML = data.map((d, i) => {
        let badgeColor = '';
        let badgeText = d.category || 'General';
        // Random badge colors for category
        const charCode = badgeText.charCodeAt(0);
        if(charCode % 3 === 0) badgeColor = 'background:rgba(59, 130, 246, 0.2); color:#60a5fa;'; // blue
        else if(charCode % 3 === 1) badgeColor = 'background:rgba(139, 92, 246, 0.2); color:#a78bfa;'; // purple
        else badgeColor = 'background:rgba(236, 72, 153, 0.2); color:#f472b6;'; // pink
        
        let statColor = '';
        if(d.status === 'PUBLISHED') statColor = 'color:#10b981;';
        else if(d.status === 'DRAFT') statColor = 'color:#9ca3af;';
        else statColor = 'color:#ef4444;';
        
        let statHtml = `<div style="display:flex; align-items:center; gap:6px; ${statColor} font-size:0.75rem;"><div style="width:6px; height:6px; border-radius:50%; background:currentColor;"></div> ${d.status === 'PUBLISHED' ? 'Published' : (d.status === 'DRAFT' ? 'Draft' : 'Unpublished')}</div>`;
        
        const pubDate = d.published_at ? new Date(d.published_at + 'Z').toLocaleString('en-US', {day:'numeric', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit'}) : '-';
        const expDate = d.expiry_date ? new Date(d.expiry_date + 'Z').toLocaleString('en-US', {day:'numeric', month:'short', year:'numeric'}) : '-';
        
        // Action buttons based on status
        let actionHtml = '';
        if(d.status !== 'PUBLISHED') {
            actionHtml += `<button class="action-btn-icon" title="Publish" onclick="publishUpdate('${d.id}')"><i data-lucide="send" style="width:14px; height:14px; color:#10b981;"></i></button>`;
        } else {
            actionHtml += `<button class="action-btn-icon" title="Unpublish" onclick="unpublishUpdate('${d.id}')"><i data-lucide="eye-off" style="width:14px; height:14px; color:#f59e0b;"></i></button>`;
        }
        
        return `
            <tr>
                <td><input type="checkbox" style="accent-color: #00D261;"></td>
                <td style="color: #9ca3af;">${i+1}</td>
                <td style="color: #fff; font-weight: 500;">${d.title}</td>
                <td><span style="${badgeColor} padding:2px 8px; border-radius:12px; font-size:0.7rem; font-weight:600;">${badgeText}</span></td>
                <td style="color: #9ca3af; font-size: 0.8rem;">${d.target_audience || 'All Students'}</td>
                <td>${statHtml}</td>
                <td style="color: #9ca3af; font-size: 0.8rem;">${pubDate}</td>
                <td style="color: #9ca3af; font-size: 0.8rem;">${expDate}</td>
                <td style="text-align: right;">
                    <div style="display:flex; justify-content:flex-end; gap:4px;">
                        ${actionHtml}
                        <button class="action-btn-icon" title="Edit" onclick="editForm('${d.id}')"><i data-lucide="edit-2" style="width:14px; height:14px; color:#9ca3af;"></i></button>
                        <button class="action-btn-icon delete" title="Delete" onclick="deleteUpdate('${d.id}')"><i data-lucide="trash-2" style="width:14px; height:14px; color:#ef4444;"></i></button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    if(window.lucide) lucide.createIcons();
}

async function saveAnnouncement(publishNow = false) {
    const id = document.getElementById('edit-id').value;
    const title = document.getElementById('form-title').value.trim();
    const content = document.getElementById('form-content').value.trim();
    const cat = document.getElementById('form-category').value;
    const aud = document.getElementById('form-audience').value;
    const prio = document.getElementById('form-priority').value;
    const expStr = document.getElementById('form-expiry').value;
    
    if(!title || !content) {
        alert("Title and Content are required.");
        return;
    }
    
    const payload = {
        title: title,
        content: content,
        category: cat,
        target_audience: aud,
        priority: prio,
        expiry_date: expStr ? new Date(expStr).toISOString() : null
    };
    
    try {
        let res;
        if(id) {
            res = await apiFetch('/live_updates/' + id, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
        } else {
            res = await apiFetch('/live_updates', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
        }
        
        const data = await res.json();
        if(data.success) {
            const savedId = data.data.id;
            if(publishNow && data.data.status !== 'PUBLISHED') {
                await publishUpdate(savedId, false);
            } else {
                resetForm();
                await fetchUpdates();
            }
        } else {
            alert(data.message || "Failed to save announcement");
        }
    } catch (e) {
        console.error(e);
        alert("An error occurred.");
    }
}

async function publishUpdate(id, doFetch = true) {
    if(!confirm("Are you sure you want to publish this announcement? Users may be notified.")) return;
    try {
        const res = await apiFetch('/live_updates/' + id + '/publish', { method: 'POST' });
        if(res.ok) {
            // Trigger push notification to all users
            localStorage.setItem('trigger_push_notification', JSON.stringify({
                title: "New Announcement",
                message: `Admin has published a new announcement.`,
                timestamp: Date.now()
            }));
            
            if(doFetch) await fetchUpdates();
            else {
                resetForm();
                await fetchUpdates();
            }
        } else {
            const data = await res.json();
            alert(data.message || "Failed to publish");
        }
    } catch (e) {
        console.error(e);
    }
}

async function unpublishUpdate(id) {
    if(!confirm("Are you sure you want to unpublish this announcement?")) return;
    try {
        const res = await apiFetch('/live_updates/' + id + '/unpublish', { method: 'POST' });
        if(res.ok) await fetchUpdates();
    } catch (e) {
        console.error(e);
    }
}

async function deleteUpdate(id) {
    if(!confirm("Are you sure you want to delete this announcement? This cannot be undone.")) return;
    try {
        const res = await apiFetch('/live_updates/' + id, { method: 'DELETE' });
        if(res.ok) await fetchUpdates();
    } catch (e) {
        console.error(e);
    }
}

function editForm(id) {
    const item = updatesData.find(d => d.id === id);
    if(!item) return;
    
    document.getElementById('edit-id').value = item.id;
    document.getElementById('form-title').value = item.title;
    document.getElementById('form-content').value = item.content;
    document.getElementById('form-category').value = item.category || 'Syllabus';
    document.getElementById('form-audience').value = item.target_audience || 'All Students';
    document.getElementById('form-priority').value = item.priority;
    
    if(item.expiry_date) {
        document.getElementById('form-expiry').value = new Date(item.expiry_date + 'Z').toISOString().split('T')[0];
    } else {
        document.getElementById('form-expiry').value = '';
    }
    
    document.getElementById('btn-cancel').style.display = 'block';
    document.getElementById('btn-save').textContent = 'Update Draft';
    
    updatePreview();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
