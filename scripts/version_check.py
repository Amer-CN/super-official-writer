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
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/Amer-CN/super-official-writer.git"
SKILL_DIR = Path(__file__).resolve().parent.parent


def _local_head() -> str | None:
    """本地版本：git 仓库 HEAD；非仓库则读 SKILL.md 版本行。"""
    try:
        r = subprocess.run(
            ["git", "-C", str(SKILL_DIR), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    # 安装拷贝（无 .git）时退化为读版本号
    try:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        import re
        m = re.search(r"版本：\s*v([\d.]+)", text)
        return f"v{m.group(1)}" if m else None
    except Exception:
        return None


def _remote_head() -> str | None:
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
    local, remote = _local_head(), _remote_head()

    if remote is None:
        status = "unknown"          # 离线/无 git：静默放行
    elif local and local.startswith("v"):
        status = "unknown"          # 安装拷贝无 git 历史可比对
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
