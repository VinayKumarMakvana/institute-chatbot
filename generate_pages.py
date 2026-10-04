import os

FRONTEND_DIR = r"c:\Users\VINAY\OneDrive\Desktop\finel-project\frontend"

def get_sidebar(is_admin, active_page):
    if is_admin:
        return f"""
        <!-- Left Sidebar (Admin) -->
        <aside class="sidebar">
            <ul class="nav-menu">
                <li><a href="admin.html" class="nav-item {'active' if active_page == 'admin' else ''}"><i data-lucide="layout-dashboard"></i> Admin Dashboard</a></li>
                <li><a href="admin_chatbot.html" class="nav-item {'active' if active_page == 'admin_chatbot' else ''}"><i data-lucide="bot"></i> Chatbot Management</a></li>
                <li><a href="admin_documents.html" class="nav-item {'active' if active_page == 'admin_documents' else ''}"><i data-lucide="folder"></i> Document Management</a></li>
                <li><a href="admin_live_updates.html" class="nav-item {'active' if active_page == 'admin_live_updates' else ''}"><i data-lucide="radio"></i> Live Updates</a></li>
                <li><a href="admin_users.html" class="nav-item {'active' if active_page == 'admin_users' else ''}"><i data-lucide="users"></i> User Management</a></li>
            </ul>
            <div class="nav-divider"></div>
            <ul class="nav-menu">
                <li><a href="login.html" class="nav-item logout-btn" style="color: #ef4444;"><i data-lucide="log-out"></i> Logout</a></li>
            </ul>
        </aside>
"""
    else:
        return f"""
        <!-- Left Sidebar (User) -->
        <aside class="sidebar">
            <ul class="nav-menu">
                <li><a href="index.html" class="nav-item {'active' if active_page == 'index' else ''}"><i data-lucide="bot"></i> Chat with AI</a></li>
                <li><a href="chat_history.html" class="nav-item {'active' if active_page == 'chat_history' else ''}"><i data-lucide="message-square"></i> My Queries</a></li>
                <li><a href="saved_answers.html" class="nav-item {'active' if active_page == 'saved_answers' else ''}"><i data-lucide="bookmark"></i> Saved Answers</a></li>
                <li><a href="documents.html" class="nav-item {'active' if active_page == 'documents' else ''}"><i data-lucide="file-text"></i> Documents (PDFs)</a></li>
                <li><a href="live_updates.html" class="nav-item {'active' if active_page == 'live_updates' else ''}"><i data-lucide="radio"></i> Live Updates</a></li>
                <li>
                    <a href="notifications.html" class="nav-item {'active' if active_page == 'notifications' else ''}">
                        <i data-lucide="bell"></i> Notifications <span class="badge" id="sidebar-badge">0</span>
                    </a>
                </li>
            </ul>
            <div class="nav-divider"></div>
            <ul class="nav-menu">
                <li><a href="profile.html" class="nav-item {'active' if active_page == 'profile' else ''}"><i data-lucide="user"></i> My Profile</a></li>
                <li><a href="login.html" class="nav-item logout-btn" style="color: #ef4444;"><i data-lucide="log-out"></i> Logout</a></li>
            </ul>
        </aside>
"""

def generate_page(filename, title, is_admin, active_page, page_header, content, custom_css=""):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{title}</title>
    
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    
    <link rel="stylesheet" href="./css/globals.css">
    <link rel="stylesheet" href="./css/dashboard.css">
    {custom_css}
</head>
<body class="dashboard-page">

    <!-- Top Navbar -->
    <nav class="top-navbar">
        <button class="mobile-menu-btn" onclick="toggleSidebar()">
            <i data-lucide="menu" size="20"></i>
        </button>
        <div class="navbar-brand">
            <i data-lucide="{'shield-alert' if is_admin else 'graduation-cap'}" class="text-green"></i>
            {('Admin <span class="text-green">Panel</span>') if is_admin else 'Institution <span class="text-green">AI Assistant</span>'}
        </div>
        
        <div class="navbar-search">
            <i data-lucide="search" class="search-icon"></i>
            <input type="text" placeholder="Search...">
        </div>
        
        <div class="navbar-actions">
            <button class="icon-action-btn" onclick="window.location.href='notifications.html'">
                <i data-lucide="bell"></i>
                <span class="badge" id="nav-badge-count">0</span>
            </button>
            <div class="user-profile" onclick="window.location.href='profile.html'" style="cursor:pointer;">
                <div class="user-avatar" id="nav-avatar">{"A" if is_admin else "U"}</div>
                <div class="user-info">
                    <span class="user-name" id="nav-name">{"Admin User" if is_admin else "Student"}</span>
                    <span class="user-role" id="nav-role">{"System Admin" if is_admin else "BCA 2nd Sem"}</span>
                </div>
            </div>
        </div>
    </nav>

    <div class="sidebar-overlay" id="sidebar-overlay" onclick="toggleSidebar()"></div>

    <div class="dashboard-body">
        {get_sidebar(is_admin, active_page)}
        
        <main class="main-content">
            {page_header}
            {content}
        </main>
    </div>

    <!-- Scripts -->
    <script src="./js/api.js"></script>
    <script>
        lucide.createIcons();
        function toggleSidebar() {{
            const sidebar = document.querySelector('.sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            if (sidebar.classList.contains('open')) {{
                sidebar.classList.remove('open');
                overlay.classList.remove('show');
            }} else {{
                sidebar.classList.add('open');
                overlay.classList.add('show');
            }}
        }}
        
        // Mock Auth check just to show user names
        document.addEventListener('DOMContentLoaded', async () => {{
            const user = await requireAuth();
            if(user) {{
                document.getElementById('nav-name').textContent = user.name;
                const initials = user.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
                document.getElementById('nav-avatar').textContent = initials;
                document.getElementById('nav-role').textContent = user.role;
            }}
        }});
    </script>
</body>
</html>
"""
    with open(os.path.join(FRONTEND_DIR, filename), "w", encoding="utf-8") as f:
        f.write(html)


# --- 1. Chatbot (index.html) ---
chat_css = """
<style>
.chat-container { display: flex; flex-direction: column; height: calc(100vh - 120px); background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(0, 210, 97, 0.15); border-radius: 12px; overflow: hidden; }
.chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; }
.message { display: flex; gap: 12px; max-width: 80%; }
.message.user { align-self: flex-end; flex-direction: row-reverse; }
.msg-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #00D261; color: #041209; flex-shrink: 0; }
.message.bot .msg-avatar { background: rgba(0, 210, 97, 0.1); color: #00D261; border: 1px solid rgba(0, 210, 97, 0.2); }
.msg-content { padding: 12px 16px; border-radius: 12px; background: rgba(255,255,255,0.03); color: #e5e7eb; font-size: 0.9rem; line-height: 1.5; }
.message.user .msg-content { background: #00D261; color: #041209; border-top-right-radius: 2px; }
.message.bot .msg-content { border-top-left-radius: 2px; border: 1px solid rgba(0, 210, 97, 0.1); }
.chat-input-area { padding: 16px; background: rgba(4, 18, 9, 0.8); border-top: 1px solid rgba(0, 210, 97, 0.15); display: flex; gap: 10px; }
.chat-input { flex: 1; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; padding: 12px 20px; color: #fff; outline: none; transition: border-color 0.3s; }
.chat-input:focus { border-color: #00D261; }
.send-btn { width: 44px; height: 44px; border-radius: 50%; background: #00D261; border: none; color: #041209; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: transform 0.2s; }
.send-btn:hover { transform: scale(1.05); }
.source-pills { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
.source-pill { font-size: 0.7rem; padding: 4px 10px; background: rgba(0, 210, 97, 0.1); color: #00D261; border-radius: 12px; border: 1px solid rgba(0, 210, 97, 0.2); display: flex; align-items: center; gap: 4px; cursor: pointer; }
</style>
"""
generate_page("index.html", "AI Chatbot", False, "index", 
    "", 
    """
    <div class="chat-container">
        <div class="chat-messages" id="chat-messages">
            <div class="message bot">
                <div class="msg-avatar"><i data-lucide="bot"></i></div>
                <div class="msg-content">
                    Hello! I am your AI Assistant. I can help you find answers from the uploaded PDFs, syllabus, and previous year papers. What do you want to learn today?
                </div>
            </div>
            <div class="message user">
                <div class="msg-avatar">U</div>
                <div class="msg-content">Can you explain what STL Vectors are in C++?</div>
            </div>
            <div class="message bot">
                <div class="msg-avatar"><i data-lucide="bot"></i></div>
                <div class="msg-content">
                    Vectors are sequence containers representing arrays that can change in size. Just like arrays, vectors use contiguous storage locations for their elements, which means that their elements can also be accessed using offsets on regular pointers to its elements.
                    <br><br>
                    <strong>Key Features:</strong><br>
                    • Dynamic sizing<br>
                    • Contiguous memory<br>
                    • Constant time access O(1)
                    <div class="source-pills">
                        <div class="source-pill"><i data-lucide="file-text" style="width:12px; height:12px;"></i> BCA_Sem2_C++.pdf (Page 45)</div>
                    </div>
                </div>
            </div>
        </div>
        <div class="chat-input-area">
            <button class="action-btn-icon" style="color: #9ca3af;"><i data-lucide="paperclip"></i></button>
            <input type="text" class="chat-input" placeholder="Ask a question..." id="chat-input-box">
            <button class="send-btn"><i data-lucide="send" style="width:18px; height:18px;"></i></button>
        </div>
    </div>
    """, custom_css=chat_css)


# --- 2. Profile ---
generate_page("profile.html", "My Profile", False, "profile",
    """
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-header-icon"><i data-lucide="user"></i></div>
            <div><h1>My Profile</h1><p>Manage your account settings and personal information.</p></div>
        </div>
    </div>
    """,
    """
    <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); padding: 2rem; border-radius: 12px; max-width: 600px;">
        <div style="display:flex; align-items:center; gap: 20px; margin-bottom: 30px;">
            <div style="width: 80px; height: 80px; border-radius: 50%; background: #00D261; color: #041209; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold;">VK</div>
            <div>
                <h2 style="color: #fff; margin-bottom: 5px;">Vinay Kumar</h2>
                <p style="color: #9ca3af; font-size: 0.9rem;">vinay@institution.edu</p>
                <span class="role-badge" style="margin-top: 8px; display: inline-block;">BCA 2nd Sem</span>
            </div>
            <button class="btn-outline-small" style="margin-left: auto;">Change Avatar</button>
        </div>
        <hr style="border:none; border-top:1px solid rgba(255,255,255,0.05); margin-bottom:20px;">
        <form style="display: flex; flex-direction: column; gap: 15px;">
            <div>
                <label style="display:block; color:#9ca3af; font-size:0.8rem; margin-bottom:5px;">Full Name</label>
                <input type="text" value="Vinay Kumar" style="width:100%; padding:10px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); color:#fff; border-radius:6px; outline:none;">
            </div>
            <div>
                <label style="display:block; color:#9ca3af; font-size:0.8rem; margin-bottom:5px;">Email Address</label>
                <input type="email" value="vinay@institution.edu" disabled style="width:100%; padding:10px; background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.05); color:#6b7280; border-radius:6px; outline:none; cursor:not-allowed;">
            </div>
            <div>
                <label style="display:block; color:#9ca3af; font-size:0.8rem; margin-bottom:5px;">New Password</label>
                <input type="password" placeholder="Leave blank to keep current" style="width:100%; padding:10px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); color:#fff; border-radius:6px; outline:none;">
            </div>
            <button type="button" class="btn-green" style="align-self: flex-start; margin-top: 10px;">Save Changes</button>
        </form>
    </div>
    """)

# --- 3. Chat History ---
generate_page("chat_history.html", "My Queries", False, "chat_history",
    """
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-header-icon"><i data-lucide="message-square"></i></div>
            <div><h1>Chat History</h1><p>Review your previous conversations with the AI.</p></div>
        </div>
        <div class="search-box" style="display:flex; align-items:center; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); padding:6px 12px; border-radius:6px; gap:8px;">
            <i data-lucide="search" style="width:16px; color:#9ca3af;"></i>
            <input type="text" placeholder="Search chats..." style="background:transparent; border:none; color:#fff; outline:none; font-size:0.8rem;">
        </div>
    </div>
    """,
    """
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;">
        <div class="category-card" style="padding: 20px; flex-direction: column; align-items: flex-start; gap: 10px; cursor: pointer;">
            <div style="display: flex; justify-content: space-between; width: 100%;">
                <h3 style="color: #fff; font-size: 1rem; margin:0;">STL Vectors vs Arrays</h3>
                <span style="color: #00D261; background: rgba(0, 210, 97, 0.1); padding: 2px 8px; border-radius: 12px; font-size: 0.7rem;">12 msgs</span>
            </div>
            <p style="color: #9ca3af; font-size: 0.8rem; margin:0;">"What is the time complexity of vector insertion?"</p>
            <span style="color: #6b7280; font-size: 0.7rem;"><i data-lucide="clock" style="width:12px; height:12px; vertical-align:middle;"></i> Today, 02:45 PM</span>
        </div>
        <div class="category-card" style="padding: 20px; flex-direction: column; align-items: flex-start; gap: 10px; cursor: pointer;">
            <div style="display: flex; justify-content: space-between; width: 100%;">
                <h3 style="color: #fff; font-size: 1rem; margin:0;">Operating System Deadlocks</h3>
                <span style="color: #00D261; background: rgba(0, 210, 97, 0.1); padding: 2px 8px; border-radius: 12px; font-size: 0.7rem;">4 msgs</span>
            </div>
            <p style="color: #9ca3af; font-size: 0.8rem; margin:0;">"Explain the 4 conditions for deadlock."</p>
            <span style="color: #6b7280; font-size: 0.7rem;"><i data-lucide="clock" style="width:12px; height:12px; vertical-align:middle;"></i> Yesterday, 10:15 AM</span>
        </div>
    </div>
    """)

# --- 4. Saved Answers ---
generate_page("saved_answers.html", "Saved Answers", False, "saved_answers",
    """
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-header-icon" style="color: #f59e0b; background: rgba(245, 158, 11, 0.1);"><i data-lucide="bookmark"></i></div>
            <div><h1>Saved Answers</h1><p>Your bookmarked AI responses for quick revision.</p></div>
        </div>
    </div>
    """,
    """
    <div style="display: flex; flex-direction: column; gap: 15px;">
        <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <h3 style="color: #fff; font-size: 1.1rem; margin: 0;">What is a Binary Search Tree?</h3>
                <button class="action-btn-icon" style="color:#ef4444;" title="Remove Bookmark"><i data-lucide="bookmark-minus"></i></button>
            </div>
            <div style="color: #e5e7eb; font-size: 0.9rem; line-height: 1.6; background: rgba(255,255,255,0.02); padding: 15px; border-radius: 8px;">
                A binary search tree (BST) is a node-based binary tree data structure which has the following properties:
                <ul>
                    <li>The left subtree of a node contains only nodes with keys lesser than the node's key.</li>
                    <li>The right subtree of a node contains only nodes with keys greater than the node's key.</li>
                    <li>The left and right subtree each must also be a binary search tree.</li>
                </ul>
            </div>
            <div style="margin-top: 15px; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #9ca3af; font-size: 0.75rem;">Saved on 1 Oct 2026</span>
                <span style="color: #00D261; font-size: 0.75rem; display: flex; align-items: center; gap:4px; cursor: pointer;"><i data-lucide="external-link" style="width:12px; height:12px;"></i> View in Chat</span>
            </div>
        </div>
    </div>
    """)

# --- 5. Documents ---
generate_page("documents.html", "Documents (PDFs)", False, "documents",
    """
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-header-icon" style="color: #3b82f6; background: rgba(59, 130, 246, 0.1);"><i data-lucide="file-text"></i></div>
            <div><h1>Document Library</h1><p>Browse syllabus, notes, and previous year papers.</p></div>
        </div>
        <select class="filter-select" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); color: #fff; padding: 8px 12px; border-radius: 6px;">
            <option>All Documents</option>
            <option>Syllabus</option>
            <option>Previous Papers</option>
        </select>
    </div>
    """,
    """
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px;">
        <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; text-align: center; transition: transform 0.2s; cursor: pointer;">
            <div style="width: 60px; height: 60px; background: rgba(239, 68, 68, 0.1); color: #ef4444; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto;">
                <i data-lucide="file-type-2" style="width: 30px; height: 30px;"></i>
            </div>
            <h4 style="color: #fff; margin: 0 0 5px 0; font-size: 0.9rem;">BCA_Sem2_Syllabus.pdf</h4>
            <p style="color: #9ca3af; font-size: 0.75rem; margin: 0 0 15px 0;">2.4 MB • 12 Pages</p>
            <button class="btn-outline-small" style="width: 100%;">Open PDF</button>
        </div>
        <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; text-align: center; transition: transform 0.2s; cursor: pointer;">
            <div style="width: 60px; height: 60px; background: rgba(239, 68, 68, 0.1); color: #ef4444; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto;">
                <i data-lucide="file-type-2" style="width: 30px; height: 30px;"></i>
            </div>
            <h4 style="color: #fff; margin: 0 0 5px 0; font-size: 0.9rem;">C++_Notes_Unit1.pdf</h4>
            <p style="color: #9ca3af; font-size: 0.75rem; margin: 0 0 15px 0;">4.1 MB • 45 Pages</p>
            <button class="btn-outline-small" style="width: 100%;">Open PDF</button>
        </div>
    </div>
    """)

# --- 6. Live Updates ---
generate_page("live_updates.html", "Live Updates", False, "live_updates",
    """
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-header-icon" style="color: #ec4899; background: rgba(236, 72, 153, 0.1);"><i data-lucide="radio"></i></div>
            <div><h1>Live Updates</h1><p>Real-time announcements and emergency notices.</p></div>
        </div>
    </div>
    """,
    """
    <div style="position: relative; padding-left: 30px; border-left: 2px solid rgba(0, 210, 97, 0.2); margin-left: 20px; display: flex; flex-direction: column; gap: 30px;">
        <div style="position: relative;">
            <div style="position: absolute; left: -39px; top: 0; width: 16px; height: 16px; border-radius: 50%; background: #00D261; border: 4px solid #041209;"></div>
            <span style="color: #9ca3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Today, 10:00 AM</span>
            <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin-top: 10px;">
                <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
                    <span style="background: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600;">URGENT</span>
                    <h3 style="color: #fff; margin: 0; font-size: 1.1rem;">Exams Rescheduled</h3>
                </div>
                <p style="color: #d1d5db; font-size: 0.9rem; line-height: 1.5; margin: 0;">Due to unforeseen circumstances, the BCA 2nd Sem Data Structures exam has been postponed to 15th October. Please check the new timetable PDF in the documents section.</p>
            </div>
        </div>
        <div style="position: relative;">
            <div style="position: absolute; left: -39px; top: 0; width: 16px; height: 16px; border-radius: 50%; background: #3b82f6; border: 4px solid #041209;"></div>
            <span style="color: #9ca3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">2 Oct 2026, 04:30 PM</span>
            <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin-top: 10px;">
                <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
                    <span style="background: rgba(59, 130, 246, 0.15); color: #3b82f6; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600;">INFO</span>
                    <h3 style="color: #fff; margin: 0; font-size: 1.1rem;">New Chatbot Features Active</h3>
                </div>
                <p style="color: #d1d5db; font-size: 0.9rem; line-height: 1.5; margin: 0;">The AI chatbot can now process Hindi queries. Try asking questions in Hindi or Hinglish!</p>
            </div>
        </div>
    </div>
    """)


# --- 7. Admin Dashboard (admin.html) ---
generate_page("admin.html", "Admin Dashboard", True, "admin",
    """
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-header-icon"><i data-lucide="layout-dashboard"></i></div>
            <div><h1>System Overview</h1><p>Monitor platform usage, AI performance, and user activity.</p></div>
        </div>
    </div>
    """,
    """
    <div class="stats-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 30px;">
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(37, 99, 235, 0.2); color: #3b82f6;"><i data-lucide="message-square"></i></div>
            <div class="stat-details">
                <span class="stat-label">Total Queries</span>
                <span class="stat-number">45,231</span>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(16, 185, 129, 0.2); color: #10b981;"><i data-lucide="zap"></i></div>
            <div class="stat-details">
                <span class="stat-label">Avg Response Time</span>
                <span class="stat-number">1.2s</span>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(245, 158, 11, 0.2); color: #f59e0b;"><i data-lucide="file-text"></i></div>
            <div class="stat-details">
                <span class="stat-label">Documents Indexed</span>
                <span class="stat-number">142</span>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(239, 68, 68, 0.2); color: #ef4444;"><i data-lucide="users"></i></div>
            <div class="stat-details">
                <span class="stat-label">Active Users</span>
                <span class="stat-number">892</span>
            </div>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
        <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px;">
            <h3 style="color:#fff; margin-bottom:20px; font-size:1.1rem;">Recent Activity</h3>
            <table class="data-table">
                <thead><tr><th>User</th><th>Action</th><th>Time</th></tr></thead>
                <tbody>
                    <tr><td>Vinay Kumar</td><td style="color:#9ca3af;">Asked a question about C++</td><td>2 mins ago</td></tr>
                    <tr><td>Riya Sharma</td><td style="color:#9ca3af;">Downloaded BCA Syllabus</td><td>15 mins ago</td></tr>
                    <tr><td>Dr. Neha</td><td style="color:#9ca3af;">Published Live Update</td><td>1 hour ago</td></tr>
                </tbody>
            </table>
        </div>
        <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px;">
            <h3 style="color:#fff; margin-bottom:20px; font-size:1.1rem;">System Health</h3>
            <div style="display: flex; flex-direction: column; gap: 15px;">
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.8rem; color: #9ca3af;">
                        <span>Vector DB Capacity</span><span>45%</span>
                    </div>
                    <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                        <div style="width: 45%; height: 100%; background: #00D261; border-radius: 3px;"></div>
                    </div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.8rem; color: #9ca3af;">
                        <span>API Rate Limits</span><span>12%</span>
                    </div>
                    <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                        <div style="width: 12%; height: 100%; background: #3b82f6; border-radius: 3px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """)

# --- 8. Admin Chatbot Mgmt (admin_chatbot.html) ---
generate_page("admin_chatbot.html", "Chatbot Management", True, "admin_chatbot",
    """
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-header-icon" style="color: #8b5cf6; background: rgba(139, 92, 246, 0.1);"><i data-lucide="bot"></i></div>
            <div><h1>Chatbot Settings</h1><p>Configure LLM provider, prompt engineering, and RAG settings.</p></div>
        </div>
        <button class="btn-green">Save Configuration</button>
    </div>
    """,
    """
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px;">
            <h3 style="color:#fff; margin-bottom:20px; font-size:1.1rem;">Model Configuration</h3>
            <form style="display: flex; flex-direction: column; gap: 15px;">
                <div>
                    <label style="display:block; color:#9ca3af; font-size:0.8rem; margin-bottom:5px;">Primary LLM Provider</label>
                    <select style="width:100%; padding:10px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); color:#fff; border-radius:6px; outline:none;">
                        <option>Google Gemini 1.5 Pro</option>
                        <option>Google Gemini 1.5 Flash</option>
                    </select>
                </div>
                <div>
                    <label style="display:block; color:#9ca3af; font-size:0.8rem; margin-bottom:5px;">Temperature (0.0 - 1.0)</label>
                    <input type="range" min="0" max="100" value="30" style="width:100%; accent-color: #00D261;">
                    <div style="text-align: right; font-size: 0.7rem; color: #9ca3af; margin-top: 4px;">Current: 0.3 (More factual)</div>
                </div>
                <div>
                    <label style="display:block; color:#9ca3af; font-size:0.8rem; margin-bottom:5px;">System Prompt (Instructions)</label>
                    <textarea rows="5" style="width:100%; padding:10px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); color:#fff; border-radius:6px; outline:none;">You are an AI assistant for a university. Only answer based on the provided document context. If the answer is not in the context, say you don't know.</textarea>
                </div>
            </form>
        </div>
        <div style="background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px;">
            <h3 style="color:#fff; margin-bottom:20px; font-size:1.1rem;">RAG (Retrieval) Settings</h3>
            <form style="display: flex; flex-direction: column; gap: 15px;">
                <div>
                    <label style="display:block; color:#9ca3af; font-size:0.8rem; margin-bottom:5px;">Top K Chunks</label>
                    <input type="number" value="5" style="width:100%; padding:10px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); color:#fff; border-radius:6px; outline:none;">
                </div>
                <div style="display:flex; align-items:center; gap:10px; margin-top: 10px;">
                    <input type="checkbox" checked style="accent-color: #00D261; width:16px; height:16px;">
                    <label style="color:#e5e7eb; font-size:0.9rem;">Enable Multilingual Support (Hindi/English)</label>
                </div>
                <div style="display:flex; align-items:center; gap:10px;">
                    <input type="checkbox" checked style="accent-color: #00D261; width:16px; height:16px;">
                    <label style="color:#e5e7eb; font-size:0.9rem;">Include Source Citations in Responses</label>
                </div>
            </form>
        </div>
    </div>
    """)

# --- 9. Admin Documents (admin_documents.html) ---
generate_page("admin_documents.html", "Document Management", True, "admin_documents",
    """
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-header-icon" style="color: #3b82f6; background: rgba(59, 130, 246, 0.1);"><i data-lucide="folder"></i></div>
            <div><h1>Knowledge Base</h1><p>Upload and manage PDFs that the AI chatbot learns from.</p></div>
        </div>
        <button class="btn-green"><i data-lucide="upload" style="width:14px; height:14px;"></i> Upload PDF</button>
    </div>
    """,
    """
    <div class="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Filename</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Chunks</th>
                    <th>Status</th>
                    <th>Uploaded</th>
                    <th style="text-align: right;">Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="color:#fff; font-weight:600;"><i data-lucide="file-text" style="width:14px; height:14px; color:#ef4444; margin-right:6px; vertical-align:middle;"></i> BCA_Sem2_Syllabus.pdf</td>
                    <td>Syllabus</td>
                    <td>2.4 MB</td>
                    <td>45</td>
                    <td><span class="status-badge" style="background:rgba(16, 185, 129, 0.15); color:#10b981;">Indexed</span></td>
                    <td>1 Oct 2026</td>
                    <td style="text-align: right;">
                        <button class="action-btn-icon delete"><i data-lucide="trash-2"></i></button>
                    </td>
                </tr>
                <tr>
                    <td style="color:#fff; font-weight:600;"><i data-lucide="file-text" style="width:14px; height:14px; color:#ef4444; margin-right:6px; vertical-align:middle;"></i> OS_Unit3.pdf</td>
                    <td>Notes</td>
                    <td>5.1 MB</td>
                    <td>-</td>
                    <td><span class="status-badge" style="background:rgba(245, 158, 11, 0.15); color:#f59e0b;"><i data-lucide="loader" style="width:10px; height:10px; animation:spin 2s linear infinite;"></i> Processing</span></td>
                    <td>Just now</td>
                    <td style="text-align: right;">
                        <button class="action-btn-icon delete"><i data-lucide="trash-2"></i></button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    """)

# --- 10. Admin Live Updates (admin_live_updates.html) ---
generate_page("admin_live_updates.html", "Live Updates Management", True, "admin_live_updates",
    """
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-header-icon" style="color: #ec4899; background: rgba(236, 72, 153, 0.1);"><i data-lucide="radio"></i></div>
            <div><h1>Manage Live Updates</h1><p>Broadcast announcements and notifications to all users.</p></div>
        </div>
        <button class="btn-green"><i data-lucide="plus" style="width:14px; height:14px;"></i> New Update</button>
    </div>
    """,
    """
    <div class="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Published At</th>
                    <th style="text-align: right;">Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="color:#fff; font-weight:600;">Exams Rescheduled</td>
                    <td><span class="status-badge" style="background:rgba(239, 68, 68, 0.15); color:#ef4444;">URGENT</span></td>
                    <td><span class="status-badge" style="background:rgba(16, 185, 129, 0.15); color:#10b981;">Published</span></td>
                    <td>Today, 10:00 AM</td>
                    <td style="text-align: right;">
                        <button class="action-btn-icon" title="Unpublish"><i data-lucide="eye-off"></i></button>
                        <button class="action-btn-icon delete"><i data-lucide="trash-2"></i></button>
                    </td>
                </tr>
                <tr>
                    <td style="color:#fff; font-weight:600;">Diwali Holiday Notice</td>
                    <td><span class="status-badge" style="background:rgba(59, 130, 246, 0.15); color:#3b82f6;">INFO</span></td>
                    <td><span class="status-badge" style="background:rgba(255, 255, 255, 0.1); color:#9ca3af;">Draft</span></td>
                    <td>-</td>
                    <td style="text-align: right;">
                        <button class="action-btn-icon" title="Publish" style="color:#10b981;"><i data-lucide="send"></i></button>
                        <button class="action-btn-icon"><i data-lucide="edit-2"></i></button>
                        <button class="action-btn-icon delete"><i data-lucide="trash-2"></i></button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    """)

print("All 10 remaining pages successfully generated!")
