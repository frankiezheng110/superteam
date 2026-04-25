# SuperTeam Upgrade

## Upgrade Rule

- do not overwrite an old release directory
- create a new version directory for every release
- keep one stable marketplace root for Claude Code

## Marketplace Model

- marketplace root: `D:\opencode项目\superteam`
- marketplace config: `D:\opencode项目\superteam\.claude-plugin\marketplace.json`
- current plugin source: `D:\opencode项目\superteam\V4.5.0_功能清单与逐功能TDD`

> **重要**：版本目录必须放在 marketplace root 下，source 使用相对路径（`./V4.x.x_说明`）。
> 绝对路径（含空格的路径如 `D:\claude code\...`）会导致 Claude Code 加载失败。

## Install

```text
/plugin marketplace add "D:\opencode项目\superteam"
/plugin install superteam@superteam
/reload-plugins
```

## GitHub Install

```text
/plugin marketplace add <owner>/<repo>
/plugin install superteam@superteam
/reload-plugins
```

## Upgrade

1. 在 `D:\claude code\superteam\` 下创建新版本目录并完成所有编辑（旧目录不动）
2. 编辑完成后，将新目录完整复制到 marketplace root：
   `cp -r "D:\claude code\superteam\V4.x.x_新说明" "D:\opencode项目\superteam\V4.x.x_新说明"`
3. 更新 marketplace root 中新目录的 `VERSION.md` 和 `CLAUDE.md`（版本号，若未同步）
4. **更新 marketplace root 中新目录的 `.claude-plugin/plugin.json`**：
   - `version` 改为新版本号（**这是 Claude Code 真正读取版本号的地方**）
   - `description` 改为新版本描述
5. **更新 `D:\opencode项目\superteam\.claude-plugin\marketplace.json`**：
   - `metadata.version` 改为新版本号
   - `plugins[0].source` 改为 `"./V4.x.x_新说明"`（相对路径，不要用绝对路径）
6. 运行 `/plugin marketplace update superteam`
7. 运行 `/reload-plugins`
8. 运行 `/plugin` 确认版本号已更新

**第 3 步最易遗漏**：plugin.json 的 version 不改，`/plugin` 永远显示旧版本号。
**第 4 步 source 必须是相对路径**，绝对路径含空格时 Claude Code 会加载失败。

## Auto-Update Note

- GitHub marketplaces can use Claude Code marketplace auto-update
- local marketplaces should use manual `/plugin marketplace update superteam`

## Gate Compatibility

`G1`, `G2`, and `G3` remain the stable supplement entry points.
