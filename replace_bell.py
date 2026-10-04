import os

files = ['frontend/chat_history.html', 'frontend/documents.html', 'frontend/index.html', 'frontend/live_updates.html', 'frontend/profile.html', 'frontend/saved_answers.html']

target = """            <button class="nav-btn" onclick="window.location.href='notifications.html'" style="background:none; border:none; color:#d1d5db; position:relative; cursor:pointer;">
                <i data-lucide="bell"></i>
                <span class="badge" style="position:absolute; top:-2px; right:-2px; background:#ef4444; width:8px; height:8px; border-radius:50%;"></span>
            </button>"""

replacement = """            <button class="icon-action-btn" onclick="window.location.href='notifications.html'">
                <i data-lucide="bell"></i>
                <span class="badge" id="nav-badge-count">0</span>
            </button>"""

target_alt = """            <button class="nav-btn" onclick="window.location.href='notifications.html'" style="background:none; border:none; color:#d1d5db; position:relative; cursor:pointer;">
                <i data-lucide="bell"></i>
                <span class="badge" style="position:absolute; top:-2px; right:-2px; background:#ef4444; width:8px; height:8px; border-radius:50%;"></span>
            </button>"""

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if target in content:
        content = content.replace(target, replacement)
    elif target_alt in content:
        content = content.replace(target_alt, replacement)
    else:
        print(f"Target not found in {f}")

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
        
print("Replacement done.")
