import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('.agents/teamwork/spec_miner_1/pdf_text_dump.txt', encoding='utf-8') as f:
    pdf_text = f.read()

with open('SRS_MedClient_Architettura_Completa.md', encoding='utf-8') as f:
    srs_text = f.read()

def search_snippets(text, kw, max_snippets=5, context_chars=300):
    matches = [m.start() for m in re.finditer(re.escape(kw), text, re.IGNORECASE)]
    snippets = []
    for pos in matches[:max_snippets]:
        start = max(0, pos - 100)
        end = min(len(text), pos + context_chars)
        snippets.append(text[start:end].replace('\n', ' '))
    return snippets

print("=== PYHPO IN PDF ===")
for s in search_snippets(pdf_text, "PyHPO"):
    print(" - ", s)
    print()

print("=== HPO IN SRS ===")
for s in search_snippets(srs_text, "HPO"):
    print(" - ", s)
    print()

print("=== DOCLING IN PDF ===")
for s in search_snippets(pdf_text, "Docling", max_snippets=3):
    print(" - ", s)
    print()

print("=== DOCLING IN SRS ===")
for s in search_snippets(srs_text, "Docling", max_snippets=3):
    print(" - ", s)
    print()

print("=== ZSTANDARD / DICTIONARY IN SRS ===")
for s in search_snippets(srs_text, "112", max_snippets=4):
    print(" - ", s)
    print()

print("=== MEDPACK STRUCTURE IN SRS ===")
for s in search_snippets(srs_text, ".medpack", max_snippets=3):
    print(" - ", s)
    print()
