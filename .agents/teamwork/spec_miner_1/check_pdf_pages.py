import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('.agents/teamwork/spec_miner_1/pdf_text_dump.txt', encoding='utf-8') as f:
    pdf_text = f.read()

pages = pdf_text.split('--- PAGE ')

print(f"Total pages: {len(pages)-1}")
for p in pages[1:]:
    lines = [l.strip() for l in p.split('\n') if l.strip()]
    page_num = lines[0].split(' ')[0] if lines else '?'
    first_few = " | ".join(lines[1:4]) if len(lines) > 1 else ""
    print(f"Page {page_num}: {first_few[:100]}")
