"""
Apply responsive upgrades to all HTML pages:
1. Add responsive.css link
2. Add mobile hamburger button to navbars
3. Add bottom navigation bar
4. Add auth mobile header to login/register
5. Add data-label attrs to table cells
"""

import re, os, glob

USER_BOTTOM_NAV = """
    <!-- Bottom Navigation (Mobile Only) -->
    <nav class="bottom-nav" id="bottom-nav">
        <a href="index.html" class="bottom-nav-item" id="bnav-chat">
            <i data-lucide="message-circle"></i>
            <span>Chatbot</span>
        </a>
        <a href="chat_history.html" class="bottom-nav-item" id="bnav-history">
            <i data-lucide="clock"></i>
            <span>History</span>
        </a>
        <a href="documents.html" class="bottom-nav-item" id="bnav-docs">
            <i data-lucide="book-open"></i>
            <span>Docs</span>
        </a>
        <a href="live_updates.html" class="bottom-nav-item" id="bnav-updates">
            <i data-lucide="megaphone"></i>
            <span>Updates</span>
        </a>
        <a href="notifications.html" class="bottom-nav-item" id="bnav-notif">
            <i data-lucide="bell"></i>
            <span>Alerts</span>
            <span class="bottom-nav-badge" id="bnav-badge" style="display:none;"></span>
        </a>
    </nav>
"""

ADMIN_BOTTOM_NAV = """
    <!-- Bottom Navigation (Mobile Only) -->
    <nav class="bottom-nav" id="bottom-nav">
        <a href="admin.html" class="bottom-nav-item" id="bnav-dashboard">
            <i data-lucide="layout-dashboard"></i>
            <span>Dashboard</span>
        </a>
        <a href="admin_chatbot.html" class="bottom-nav-item" id="bnav-chatbot">
            <i data-lucide="bot"></i>
            <span>Chatbot</span>
        </a>
        <a href="admin_documents.html" class="bottom-nav-item" id="bnav-docs">
            <i data-lucide="file-text"></i>
            <span>Docs</span>
        </a>
        <a href="admin_live_updates.html" class="bottom-nav-item" id="bnav-updates">
            <i data-lucide="megaphone"></i>
            <span>Updates</span>
        </a>
        <a href="admin_users.html" class="bottom-nav-item" id="bnav-users">
            <i data-lucide="users"></i>
            <span>Users</span>
        </a>
    </nav>
"""

AUTH_MOBILE_HEADER = """
    <!-- Mobile Logo Header (only shown on mobile) -->
    <div class="auth-mobile-header">
        <i data-lucide="graduation-cap"></i>
        <span>Institute <span class="text-green">AI Agent</span></span>
    </div>
"""

HAMBURGER_BTN = '<button class="mobile-menu-btn" onclick="toggleSidebar()" aria-label="Toggle menu"><i data-lucide="menu"></i></button>'

BOTTOM_NAV_ACTIVE_SCRIPT = """
    <script>
    // Activate bottom nav item based on current page
    (function() {
        var page = window.location.pathname.split('/').pop() || 'index.html';
        var map = {
            'index.html': 'bnav-chat',
            'chat_history.html': 'bnav-history',
            'documents.html': 'bnav-docs',
            'live_updates.html': 'bnav-updates',
            'notifications.html': 'bnav-notif',
            'saved_answers.html': 'bnav-docs',
            'profile.html': 'bnav-notif',
            'admin.html': 'bnav-dashboard',
            'admin_chatbot.html': 'bnav-chatbot',
            'admin_documents.html': 'bnav-docs',
            'admin_live_updates.html': 'bnav-updates',
            'admin_users.html': 'bnav-users',
        };
        var active = map[page];
        if (active) {
            var el = document.getElementById(active);
            if (el) el.classList.add('active');
        }
    })();
    </script>
"""

def add_responsive_css(content):
    """Add responsive.css after last existing css link"""
    if 'responsive.css' in content:
        return content
    # Find last stylesheet link
    matches = list(re.finditer(r'<link[^>]+stylesheet[^>]+>', content))
    if not matches:
        return content
    last = matches[-1]
    insert_pos = last.end()
    version = ''
    vm = re.search(r'\?v=(\d+)', content)
    if vm:
        version = f'?v={vm.group(1)}'
    new_link = f'\n    <link rel="stylesheet" href="./css/responsive.css{version}">'
    return content[:insert_pos] + new_link + content[insert_pos:]

def add_hamburger_to_navbar(content, is_admin=False):
    """Add hamburger button to the navbar-brand div"""
    if 'mobile-menu-btn' in content:
        return content
    # Add hamburger after navbar-brand closing div
    pattern = r'(</div>\s*)(<!--.*?-->\s*)?\s*(<div class="navbar-search")'
    replacement = r'\1\2    ' + HAMBURGER_BTN + r'\n        \3'
    new_content = re.sub(pattern, replacement, content, count=1)
    if new_content == content:
        # Try another pattern - after navbar-brand div
        pattern2 = r'(<div class="navbar-brand"[^>]*>.*?</div>)(\s*\n\s*)(<div class="navbar-search")'
        replacement2 = r'\1\2        ' + HAMBURGER_BTN + r'\n        \3'
        new_content = re.sub(pattern2, replacement2, content, count=1, flags=re.DOTALL)
    return new_content

def add_hamburger_for_nodashboard(content):
    """For chat app (index.html) pages without standard navbar"""
    if 'mobile-menu-btn' in content:
        return content
    # Add to chat-header
    pattern = r'(<div class="chat-header-left">)'
    replacement = HAMBURGER_BTN + r'\n            \1'
    return re.sub(pattern, replacement, content, count=1)

def add_bottom_nav(content, is_admin=False, is_chat=False):
    """Add bottom nav before closing body tag"""
    if 'bottom-nav' in content:
        return content
    nav = ADMIN_BOTTOM_NAV if is_admin else USER_BOTTOM_NAV
    # Insert before </body>
    content = content.replace('</body>', nav + BOTTOM_NAV_ACTIVE_SCRIPT + '\n</body>')
    return content

def add_auth_mobile_header(content):
    """Add mobile header to auth pages"""
    if 'auth-mobile-header' in content:
        return content
    # Add after body tag or before split-layout
    pattern = r'(<body[^>]*>)'
    replacement = r'\1\n' + AUTH_MOBILE_HEADER
    return re.sub(pattern, replacement, content, count=1)

def process_file(filepath):
    filename = os.path.basename(filepath)
    is_admin = filename.startswith('admin_') or filename == 'admin.html'
    is_auth = filename in ('login.html', 'register.html')
    is_chat = filename == 'index.html'

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    orig = content

    # 1. Add responsive.css
    content = add_responsive_css(content)

    # 2. Hamburger button
    if 'navbar-search' in content:
        content = add_hamburger_to_navbar(content, is_admin)
    elif 'chat-header-left' in content:
        content = add_hamburger_for_nodashboard(content)

    # 3. Bottom nav (skip auth pages)
    if not is_auth:
        content = add_bottom_nav(content, is_admin, is_chat)

    # 4. Auth mobile header
    if is_auth:
        content = add_auth_mobile_header(content)

    if content != orig:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filename}")
    else:
        print(f"No change: {filename}")

# Process all HTML files
html_files = glob.glob('frontend/*.html')
for f in html_files:
    process_file(f)

print("\nDone!")
