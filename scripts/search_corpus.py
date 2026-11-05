#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""search_corpus.py — 分层知识库的排序检索（零第三方依赖）。

为什么有它：1855 条知识按 28 个层文件存放，原检索方式是「读 INDEX.md 找分类 →
grep 层文件」，能命中字面但不会排序，长尾问题容易漏。本脚本对条目做轻量 TF-IDF
排序，让 Step2 磨刀子 / Step4 敲键子 直接拿到最相关的前 N 条。

用法：
    python scripts/search_corpus.py "述职报告 问题"
    python scripts/search_corpus.py "核稿 批复" --top 5
    python scripts/search_corpus.py "讲话稿 开场" --layer blogger --top 10
    python scripts/search_corpus.py "请示 一文一事" --json
    python scripts/search_corpus.py --stats

设计：
- 中文不切词：查询按空白/标点切成 ≥2 字片段，用「子串计数」当词频；跨条目统计
  文档频率得 IDF；标题命中加权。长片段（>8 字）若整词零命中，自动拆二元组回退。
- 只认 references/corpus/*.md 里以 "- **标题**：正文" 开头的条目（INDEX.md 跳过）。
- 输出：相关度、层文件:行号、标题、命中词、上下文片段；--json 供程序调用。
"""
import argparse
import json
import math
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = ROOT / "references" / "corpus"

_SPLIT_RE = re.compile(r"[\s,，。、；;：:!?！？（）()《》〈〉【】\[\]\"'“”‘’\-—…·/\\|]+")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_K1 = 1.2          # TF 饱和参数
_TITLE_BOOST = 1.8  # 标题命中的权重倍率


def load_entries(layer_filter=None):
    """读取 corpus 分层文件里的知识条目。"""
    entries = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        if layer_filter and layer_filter.lower() not in path.name.lower():
            continue
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            if not line.startswith("- **"):
                continue
            end = line.find("**", 4)
            if end == -1:
                continue
            title = line[4:end].strip()
            body = line[end + 2:].lstrip("：: ").strip()
            if not title:
                continue
            entries.append({
                "file": path.name,
                "line": lineno,
                "title": title,
                "body": body,
                "text": (title + "。" + body).lower(),
            })
    return entries


def query_terms(query):
    """查询切分：空白/标点分段，丢掉单字噪声。"""
    segs = [s.strip().lower() for s in _SPLIT_RE.split(query)]
    return list(dict.fromkeys(s for s in segs if len(s) >= 2))


def _expand_terms(terms, entries):
    """整词零命中且较长时，拆成二元组回退；返回 (terms, df)。"""
    df = {}
    expanded = []
    for t in terms:
        if t not in df:
            df[t] = sum(1 for e in entries if t in e["text"])
        if df[t] == 0 and len(t) >= 4 and _CJK_RE.search(t):
            for i in range(len(t) - 1):
                g = t[i:i + 2]
                if g not in df:
                    df[g] = sum(1 for e in entries if g in e["text"])
                expanded.append(g)
        else:
            expanded.append(t)
    return list(dict.fromkeys(expanded)), df


def _snippet(body, terms, idf, width=70):
    """取命中词附近的一小段上下文。"""
    low = body.lower()
    best = None
    for t in terms:
        pos = low.find(t)
        if pos == -1:
            continue
        if best is None or idf.get(t, 0) > best[1]:
            best = (pos, idf.get(t, 0), t)
    if best is None:
        head = body[: width * 2].replace("\n", " ")
        return head + ("…" if len(body) > width * 2 else "")
    pos, _, term = best
    start = max(0, pos - width)
    end = min(len(body), pos + len(term) + width)
    return ("…" if start > 0 else "") + body[start:end].replace("\n", " ") + ("…" if end < len(body) else "")


def search(query, entries, top=8, min_score=0.0):
    """返回按相关度降序的命中条目列表。"""
    terms = query_terms(query)
    if not terms:
        return []
    terms, df = _expand_terms(terms, entries)
    n = len(entries)
    idf = {t: math.log((n + 1) / (df.get(t, 0) + 0.5)) + 1.0 for t in terms}

    hits = []
    for e in entries:
        score = 0.0
        present = 0
        matches = {}
        title_low = e["title"].lower()
        for t in terms:
            tf = e["text"].count(t)
            if not tf:
                continue
            present += 1
            matches[t] = tf
            score += tf / (tf + _K1) * idf[t] * (_TITLE_BOOST if t in title_low else 1.0)
        if score <= 0:
            continue
        score *= 0.6 + 0.4 * (present / len(terms))
        if score < min_score:
            continue
        hits.append({
            "score": round(score, 4),
            "file": e["file"],
            "line": e["line"],
            "title": e["title"],
            "matches": matches,
            "snippet": _snippet(e["body"], terms, idf),
        })

    hits.sort(key=lambda h: (-h["score"], h["file"], h["line"]))
    return hits[:top]


def _stats(entries):
    by_file = {}
    for e in entries:
        by_file[e["file"]] = by_file.get(e["file"], 0) + 1
    total_chars = sum(len(e["text"]) for e in entries)
    print(f"知识库：{len(by_file)} 层 / {len(entries)} 条 / 约 {total_chars / 10000:.0f} 万字符")
    for name, cnt in sorted(by_file.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {cnt:4d} 条  {name}")


def main():
    parser = argparse.ArgumentParser(
        description="分层知识库排序检索（TF-IDF，零依赖）",
        epilog="示例：python scripts/search_corpus.py \"核稿 批复\" --top 5",
    )
    parser.add_argument("query", nargs="*", help="检索词，空格分隔多个词")
    parser.add_argument("--top", type=int, default=8, help="返回条数（默认 8）")
    parser.add_argument("--layer", default=None, help="只搜文件名包含该串的层（如 hegao / blogger）")
    parser.add_argument("--min-score", type=float, default=0.0, help="最低相关度")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--stats", action="store_true", help="只显示知识库统计")
    args = parser.parse_args()

    entries = load_entries(args.layer)
    if not entries:
        print("错误：没有匹配的条目（检查 --layer）", file=sys.stderr)
        return 2

    if args.stats:
        _stats(entries)
        return 0

    query = " ".join(args.query).strip()
    if not query:
        parser.print_help()
        return 2

    t0 = time.time()
    hits = search(query, entries, top=args.top, min_score=args.min_score)
    took_ms = (time.time() - t0) * 1000

    if args.json:
        print(json.dumps({
            "query": query,
            "total_entries": len(entries),
            "hits": len(hits),
            "took_ms": round(took_ms, 1),
            "results": hits,
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"检索「{query}」：{len(hits)} 条命中 / 共 {len(entries)} 条（{took_ms:.0f} ms）")
    for i, h in enumerate(hits, 1):
        m = " ".join(f"{t}×{c}" for t, c in h["matches"].items())
        print(f"\n{i}. {h['score']:.2f}  {h['file']}:{h['line']}")
        print(f"   {h['title']}")
        print(f"   命中：{m}")
        print(f"   {h['snippet']}")
    if not hits:
        print("（无命中：换个更短的关键词，或用 --layer 缩小范围）")
    return 0


if __name__ == "__main__":
    sys.exit(main())