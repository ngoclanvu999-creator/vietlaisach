# -*- coding: utf-8 -*-
"""Đồng bộ ĐỊNH DẠNG MỚI: khớp mỗi file đã triển khai (theo tiêu đề bìa) với file
vừa dựng lại trong scratchpad, rồi ghi đè. Không đổi tên, không đổi vị trí."""
import os, glob, shutil, re, sys
from docx import Document

SP = os.path.dirname(__file__)
BUILD_DIRS = ["l1_build", "l2_build", "l3_build", "l_mn_build",
              "l5_f6", "l5_f7", "l5_hsg", "l5_book1", "l5_book23",
              "book", "book2", "book3", "book4", "book5"]
# thư mục đích: curriculum + kho nguồn
TARGET_ROOTS = [
    r"D:\Tài liệu số\Tiểu học 2026-2027",
    r"D:\Tài liệu số\Toán\Toán 1", r"D:\Tài liệu số\Toán\Toán 2",
    r"D:\Tài liệu số\Toán\Toán 3", r"D:\Tài liệu số\Toán\Toán 4",
    r"D:\Tài liệu số\Toán\Toán 5",
]


def norm(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[\s\u2013\u2014\-–—_:.,()]+", " ", s)
    s = s.replace("\n", " ").replace("  ", " ").strip()
    return s


def cover_title(path):
    try:
        d = Document(path)
    except Exception:
        return None
    chunks = []
    for p in list(d.paragraphs[:30]):
        for r in p.runs:
            if r.font.size and r.font.size.pt and r.font.size.pt >= 22:
                tx = r.text.strip().strip("—-  ")
                if len(tx) >= 3:
                    chunks.append(tx)
    if not chunks:
        return None
    return " ".join(chunks)


# 1) chỉ mục các file vừa dựng
built = {}
for bd in BUILD_DIRS:
    for f in glob.glob(os.path.join(SP, bd, "*.docx")):
        t = cover_title(f)
        if not t:
            continue
        key = norm(t)
        built.setdefault(key, f)          # gặp trùng: giữ cái đầu (nội dung như nhau)
print("Đã dựng lại:", len(built), "tiêu đề")

# 2) quét file đích, ghi đè nếu khớp
n_ok = 0
miss = []
for root in TARGET_ROOTS:
    if not os.path.isdir(root):
        continue
    for f in glob.glob(os.path.join(root, "**", "*.docx"), recursive=True):
        if os.path.basename(f).startswith("~$"):
            continue
        t = cover_title(f)
        if not t:
            continue
        key = norm(t)
        src = built.get(key)
        if src:
            shutil.copy2(src, f)
            n_ok += 1
        else:
            # chỉ báo miss cho file "tự biên soạn" (có dòng kiểm chứng bằng phần mềm)
            miss.append((t, f))
print("Đã ghi đè:", n_ok, "file")
if "-v" in sys.argv:
    seen = set()
    for t, f in miss:
        if norm(t) in seen:
            continue
        seen.add(norm(t))
        print("  chưa khớp:", t[:60], "|", os.path.relpath(f, r"D:\Tài liệu số"))
