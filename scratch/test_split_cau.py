import re

line = "D. 3322 Câu 3: Phương trình 3 cos x + 2 | sin x | = 2 có nghiệm là"
# Tách các câu bị dính liền trên 1 dòng
parts = re.split(r'(?=\b(?:câu|cau|bài|bai)\s*\d+[\s.:\-–—])', line, flags=re.IGNORECASE)
print("Splitted parts:")
for p in parts:
    print(" ->", repr(p.strip()))
