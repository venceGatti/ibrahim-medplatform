import re

file_path = "medclient/sidecar-python/src/api/sdui_routes.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("recommended_alternatives=[a.model_dump() for a in recommended_alternatives],", "recommended_alternatives=recommended_alternatives,")
content = content.replace("recommended_alternatives: List[Dict[str, Any]] = []", "recommended_alternatives: List[Dict[str, Any]] = []")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
