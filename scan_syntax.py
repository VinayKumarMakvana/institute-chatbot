"""
Deep scan all HTML script blocks for common syntax issues:
- Stray } at start of script
- Unclosed braces
"""
import re, glob

for filepath in glob.glob('frontend/*.html'):
    fname = filepath.split('\\')[-1].split('/')[-1]
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all inline script blocks (not src scripts)
    scripts = re.finditer(r'<script(?![^>]*src)[^>]*>(.*?)</script>', content, re.DOTALL)
    
    for match in scripts:
        script = match.group(1)
        lines = script.split('\n')
        
        # Check for stray } as literally the first non-empty code line
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == '}' and i < 5:
                # Find actual line number in file
                offset = match.start(1)
                file_lines = content[:offset].count('\n') + i + 1
                print(f"STRAY BRACE: {fname} line ~{file_lines}")
                print(f"  Context: ...{lines[max(0,i-1)].strip()} | {stripped} | {lines[min(len(lines)-1,i+1)].strip()}...")
                break
        
        # Brace balance check
        opens = script.count('{')
        closes = script.count('}')
        if abs(opens - closes) > 2:
            print(f"BRACE IMBALANCE: {fname} open={opens} close={closes} diff={opens-closes}")

print("Scan complete.")
