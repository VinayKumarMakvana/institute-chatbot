import glob
import re

for filename in glob.glob('*.html'):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Remove the mobile menu button
    content = re.sub(
        r'<button class="mobile-menu-btn"[^>]*>.*?<\/button>', 
        '', 
        content, 
        flags=re.DOTALL
    )
    
    # 2. Fix lucide.createIcons() position
    # First, remove it if it exists as a standalone script block
    content = re.sub(
        r'<script>\s*lucide\.createIcons\(\);\s*</script>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Also remove it if it's inside the active nav logic just in case
    # (We will append it at the very end to ensure it runs last)
    
    # Let's insert lucide.createIcons() right before </body>
    if 'lucide.createIcons();' not in content:
        content = content.replace(
            '</body>', 
            '    <script>\n        lucide.createIcons();\n    </script>\n</body>'
        )
    else:
        # If it's already there (maybe in another block), just ensure it's at the end
        # We can strip all instances of lucide.createIcons(); and re-add it
        content = content.replace('lucide.createIcons();', '')
        content = content.replace(
            '</body>', 
            '    <script>\n        lucide.createIcons();\n    </script>\n</body>'
        )
        
    # Edge case: If there are multiple empty scripts now
    content = re.sub(r'<script>\s*</script>', '', content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Fixed {filename}")
