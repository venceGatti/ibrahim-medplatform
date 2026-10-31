import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

print("=== INSPECTING PDF DUMP ===")
with open('.agents/teamwork/spec_miner_1/pdf_text_dump.txt', encoding='utf-8') as f:
    pdf_text = f.read()

# Find major headers in PDF
headers = re.findall(r'(?:^|\n)(#{1,4}\s+[^\n]+|[A-Z0-9\.\s\-]{4,50}\n---|\b(?:Fase|Modulo|Capitolo|Sezione|Architettura)\b[^\n]+)', pdf_text, re.IGNORECASE)
print(f"Total potential headers found in PDF: {len(headers)}")
for h in headers[:40]:
    clean_h = h.strip()
    if clean_h:
        print("  PDF:", clean_h[:80])

print("\n=== SEARCHING KEYWORDS IN PDF ===")
keywords = [
    "Docling", "PyHPO", "Zstandard", "112", "medpack", "Tauri", "FastAPI",
    "Blue/Green", "med-asset://", "mmap", "log-odds", "rule-out", "CYP450",
    "Cross-Encoder", "FSRS", "Agentic", "300MB", "50ms", "jemalloc", "Job Object"
]
for kw in keywords:
    matches = len(re.findall(re.escape(kw), pdf_text, re.IGNORECASE))
    print(f"  Keyword '{kw}': {matches} occurrences in PDF")

print("\n=== SEARCHING KEYWORDS IN SRS ===")
with open('SRS_MedClient_Architettura_Completa.md', encoding='utf-8') as f:
    srs_text = f.read()

for kw in keywords:
    matches = len(re.findall(re.escape(kw), srs_text, re.IGNORECASE))
    print(f"  Keyword '{kw}': {matches} occurrences in SRS")
