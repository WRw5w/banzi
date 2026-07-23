#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并 板子.pdf 和 错题本_v2.pdf 为 合订本.pdf
"""
import fitz  # PyMuPDF
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

banzi_pdf   = os.path.join(base_dir, "banzi",  "板子.pdf")
cuoti_pdf   = os.path.join(base_dir, "错题本", "错题本_v2.pdf")
output_pdf  = os.path.join(base_dir, "合订本.pdf")

print(f"[1/3] 读取 {banzi_pdf}")
doc1 = fitz.open(banzi_pdf)
print(f"      共 {len(doc1)} 页")

print(f"[2/3] 读取 {cuoti_pdf}")
doc2 = fitz.open(cuoti_pdf)
print(f"      共 {len(doc2)} 页")

print(f"[3/3] 合并并写出 {output_pdf}")
doc1.insert_pdf(doc2)
doc1.save(output_pdf, garbage=4, deflate=True)
doc1.close()
doc2.close()

size_kb = os.path.getsize(output_pdf) / 1024
print(f"\n[OK] 合订本.pdf 生成成功，共 {len(fitz.open(output_pdf))} 页，大小 {size_kb:.1f} KB")
