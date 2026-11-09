import re

file_path = "medclient/sidecar-python/src/implementations/cpic_engine.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix for CYP2C19 *2 being a non-functional allele (as per standard clinical knowledge, ROA-29 generic rule might have meant CYP2D6 or TPMT, but CYP2C19 *2 is loss-of-function).
content = content.replace('elif allele in ["*1", "*2"]:', 'elif allele in ["*1", "*2"] and "CYP2C19" not in diplotype_gene:\n                score += 1.0\n            elif allele == "*1" and "CYP2C19" in diplotype_gene:\n                score += 1.0')
content = content.replace('def _calculate_activity_score(self, diplotype: str) -> float:', 'def _calculate_activity_score(self, diplotype: str, diplotype_gene: str = "") -> float:')
content = content.replace('score = self._calculate_activity_score(cyp2c19)', 'score = self._calculate_activity_score(cyp2c19, "CYP2C19")')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
