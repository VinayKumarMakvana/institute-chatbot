// Centralized API configuration and token management
const API_URL = 'http://127.0.0.1:8000/api/v1';

// Global Page Transition Loader
(function() {
    const isAuth = window.location.pathname.endsWith('login.html') || window.location.pathname.endsWith('register.html');
    if (!isAuth) {
        document.write(`
        <style>
            #global-page-loader {
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: #070B0E; z-index: 999999; display: flex; align-items: center; justify-content: center;
                transition: opacity 0.3s ease;
            }
            .g-spinner {
                width: 40px; height: 40px; border: 3px solid rgba(46, 204, 113, 0.2);
                border-top-color: #2ECC71; border-radius: 50%; animation: g-spin 0.8s linear infinite;
            }
            @keyframes g-spin { to { transform: rotate(360deg); } }
            .dashboard-body, .main-content { opacity: 0; transition: opacity 0.3s ease; }
            body.page-ready .dashboard-body, body.page-ready .main-content { opacity: 1; }
        </style>
        <div id="global-page-loader"><div class="g-spinner"></div></div>
        `);
    }
})();

// Token Management
function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function clearToken() {
    localStorage.removeItem('token');
}

// Fetch Wrapper with automatic token injection
async function apiFetch(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        // Handle unauthorized globally
        if (response.status === 401 || response.status === 403) {
            clearToken();
            if (!window.location.pathname.endsWith('login.html') && !window.location.pathname.endsWith('register.html')) {
                window.location.href = 'login.html';
            }
        }
        
        return response;
    } catch (error) {
        console.error('API Fetch Error:', error);
        throw error;
    }
}

// Route Protection Logic
async function requireAuth(requiredRole = null) {
    const token = getToken();
    const isAuthPage = window.location.pathname.endsWith('login.html') || window.location.pathname.endsWith('register.html');
    
    if (!token) {
        if (!isAuthPage) {
            window.location.href = 'login.html';
        }
        return null;
    }

    try {
        const res = await apiFetch('/auth/me');
        if (!res.ok) {
            clearToken();
            if (!isAuthPage) window.location.href = 'login.html';
            return null;
        }

        const data = await res.json();
        const user = data.data; // assuming { success: true, data: { role: 'ADMIN', ... } }

        const isAdminPage = window.location.pathname.includes('admin');
        const isUserPage = !isAdminPage && !isAuthPage;

        // Strict App Separation
        if (user.role === 'ADMIN') {
            // Admins cannot access user pages or auth pages
            if (isUserPage || isAuthPage) {
                window.location.replace('admin.html');
                return null; // Stop execution
            }
        } else {
            // Users cannot access admin pages or auth pages
            if (isAdminPage || isAuthPage) {
                window.location.replace('index.html');
                return null; // Stop execution
            }
        }

        // Additional explicit role check if required by the caller
        if (requiredRole && user.role !== requiredRole) {
            window.location.replace(user.role === 'ADMIN' ? 'admin.html' : 'index.html');
            return null;
        }

        // Globally populate Navbar if present
        if(document.getElementById('nav-name')) {
            document.getElementById('nav-name').textContent = user.name;
            const initials = user.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
            if(document.getElementById('nav-avatar')) document.getElementById('nav-avatar').textContent = initials;
            if(document.getElementById('nav-role')) document.getElementById('nav-role').textContent = user.role === 'ADMIN' ? 'Super Admin' : (user.role === 'FACULTY' ? 'Faculty' : 'Student');
        }

        // Hide global loader after a short delay to allow subsequent page fetches to complete
        setTimeout(() => {
            const loader = document.getElementById('global-page-loader');
            if (loader) {
                loader.style.opacity = '0';
                setTimeout(() => loader.remove(), 300);
            }
            document.body.classList.add('page-ready');
            
            // Initialize push notifications
            initNotifications(user);
        }, 200);

        return user;
    } catch (e) {
        clearToken();
        if (!isAuthPage) window.location.href = 'login.html';
        return null;
    }
}

// Web Push Notifications Setup
function initNotifications(user) {
    if (user.role === 'ADMIN') return; // Only users receive the notifications
    if (!("Notification" in window)) return;

    if (Notification.permission === "default") {
        // Request permission on load
        Notification.requestPermission();
    }

    // Listen for storage events (simulating real-time WebSocket for demo purposes)
    window.addEventListener('storage', (e) => {
        if (e.key === 'trigger_push_notification' && e.newValue) {
            if (Notification.permission === "granted") {
                const data = JSON.parse(e.newValue);
                new Notification(data.title || "Institution AI Update", {
                    body: data.message,
                });
            }
        }
    });
}

// Global Logout Setup
function setupLogout() {
    document.querySelectorAll('.logout-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            clearToken();
            window.location.href = 'login.html';
        });
    });
}
