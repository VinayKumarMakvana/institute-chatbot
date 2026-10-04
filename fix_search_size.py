import os

files = ['frontend/chat_history.html', 'frontend/documents.html']

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace search-box inline styles
    content = content.replace(
        "padding:8px 12px;", 
        "padding:4px 10px; height: 36px;"
    )
    
    # Also fix select inline styles to remove padding: 0 10px (since we added it to css)
    content = content.replace(
        "padding: 0 10px;",
        ""
    )
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
        
print("Fixed search box sizing.")
