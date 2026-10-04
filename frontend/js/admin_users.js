let usersData = [];
let currentUser = null;

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Authenticate user using api.js
    currentUser = await requireAuth();
    if(!currentUser) return;

    // 3. Fetch Real Data
    await fetchUsers();
});

async function fetchUsers() {
    try {
        const response = await apiFetch('/users');
        const data = await response.json();
        if(data.success) {
            usersData = data.data.map((u, i) => mapBackendToFrontend(u, i));
            updateKPIs();
            filterUsers();
        }
    } catch (e) {
        console.error("Failed to load users", e);
    }
}

function mapBackendToFrontend(n, index) {
    // Map backend data using real values (removing fake assignments)
    let mappedRole = n.role === 'ADMIN' ? 'Super Admin' : (n.role === 'FACULTY' ? 'Faculty' : 'Student');
    let mappedDept = '-'; // Not tracked in DB yet
    let mappedStatus = n.is_active ? 'Active' : 'Inactive';

    const dateObj = new Date(n.last_login_at ? n.last_login_at + 'Z' : n.created_at + 'Z'); 
    const dateStr = dateObj.toLocaleString('en-US', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });

    return {
        id: n.id,
        index: index + 1,
        name: n.name,
        email: n.email,
        role: mappedRole,
        department: mappedDept,
        status: mappedStatus,
        lastActive: dateStr
    };
}

function updateKPIs() {
    const total = usersData.length;
    const students = usersData.filter(u => u.role === 'Student').length;
    const faculty = usersData.filter(u => u.role === 'Faculty').length;
    const admins = usersData.filter(u => u.role === 'Super Admin').length;
    const inactive = usersData.filter(u => u.status === 'Inactive').length;

    // Formatting with commas for large numbers
    document.getElementById('kpi-total').textContent = total.toLocaleString();
    document.getElementById('kpi-students').textContent = students.toLocaleString();
    document.getElementById('kpi-faculty').textContent = faculty.toLocaleString();
    document.getElementById('kpi-admins').textContent = admins.toLocaleString();
    document.getElementById('kpi-inactive').textContent = inactive.toLocaleString();
    
    document.getElementById('pag-total').textContent = total.toLocaleString();
}

function renderUsers(users) {
    const tbody = document.getElementById('users-table-body');
    
    if (users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 2rem; color: #9ca3af;">No users found matching criteria.</td></tr>`;
        return;
    }

    tbody.innerHTML = users.map(u => {
        const initials = u.name.split(' ').map(n => n[0]).join('').substring(0,2).toUpperCase();
        
        let roleHtml = '';
        if (u.role === 'Student') {
            roleHtml = `<span class="role-badge" style="background:#2563eb; color:#fff; border:none; padding:4px 12px; border-radius:12px;">Student</span>`;
        } else if (u.role === 'Faculty') {
            roleHtml = `<span class="role-badge" style="background:#8b5cf6; color:#fff; border:none; padding:4px 12px; border-radius:12px;">Faculty</span>`;
        } else {
            roleHtml = `<span class="role-badge" style="background:#ef4444; color:#fff; border:none; padding:4px 12px; border-radius:12px;">Super Admin</span>`;
        }
            
        let statusHtml = '';
        if (u.status === 'Active') {
            statusHtml = `<span class="status-badge" style="background:rgba(16, 185, 129, 0.15); color:#10b981;"><span class="status-dot" style="background:#10b981; width:6px; height:6px; border-radius:50%; display:inline-block;"></span> Active</span>`;
        } else if (u.status === 'Inactive') {
            statusHtml = `<span class="status-badge" style="background:rgba(239, 68, 68, 0.15); color:#ef4444;"><span class="status-dot" style="background:#ef4444; width:6px; height:6px; border-radius:50%; display:inline-block;"></span> Inactive</span>`;
        } else {
            statusHtml = `<span class="status-badge" style="background:rgba(245, 158, 11, 0.15); color:#f59e0b;"><span class="status-dot" style="background:#f59e0b; width:6px; height:6px; border-radius:50%; display:inline-block;"></span> Pending</span>`;
        }

        // Generate avatar color based on role
        let avatarBg = '#2563eb';
        if(u.role === 'Faculty') avatarBg = '#d946ef';
        if(u.role === 'Super Admin') avatarBg = '#10b981';

        return `
            <tr>
                <td><input type="checkbox" style="accent-color: #00D261;"></td>
                <td style="color: #9ca3af;">${u.index}</td>
                <td>
                    <div class="user-cell">
                        <div class="table-avatar" style="background: ${avatarBg}; color: #fff;">${initials}</div>
                        <span class="user-cell-name">${u.name}</span>
                    </div>
                </td>
                <td style="color: #9ca3af;">${u.email}</td>
                <td>${roleHtml}</td>
                <td style="color: #9ca3af;">${u.department}</td>
                <td>${statusHtml}</td>
                <td style="color: #9ca3af;">${u.lastActive}</td>
                <td style="text-align: right;">
                    <div class="action-buttons" style="justify-content: flex-end; gap:4px;">
                        <button class="action-btn-icon" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 6px;"><i data-lucide="eye" style="width:14px; height:14px;"></i></button>
                        <button class="action-btn-icon" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 6px;"><i data-lucide="edit-2" style="width:14px; height:14px;"></i></button>
                        <button class="action-btn-icon" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 6px;"><i data-lucide="more-horizontal" style="width:14px; height:14px;"></i></button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    document.getElementById('pag-end').textContent = users.length;
    
    if(window.lucide) {
        lucide.createIcons();
    }
}

function filterUsers() {
    const query = document.getElementById('user-search').value.toLowerCase();
    const roleFilter = document.getElementById('role-filter').value;
    const statusFilter = document.getElementById('status-filter').value;
    
    const filtered = usersData.filter(u => {
        const matchQuery = u.name.toLowerCase().includes(query) || u.email.toLowerCase().includes(query);
        const matchRole = roleFilter === 'all' || 
                          (roleFilter === 'USER' && u.role === 'Student') || 
                          (roleFilter === 'FACULTY' && u.role === 'Faculty') || 
                          (roleFilter === 'ADMIN' && u.role === 'Super Admin');
        const matchStatus = statusFilter === 'all' || u.status === statusFilter;
        
        return matchQuery && matchRole && matchStatus;
    });
    
    renderUsers(filtered);
}
