import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('SRS_MedClient_Architettura_Completa.md', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if line.startswith('#'):
        if line.startswith('# ') or line.startswith('## '):
            print(f"Line {idx+1}: {line.strip()}")
