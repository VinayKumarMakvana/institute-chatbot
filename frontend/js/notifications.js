let notificationsData = [];
let currentUser = null;

const categories = [
    { id: 'all', name: 'All Notifications', short: 'All', icon: 'grid' },
    { id: 'Announcements', name: 'Announcements', short: 'Announcements', icon: 'megaphone', subtitle: 'Important Updates' },
    { id: 'New Documents', name: 'New Documents', short: 'New Documents', icon: 'file-text', subtitle: 'PDFs & Study Material' },
    { id: 'Q&A Updates', name: 'Q&A Updates', short: 'Q&A Updates', icon: 'message-square', subtitle: 'Answers & Solutions' },
    { id: 'System', name: 'System Notifications', short: 'System', icon: 'settings', subtitle: 'Account & Technical' },
    { id: 'Others', name: 'Others', short: 'Others', icon: 'bell', subtitle: 'Miscellaneous' }
];

let activeFilter = 'all';

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Authenticate user using api.js
    currentUser = await requireAuth();
    if(!currentUser) return; // Unauthenticated, api.js redirects

    // 2. Set Profile info
    const nameSplit = currentUser.name.split(' ');
    document.querySelector('.user-avatar').textContent = nameSplit[0][0] + (nameSplit[1] ? nameSplit[1][0] : '');
    document.querySelector('.user-name').textContent = currentUser.name;
    document.querySelector('.user-role').textContent = currentUser.role || 'Student';

    // 3. Fetch Real Data
    await fetchNotifications();
    
    // 4. Setup Logout
    if(typeof setupLogout === 'function') setupLogout();
});

async function fetchNotifications() {
    try {
        const response = await apiFetch('/notifications');
        const data = await response.json();
        if(data.success) {
            notificationsData = data.data.map(mapBackendToFrontend);
            renderUI();
        }
    } catch (e) {
        console.error("Failed to load notifications", e);
        // Show empty state if server is down
        renderUI(); 
    }
}

function mapBackendToFrontend(n) {
    let cat = 'Others';
    let icon = 'bell';
    let color = 'gray';

    if (n.type === 'DOCUMENT') { cat = 'New Documents'; icon = 'file-text'; color = 'blue'; }
    else if (n.type === 'SYSTEM') { cat = 'System'; icon = 'settings'; color = 'red'; }
    else if (n.type === 'QA') { cat = 'Q&A Updates'; icon = 'message-square'; color = 'green'; }
    else if (n.type === 'ANNOUNCEMENT') { cat = 'Announcements'; icon = 'megaphone'; color = 'purple'; }
    
    // Format date string from n.created_at
    const dateObj = new Date(n.created_at + 'Z'); 
    const dateStr = dateObj.toLocaleString('en-US', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });

    return {
        id: n.id,
        category: cat,
        icon: icon,
        color: color,
        title: n.title,
        description: n.message,
        date: dateStr,
        unread: !n.is_read
    };
}

function setFilter(filterId) {
    activeFilter = filterId;
    renderUI();
}

async function openNotificationModal(id) {
    const notif = notificationsData.find(n => n.id === id);
    if(!notif) return;

    // Mark as read immediately when opened
    if (notif.unread) {
        notif.unread = false;
        renderUI(); // updates background lists and counters
        // Send request to backend
        try {
            await apiFetch(`/notifications/${id}/read`, { method: 'POST' });
        } catch(e) { console.error("Failed to mark as read in DB"); }
    }

    // Populate modal
    document.getElementById('modal-icon').innerHTML = `<i data-lucide="${notif.icon}"></i>`;
    document.getElementById('modal-icon').className = `modal-icon ${notif.color}`;
    document.getElementById('modal-title').textContent = notif.title;
    document.getElementById('modal-date').innerHTML = `<i data-lucide="clock" style="width:12px; height:12px; margin-right:4px;"></i> ${notif.date}`;
    document.getElementById('modal-desc').textContent = notif.description;

    const actionBtn = document.getElementById('modal-action-btn');
    if (notif.category === 'New Documents') {
        actionBtn.textContent = 'View Document';
    } else if (notif.category === 'Q&A Updates') {
        actionBtn.textContent = 'Go to Chat';
    } else {
        actionBtn.textContent = 'Dismiss';
    }

    // Show modal
    document.getElementById('notif-modal').classList.add('show');
    lucide.createIcons();
}

function closeModal(event) {
    if (event && event.target.id !== 'notif-modal') return;
    document.getElementById('notif-modal').classList.remove('show');
}

async function markAllAsRead() {
    let hasUnread = false;
    notificationsData.forEach(n => {
        if(n.unread) hasUnread = true;
        n.unread = false;
    });
    
    renderUI();

    if(hasUnread) {
        try {
            await apiFetch('/notifications/read-all', { method: 'POST' });
        } catch(e) { console.error("Failed to mark all as read"); }
    }
}

function clearAllNotifications() {
    if(confirm("Are you sure you want to hide all notifications from this view?")) {
        notificationsData = [];
        renderUI();
    }
}

function getFilteredData() {
    if(activeFilter === 'all') return notificationsData;
    return notificationsData.filter(n => n.category === activeFilter || (activeFilter === 'System Notifications' && n.category === 'System'));
}

function getUnreadCount(catId) {
    if(catId === 'all') return notificationsData.filter(n => n.unread).length;
    let targetCat = catId === 'System Notifications' ? 'System' : catId;
    return notificationsData.filter(n => n.category === targetCat && n.unread).length;
}

function renderUI() {
    renderCategories();
    renderFilters();
    renderNotifications();
    updateStats();
    if(window.lucide) lucide.createIcons();
}

function renderCategories() {
    const container = document.getElementById('category-row');
    container.innerHTML = categories.map(cat => {
        const unreadCount = getUnreadCount(cat.id);
        const activeClass = activeFilter === cat.id ? 'active' : '';
        return `
            <div class="category-card ${activeClass}" onclick="setFilter('${cat.id}')">
                <div class="cat-icon"><i data-lucide="${cat.icon}"></i></div>
                <div class="cat-info">
                    <div class="cat-title-row">
                        <h4 class="cat-title">${cat.short}</h4>
                        ${unreadCount > 0 ? `<span class="cat-count">${unreadCount}</span>` : ''}
                    </div>
                    ${cat.subtitle ? `<p class="cat-sub">${cat.subtitle}</p>` : '<p class="cat-sub">All Notifications</p>'}
                </div>
            </div>
        `;
    }).join('');
}

function renderFilters() {
    const container = document.getElementById('filter-list');
    container.innerHTML = categories.map(cat => {
        const unreadCount = getUnreadCount(cat.id);
        const activeClass = activeFilter === cat.id ? 'active' : '';
        return `
            <div class="filter-item ${activeClass}" onclick="setFilter('${cat.id}')">
                <div class="filter-left">
                    <i data-lucide="${cat.icon}"></i>
                    <span>${cat.name}</span>
                </div>
                ${unreadCount > 0 ? `<span class="filter-count">${unreadCount}</span>` : ''}
            </div>
        `;
    }).join('');
}

function renderNotifications() {
    const container = document.getElementById('notif-container');
    const titleEl = document.getElementById('list-title');
    
    const filtered = getFilteredData();
    const catName = categories.find(c => c.id === activeFilter)?.name || 'All Notifications';
    titleEl.textContent = `${catName} (${filtered.length})`;

    if(filtered.length === 0) {
        container.innerHTML = `<div style="text-align:center; padding: 2rem; color: #9ca3af; font-size: 0.8rem;">No notifications found for this category.</div>`;
        return;
    }

    container.innerHTML = filtered.map(notif => `
        <div class="notif-item" onclick="openNotificationModal('${notif.id}')">
            <div class="n-icon-box ${notif.color}">
                <i data-lucide="${notif.icon}"></i>
            </div>
            <div class="n-content">
                <h4 class="n-title">${notif.title}</h4>
                <p class="n-desc">${notif.description}</p>
            </div>
            <div class="n-meta">
                <span class="n-time">${notif.date}</span>
                <span class="n-status ${notif.unread ? 'unread' : 'read'}">
                    <span class="status-dot"></span>
                    ${notif.unread ? 'Unread' : 'Read'}
                </span>
            </div>
            <button class="n-menu-btn" onclick="event.stopPropagation()"><i data-lucide="more-vertical"></i></button>
        </div>
    `).join('');
}

function updateStats() {
    const total = notificationsData.length;
    const unread = notificationsData.filter(n => n.unread).length;
    const read = total - unread;

    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-unread').textContent = unread;
    document.getElementById('stat-read').textContent = read;
    
    document.getElementById('nav-badge-count').textContent = unread;
    document.getElementById('sidebar-badge').textContent = unread;
}
