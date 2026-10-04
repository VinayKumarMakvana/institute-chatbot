import glob

files = ['frontend/chat_history.html', 'frontend/documents.html', 'frontend/index.html', 'frontend/live_updates.html', 'frontend/notifications.html', 'frontend/profile.html', 'frontend/saved_answers.html']

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if '<i data-lucide="bell"></i>' in line:
                if 'nav-btn' in lines[i-1] or 'icon-action-btn' in lines[i-1]:
                    print(f'{f}:')
                    print(lines[i-1].strip())
                    print(lines[i].strip())
                    if i+1 < len(lines):
                        print(lines[i+1].strip())
                    print('---')
