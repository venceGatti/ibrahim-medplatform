import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('SRS_MedClient_Architettura_Completa.md', encoding='utf-8') as f:
    srs_text = f.read()

with open('.agents/teamwork/spec_miner_1/pdf_text_dump.txt', encoding='utf-8') as f:
    pdf_text = f.read()

with open(r'C:\Users\vence\.gemini\antigravity\brain\3aa6efc6-1a77-4cff-b774-120f18a304fb\piano_costruzione_autonoma_medplatform.md', encoding='utf-8') as f:
    plan_text = f.read()

# Let's check sections in SRS
module_pattern = re.compile(r'## (Modulo \d+\.\d+: [^\n]+)')
matches = list(module_pattern.finditer(srs_text))

print(f"Total Modules in SRS: {len(matches)}")
modules_data = []
for i, m in enumerate(matches):
    start = m.start()
    end = matches[i+1].start() if i+1 < len(matches) else len(srs_text)
    mod_title = m.group(1)
    mod_content = srs_text[start:end]
    modules_data.append((mod_title, mod_content))
    print(f"{i+1}. {mod_title} ({len(mod_content)} chars)")

# Let's inspect specific items in each module
print("\n--- DETAILED EXTRACTION PER MODULE ---")
for title, content in modules_data:
    print(f"\n==========================================")
    print(f"MODULE: {title}")
    # Extract subheadings
    subheads = re.findall(r'(?:^|\n)(#{3,5}\s+[^\n]+)', content)
    print("Subheadings:")
    for sh in subheads[:10]:
        print("  ", sh.strip())
    # Extract schemas/code blocks
    code_blocks = re.findall(r'```(?:python|rust|json|sql|text|bash)?\n(.*?)```', content, re.DOTALL)
    print(f"Code blocks: {len(code_blocks)}")
    # Find Pydantic models or structs
    pydantic_classes = re.findall(r'class\s+([A-Za-z0-9_]+)\((?:BaseModel|BaseSettings)[^\)]*\):', content)
    if pydantic_classes:
        print("  Pydantic Classes:", pydantic_classes)
    rust_structs = re.findall(r'(?:pub\s+)?struct\s+([A-Za-z0-9_]+)', content)
    if rust_structs:
        print("  Rust Structs:", rust_structs)
    # Find SQL tables
    sql_tables = re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z0-9_]+)', content, re.IGNORECASE)
    if sql_tables:
        print("  SQL Tables:", sql_tables)
