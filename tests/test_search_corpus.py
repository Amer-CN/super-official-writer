#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检索脚本回归自测（CI 与本地共用）。

运行：python tests/test_search_corpus.py
断言：
  1. 语料可解析（条目数下限、必备字段）
  2. 领域查询能命中预期层文件
  3. 排序确定（同一查询两次结果一致）
  4. --layer 过滤生效
  5. 单次检索耗时在预算内（防止算法退化为全量重切）
  6. 无含义长串不产生噪声命中（二元组回退只对中文生效）
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import search_corpus as sc  # noqa: E402


def main():
    entries = sc.load_entries()
    assert len(entries) >= 1800, f"条目数异常：{len(entries)}（预期 ≥1800）"
    for e in entries[:5]:
        assert {"file", "line", "title", "body", "text"} <= set(e), "条目字段缺失"
        assert isinstance(e["line"], int) and e["line"] > 0

    # 1. 核稿/批复类应命中核稿病例层
    hits = sc.search("核稿 批复", entries, top=5)
    assert hits, "「核稿 批复」无命中"
    assert any(h["file"] == "book-hegao.md" for h in hits), \
        f"预期命中 book-hegao.md，实际：{[h['file'] for h in hits]}"

    # 2. 文种规则类应命中同一层（请示一文一事）
    hits2 = sc.search("请示 一文一事", entries, top=5)
    assert hits2 and any(h["file"] == "book-hegao.md" for h in hits2), \
        f"「请示 一文一事」未命中核稿层：{[h['file'] for h in hits2]}"

    # 3. 述职报告类非空
    hits3 = sc.search("述职报告 问题", entries, top=8)
    assert hits3, "「述职报告 问题」无命中"

    # 4. 结果必须带片段与命中词
    for h in hits3:
        assert h["snippet"], "片段为空"
        assert h["matches"], "命中词为空"

    # 5. 确定性：同一查询两次排序一致
    again = sc.search("核稿 批复", entries, top=5)
    assert [(h["file"], h["line"]) for h in hits] == [(h["file"], h["line"]) for h in again], "排序不确定"

    # 6. --layer 过滤
    only = sc.load_entries("hegao")
    assert only and all(e["file"] == "book-hegao.md" for e in only), "层过滤失效"

    # 7. 性能预算：4 次查询 < 5s（当前机器约 0.3s）
    t0 = time.time()
    for q in ("讲话稿 开场", "核稿 十查", "通知 正文", "调研报告 结构"):
        sc.search(q, entries, top=8)
    elapsed = time.time() - t0
    assert elapsed < 5.0, f"检索过慢：{elapsed:.2f}s"

    # 8. 无含义长串不产生噪声命中（二元组回退仅对中文生效）
    assert sc.search("zzzz_not_a_term", entries, top=3) == [], "无命中查询产生了噪声结果"

    print(f"PASS 检索自测：{len(entries)} 条 / 8 项断言 / 4 次查询 {elapsed:.2f}s")


if __name__ == "__main__":
    main()