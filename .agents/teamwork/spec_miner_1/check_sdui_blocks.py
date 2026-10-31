import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('SRS_MedClient_Architettura_Completa.md', encoding='utf-8') as f:
    srs_text = f.read()

def show_section(title, length=3000):
    pos = srs_text.find(title)
    if pos != -1:
        print(f"=== {title} ===")
        print(srs_text[pos:pos+length])
    else:
        print(f"NOT FOUND: {title}")

show_section("## 2.3 Schemi Pydantic V2 dei 4 Blocchi Fondamentali", 3500)
