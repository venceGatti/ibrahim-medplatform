import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('SRS_MedClient_Architettura_Completa.md', encoding='utf-8') as f:
    srs_text = f.read()

# Let's inspect:
# 1. Blue/Green swap in Modulo 1.4
# 2. ChromaDB vs SQLite in Modulo 2.2
# 3. Log-Odds algorithm in Modulo 3.1
# 4. CYP450 algorithm in Modulo 3.2
# 5. Exam DAG and NLI in Modulo 4.1
# 6. FSRS algorithm in Modulo 4.2

def search_text(kw, start_str=None, length=2000):
    idx = 0
    if start_str:
        idx = srs_text.find(start_str)
        if idx == -1:
            print(f"Start string '{start_str}' not found")
            return
    matches = [m.start() for m in re.finditer(re.escape(kw), srs_text[idx:], re.I)]
    print(f"=== Keyword '{kw}' from '{start_str}' (found {len(matches)}) ===")
    for m in matches[:2]:
        pos = idx + m
        print(srs_text[pos-50:pos+length])
        print("\n" + "="*40 + "\n")

print("--- BLUE/GREEN SWAP IN MODULO 1.4 ---")
search_text("swap", "## Modulo 1.4", 1500)

print("--- CHROMADB IN MODULO 2.2 ---")
search_text("chromadb", "## Modulo 2.2", 1500)

print("--- LOG-ODDS IN MODULO 3.1 ---")
search_text("log-odds", "## Modulo 3.1", 1500)

print("--- CYP450 IN MODULO 3.2 ---")
search_text("CYP450", "## Modulo 3.2", 1500)

print("--- FSRS IN MODULO 4.2 ---")
search_text("FSRS", "## Modulo 4.2", 1500)
