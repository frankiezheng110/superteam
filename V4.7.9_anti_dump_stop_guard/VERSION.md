# SuperTeam V4.7.9 — anti-dump self-stop guard + ≥4 threshold loop valve

**发布日期**: 2026-04-26
**前置版本**: V4.7.8_plugin_json修复
**类型**: Patch (修补 V4.7.7 引入的硬约束漏洞 + 加固反循环机制)

## 触发事件

2026-04-26 SMS phase-4-s3-module 会话中,主会话 OR 在 U-Q3b verify PASS 后输出长段总结 + dump"由你决定继续推还是先停"等等待用户决定的文字,**没有任何 tool call**。Turn 结束 → Stop hook 触发 → 模型真停下。后续 user 多次反馈"为什么又停了"。

经 transcript 量化分析:本会话 LLM 触发 33 次 end_turn,Hook 实际拦下 7 次,**漏洞放行 26 次**(放行率 79%)。绝大多数"漏洞放行"都是 case-2 (OR 顽固 dump 文字),不是 case-3 (hook 真死循环)。

用户原话:
- "为什么又停了,难道状态机出错了"
- "既然状态机状态没有错,说明 hook 设计漏掉了某些环节"
- "我不允许任何软规则来判定你是否继续工作,必须是硬规则,硬约束"
- "项目没有结束 = 状态机 true = 永远不能停下"
- "有任何例外都必须被删除,哪怕是 Claude 官方也不行"
- 最终阈值方案:"阈值设置成 ≥4"

## 根因

V4.7.7 `hooks/dispatch/stop.py` L44:

```python
def _or_self_stop_check(payload):
    if payload.get("stop_hook_active"):
        return True, ""              # 1-strike pass = 漏洞通道
    if mode_state.project_lifecycle() == "running":
        return False, ...
```

`stop_hook_active=true` 是 **Claude Code runtime 的内置防呆 flag**,在 hook 已拦截过一次且模型再次尝试停且未做新 progress 时由 runtime 自动注入。它的语义是 "防 hook 把会话锁死",**不是 "OR 已被授权停止"**。

V4.7.7 错误地把这个 runtime 内部 flag 当作业务授权信号 1-strike 直接放行,等于 OR 只要 dump 2 次就能逃出 hook 拦截。配合 V4.7.7 BLOCK reason 文本极简("OR 不允许自停"),LLM 看到后没有具体行动指引,继续 dump → 触发 stop_hook_active → 漏洞放行 → 真停。

软规则 (`feedback_superteam_or_self_decide_post_g3.md` 禁 OR dump 选项) 与硬规则 (stop hook) 之间出现 gap。

## 修复(分层硬约束)

### 1. `hooks/dispatch/stop.py` 内核重写

**单 bit 状态机判定**:
```python
if not mode_state.is_project_alive():
    return True, ""    # 项目结束(/end)或未装载(.superteam/state/mode.json 缺失)→ 唯一合法退出
```

**≥4 阈值 valve 替代 1-strike 放行**:
```python
is_repeat = bool(payload.get("stop_hook_active"))
count = mode_state.bump_stop_block_count(reset_to_one=not is_repeat)
if count >= mode_state._STOP_BLOCK_THRESHOLD:    # =4
    mode_state.reset_stop_block_count()
    return True, ""    # case-3 hook-bug 救命阀
return False, REASON   # case-1/2 BLOCK
```

**5 要素强引导 reason**:
```
SuperTeam V4.7.9 self-stop block · 项目未结束,不允许中途停止。读 plan 文件推进下一步。唯一退出: /superteam:end。
```

包含:
- (1) 标识 hook 拦截事件 (`SuperTeam V4.7.9 self-stop block`)
- (2) 硬约束依据 (`项目未结束`)
- (3) 禁止指令 (`不允许中途停止`)
- (4) 行动指引 (`读 plan 文件推进下一步`)
- (5) 唯一退出 (`/superteam:end`)

**fail-closed 双层 try/except**:
- `is_project_alive()` 内部 try/except,任何异常返回 True (alive)
- `main()` 全函数 try/except,任何异常 emit_block (绝不 emit_allow)

### 2. `hooks/lib/mode_state.py` 新增 API

| 函数 | 作用 |
|---|---|
| `is_project_alive() -> bool` | 单 bit lifecycle 判定 (mode.json 不存在 / lifecycle=ended → False;其他 → True) |
| `stop_block_count() -> int` | 读取 mode.json 中持久化计数器 |
| `bump_stop_block_count(*, reset_to_one) -> int` | 累加(reset_to_one=False)或重置为 1(reset_to_one=True) |
| `reset_stop_block_count() -> None` | valve 触发或 OR 真做 progress 后清零 |
| `_STOP_BLOCK_THRESHOLD = 4` | 模块常量,阈值定义 |

### 3. `tests/test_v477_stop_purity.py` AST 防回潮

- ALLOWED_NAMES 加入 `is_project_alive`, `stop_hook_active`(作为周期 marker), `bump_stop_block_count`, `reset_stop_block_count`, `_STOP_BLOCK_THRESHOLD`
- BANNED_NAMES 保留所有 V4.7.7 瞬态字段 + 新增 `project_lifecycle` 字符串字段(强制只走 boolean accessor,不允许多值字符串比较)

### 4. `tests/test_v477_lifecycle.py`

- L2 反转: paused → BLOCK (V4.7.7 半门关闭)
- L4 反转: 单次 stop_hook_active=true 仍 BLOCK
- L5 新增: 第 4 次 consecutive block 触发 valve ALLOW
- 总 8 个 case (原 7 + 1 新增)

### 5. `tests/test_or_self_stop_v475.py`

- A8 反转: 单次 stop_hook_active=true 仍 BLOCK,期望文字改为 V4.7.9
- A4 reason 期望文字更新

### 6. 端到端模拟测试

- `tests/demo_v479_threshold_loop.py`: 4 次循环模拟,验证前 3 次 BLOCK + 5 要素 reason 注入,第 4 次 valve 触发,counter reset
- `tests/demo_v479_real_llm_loop.sh`: 真实 Claude Haiku 4.5 调用,对比无引导语 vs 有引导语的 LLM 输出,验证引导语将 OR 行为锁定为"读 plan 推进 PENDING"

## 测试结果

| 测试套件 | cases | 结果 |
|---|---|---|
| `test_v477_stop_purity.py` | 2 | PASS |
| `test_v477_lifecycle.py` | 8 (原 7 + 新增 L5) | PASS |
| `test_or_self_stop_v475.py` | 15 | PASS |
| `demo_v479_threshold_loop.py` | 5 rounds | PASS (4 BLOCK + 1 ALLOW + 1 reset 验证) |
| `demo_v479_real_llm_loop.sh` | 2 阶段 | LLM 阶段 B 输出明确含"读 plan-progress / 推进 MUST-auto-003 / 必须主动推进 vs 等待用户" |

## 三种 case 的最终行为

| case | 描述 | V4.7.9 行为 |
|---|---|---|
| 1 | OR 合规,看 reason 立刻 tool_use | 不触发 stop hook,counter 自然为 0 |
| 2 | OR 顽固 dump 文字 | 前 3 次 BLOCK + 强引导,LLM 几乎必在第 1-3 次内顺从 |
| 3 | hook 自身 bug 永远 BLOCK | 第 4 次循环 valve 触发,counter reset,会话恢复 |

## 与 60s runtime timeout 的对比

旧设计依赖 Claude Code runtime 60s hook timeout 作为 case-3 兜底,V4.7.9 改用循环次数计数器,优势:
- **确定性**: count-based 是 OR 行为信号,不受网络/IO 延时干扰
- **粒度**: 4 次循环 = 明确的 LLM 反复 dump 信号,timeout 60s 可能在 hook 跑得慢时误触发
- **自治**: SuperTeam 自己持有兜底逻辑,不依赖 Claude 官方 runtime 行为(避免官方 runtime 升级时旁路被绕过)

## 已知遗留问题(V4.7.10 候选)

- 用户文字"暂停 / 先停 / pause" vs `/superteam:pause` slash command 的语义鸿沟仍存在
- /superteam:pause 在 V4.7.9 下也被 BLOCK (paused 也 BLOCK), 实际 pause 语义已被收口为"标记意图但不放行 self-stop"
- V4.7.10 候选: 在 user_prompt hook 加文字模式识别,匹配暂停意图后自动调 mode_state.end()(非 pause,因为 pause 已无效)
- 本次 patch 不涵盖

## 升级路径

发布到 GitHub `frankiezheng110/superteam` main 分支后,用户跑:
```
/plugin marketplace update superteam
/reload-plugins
/plugin              # 验证 superteam 显示 4.7.9
```

## 不变的

- 主会话即 OR 哲学 (V4.7.0+)
- mode.json schema (V4.7.7+,新增 stop_block_count 字段为可选)
- 多文件 plan/ 兼容层 (V4.7.6)
- slug 双源解析 (V4.7.6)
- `verify.md` / `verification.md` 双命名接受 (V4.7.6)
- 状态机控制文件 BLOCK 列表 (V4.7.5,mode.json 仍允许主会话 Edit 切 lifecycle)
- `/superteam:pause` / `/superteam:resume` / `/superteam:end` 三命令 (语义微调:pause 不再让 OR 自停)
- plugin.json description 转义规约 (V4.7.8)
