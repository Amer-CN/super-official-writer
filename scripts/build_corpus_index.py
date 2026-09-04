#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 references/corpus/INDEX.md：蒸馏知识库按知识分类的条目索引。

读 lingyun 数据集的 category 字段，按分类分组（条目数降序），
每条一行：id｜title｜定位文件。重建命令：python scripts/build_corpus_index.py
"""

import json
import re
from collections import OrderedDict
from pathlib import Path

DATASET = Path('F:/AIXM/XZ/lingyun/dataset/gongwen_writing_dataset.jsonl')
OUT = Path(__file__).resolve().parent.parent / 'references' / 'corpus' / 'INDEX.md'

# ---------- 数字承诺一致性抽检（WARN，不阻断） ----------
# 标题承诺"两套路/三大框架/123/五步/六式"等 N 点，正文可提取要点数不足时输出 WARN 列表。
_PROMISE_RE = re.compile(
    r'([一二两三四五六七八九十])\s*(?:大)?\s*'
    r'(套路|套|框架|招|式|步|法|条|字|诀|心|点|维|看|言|板|把|重|精|用|变|化|新|棋|部曲|讲|忌|戒|铁律|金句|组|层|问|题|遍|密码|功夫|维度|连招)')
_RUN_RE = re.compile(r'["“](\d+)["”]')  # 引号内连号，如 "123"
_DIGIT_RE = re.compile(r'(\d+)\s*(?:个|条|招|式|步|句|组|张|项|大|法|字|点)')
_NUM = {'一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
        '七': 7, '八': 8, '九': 9, '十': 10}
_RUN_123 = re.compile(r'1(?:2(?:3(?:4(?:5(?:6(?:7(?:8(?:9)?)?)?)?)?)?)?)?')


def parse_promise(title):
    """标题中的数字承诺 → 期望要点数；无承诺返回 None。"""
    m = _RUN_RE.search(title)
    if m and _RUN_123.fullmatch(m.group(1)):
        return len(m.group(1))
    m = _PROMISE_RE.search(title)
    if m:
        return _NUM.get(m.group(1))
    m = _DIGIT_RE.search(title)
    if m:
        return int(m.group(1))
    return None


def count_points(text):
    """正文可提取要点数：多种序号口径各数一遍，取最大值。"""
    strategies = [
        len(re.findall(r'[①②③④⑤⑥⑦⑧⑨⑩]', text)),
        len(set(re.findall(r'(?<![\d.])([1-9]\d?)\)', text))),
        len(re.findall(r'[一二两三四五六七八九十]是', text)),
        len(re.findall(r'[一二两三四五六七八九十][个、]', text)),
        len(re.findall(r'第[一二两三四五六七八九十][个，,、]', text)),
    ]
    return max(strategies) if strategies else 0


def numeric_promise_check(entries):
    """抽检返回 WARN 行列表（只提示，不阻断生成）。"""
    warns = []
    for e in entries:
        expected = parse_promise(e['title'])
        if expected is None:
            continue
        actual = count_points(e.get('content', ''))
        if actual < expected:
            warns.append(
                f"- WARN {e['id'].strip()}｜{e['title'].strip()}｜标题承诺 {expected} 点，正文仅可提取 {actual} 点")
    return warns

# id 前缀 → 分层文件（书1/书2/书1补遗 shu1 = 文种规范层 B 系列；书3/书3补遗 shu3 = 核稿病例层 C 系列；
# domain = 领域素材层，v0.12 新增；chengwen-fanli 成稿范例不入 dataset，无 id 映射需求）
PREFIX_TO_FILE = {
    'lingyun': 'lingyun-huishui.md',
    'huishui': 'lingyun-huishui.md',
    'book1': 'book-wenzhong.md',
    'book2': 'book-wenzhong.md',
    'shu1': 'book-wenzhong.md',
    'book3': 'book-hegao.md',
    'shu3': 'book-hegao.md',
    'shouji2': 'book-shouji2.md',
    'fanben': 'book-fuchuan.md',
    'sgzbg': 'gongzuobaogao.md',
    'zhuodaoren': 'blogger-zhuodaoren.md',
    'gongwenbaidu': 'blogger-gongwenbaidu.md',
    'gaigaoshi': 'blogger-gaigaoshi.md',
    'dayu': 'blogger-dayu.md',
    'wenxiong': 'blogger-wenxiong.md',
    'domain': 'domains.md',
    'tiaoli': 'chengwen-fanli.md',
}


def clean_category(cat):
    """数据集有 27 条 gongwenbaidu 条目的 category 字段为「正文片段 → 真实分类」，取最后一个「→」之后的真实分类。"""
    if '\u2192' in cat:
        return cat.rsplit('\u2192', 1)[1].strip()
    return cat.strip()


def main():
    entries = []
    with open(DATASET, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    warns = numeric_promise_check(entries)

    groups = OrderedDict()
    for e in entries:
        groups.setdefault(clean_category(e['category']), []).append(e)

    out = []
    out.append('# 蒸馏知识库·知识分类索引（自动生成）')
    out.append('')
    out.append('> 自动生成，勿手改；重建命令：`python scripts/build_corpus_index.py`')
    out.append('> 数据源：lingyun/dataset/gongwen_writing_dataset.jsonl'
              f'（{len(entries)} 条，{len(groups)} 类）；条目正文位于 references/corpus/ 分层文件。')
    out.append('> 检索用法（两级）：先在本索引按分类定位条目与层文件 → 再 grep 对应层文件取条目全文。')

    for cat, group in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        out.append('')
        out.append(f'## {cat}（{len(group)} 条）')
        out.append('')
        for e in group:
            out.append(f"- {e['id'].strip()}｜{e['title'].strip()}｜{PREFIX_TO_FILE[e['id'].split('_', 1)[0]]}")

    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print(f'written: {OUT} ({len(entries)} entries, {len(groups)} categories)')

    # 数字承诺一致性抽检：输出 WARN 列表（仅提示，不阻断）
    if warns:
        print(f'WARN 数字承诺一致性抽检：{len(warns)} 条标题承诺与正文可提取要点数不符：')
        for w in warns:
            print(w)
    else:
        print('WARN 数字承诺一致性抽检：无')


if __name__ == '__main__':
    main()
