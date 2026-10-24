# LightCraft Skill

通过 LightCraft MCP 为照片做自然修图、参考图调色和分组批量处理，按照“观察图片 → 决定调整 → 执行 → 看结果”的流程工作。

## 功能

- 自然修图：调整曝光、白平衡、明暗、色彩和细节，保留现场氛围。
- 风格调色：分析参考图的明暗、冷暖和颜色关系，迁移适合目标照片的风格。
- 局部处理：结合蒙版处理主体、特定光区和局部色彩。
- 批量处理：按光源、曝光和场景分组，统一色调并检查异常照片。
- 导出验证：比较调整前后效果，检查导出文件的格式、尺寸和实际图像。

完整说明见 [lightcraft/SKILL.md](lightcraft/SKILL.md)，配套资料位于 [lightcraft/references](lightcraft/references)。

## 使用前准备

- 安装并打开 LightCraft，导入需要处理的照片。
- 在支持 Skill 和 MCP 的 AI 客户端中连接 LightCraft MCP。

## 安装

将完整的 `lightcraft/` 目录复制到客户端的 Skills 目录，不要只复制 `SKILL.md`。

以 Codex 为例，默认目录为 `~/.codex/skills/`：

```bash
git clone https://github.com/cacheqian/public-skill.git
mkdir -p ~/.codex/skills
cp -R public-skill/lightcraft ~/.codex/skills/
```

安装后重新加载客户端，并确认 LightCraft MCP 可用。

## 用法

在对话中调用 `$lightcraft`，说明目标照片、期望效果和导出要求，例如：

```text
$lightcraft 帮我自然修一下当前照片，保留夜景氛围，让主体更清楚。

$lightcraft 参考这张图的冷暖和色调处理当前照片，不改变构图。

$lightcraft 把选中的照片按光源分组统一色调，先看代表图再批量处理。

$lightcraft 将当前照片导出为 sRGB JPEG，长边 2048 像素，保存到我指定的目录。
```

未指定风格时，默认从保留现场光线和主体特征的自然调整开始。修图会保留原图，导出为新文件。
