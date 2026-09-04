#!/usr/bin/env python3
"""公文参数自检器（super-official-writer v0.7）

适配自 larashero3-dotcom/lieflat-gongwen 的 check_params.py（MIT License），
原脚本版权与"只判硬冲突"设计归原作者（lieflat、shiujan）所有。
本仓库仅做适配：参考值与 references/style-params.md 逐项一致，
报错文案改为指向本 skill 的文件，并保证 Windows python 可直接运行。

在本 skill 中的用法（第 5 步「收果子」成稿后运行）：
  python scripts/check_params.py 成稿.md --genre 调研报告   # 已知文种，逐项对照
  python scripts/check_params.py 成稿.md --genre 短经验材料
  python scripts/check_params.py 成稿.md --match            # 不确定文种，猜最像哪个
  python scripts/check_params.py --list                     # 列出支持的文体

设计原则：只判"硬冲突"（文种识别错误），其余仅作对照提示。
理由：真实公文的个体差异极大（如调研报告"一是二是"从 0 到 20 次都有），
      用均值当合格线会把好作品判成不合格。本脚本的参考值统一为
      中位数 + 四分位（p25-p75），与 references/style-params.md 完全一致。
      读报告只看两类信号：硬冲突（✗），以及连续多项参数同向偏离（节奏问题）。
"""
import argparse, json, re, sys
from pathlib import Path

# Windows 控制台默认 GBK，无法编码报告中的 ✓/✗/⚠/★ 等字符，统一转 UTF-8 输出
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# ── 语料中位数与常见区间（p25-p75），仅供对照，不作判定 ──
REF = {
    '调研报告':  dict(n=75, chars=(3108,3820,3492), sent=(45,59,53), h1=(3,3,3), h2=(0,11,9),
                  h3=(0,0,0), yishi=(0,12,9), dun=(19,26,22), qz=(0,2,1), yq=(18,31,26),
                  jy=(2,5,3), pct=(0,1,0)),
    '领导讲话':  dict(n=44, chars=(3100,4200,3700), sent=(48,64,56), h1=(3,3,3), h2=(3,9,5),
                  h3=(0,0,0), yishi=(2,8,5), dun=(18,27,21), qz=(1,3,2), yq=(35,55,45),
                  jy=(0,4,2), pct=(0,0,0)),
    '工作意见':  dict(n=25, chars=(2900,3800,3300), sent=(52,66,58), h1=(4,6,5), h2=(9,14,13),
                  h3=(0,0,0), yishi=(0,3,1), dun=(25,31,28), qz=(1,3,2), yq=(30,55,40),
                  jy=(0,2,1), pct=(0,1,0)),
    '经验材料':  dict(n=22, chars=(2900,4600,3600), sent=(50,63,56), h1=(2,3,2), h2=(0,4,2),
                  h3=(0,3,1), yishi=(2,9,6), dun=(14,23,19), qz=(0,3,1), yq=(12,30,20),
                  jy=(1,5,3), pct=(0,2,1)),
    '工作方案':  dict(n=10, chars=(2700,5000,3600), sent=(45,68,55), h1=(4,6,5), h2=(4,9,8),
                  h3=(5,17,11), yishi=(0,2,1), dun=(14,22,18), qz=(1,4,2), yq=(14,32,22),
                  jy=(3,10,6), pct=(0,1,0)),
    '经验总结':  dict(n=8,  chars=(2100,2700,2500), sent=(58,71,64), h1=(3,4,3), h2=(2,6,4),
                  h3=(0,0,0), yishi=(3,8,5), dun=(23,31,27), qz=(0,1,0), yq=(10,20,14),
                  jy=(0,1,0), pct=(0,0,0)),
    '短经验材料': dict(n=77, chars=(950,1300,1119), sent=(45,57,51), h1=(0,0,0), h2=(0,1,0),
                  h3=(0,0,0), yishi=(0,1,1), dun=(20,27,24), qz=(0,1,0), yq=(1,4,3),
                  jy=(0,1,0), pct=(0,1,0), paras=(5,7,6), para_len=(130,185,156), quote=(10,18,14),
                  quote_long=(1.8,4.0,2.9)),
}

# ── 硬冲突规则：违反即为文种识别错误，不是风格差异 ──
# (字段, 判据函数, 报错文案, 依据)
HARD = {
    '短经验材料': [
        ('h1', lambda v: v <= 1, '千字级经验材料不应用多个一级标题', '77篇语料共 3 个一级标题'),
        ('chars', lambda v: 700 <= v <= 2000, '短经验材料篇幅应在 700-2000 字', '语料区间 558-3022，中位 1119'),
    ],
    '经验总结': [
        ('pct', lambda v: v == 0, '经验总结不用百分比', '8篇语料 100% 零百分比'),
    ],
    '领导讲话': [
        ('h3', lambda v: v == 0, '领导讲话不用三级标题', '44篇语料三级标题总数为 0'),
    ],
    '工作意见': [
        ('h3', lambda v: v <= 2, '工作意见几乎不用三级标题', '25篇语料平均 0.1 个，最多 2 个'),
    ],
}

# 跨文体族硬约束（所有公文族文种共用）
GONGWEN = ['调研报告','领导讲话','工作意见','经验材料','工作方案','经验总结']
for g in GONGWEN:
    HARD.setdefault(g, []).append(
        ('chars', lambda v: v >= 1200, '公文族篇幅不应低于 1200 字（低于此值应按党建族写）',
         '公文语料最短 1423 字'))

# 软提示：偏离即提醒，但不判错（因真实作品存在合法变体）
SOFT = {
    '工作方案': [
        ('h3', lambda v: v >= 3, '工作方案通常有三级标题（"1."）',
         '语料平均 11.5 个，但 10 篇中 3 篇为 0（存在无三级标题的变体）'),
    ],
    '工作意见': [
        ('h2', lambda v: v >= 5, '工作意见通常有较多二级标题（"（一）"）',
         '语料平均 13.2 个，但存在把重点任务拆成多个平行一级标题的扁平变体'),
    ],
    '调研报告': [
        ('yishi', lambda v: v >= 3, '调研报告通常用"一是二是"做段内分层',
         '语料中位 9 次，但四分之一的作品完全不用'),
    ],
}

# ── 重心分布：最重一段占全篇的比例，p25-p75 与中位 ──
#
# 数据来源：lieflat-gongwen 对 188 篇可切分语料的**全量统计**（含至少两个一级标题者）。
#
# ⚠ 不要用抽样精读的区间做验收。抽样值与全量差异很大（经验材料抽样 47-59%，
# 全量实为 27-56%，中位 33）。用抽样值当合格线，真实公文的命中率很低。
#
# 因此本项**只作对照提示，不参与硬冲突判定**。个体离散度极大
# （调研报告最重一段从 17% 到 72% 都有），区间外不等于写错。
# 它的用途是提醒一种特定失误：该单段独大的文种写成了均衡分布，
# 或反之——此时通常伴随其他参数同向偏离，两者合看才有意义。
FOCUS = {
    '工作方案':  (37, 58, 46, '任务段较重'),
    '工作意见':  (24, 50, 42, '任务段较重'),
    '经验材料':  (27, 56, 33, '做法段较重'),
    '调研报告':  (35, 49, 41, '各功能段较均衡'),
    '经验总结':  (29, 42, 36, '各段近乎等重'),
    '领导讲话':  (33, 41, 36, '各段近乎等重'),
}

ID_PARAM = {
    '调研报告': '一是二是分层最密 + 建议词最多（向上级建言）',
    '领导讲话': '要求词密度最高 + 三级标题为 0',
    '工作意见': '二级标题最多（约13个）+ 几乎不用"一是"',
    '经验材料': '一级标题最少（约2个），靠段落推进',
    '工作方案': '三级标题最多（约11个），唯一大量用"1."的文种',
    '经验总结': '引号概念密度冠军 + 零百分比',
    '短经验材料': '零一级标题 + 长引号引语多（引群众原话）',
}

# 法定公文：结构由制度锁定，是固定填空而非写作技法，故不设参数行。
# 用 --genre 指定这些文种时给出解释，而不是只报"未知文体"。
NO_PARAM = ('报告', '通知', '请示', '批复', '函', '决定', '条例', '意见', '通报', '纪要')

BAD_WORDS = {
    '我觉得': '公文不用第一人称主观判断 → 研究认为/实践表明',
    '我认为': '公文不用第一人称主观判断 → 研究认为/实践表明',
    '非常': '空洞程度副词 → 用数据或事实替代',
    '取得了显著成效': '万能废话 → 说清具体成效',
    '希望领导重视': '太直白 → 用论证逻辑自然导向结论',
    '问题很多': '缺乏具体性 → 列举具体问题',
    '尽快': '模糊时限 → 明确到月/日',
    '相关部门': '模糊主体 → 明确牵头和配合单位',
}

# 固定提法白名单（评测 P1-4）：标准提法中的力度字样（如"三管三必须"的 3 个"必须"）
# 属不可改写的固定表述，统计前整句剔除，避免计入强制词配额诱导改稿破坏提法。
# 扩充方式：往列表追加短语即可，统计端自动生效。
FIXED_PHRASES = [
    '管行业必须管安全、管业务必须管安全、管生产经营必须管安全',
]


def analyze(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    body_lines = []
    for l in lines:
        if re.match(r'^#{1,6}\s', l):
            body_lines.append(re.sub(r'^#{1,6}\s*', '', l))
        elif re.match(r'^(\||-{3,}|>)', l):
            continue
        else:
            body_lines.append(l)
    body = '\n'.join(body_lines)
    plain = re.sub(r'\*\*|__|`', '', body)
    chars = len(plain.replace('\n', ''))
    if chars == 0:
        return None

    sents = [s for s in re.split(r'[。！？；]', plain) if len(s.strip()) >= 4]
    paras = [l for l in body_lines if len(l) > 40
             and not re.match(r'^[一二三四五六七八九十]+、|^（[一二三四五六七八九十]+）|^\d+[．.]', l)]

    h1 = []
    for m in re.finditer(r'^\**([一二三四五六七八九十]+、)([^\n]{2,80})', body, re.M):
        t = re.split(r'[。！？；]', m.group(2))[0]
        t = re.split(r'　{2,}|\s{3,}', t)[0]
        h1.append(t.strip()[:40])

    # 力度词统计前先剔除引号内内容。
    # 理由：自造概念常带力度字样（如需求分类"必须改""可以缓"），
    # 计入后会顶破配额。经验总结强制词配额仅 0-1，任何误判都致命。
    depunct = re.sub(r'[“"][^”"]{0,20}[”"]', '', plain)
    # 固定提法白名单：标准提法（"三管三必须"等）内的力度词不计入任何配额
    for _ph in FIXED_PHRASES:
        depunct = depunct.replace(_ph, '□' * len(_ph))
    # "不得不"是"只能"义，不是禁止义，需从"不得"中排除
    qz_text = depunct.replace('不得不', '＃＃＃')

    return dict(
        chars=chars,
        sent=round(sum(len(s) for s in sents)/len(sents), 1) if sents else 0,
        h1=len(h1), h1_titles=h1,
        h2=len(re.findall(r'^\**（[一二三四五六七八九十]+）', body, re.M)),
        h3=len(re.findall(r'^\**\d+[．.]\s*\D', body, re.M)),
        yishi=len(re.findall(r'[一二三四五六七八九]是[，、]?', plain)),
        dun=round(1000*plain.count('、')/chars, 1),
        qz=sum(qz_text.count(w) for w in ['应当','必须','不得','严禁']),
        yq=sum(depunct.count(w) for w in ['要','切实','确保','务必']),
        # 建议词只计建言档（建议/可以）；倡议档（鼓励/支持/倡导）单独计 chang，
        # 不占建议词配额（评测 P1-3：照旧计入会把改稿引向删除正当的"鼓励"表述）
        jy=sum(depunct.count(w) for w in ['建议','可以']),
        chang=sum(depunct.count(w) for w in ['鼓励','支持','倡导']),
        # 占位符内的 % 不是真实数据（如【待补：xx%】），先剔除
        pct=len(re.findall(r'\d+(?:\.\d+)?%',
                           re.sub(r'【[^】]*】', '', plain))),
        quote=len(re.findall(r'[“"][^”"]{1,8}[”"]', plain)),
        # 长引号引语：党建族引群众原话，中位 2.9‰，是它的正向指纹。
        # 公文族语料无此字段，实测值高仍能把党建族拉近、把公文族推远，保留有效。
        # 仅统计中文弯引号——ASCII 直角引号无法配对，会把相邻两个引号
        # 之间的正文误判为引语。
        quote_long=round(1000*len(re.findall(r'[“][^”]{9,}[”]', plain))/chars, 1),
        paras=len(paras),
        para_len=round(sum(len(p) for p in paras)/len(paras)) if paras else 0,
        ascii_quote=plain.count('"'),
        dash=plain.count('——'),
        sections=section_weights(body_lines),
        plain=plain,
    )


def section_weights(body_lines):
    """按一级标题切分，返回各段字数占比。

    自检器原先只查参数不查重心分布，而重心分布恰是区分
    「单段独大型」与「均衡型」的关键——参数可以全部达标而文种写错。
    """
    secs, cur = [], ['导语', 0]
    for l in body_lines:
        if re.match(r'^\**[一二三四五六七八九十]+、', l):
            secs.append(cur)
            cur = [re.sub(r'^\**', '', l)[:16], 0]
        cur[1] += len(l)
    secs.append(cur)
    tot = sum(n for _, n in secs) or 1
    return [(name, n, round(100 * n / tot, 1)) for name, n in secs]


def match_genre(a):
    """算参数向量与各文种中位数的归一化距离，返回排序结果

    quote_long 保留在 KEYS 里：它只定义在党建族一行，公文族各文种没有
    这个字段而被跳过，因此实测长引语高会拉近党建族、拉远公文族。
    """
    KEYS = ['chars','sent','h1','h2','h3','yishi','dun','qz','yq','jy','pct',
            'quote_long']
    out = []
    for g, r in REF.items():
        d, cnt = 0.0, 0
        for k in KEYS:
            if k not in r: continue
            lo, hi, mid = r[k]
            scale = max(hi - lo, abs(mid) * 0.3, 1)
            d += abs(a[k] - mid) / scale
            cnt += 1
        out.append((g, d / cnt))
    return sorted(out, key=lambda x: x[1])


def bar(val, lo, hi):
    """在 p25-p75 区间中的位置示意"""
    if hi <= lo:
        return '│' if val == lo else ('←' if val < lo else '→')
    span = hi - lo
    pos = (val - lo) / span
    if pos < -0.15: return '←低'
    if pos > 1.15:  return '高→'
    slot = max(0, min(9, int(pos * 9)))
    return '·' * slot + '●' + '·' * (9 - slot)


def report(a, genre):
    r, hard = REF[genre], HARD.get(genre, [])
    print(f'\n{"="*76}')
    print(f'  文体：{genre}   语料样本 n={r["n"]}')
    print(f'  身份证参数：{ID_PARAM[genre]}')
    print(f'{"="*76}\n')

    # ① 硬冲突
    fails = []
    for key, ok_fn, msg, basis in hard:
        if not ok_fn(a[key]):
            fails.append((key, a[key], msg, basis))
    print('【硬冲突检查】判文种识别错误，非风格差异')
    print('-'*76)
    if not fails:
        print(f'✓ 通过（{len(hard)} 项）')
    else:
        for key, val, msg, basis in fails:
            print(f'✗ {msg}')
            print(f'   实测 {key}={val}   依据：{basis}')

    # 软提示
    softs = [(k, a[k], m, b) for k, fn, m, b in SOFT.get(genre, []) if not fn(a[k])]
    if softs:
        print()
        for key, val, msg, basis in softs:
            print(f'⚠ {msg}')
            print(f'   实测 {key}={val}   {basis}')
    print()

    # ② 对照表
    print('【参数对照】仅供参考，偏离不等于错误')
    print('-'*76)
    LABEL = {'chars':'字数','sent':'平均句长','h1':'一级标题','h2':'二级标题','h3':'三级标题',
             'yishi':'"一是二是"','dun':'顿号密度‰','qz':'强制词','yq':'要求词','jy':'建议词',
             'pct':'百分比','paras':'段落数','para_len':'段落长度','quote':'引号概念',
             'quote_long':'长引语‰'}
    print(f'{"指标":<12}{"你的":>8}{"中位":>8}{"常见区间":>12}   位置')
    for k, label in LABEL.items():
        if k not in r: continue
        lo, hi, mid = r[k]
        v = a[k]
        flag = '' if lo <= v <= hi else '  ⚠偏离'
        print(f'{label:<12}{v:>8}{mid:>8}{f"{lo}-{hi}":>12}   {bar(v,lo,hi)}{flag}')
    # 倡议词单独计档（评测 P1-3）：不占建议词配额；暂无语料区间，仅报数值
    print(f'{"倡议词":<12}{a["chang"]:>8}{"—":>8}{"—":>12}   （鼓励/支持/倡导，不计入建议词）')

    # ②b 标点修辞检查
    dash_issues = []
    if a['dash'] > 1:
        dash_issues.append(f'正文破折号 {a["dash"]} 个（语料平均 0.2-0.9 个/篇，建议不超过 1 个）')
    # 非引语冒号（【待补：…】占位内的冒号是待填标记，先剔除再检测——评测 P1-5）
    non_quote_colons = []
    plain_noph = re.sub(r'【[^】]*】', '', a['plain'])
    for cm in re.finditer(r'([^\n]{0,12})：', plain_noph):
        before = cm.group(1).strip()
        if re.search(r'[一二三四五六七八九十]+、|（[一二三四五六七八九十]）|\d+[．.]', before):
            continue
        if re.search(r'说|问|讲|提|指出|反映|回忆|告诉|表示|答', before):
            continue
        if re.search(r'人民政府|部门|单位|书记|镇长|同志|负责人', before):
            continue
        if '待补' in before or '待核' in before:
            continue
        non_quote_colons.append(cm.group(0)[:25])
    if non_quote_colons:
        dash_issues.append(f'非引语冒号 {len(non_quote_colons)} 处（冒号应只用于引语引入、主送机关、层次标题）')
    # 元评论词（排除引号内——引语里的口语保留）
    depunct_meta = re.sub(r'[“][^”]*[”]', '', a['plain'])
    meta_words = re.findall(r'其实[是就]|说到底|归根到底|本质上', depunct_meta)
    if meta_words:
        dash_issues.append(f'元评论词 {len(meta_words)} 处（{", ".join(set(meta_words))}）')
    if dash_issues:
        print('\n【标点修辞检查】')
        print('-'*76)
        for di in dash_issues:
            print(f'⚠ {di}')
    elif a['dash'] <= 1:
        pass  # 不额外打印通过信息，保持报告简洁

    # ③ 一级标题字数
    if a['h1_titles']:
        avg = sum(len(t) for t in a['h1_titles'])/len(a['h1_titles'])
        biz = genre in ('工作意见','工作方案')
        tgt = '4-12（业务类）' if biz else '14-24（分析类）'
        print(f'\n一级标题平均 {avg:.1f} 字，目标 {tgt}')
        for t in a['h1_titles'][:6]:
            print(f'   · {t}')

    # ③b 重心分布：参数表测不到这一项，但它单独不足以判错（见 FOCUS 注释）
    if genre in FOCUS and len(a['sections']) > 1:
        lo, hi, mid, note = FOCUS[genre]
        body = [s for s in a['sections'] if s[0] != '导语']
        top = max(body, key=lambda s: s[2]) if body else None
        print(f'\n【重心分布】仅供对照，偏离不等于错误')
        print('-'*76)
        for name, n, pct in a['sections']:
            mark = ' ←最重' if top and name == top[0] else ''
            print(f'{pct:>6.1f}%  {n:>5}字  {name}{mark}')
        if top:
            print(f'最重一段 {top[2]}%　语料中位 {mid}%，常见 {lo}-{hi}%（{note}）')
            if top[2] < lo or top[2] > hi:
                print(f'   个体离散度大，此项区间外不作为错误；'
                      f'若同时有多项参数同向偏离，再考虑整体节奏问题。')

    # ③c 引号书写提示：ASCII 直角引号无法配对，会令引号三项统计失真
    if a['ascii_quote']:
        print(f'\n⚠ 检出 {a["ascii_quote"]} 个 ASCII 直角引号(")。'
              f'语料使用中文弯引号，混用会使引号概念与长引语统计失真')

    # ④ 文种匹配度（仅在跨文体族误配、或差距显著时提示）
    m = match_genre(a)
    rank = [g for g, _ in m]
    FAMILY = {'短经验材料': '党建族'}
    fam_self = FAMILY.get(genre, '公文族')
    fam_top = FAMILY.get(rank[0], '公文族')

    if fam_self != fam_top:
        # 跨文体族误配：两族在篇幅和一级标题上不重叠，这个信号强。
        print(f'\n【文体族检查】')
        print('-'*76)
        print(f'⚠ 你声明「{genre}」（{fam_self}），但参数上更像「{rank[0]}」（{fam_top}）')
        print(f'   两族参数互斥，判错族后所有参数都会偏。距离：'
              + '  '.join(f'{g} {d:.2f}' for g, d in m[:3]))
    elif genre in rank[3:]:
        # 同族内排名靠后才提示——同族文种参数重叠严重，Top1 准确率有限
        print(f'\n【结构习惯提示】')
        print('-'*76)
        print(f'ⓘ 参数上「{genre}」排在第 {rank.index(genre)+1} 位，前三位是 '
              + '、'.join(rank[:3]))
        print('   同族文种参数重叠大，此信号仅供参考，不代表文种判错。')

    # ⑤ 避坑词
    hits = [(w, why) for w, why in BAD_WORDS.items() if w in a['plain']]
    if hits:
        print(f'\n【避坑词】')
        print('-'*76)
        for w, why in hits:
            print(f'⚠ "{w}" — {why}')

    # ⑥ 力度词配额提示：改稿时最易踩的坑
    if 'qz' in r and a['qz'] > r['qz'][1]:
        print(f'\n⚠ 强制词超配额（{a["qz"]} > {r["qz"][1]}）。'
              f'"要"属要求词、"必须/应当"属强制词，两者配额独立且相差一个量级，'
              f'\n   改稿时把"要"整批替换成"必须"会直接顶破上限。')

    print()
    return len(fails)


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('file', nargs='?')
    ap.add_argument('--genre', '-g')
    ap.add_argument('--match', action='store_true')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('-h', '--help', action='store_true')
    args = ap.parse_args()

    if args.help or (not args.file and not args.list):
        print(__doc__); sys.exit(0)
    if args.list:
        print('支持的文体（参数与 references/style-params.md 同源）：')
        for k, v in ID_PARAM.items():
            print(f'  {k:<10} n={REF[k]["n"]:<4} {v}')
        sys.exit(0)

    try:
        raw = Path(args.file).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f'找不到文件：{args.file}', file=sys.stderr); sys.exit(2)
    except IsADirectoryError:
        print(f'这是一个目录，不是文件：{args.file}', file=sys.stderr); sys.exit(2)
    except UnicodeDecodeError:
        print(f'无法按 UTF-8 读取（请确认是文本文件）：{args.file}', file=sys.stderr); sys.exit(2)
    except OSError as e:
        print(f'读取失败：{args.file}（{e.strerror}）', file=sys.stderr); sys.exit(2)

    a = analyze(raw)
    if not a:
        print('文件为空或无法解析', file=sys.stderr); sys.exit(2)

    if args.match or not args.genre:
        print(f'\n{args.file} 参数向量匹配结果：\n')
        for i, (g, d) in enumerate(match_genre(a)):
            print(f'{"★" if i==0 else " "} {g:<10} 距离 {d:.2f}')
        print(f'\n实测：{a["chars"]}字 句长{a["sent"]} 一级{a["h1"]} 二级{a["h2"]} '
              f'三级{a["h3"]} 一是{a["yishi"]} 顿号{a["dun"]}‰ 引号{a["quote"]} '
              f'长引语{a["quote_long"]}‰')
        body = [s for s in a['sections'] if s[0] != '导语']
        if body:
            top = max(body, key=lambda s: s[2])
            print(f'重心：最重一段 {top[2]}%（{top[0]}）'
                  f'　各文种语料中位 33-46%\n')
        else:
            print()
        sys.exit(0)

    if args.genre not in REF:
        print(f'未知文体：{args.genre}', file=sys.stderr)
        print(f'可选：{"、".join(REF)}', file=sys.stderr)
        if args.genre in NO_PARAM:
            print(f'\n说明：{args.genre}属法定公文，本脚本不为其设参数行——'
                  f'其正文结构由制度锁定，是固定填空而非写作技法，统计参数没有意义。',
                  file=sys.stderr)
            print(f'法定公文版式要素（发文字号、主送机关、成文日期、公开标识）'
                  f'请对照 references/format-spec.md（GB/T 9704-2012）；'
                  f'文种框架见 references/templates.md；'
                  f'用 --match 可查它是否落在公文族内。', file=sys.stderr)
        sys.exit(2)

    fails = report(a, args.genre)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
