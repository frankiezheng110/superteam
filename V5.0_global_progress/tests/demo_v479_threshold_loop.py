"""V4.7.9 端到端模拟 · OR 顽固 self-stop 4 次循环演示。

模拟场景:
  OR (LLM) 在 lifecycle=running 时连续 4 次试图 self-stop,
  每次都不响应 hook 引导语 (case-2 worst case)。
  验证:
    1. 前 3 次 hook 注入完整引导语让 OR 看到 (修正机会)
    2. 第 4 次循环触发 ≥4 阈值 valve,允许停 (case-3 救命)
    3. 阈值边界精确无差错

Run:
    python tests/demo_v479_threshold_loop.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# 测试 harness 与正式测试同源,不重复实现
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

from harness import (  # noqa: E402
    invoke,
    make_workspace,
    destroy_workspace,
)
from test_v477_lifecycle import (  # noqa: E402
    write_mode_lifecycle,
    stop_payload,
)


def _separator(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def _show_hook_round(round_num: int, hook_active: bool, res) -> None:
    """打印一轮 hook 调用的详情。"""
    print(f"\n--- Round {round_num} ---")
    print(f"  Input payload : stop_hook_active={hook_active}")
    print(f"  Hook decision : {'BLOCK' if res.blocked else 'ALLOW'}")
    if res.blocked and res.reason:
        # 验证引导语 5 要素
        markers = {
            "标识 hook": "self-stop block" in res.reason,
            "硬约束依据": "项目未结束" in res.reason,
            "禁止指令": "不允许中途停止" in res.reason,
            "行动指引": "读 plan" in res.reason and "推进下一步" in res.reason,
            "唯一退出": "/superteam:end" in res.reason,
        }
        print(f"  Reason text   :")
        for line in res.reason.split("\n"):
            print(f"      | {line}")
        print(f"  Reason 5-element check:")
        for k, ok in markers.items():
            mark = "✓" if ok else "✗"
            print(f"      {mark} {k}")
        all_ok = all(markers.values())
        if not all_ok:
            print(f"  >>> WARN: reason 缺要素")
    elif not res.blocked:
        print(f"  Reason text   : (none — valve tripped, OR allowed to stop)")


def main() -> int:
    _separator("V4.7.9 OR 顽固 self-stop 4 次循环模拟")
    print(
        "场景:lifecycle=running · OR 收到 hook 引导语后仍持续 dump 文字\n"
        "      (case-2 worst case · 模拟 LLM 完全不响应硬引导)\n"
        "预期:前 3 次 BLOCK + 引导语注入,第 4 次 valve 触发 ALLOW"
    )

    ws = make_workspace()
    failures: list[str] = []
    try:
        ws.init(slug="demo-loop-t1", stage="execute")
        write_mode_lifecycle(ws, project_lifecycle="running", slug="demo-loop-t1")

        # Round 1: 全新 stop 周期 (OR 第一次 try stop)
        res1 = invoke("stop", stop_payload(hook_active=False), cwd=ws.path)
        _show_hook_round(1, False, res1)
        if not res1.blocked:
            failures.append("Round 1 应 BLOCK 但 ALLOW")

        # Round 2-3: OR 没顺从,继续 try stop (case-2 顽固)
        res2 = invoke("stop", stop_payload(hook_active=True), cwd=ws.path)
        _show_hook_round(2, True, res2)
        if not res2.blocked:
            failures.append("Round 2 应 BLOCK 但 ALLOW")

        res3 = invoke("stop", stop_payload(hook_active=True), cwd=ws.path)
        _show_hook_round(3, True, res3)
        if not res3.blocked:
            failures.append("Round 3 应 BLOCK 但 ALLOW")

        # Round 4: 阈值触发,valve 救命 (case-3 假定 hook bug)
        res4 = invoke("stop", stop_payload(hook_active=True), cwd=ws.path)
        _show_hook_round(4, True, res4)
        if res4.blocked:
            failures.append("Round 4 应触发 valve ALLOW 但仍 BLOCK")

        # Round 5: valve 触发后 counter 应已 reset,新一轮又从 BLOCK 开始
        res5 = invoke("stop", stop_payload(hook_active=False), cwd=ws.path)
        _show_hook_round(5, False, res5)
        if not res5.blocked:
            failures.append("Round 5(reset 后第一次)应 BLOCK 但 ALLOW")

    finally:
        destroy_workspace(ws)

    _separator("总结")
    if failures:
        print(f"FAIL · {len(failures)} 项异常:")
        for f in failures:
            print(f"  · {f}")
        return 1

    print("PASS · V4.7.9 阈值机制行为符合设计")
    print("  · 前 3 次循环 BLOCK,引导语 5 要素完整注入(给 OR 修正机会)")
    print("  · 第 4 次循环触发 valve ALLOW(case-3 hook-bug 救命)")
    print("  · valve 触发后 counter reset,新周期重新计数")
    print()
    print("第 1 个验证目标:hook+引导语能否修正 OR 自决")
    print("  · 引导语注入完整(项目未结束/不允许停/读 plan/唯一退出)")
    print("  · LLM 看到这条 reason 后,通常 1-3 轮内会改用 tool_use 推进")
    print("  · 注:实际 LLM 行为修正由模型本身完成,本测试验证的是 hook 端")
    print("        的输入与引导语注入正确性")
    print()
    print("第 2 个验证目标:多次循环真的会被反循环机制终止")
    print("  · 第 4 次循环精确触发 valve ALLOW")
    print("  · counter 在 ALLOW 后 reset,不会一次 valve 永久放行")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
