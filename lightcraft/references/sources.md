# 来源、版本与使用边界

研究日期：2026-10-24。此 Skill 以 **LightCraft 0.13.0** 的运行接口为执行基线；其余项目提供概念、工作流和风格参考。未安装这些色彩库或应用，没有复制/分发它们的源码、LUT、配置或预设载荷。

## 证据怎样使用

- **源码/文档事实**：某版本中实际存在的实现、参数或公开说明。不能自动升级为真实照片效果验证。
- **工作流综合**：从来源提炼的观察、调整和比较建议；候选原因要在图像上验证。
- **运行验证**：本机实际调用、设置读回、预览或文件级检查。具体范围见 [验证记录](validation.md)。
- **未知/待验证**：缺少当前工具、源数据、显示条件或实测的部分。没有证据时不填成成功，也不编造胶片/肤色/RAW 保真度。

## 来源快照与分工

| 来源 | 使用的版本/提交 | 用于什么 | 不推出什么 |
|---|---|---|---|
| [LightCraft](https://github.com/storytold/lightcraft/tree/23e181283cb448205d865e8cd288b56afe987986) | v0.13.0 / `23e1812` | MCP、控件、WB、选择/撤销、渲染、导出、LUT | 代码存在不等于每种相机/模型/效果已实测 |
| [已有 LightCraft Skill](https://github.com/midasmatterhorn/artcraft-skills/tree/8287b5eb6641c6376cde2c1ad7480648f34349ac/lightcraft) | `8287b5e`，其依据是 LightCraft 0.12.0 | 能力边界、源码证据组织和验证要求的参考 | 不照搬 macOS 路径、旧版能力、作者未做的运行验证 |
| [Colour](https://github.com/colour-science/colour/tree/e82dd140c02d66a174072281e667d595ac5b6951) | develop / `e82dd14` | RGB 空间、编码、白点/色适应、色差的条件 | 不是通用调色处方，不给审美/肤色打绝对分 |
| [OpenColorIO](https://github.com/AcademySoftwareFoundation/OpenColorIO/tree/22dd9c4faa0d1b7cfb3d64d1a6e9cb454acc6cfd) | `22dd9c4` | 场景/显示参考、look 的处理空间、LUT 域与技术变换 | 不代表 LightCraft 原生支持 OCIO、ACES 或任意 log 链 |
| [darktable](https://github.com/darktable-org/darktable/tree/e1e2e26baacde918ccfb07c192c32b832b60f87c) | master / `e1e2e26` | 场景明暗、颜色、局部处理、细节及风格的分工 | 不移植模块数字或承诺跨软件同参同效果 |
| [Raw-Alchemy](https://github.com/shenmintao/Raw-Alchemy/tree/c34ead5ad282b057714faf0458ff777c38df62b4) | `c34ead5` | RAW→已知线性空间→目标 log/色域→LUT 的输入契约意识 | 其效果描述不等于本 Skill 的效果证明，也不自动成为 LightCraft 功能 |
| [t3mujinpack](https://github.com/t3mujinpack/t3mujinpack/tree/0b421f3e25209ed78253d1724a29cc6255c5e7fe) | `0b421f3` | 基础处理、有限模块风格和后续微调的关系 | darktable 胶片风格文件不等于可导入 LightCraft 的预设；没有精确胶片验证 |

## 执行接口的关键依据

- [MCP 设计及 Codex/安装说明](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/docs/mcp.md#L1-L110)：headless/connect、stdio、单库锁、CLI 与桌面版本一致。
- [工具定义与 set_develop 实现](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/mcp/src/tools.rs#L150-L215)、[实现分派](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/mcp/src/tools.rs#L660-L725)：查询、选择、values/settings、部分合并及返回语义。
- [白平衡说明](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/docs/control-protocol.md#L112-L120)、[显影命令](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/engine/src/cmd/develop.rs#L165-L228)：source-aware WB、mode/scale、滑杆写入。
- [控件定义](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/develop/src/controls.rs#L170-L293)：准确 ID、范围与默认值，不从其他软件移植数字。
- [导出参数验证](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/engine/src/export.rs#L894-L1018)：显式参数及格式/位深约束；保存的旧偏好清理与新调用参数验证是不同路径。
- [实际渲染阶段](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/pipeline/src/lib.rs#L1-L23)、[LUT 解析与域](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/pipeline/src/lut.rs#L1-L80)、[LUT 应用位置](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/pipeline/src/finish.rs#L583-L666)。

## 色彩与风格的关键依据

- Colour：[RGB_Colourspace](https://github.com/colour-science/colour/blob/e82dd140c02d66a174072281e667d595ac5b6951/colour/models/rgb/rgb_colourspace.py#L83-L167)、[Von Kries 适应](https://github.com/colour-science/colour/blob/e82dd140c02d66a174072281e667d595ac5b6951/colour/adaptation/vonkries.py#L58-L177)。用于明确色彩解释与参考条件；照片判断表的条件化建议属于本 Skill 综合。
- OCIO：[场景/显示编码](https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/22dd9c4faa0d1b7cfb3d64d1a6e9cb454acc6cfd/docs/guides/authoring/colorspaces.rst#L209-L249)、[look 的 process_space](https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/22dd9c4faa0d1b7cfb3d64d1a6e9cb454acc6cfd/docs/guides/authoring/looks.rst#L18-L35)、[LUT 采样域](https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/22dd9c4faa0d1b7cfb3d64d1a6e9cb454acc6cfd/docs/guides/authoring/allocation_vars.rst#L29-L92)。
- darktable：[filmicrgb 的 view-transform 定义](https://github.com/darktable-org/darktable/blob/e1e2e26baacde918ccfb07c192c32b832b60f87c/src/iop/filmicrgb.c#L337-L350)、[colorbalancergb 的场景工作域](https://github.com/darktable-org/darktable/blob/e1e2e26baacde918ccfb07c192c32b832b60f87c/src/iop/colorbalancergb.c#L175-L190)。只借鉴职责与输入域，不视为 LightCraft 的算法说明。
- Raw-Alchemy：[流程说明](https://github.com/shenmintao/Raw-Alchemy/blob/c34ead5ad282b057714faf0458ff777c38df62b4/README_zh-CN.md#L18-L46)、[core.py](https://github.com/shenmintao/Raw-Alchemy/blob/c34ead5ad282b057714faf0458ff777c38df62b4/src/raw_alchemy/core.py)。用于说明 log LUT 的先决条件；未运行该项目或验证其跨工具一致性。
- t3mujinpack：[设计与使用说明](https://github.com/t3mujinpack/t3mujinpack/blob/0b421f3e25209ed78253d1724a29cc6255c5e7fe/README.md#L12-L16)、[Usage](https://github.com/t3mujinpack/t3mujinpack/blob/0b421f3e25209ed78253d1724a29cc6255c5e7fe/README.md#L144-L165)。Lab 曲线/通道混合和基础曝光/WB要求属于该项目上下文，不形成一刀切的“所有照片先中性化”规则。

本 Skill 的中文正文为重新组织的任务指引；不复制原 Skill 的完整能力目录。原始仓库作者与各自许可证保留在链接来源中。研究中读取的更多文件与逐条证据索引保存在本地研究目录，未全部注入每次任务上下文。

## 本轮新增知识的依据

补充日期：2026-10-24。LightCraft 仍使用上面的固定 0.13.0 快照；darktable 手册读取的是 development 页面，概念用于提炼，后续页面可能更新。

| 依据 | 提炼进入本地文件的内容 | 边界 |
|---|---|---|
| [LightCraft tone map](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/pipeline/src/tone.rs#L1-L11)、[JPEG 映射](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/pipeline/src/tone.rs#L176-L208) | 明暗与控件选择：整体曝光、亮度分布、端部控制各有职责 | 不把控件名称当跨软件算法等价 |
| [LightCraft 色彩工具](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/pipeline/src/colorops.rs#L1-L51) | 调色实践：颜色范围与实际像素色相相关，不能识别对象 | 题材处理建议属于综合，不是源码内置诊断 |
| [蒙版创建](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/engine/src/cmd/masks.rs#L230-L300)、[局部调整及删除/可见性](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/engine/src/cmd/masks.rs#L606-L671) | 局部处理：实际命令、mask ID、部分更新、指定回退 | 不据此宣称真人边缘选择已验证 |
| [新蒙版继承效果](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/engine/src/cmd/mask_effects.rs#L300-L311)、[源图坐标及组合](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/pipeline/src/masks.rs#L1-L7) | 创建后核对实际初值，区分源图与裁剪后坐标，按区域组合 | 不假定新建零效果、AI 名称或软羽化能保证正确 |
| [多蒙版贡献](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/pipeline/src/finish.rs#L410-L427) | 旧蒙版字段保留仍需检查重叠后的外观；曝光等局部项按 alpha 累积，着色项行为不同 | 属于 CPU 源码语义，未据此宣称所有 GPU/复杂局部效果已实测 |
| [点曲线写入](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/engine/src/cmd/develop.rs#L509-L529) | 明暗与控件选择：完整点列、0…1 坐标、保存原通道再试 | 不把输入坐标当 EV，不抄其他软件曲线数值 |
| [darktable exposure](https://docs.darktable.org/usermanual/development/en/module-reference/processing-modules/exposure/) | 整体亮度调整与组内个别曝光修正的区别 | 没有移植其区域自动测光/匹配功能 |
| [darktable tone equalizer](https://docs.darktable.org/usermanual/development/en/module-reference/processing-modules/tone-equalizer/) | 分区塑光同时考虑局部反差、区域边界与平滑过渡 | 不声称 LightCraft 实现相同 equalizer |
| [darktable color balance RGB](https://docs.darktable.org/usermanual/development/en/module-reference/processing-modules/color-balance-rgb/) | 区分颜色维度、明度分区与创意风格目的 | 不把该模块色彩空间/算法/数值写成 LightCraft 特性 |
| [darktable color zones](https://docs.darktable.org/usermanual/development/en/module-reference/processing-modules/color-zones/) | 按颜色范围调整仍需关注同色物体、范围过渡和空间隔离 | 不把颜色范围当对象识别，也不移植 Lab 曲线 |

[明暗与控件选择](tone-and-tools.md)、[调色实践](color-practice.md)、[局部处理](local-editing.md) 中的诊断路径、试调步长、题材验收和风格候选为本 Skill 的条件化综合；它们尚未逐项完成实片验证。[两张夜景案例](cases.md) 仅陈述已有操作与观察，没有编造失败尝试或用户偏好。
