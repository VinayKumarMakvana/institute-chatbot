"""
Fix the broken syntax caused by the update_toggle.py script.
The old toggleSidebar regex only removed the if-block but left the else-block.
This fixes all affected files.
"""
import re, glob

# The broken pattern that was left behind
BROKEN_PATTERN = r"""lucide\.createIcons\(\);
\s*else \{
\s*sidebar\.classList\.add\('open'\);
\s*overlay\.classList\.add\('show'\);
\s*\}
\s*\}"""

FIXED = "lucide.createIcons();"

UNIVERSAL_TOGGLE = """
        function toggleSidebar() {
            const sidebar = document.querySelector('.sidebar, .chat-sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            if (!sidebar) return;
            const isOpen = sidebar.classList.contains('open');
            if (isOpen) {
                sidebar.classList.remove('open');
                if (overlay) overlay.classList.remove('show');
                document.body.style.overflow = '';
            } else {
                sidebar.classList.add('open');
                if (overlay) overlay.classList.add('show');
                document.body.style.overflow = 'hidden';
            }
        }
"""

for filepath in glob.glob('frontend/*.html'):
    fname = filepath.split('\\')[-1].split('/')[-1]
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    orig = content
    
    # Fix broken else blocks
    content = re.sub(BROKEN_PATTERN, FIXED, content, flags=re.DOTALL)
    
    # Also check for duplicate/broken toggleSidebar definitions and clean up
    # Remove any partial else { sidebar.classList.add('open') floating around
    content = re.sub(
        r"\s*else \{\s*sidebar\.classList\.add\('open'\);\s*(?:if \(overlay\)[^}]+\}|overlay\.classList\.add\('show'\);)\s*\}",
        "",
        content,
        flags=re.DOTALL
    )
    
    # Make sure there's a working toggleSidebar function if it's missing
    if 'mobile-menu-btn' in content and 'function toggleSidebar()' not in content:
        content = content.replace('</script>', UNIVERSAL_TOGGLE + '\n        </script>', 1)
        print(f"Added toggleSidebar to: {fname}")
    
    if content != orig:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {fname}")
    else:
        print(f"OK: {fname}")

print("\nDone!")
