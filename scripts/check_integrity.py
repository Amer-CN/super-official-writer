#!/usr/bin/env python3
"""check_integrity.py — 仓库完整性自动化断言（治理门禁）

背景：计数漂移与口径失真在本项目已反复发生（190/897、README 897×4、dataset 958→961→965、
文兄 207/208/209），按"同类违规第三次出现即设确定性门禁"原则建立本脚本。
每次版本收尾/推送前跑一遍；CI 化留给将来。

用法：
    python scripts/check_integrity.py            # 逐条输出 PASS/FAIL
    python scripts/check_integrity.py --quiet    # 只看 exit code（0=全过，1=有 FAIL）

断言清单：
  1. 版本三处一致（SKILL 锚点 / CHANGELOG 最新条 / README 徽章）
  2. dataset jsonl：id 唯一；条数 == dataset/README.md 合计行
  3. SKILL 七·二计数行自洽（分段和 + 5 篇纯范例 == 合计）
  4. INDEX.md 重生成零 diff（防手改/漂移）
  5. 终检门回归：run3/run4 存档成稿 --final 全 PASS
  6. run4 盲卷身份零泄漏（防串通证据不被污染）
  7. corpus-lingyun.md 索引页计数抽查 == 层文件实数（主层/文兄/领域）
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINGYUN = Path("F:/AIXM/XZ/lingyun")
DS = LINGYUN / "dataset" / "gongwen_writing_dataset.jsonl"
FAILS = []


def check(name, ok, detail=""):
    tag = "PASS" if ok else "FAIL"
    line = f"{tag}  {name}"
    if detail:
        line += f"  — {detail}"
    print(line)
    if not ok:
        FAILS.append(name)


def main():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # 1. 版本三处一致
    anchor = re.search(r"<!--\s*skill-version:\s*(v[\d.]+)\s*-->", skill)
    cl = re.search(r"^## (v[\d.]+)", changelog, re.M)
    badge = re.search(r"Version-(v[\d.]+)-", readme)
    ok = bool(anchor and cl and badge and anchor.group(1) == cl.group(1) == badge.group(1))
    detail = f"{anchor.group(1) if anchor else '?'}/{cl.group(1) if cl else '?'}/{badge.group(1) if badge else '?'}"
    check("版本三处一致（锚点/CHANGELOG/README 徽章）", ok, detail)

    # 2. dataset 唯一 id + 计数对账
    lines = [l for l in DS.read_text(encoding="utf-8").splitlines() if l.strip()]
    ids = [json.loads(l)["id"] for l in lines]
    check("dataset id 唯一", len(ids) == len(set(ids)), f"{len(ids)} 行 / {len(set(ids))} 唯一")
    ds_readme = (DS.parent / "README.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*合计\*\*\s*\|\s*\*\*(\d+)\*\*", ds_readme)
    ok = bool(m) and len(ids) == int(m.group(1))
    check("dataset 条数 == dataset/README 合计", ok, f"jsonl={len(ids)} vs README={m.group(1) if m else '?'}")

    # 3. SKILL 七·二计数行自洽
    m = re.search(r"凌云笔杆子\+惠水组工 (\d+) 条[\s\S]*?合计 (\d+) 条蒸馏知识库", skill)
    if m:
        head = skill[m.start():m.end()].split("合计")[0]
        seg = [int(x) for x in re.findall(r"(\d+) 条", head)]
        declared = int(m.group(2))
        check("SKILL 计数行自洽（分段和+5 纯范例=合计）", sum(seg) + 5 == declared,
              f"{seg}+5={sum(seg)+5} vs 合计 {declared}")
    else:
        check("SKILL 计数行自洽", False, "计数行模式未匹配（行文可能已变，请同步本断言）")

    # 4. INDEX 重生成零 diff
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_corpus_index.py")],
                   capture_output=True)
    st = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain",
                         "references/corpus/INDEX.md"], capture_output=True, text=True).stdout.strip()
    check("INDEX 重生成零 diff", st == "", st[:100] if st else "")
    if st:
        subprocess.run(["git", "-C", str(ROOT), "checkout", "--", "references/corpus/INDEX.md"])

    # 5. 终检门回归：run3/run4 存档成稿 --final 全 PASS
    drafts = sorted((LINGYUN / "evaluation" / "run3").glob("case*.md"))
    drafts += sorted((LINGYUN / "evaluation" / "run4").glob("case-*.md"))
    npass = 0
    bad = []
    for d in drafts:
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_params.py"),
                            str(d), "--final"], capture_output=True)
        if r.returncode == 0:
            npass += 1
        else:
            bad.append(d.name)
    check(f"终检门回归（存档成稿 {npass}/{len(drafts)} PASS）", npass == len(drafts) and drafts,
          "FAIL: " + ",".join(bad) if bad else "")

    # 6. run4 盲卷身份零泄漏
    leak = []
    for f in sorted((LINGYUN / "evaluation" / "run4" / "blind").glob("*.md")):
        t = f.read_text(encoding="utf-8").lower()
        for kw in ["executor", "glm", "主窗口", "kimi", "deepseek", "qwen", "omen", "advisor"]:
            if kw in t:
                leak.append(f"{f.name}:{kw}")
    check("run4 盲卷身份零泄漏", not leak, ",".join(leak))

    # 8. README 散文中的 jsonl 条数 == dataset 实数（历史版本行用"条/48 类"句式，不会误伤）
    jsonl_counts = [int(x) for x in re.findall(r"(\d+) 条 jsonl", readme)]
    check("README 散文 jsonl 条数 == dataset 实数",
          all(c == len(ids) for c in jsonl_counts),
          f"出现 {jsonl_counts} vs 实数 {len(ids)}" if jsonl_counts and any(c != len(ids) for c in jsonl_counts) else "")

    # 9. 致谢博主覆盖：注册表全部抖音博主必须出现在 README"视频蒸馏来源"
    registry = (LINGYUN / "blogger-registry.md").read_text(encoding="utf-8")
    # ERP 独立数据集博主（如锦鲤 baba）明确标注"独立 … 未并入公文 skill"，不在本断言范围内
    reg_names = []
    for line in registry.splitlines():
        # 凌云笔杆子行无 sec_uid（未存档），以"未存档"识别；锦鲤 baba（ERP 独立）排除
        m2 = re.match(r"\| ([^|]+) \| (MS4w|（早期蒸馏)", line)
        if m2 and "未并入公文 skill" not in line:
            reg_names.append(m2.group(1).strip())
    mm = re.search(r"\*\*视频蒸馏来源（(\d+) 位博主）：\*\*([\s\S]*?)\n\n", readme)
    if mm and reg_names:
        declared_n, body = int(mm.group(1)), mm.group(2)
        listed = len(re.findall(r"^- 抖音", body, re.M))
        missing = [n for n in reg_names if n not in body]
        check(f"致谢博主覆盖（声明 {declared_n}/列出 {listed}/注册表 {len(reg_names)}）",
              declared_n == listed == len(reg_names) and not missing,
              f"缺 {missing}" if missing else f"声明 {declared_n} vs 列出 {listed} vs 注册表 {len(reg_names)}")
    else:
        check("致谢博主覆盖", False, "README 致谢节或注册表格式未匹配")

    # 12. 版本字符串一致性（散落版本标注第二类）
    # SKILL 锚点之外允许的版本号：CHANGELOG 历史行、README 版本历史行、creator 去版本化后应无 "v0.X"
    import glob as _g
    ver_hits = []
    ver_hits += [("SKILL.md 融合设计节", 1 if "设计时版本" in skill else 0)]
    rj = (ROOT / "scripts" / "render_docx.js").read_text(encoding="utf-8")
    ver_hits.append(("render_docx.js creator 去版本化", 1 if re.search(r'creator:\s*"super-official-writer"', rj) else 0))
    # SKILL 正文裸 "v0.X"（除锚点/设计时版本/CHANGELOG 指代外）应为 0
    body = re.sub(r"<!--\s*skill-version:[^>]*>", "", skill)
    body = body.replace("设计时版本", "")
    stray = re.findall(r"现行\s*v0\.[\d.]+|版本[：:]\s*v0\.[\d.]+", body)
    ver_hits.append(("SKILL 正文无裸现役版本标注", 1 if not stray else 0))
    for name, ok in ver_hits:
        check(name, bool(ok), "" if ok else "见上")

    # 7. corpus-lingyun.md 索引页计数抽查 == 层文件实数
    idx = (ROOT / "references" / "corpus-lingyun.md").read_text(encoding="utf-8")
    pairs = [("lingyun-huishui.md", r"惠水组工 20 期实战方法，35 类速查（(\d+) 条）"),
             ("blogger-wenxiong.md", r"加夜班的文兄（220 期，含 19 图文期）[\s\S]*?（(\d+) 条，"),
             ("domains.md", None)]  # domains 在索引页无独立行，改用 SKILL 计数行已覆盖
    for fname, pat in pairs:
        if pat is None:
            continue
        f = ROOT / "references" / "corpus" / fname
        actual = len(re.findall(r"^- \*\*", f.read_text(encoding="utf-8"), re.M))
        m = re.search(pat, idx)
        ok = bool(m) and int(m.group(1)) == actual
        check(f"索引页计数 == {fname} 实数", ok, f"声明 {m.group(1) if m else '?'} vs 实数 {actual}")

    print()
    if FAILS:
        print(f"[integrity] {len(FAILS)} 项 FAIL：{'；'.join(FAILS)}")
        return 1
    print("[integrity] 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
