"""
Update the toggleSidebar function in all HTML files to support both .sidebar and .chat-sidebar,
and also initialize bottom nav badge from notification count.
"""
import re, glob

# Universal toggleSidebar that works for all page types
UNIVERSAL_TOGGLE = """
        function toggleSidebar() {
            const sidebar = document.querySelector('.sidebar, .chat-sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            if (!sidebar) return;
            const isOpen = sidebar.classList.contains('open');
            if (isOpen) {
                sidebar.classList.remove('open');
                if (overlay) { overlay.classList.remove('show'); }
                document.body.style.overflow = '';
            } else {
                sidebar.classList.add('open');
                if (overlay) { overlay.classList.add('show'); }
                document.body.style.overflow = 'hidden';
            }
        }
"""

for filepath in glob.glob('frontend/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace old toggleSidebar with universal one
    pattern = r'function toggleSidebar\(\)\s*\{[^}]*(?:\{[^}]*\}[^}]*)?\}'
    matches = list(re.finditer(pattern, content, re.DOTALL))
    if matches:
        # Replace ALL occurrences with the universal one (only keep first)
        new_content = re.sub(pattern, '', content, flags=re.DOTALL)
        # Insert the universal function before the first </script>
        new_content = new_content.replace(
            '</script>',
            UNIVERSAL_TOGGLE + '\n        </script>',
            1  # only replace first occurrence
        )
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated toggleSidebar: {filepath.split('/')[-1]}")
    else:
        print(f"No toggleSidebar found: {filepath.split('/')[-1]}")

print("Done!")
