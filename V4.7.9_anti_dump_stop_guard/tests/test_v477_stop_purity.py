"""V4.7.7 stop hook 纯净性 · AST 扫描禁止瞬时字段进 stop 判定。

V4.7.7 契约: stop hook 只读 mode.json.project_lifecycle 一个字段做项目
状态判定。任何引用瞬时进度字段 (stage / subagent / turn / 时间戳) 的代码
都属于回潮,必须在 commit 前拦下。

Run:
    python tests/test_v477_stop_purity.py
"""
from __future__ import annotations

import ast
from pathlib import Path

# Names allowed inside _or_self_stop_check. V4.7.9 uses two inputs:
#   1. is_project_alive() — the lifecycle bit
#   2. stop_block_count via bump_stop_block_count + threshold — counts
#      consecutive blocks in this stop cycle, with stop_hook_active used
#      only as the cycle marker (false=new cycle, true=same cycle continues)
# stop_hook_active is allowed back in (it was BANNED in earlier V4.7.9
# drafts that tried to delete the safety valve entirely; user accepted
# a >=4 threshold as healthier than runtime 60s timeout).
ALLOWED_NAMES = frozenset({
    "is_project_alive",
    "stop_hook_active",
    "bump_stop_block_count", "reset_stop_block_count",
    "_STOP_BLOCK_THRESHOLD",
    "is_repeat", "count",
    "payload", "get", "bool", "not", "del",
    "mode_state", "True", "False", "None",
})

# Names that must NEVER appear inside _or_self_stop_check. Each one
# describes in-flight progress or runtime internals, not project lifecycle,
# so referencing them re-couples the stop decision to V4.7.5-era heuristics
# (or, for stop_hook_active, the V4.7.7 runtime-bypass loophole).
BANNED_NAMES = frozenset({
    "is_subagent_running", "spawned_in_current_turn", "current_stage",
    "is_or_active", "is_user_paused", "pause_owner",
    "_EXEC_CLASS_STAGES", "blocker_summary", "blocked_reason",
    "spawn_log_path", "subagent_stop_log_path",
    "last_subagent_stop_ts", "last_spawn_ts",
    "active_subagent", "turn_id", "current_turn_id", "last_spawn_turn_id",
    "is_active",
    # V4.7.9: string-valued lifecycle field is for diagnostics only.
    # The hook must see only the boolean `is_project_alive()`. Reading
    # the string would re-introduce multi-value comparisons.
    "project_lifecycle",
})


class CaseFail(AssertionError):
    pass


def expect(label: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS · {label}")
    else:
        print(f"  FAIL · {label}{(' :: ' + detail) if detail else ''}")
        raise CaseFail(label)


def case_p1_stop_check_uses_only_state_machine() -> None:
    """_or_self_stop_check 不得引用 BANNED_NAMES 中的任何符号。"""
    stop_py = Path(__file__).resolve().parents[1] / "hooks" / "dispatch" / "stop.py"
    tree = ast.parse(stop_py.read_text(encoding="utf-8"))

    target = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_or_self_stop_check":
            target = node
            break
    expect(
        "P1.0 _or_self_stop_check 函数存在",
        target is not None,
        f"未在 {stop_py} 找到 _or_self_stop_check",
    )

    violations: list[str] = []
    for node in ast.walk(target):
        if isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            violations.append(f"L{node.lineno}: Name '{node.id}'")
        if isinstance(node, ast.Attribute) and node.attr in BANNED_NAMES:
            violations.append(f"L{node.lineno}: Attribute '.{node.attr}'")

    expect(
        "P1.1 stop check 不引用任何禁止符号",
        not violations,
        "; ".join(violations) if violations else "",
    )


def case_p2_stop_module_no_exec_class_constant() -> None:
    """stop.py 模块级别不得保留 _EXEC_CLASS_STAGES 常量 (V4.7.5 残留)。"""
    stop_py = Path(__file__).resolve().parents[1] / "hooks" / "dispatch" / "stop.py"
    src = stop_py.read_text(encoding="utf-8")
    expect(
        "P2 _EXEC_CLASS_STAGES 已移除",
        "_EXEC_CLASS_STAGES" not in src,
        "stop.py 仍含 V4.7.5 时代的 stage 集合常量",
    )


CASES = [
    ("P1", case_p1_stop_check_uses_only_state_machine),
    ("P2", case_p2_stop_module_no_exec_class_constant),
]


def main() -> int:
    failures: list[str] = []
    for label, fn in CASES:
        print(f"\n[{label}] {fn.__name__}")
        try:
            fn()
        except CaseFail as e:
            failures.append(f"{label}: {e}")
        except Exception as e:  # pragma: no cover
            failures.append(f"{label} ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    print("\n========================================")
    if failures:
        print(f"FAIL · {len(failures)}/{len(CASES)} cases failed:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS · all {len(CASES)} cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
