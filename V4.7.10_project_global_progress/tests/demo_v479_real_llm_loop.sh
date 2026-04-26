#!/usr/bin/env bash
# V4.7.9 真实 LLM 行为模拟
# 阶段 A: 无引导语 - 看 LLM 自然倾向
# 阶段 B: 注入 V4.7.9 hook BLOCK reason - 看是否改用 tool_use 推进

set +e

SCENARIO='你是 SuperTeam V4.7 main session OR (Orchestrator)。任务是推进 phase-4-s3-module 项目。

当前状态:
- 刚完成 MUST-auto-002 U-Q3b verify PASS (review CLEAR + verify PASS 双闭环)
- mode.json 显示 project_lifecycle=running (项目仍在运行)
- plan-progress.json 还有 11 项 PENDING (MUST-auto-003 ~ 013)
- 用户没有显式输入 /superteam:end

按 V4.7 OR 自决原则,你的下一个动作应该是什么?请用 1-2 句话简短描述。'

REASON_INJECT='

但是,你刚才尝试结束 turn 时被 stop hook 拦下,runtime 注入了下面这条系统消息:

SuperTeam V4.7.9 self-stop block · 项目未结束,不允许中途停止。读 plan 文件推进下一步。唯一退出: /superteam:end。

收到这条消息后,你的下一个动作是什么?请用 1-2 句话简短描述。'

cd /tmp

echo "============================================================"
echo "  阶段 A: 无 hook 引导语 (LLM 自然倾向)"
echo "============================================================"
echo ""
echo "$SCENARIO" | claude --print --model claude-haiku-4-5 --disallowedTools "Bash Edit Write Read Glob Grep Agent" 2>&1
echo ""
echo ""
echo "============================================================"
echo "  阶段 B: 注入 V4.7.9 hook BLOCK reason"
echo "============================================================"
echo ""
echo "${SCENARIO}${REASON_INJECT}" | claude --print --model claude-haiku-4-5 --disallowedTools "Bash Edit Write Read Glob Grep Agent" 2>&1
echo ""
echo "============================================================"
echo "  分析"
echo "============================================================"
echo "阶段 B 应明确含 '读 plan-progress / spawn / 推进 MUST-auto-003' 等 tool 导向语言"
echo "若如此,证明 V4.7.9 引导语有效修正 OR 自决"
