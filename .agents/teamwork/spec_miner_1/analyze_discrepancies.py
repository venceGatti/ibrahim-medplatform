import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('SRS_MedClient_Architettura_Completa.md', encoding='utf-8') as f:
    srs_text = f.read()

with open('.agents/teamwork/spec_miner_1/pdf_text_dump.txt', encoding='utf-8') as f:
    pdf_text = f.read()

with open(r'C:\Users\vence\.gemini\antigravity\brain\3aa6efc6-1a77-4cff-b774-120f18a304fb\piano_costruzione_autonoma_medplatform.md', encoding='utf-8') as f:
    plan_text = f.read()

print("=== CHECKING DISCREPANCIES ===")

# 1. SDUI Block Names
print("\n--- 1. SDUI Block Names ---")
print("In Plan:")
for line in plan_text.split('\n'):
    if 'Block' in line:
        print("  Plan:", line.strip())

print("In SRS Modulo 4.3:")
for line in srs_text[srs_text.find("## Modulo 4.3"):].split('\n')[:80]:
    if 'Block' in line or 'class ' in line:
        print("  SRS:", line.strip())

# 2. Vector DB vs SQLite FTS5 / Search Engine
print("\n--- 2. Vector Search / ChromaDB vs SQLite FTS5 ---")
print("ChromaDB in Plan:", "chromadb" in plan_text.lower())
print("ChromaDB in SRS:", "chromadb" in srs_text.lower())
matches_chroma_srs = re.findall(r'.{0,50}chromadb.{0,50}', srs_text, re.IGNORECASE)
print(f"ChromaDB mentions in SRS: {len(matches_chroma_srs)}")
for m in matches_chroma_srs[:3]:
    print("  SRS:", m.strip())

# 3. Cryptography & Signatures: BLAKE3 vs Ed25519 vs ChaCha20-Poly1305 vs SHA256
print("\n--- 3. Hashing and Signatures ---")
for kw in ["BLAKE3", "Ed25519", "ChaCha20", "SHA256"]:
    print(f"Keyword '{kw}': Plan={len(re.findall(kw, plan_text, re.I))}, SRS={len(re.findall(kw, srs_text, re.I))}, PDF={len(re.findall(kw, pdf_text, re.I))}")

# 4. Port & IPC Secret Mechanism
print("\n--- 4. IPC Secret and Port ---")
for kw in ["X-Tauri-IPC-Secret", "stdin", "Job Object", "WaitForSingleObject", "med-asset://"]:
    print(f"Keyword '{kw}': Plan={len(re.findall(re.escape(kw), plan_text, re.I))}, SRS={len(re.findall(re.escape(kw), srs_text, re.I))}, PDF={len(re.findall(re.escape(kw), pdf_text, re.I))}")

# 5. Database Names and Schemas
print("\n--- 5. SQLite Database Names ---")
for kw in ["module_kb.sqlite", "user_state.sqlite", "netmedic", "blue", "green"]:
    print(f"Keyword '{kw}': Plan={len(re.findall(re.escape(kw), plan_text, re.I))}, SRS={len(re.findall(re.escape(kw), srs_text, re.I))}, PDF={len(re.findall(re.escape(kw), pdf_text, re.I))}")

# 6. ONNX Models
print("\n--- 6. ONNX Model References ---")
for kw in ["all-MiniLM-L6-v2", "bge-micro", "nli-deberta", "Cross-Encoder", "INT8", "SQ8"]:
    print(f"Keyword '{kw}': Plan={len(re.findall(re.escape(kw), plan_text, re.I))}, SRS={len(re.findall(re.escape(kw), srs_text, re.I))}, PDF={len(re.findall(re.escape(kw), pdf_text, re.I))}")
