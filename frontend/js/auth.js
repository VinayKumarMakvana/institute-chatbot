// Handles Login and Registration forms

document.addEventListener('DOMContentLoaded', async () => {
    // If we are on an auth page, redirect if already logged in
    const currentPage = window.location.pathname.split('/').pop();
    if (currentPage === 'login.html' || currentPage === 'register.html') {
        await requireAuth();
    }

    // Single Login Handler
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const emailInput = document.getElementById('login-email');
            const passwordInput = document.getElementById('login-password');
            const errorEl = document.getElementById('auth-error');
            const submitBtn = document.getElementById('login-submit-btn');
            
            errorEl.textContent = '';
            submitBtn.disabled = true;
            const originalBtnHtml = submitBtn.innerHTML;
            submitBtn.innerHTML = 'Logging in...';

            try {
                const response = await fetch(`${API_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: emailInput.value.trim(),
                        password: passwordInput.value
                    })
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    setToken(data.data.token);
                    // Redirect based on role
                    if (data.data.user.role === 'ADMIN') {
                        window.location.href = 'admin_users.html';
                    } else {
                        window.location.href = 'index.html';
                    }
                } else {
                    errorEl.textContent = data.detail || data.message || 'Invalid credentials.';
                }
            } catch (err) {
                console.error("Login request failed:", err);
                errorEl.textContent = 'Server connection failed. Is the backend running?';
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnHtml;
                lucide.createIcons(); // re-init icons in button
            }
        });
    }
    // Registration Handler
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const nameInput = document.getElementById('reg-name');
            const emailInput = document.getElementById('reg-email');
            const rollInput = document.getElementById('reg-roll');
            const deptInput = document.getElementById('reg-dept');
            const courseInput = document.getElementById('reg-course');
            const semInput = document.getElementById('reg-sem');
            const phoneInput = document.getElementById('reg-phone');
            const passwordInput = document.getElementById('reg-pass');
            const confirmInput = document.getElementById('reg-pass-conf');
            const errorEl = document.getElementById('auth-error');
            const submitBtn = document.querySelector('#register-form button[type="submit"]');
            
            errorEl.style.display = 'none';
            
            if (passwordInput.value !== confirmInput.value) {
                errorEl.textContent = 'Passwords do not match.';
                errorEl.style.display = 'block';
                return;
            }
            
            submitBtn.disabled = true;
            const originalBtnHtml = submitBtn.innerHTML;
            submitBtn.innerHTML = 'Creating Account...';

            try {
                const response = await fetch(`${API_URL}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: nameInput.value.trim(),
                        email: emailInput.value.trim(),
                        roll_number: rollInput.value.trim(),
                        department: deptInput.value,
                        course: courseInput.value,
                        semester: semInput.value,
                        mobile_number: phoneInput.value.trim(),
                        password: passwordInput.value
                    })
                });
                
                const data = await response.json();
                
                if (response.ok && (data.success || !data.detail)) { // Handle possible fastAPI standard responses
                    // On success, try to login or redirect to login
                    window.location.href = 'login.html?registered=true';
                } else {
                    errorEl.textContent = data.detail || data.message || 'Registration failed.';
                    errorEl.style.display = 'block';
                }
            } catch (err) {
                console.error("Registration request failed:", err);
                errorEl.textContent = 'Server connection failed. Is the backend running?';
                errorEl.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnHtml;
                lucide.createIcons();
            }
        });
    }
});
