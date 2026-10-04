// Centralized API configuration and token management
const API_URL = 'http://127.0.0.1:8000/api/v1';

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

        return user;
    } catch (e) {
        clearToken();
        if (!isAuthPage) window.location.href = 'login.html';
        return null;
    }
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
