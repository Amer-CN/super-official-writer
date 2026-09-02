#!/usr/bin/env python3
"""version_check.py — 超级公文写作 Skill 版本自检（Step 0）

用法：
    python scripts/version_check.py            # 输出 JSON 状态
    python scripts/version_check.py --quiet    # 只 exit code（0=current/behind, 2=unknown）

输出 JSON：
    {"status": "current",  "local": "5601f54", "remote": "5601f54"}
    {"status": "behind",   "local": "5601f54", "remote": "a359983"}  # 有新版本
    {"status": "unknown",  "local": "5601f54", "remote": null}      # 离线/无git

设计铁律：
- **永不阻塞写作任务**：任何异常（断网、无 git、非仓库目录）都归为 unknown，exit 0
- behind 时提示更新但不强制；由用户裁决
- 本脚本只读（git ls-remote 不改本地任何东西），无凭据传输
"""
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_URL = "https://github.com/Amer-CN/super-official-writer.git"
SKILL_DIR = Path(__file__).resolve().parent.parent


def _local_version() -> str | None:
    """本地版本：优先读 SKILL.md 锚点（`<!-- skill-version: vX.Y -->`），
    其次读"版本：vX.Y"行；两者都取不到时退化为 git HEAD 短哈希。"""
    try:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        import re
        m = re.search(r"<!--\s*skill-version:\s*(v[\d.]+)\s*-->", text)
        if m:
            return m.group(1)
        m = re.search(r"版本：\s*(v[\d.]+)", text)
        if m:
            return m.group(1)
    except Exception:
        pass
    try:
        r = subprocess.run(
            ["git", "-C", str(SKILL_DIR), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None


RAW_URL = "https://raw.githubusercontent.com/Amer-CN/super-official-writer/master/SKILL.md"


def _remote_version() -> str | None:
    """远端版本：优先 GitHub raw SKILL.md 锚点版本；失败退化 ls-remote HEAD 短哈希。"""
    try:
        req = urllib.request.Request(
            RAW_URL, headers={"User-Agent": "skill-version-check/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
            m = re.search(r"<!--\s*skill-version:\s*(v[\d.]+)\s*-->", text)
            if m:
                return m.group(1)
    except Exception:
        pass
    try:
        r = subprocess.run(
            ["git", "ls-remote", REPO_URL, "HEAD"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.split()[0][:7]
    except Exception:
        pass
    return None


def main() -> int:
    quiet = "--quiet" in sys.argv
    local, remote = _local_version(), _remote_version()

    if remote is None:
        status = "unknown"          # 离线/无 git：静默放行
    elif local and local.startswith("v") and remote and remote.startswith("v"):
        status = "current" if local >= remote else "behind"   # 双版本号直接比较
    elif local and local.startswith("v"):
        status = "unknown"          # 本地版本号 vs 远端哈希：不可比
    elif local and remote and local != remote:
        status = "behind"
    else:
        status = "current"

    result = {"status": status, "local": local, "remote": remote}
    if not quiet:
        print(json.dumps(result, ensure_ascii=False))
        if status == "behind":
            print(f"[skill 更新] 发现新版本（本地 {local} → 远端 {remote}）。", file=sys.stderr)
            print("建议：cd 技能目录 && git pull，或重新克隆覆盖。也可先继续当前任务。", file=sys.stderr)
    return 0 if status in ("current", "behind", "unknown") else 2


if __name__ == "__main__":
    sys.exit(main())
