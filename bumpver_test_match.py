import re

with open("pyproject.toml", "r", encoding="utf-8") as f:
    lines = f.readlines()

pattern = r'version = "2025\.1001-dev"  # {bumpver}'

for i, line in enumerate(lines):
    if re.match(pattern, line):
        print(f"✅ MATCH on line {i+1}: {line.strip()}")
        break
else:
    print("❌ NO MATCH")
    print("Showing lines for review:")
    print("".join(lines[:10]))
