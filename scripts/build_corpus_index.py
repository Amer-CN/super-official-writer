#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 references/corpus/INDEX.md：蒸馏知识库按知识分类的条目索引。

读 lingyun 数据集的 category 字段，按分类分组（条目数降序），
每条一行：id｜title｜定位文件。重建命令：python scripts/build_corpus_index.py
"""

import json
from collections import OrderedDict
from pathlib import Path

DATASET = Path('F:/AIXM/XZ/lingyun/dataset/gongwen_writing_dataset.jsonl')
OUT = Path(__file__).resolve().parent.parent / 'references' / 'corpus' / 'INDEX.md'

# id 前缀 → 分层文件（书1/书2/书1补遗 shu1 = 文种规范层 B 系列；书3/书3补遗 shu3 = 核稿病例层 C 系列）
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


if __name__ == '__main__':
    main()
