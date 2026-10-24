# LightCraft 调用与参数

依据 `storytold/lightcraft` **v0.13.0 / 23e181283cb448205d865e8cd288b56afe987986** 的源码与实时 MCP schema。已有 Skill 的 v0.12.0 文档用于查找线索；实际执行以当前连接的工具与控件为准。来源见 [来源与边界](sources.md)。

## 1. 发现、范围与基线

使用现有 MCP 连接，不为一次修图重装服务。本机目前名为 `lightcraft-app`，宿主会生成工具前缀；其他环境需动态发现。connect 模式操作已打开窗口；headless 模式有独立会话。

| 动作 | 工具 | 注意 |
|---|---|---|
| 确认库/当前选择/历史 | `doc_inspect {}` | 当前选择不自动等于用户授权的整批范围 |
| 找到照片及源类型 | `query_photos {offset, limit, …}` | 返回 `photos` 与 `total`，分页面查询；筛选对象参数应查实时定义 |
| 读取编辑 | `get_develop {id}` | 不改变选择；保存本轮基线，注意现有 masks、曲线、profile、process 和 WB |
| 读取滑杆 | `list_controls {section?}` | 对活动照片返回 id、单位/范围、默认和当前值；不要从 label 猜字段 |
| 查看真实渲染 | `render_preview {id, max_side, format}` | 不写文件，不改变选择；返回图像块，必须实际查看 |
| 发现额外命令 | `command_list {filter}` | 先关键词查询 id、参数、enabled，再 `command_run {id, params}` |

compact 模式保留辅助工具和命令发现/执行；没有 `cmd_*` 并非能力缺失。不同模式、版本的工具总数不同，不以总数判连接是否正常。

`list_controls` 针对当前活动图；若查询其他照片，先确定是否需要改变选择。`get_develop` / `render_preview` 带 ID 可以只读检查其他图，适合批量前抽样。

## 2. values 与 settings

```json
{"id": 21, "values": {"light.exposure": 0.15}}
```

这里只演示参数形状：ID 和 0.15 均不是实际任务默认值。`values` 写滑杆的**绝对值**，不是增量。先读当前值；若需要增量，通过已发现的 `develop.adjust` 或计算目标值执行。

- `set_develop.values` 调 `develop.set`，使用 `light.exposure`、`detail.sharpenAmount` 等控件 ID；参数越界可能被钳制，必须读回。不要利用钳制来替代检查范围。
- `set_develop.settings` 调 `develop.merge`，使用 `get_develop` 返回的结构，例如 `{"detail":{"sharpen_amount":30}}`。对象递归合并，标量和数组整体替换，未提及字段保留。不要把控件的 camelCase ID 当作结构的 snake_case 字段。
- 曲线点列、蒙版和 spots 等数组需完整保存；不能假定只传一个数组元素会修改对应旧元素。复杂结构优先查专用命令。
- 同次传入 `values` 和 `settings` 会依次执行，可能产生两个撤销步骤；后一步失败不表示前一步已回滚。返回的 touched controls 主要对应 `values`，不能用空 controls 推断 `settings` 未生效。
- 未知/无实现字段不一定以预期方式报错。只写经当前 schema、命令表和源码确认的字段，读取结果并渲染确认。

## 3. 常见控件与容易误用的语义

| 类别 | 0.13.0 常见控件 ID | 使用原则 |
|---|---|---|
| 明暗 | `light.exposure`、`light.contrast`、`light.highlights`、`light.shadows`、`light.whites`、`light.blacks` | 曝光单位 EV，范围 -5…5；其余常见为 -100…100。恢复重要层次，不要求黑白场铺满 |
| 白平衡 | `wb.temp`、`wb.tint` | 先判断 source / mode / scale；色温提高通常使图更暖，正 tint 加品红、负 tint 加绿；均需看实际结果 |
| 色彩 | `color.vibrance`、`color.saturation`、`mixer.<band>.hue/sat/lum` | 先区分照明与固有色；色相带不是物体识别，改 orange 也可能改背景 |
| 明暗分级 | `grading.<shadows/midtones/highlights/global>.hue/sat/lum`、`grading.balance/blending` | 不同明度区的色彩关系；低彩度先试，不机械加入青橙 |
| 效果/细节 | `effects.texture/clarity/dehaze`、`detail.sharpenAmount`、`detail.nrLuminance` 等 | 整体和 100% 细节都看；过度清晰/锐化可能加光晕和噪声 |
| 暗角/颗粒 | `vignette.amount`、`grain.amount` | 暗角负值压暗边缘，正值提亮；颗粒属于风格，强度要按输出尺寸检查 |

这里只列常用 ID，不维护穷举表。具体范围、当前值及新增控件由实时查询给出。

### 白平衡 scale

- 有矩阵的 RAW 可以按 Kelvin 使用 `values` 中的 `wb.temp`；渲染图及其他情形可能使用以 6500/0 为基准的相对模型，UI 又可能显示 -100…100。UI 文本刻度与 API 数字不能直接互抄。
- `settings.wb` 提供 temp/tint 而没有 `scale: "kelvin"` 时，会按相对标度解释；这与给 Kelvin RAW 写 `values` 的语义不同。原有快照若包含 scale，恢复时必须保留。无法判断时先查 `develop.get`、`develop.wb` 及源类型，不猜。
- `values` 修改 temp/tint 会把 mode 改为 custom，并按源信息处理基准。恢复白平衡时只写旧 temp 可能无法恢复旧 mode/scale；应恢复这几个相关字段，并读回。

### 自动调整、预设、曲线

- `develop.auto` 会重新设定六个 light 控件以及 vibrance/saturation。它不会替你完成全部精修，也不应在人工微调后无意覆盖这些字段。
- `apply_preset` 要先从 `presets.list` 取得实际 ID。Amount 不保证所有结构均是简单数值混合；预设里的蒙版有追加/去重语义。用后检查已有蒙版、曲线、白平衡和 profile。
- `develop.curve` 替换指定通道的点列；参数曲线和点曲线可以同时影响结果。保存完整旧点列后再试，避免重复塑形压坏高光或暗部。
- `develop.reset` 回到导入默认及相应处理版本，不等于本轮开始状态，也不一定全零。不得用 reset 代替保护已有编辑。

## 4. 选择、撤销和隔离

- `set_develop`、`crop`、`export` 带单个 `id` 时会先选中那一张并结束当前编辑交互。`export` 不带目标 ID 可能处理当前选择；批量任务应显式给目标列表，并逐项核对结果。
- 大幅风格探索可用已发现的 `photo.virtualCopy {ids, name?}` 建独立编辑副本；这是新的 catalog 记录，仍属于写入。`version.create` 是保存同图设置的命名版本，两者不等同。
- 精确恢复本轮改动优先还原已记录字段。`edit.undo` 只在历史归属可确认、没有用户并行插入编辑时使用；调用后再次读取状态。
- 需要把连续滑杆修改合成一次交互时，先确定活动照片，再 `develop.beginInteraction`，中间不要反复带 ID 触发选择，最后 `develop.endInteraction`；是否取消及 `develop.cancelInteraction` 行为先查当前命令。失败时不能假定所有步骤已自动取消。
- `command_batch` 逐步执行，前面成功的步骤可能保留；不是数据库事务。一个库只允许一个进程写；不要同时让 GUI 和 headless 打开同一库或移除锁。
- 断线/超时后，“未收到回复”不是“未执行”。先查询当前参数、历史和输出，再决定恢复或重试；不盲目重复 undo、导入、应用预设或导出。

### 批量同步的字段与 Auto Sync

`develop.copy` / `develop.paste` / `develop.sync` 的 `groups` 在 0.13.0 使用这些 camelCase 值：

```text
profile, treatment, whiteBalance, light, toneCurve, color, colorMixer,
colorGrading, effects, vignette, grain, detail, optics, geometry, crop,
masks, spots, redEye, lensBlur, calibration
```

先查询命令形状，再显式给选定组，例如 `{"groups":["colorGrading","grain"]}`；这只是参数例子，不表示这两个组适合所有任务。默认复制排除 crop/masks/spots/redEye，**仍包含 WB、曝光等**，不能当成安全的“只复制风格”。复制一个组也会覆盖该组相应设置，不是相对每张原值自动加同样风格；若要保留该组人工调整，先逐图读取并决定哪些字段可改变。

`develop.sync` 从活动图同步到当前选中图；`develop.paste` 可给明确 `ids`。先确定源和目标，再 copy/paste/sync，核对实际 changed 数量和逐图设置。

`develop.autoSync {on?}` 会将活动图发生变化的设置传播到其他选中图。**省略 on 会切换，不是查询。** 单图试验优先明确单选或用带单个 ID 的辅助工具隔离；需要保留多选又要逐张编辑时，查明现有状态，必要时在该任务内显式设置 `on:false` 并告知用户。不自动开启 Auto Sync，也不在不知道原状态时承诺“恢复了原开关”。

依据：[SettingsGroup 与默认复制组](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/develop/src/presets.rs#L17-L74)、[同步](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/engine/src/cmd/develop.rs#L884-L913)、[Auto Sync](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/engine/src/cmd/develop.rs#L998-L1008)。

## 5. 预览、异步与导出

- `render_preview` 返回当前设置的裁剪后预览；`max_side` 默认 1024、上限 4096。读取图像块，不只读尺寸元数据。
- headless 模式没有桌面窗口可放大；提高预览尺寸仍不保证大图达到原片 100%。需要时导出全尺寸测试文件并用可用查看器检查；做不到就明确细节未验证，不把 compact 与 headless 混为同一限制。
- GUI 截图需确认目标图、`loupe.pending` 和 `loupe.failed`；若自动等待超时仍需检查，不能把旧帧当调整结果。需要 100% 细节时使用足够分辨率或应用内放大。
- `render_photo {path}`、`screenshot {path}` 会写文件；无路径的 `render_preview` / `ui_screenshot` 用于只读查看。
- `export` 使用返回的实际路径。`dir` 批量按 `conflict` 处理，默认 unique；显式 `path` 可替换已有普通文件。目录中已编目原图/侧车的保护不代表其他文件也不会被覆盖。
- 明确传入所需尺寸：无尺寸参数时存在默认缩放行为，不能默认为全尺寸。0.13.0 的 `longEdge: 0` 表示全尺寸，仍需看实际裁剪及返回尺寸。
- 桌面 `background: true` 可能只返回已开始，需查 `activity.list` 与 UI 的 `export.running/last` 等已发现状态直到终态。headless 导出阻塞；`background: false` 也应检查工具结果和文件，不把函数返回等同成品正确。
- PNG 8/16、TIFF 8/16/32、JPEG 8-bit 等按格式选择；**不支持的显式 bitDepth 会被验证拒绝**，不应假设自动转换为合适位深。格式、空间和位深以当前 schema 为准。
- 普通分享可用 sRGB JPEG；高位深精修、透明、HDR 则按用途决定。HDR 需要相应编辑状态与支持格式，不能仅把扩展名改成 HDR 或从 8-bit 预览宣称得到高动态范围细节。
- 检查文件非空、解码、尺寸、输出格式和需要的 ICC/位深，再重新打开查看。定位/元数据是否删除按用户要求处理，不暗中改交付策略。

### HDR 编辑与 SDR 版本

先明确用户要 HDR 显示成品，还是在 SDR 中保留高光层次；普通修图不默认开启 HDR。0.13.0 的 `develop.hdr` 可显式给 `enabled` 和 `maxEv`，省略 enabled 会切换；`hdr.maxEv` 控制高于 SDR 白的 headroom，`hdr.sdrBrightness/Contrast/Highlights/Shadows/Whites/Clarity` 调节 SDR 呈现。实际使用前查询当前控件与输出支持，并保存已有状态。

常规 SDR 预览只能评价 SDR 版本，不能验证 HDR 显示峰值、亮度映射或设备观感。比较时保持相同输出条件；没有支持 HDR 的显示与查看链就把该部分列为未验证。依据：[HDR 命令](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/engine/src/cmd/develop.rs#L728-L754)、[HDR 控件](https://github.com/storytold/lightcraft/blob/23e181283cb448205d865e8cd288b56afe987986/crates/develop/src/controls.rs#L180-L186)。

## 6. 模型、LUT 与外部格式

局部选择、mask ID、创建时可能继承的效果、可见性 A/B 与指定蒙版回退，见 [局部处理](local-editing.md)。需要曲线/曝光/高光阴影的选择依据时，见 [明暗与控件选择](tone-and-tools.md)。

- Object/Describe 蒙版、AI 降噪、人脸模型属于可选能力；模型、输入类型和实现各有限制。普通 sky/subject/background 可能是启发式，不把“工具名字有 AI”当成已装模型。
- `enhance.raw_details` / `super_resolution` 等设置字段的存在不证明管线实现。不要承诺未核实功能。
- 3D `.cube` 可通过 `profile.import` 成为创意 profile，具体输入域和管线位置见 [色彩与渲染](color-and-rendering.md#5-lut先核对输入契约)。导入会改库设置，不能以“阅读参考”为理由自动导入。
- darktable `.dtstyle`、OCIO 配置与 Raw-Alchemy 的 log 转换链不属于已确认的原生能力。t3mujinpack 用于理解风格关系，不按参数抄成等价 LightCraft 预设。
- 某些 RAW 只能显示嵌入预览，HEIC 等还与构建特性有关；具体文件的解码/质量要单独验证。软件仍为 Alpha，不把源码路径存在当效果已验证。

## 7. WSL 与 Windows

保持现有 `Codex in WSL → Windows CLI 的 stdio → Windows LightCraft 的 loopback` 连接。Windows CLI 自己访问 `127.0.0.1:7980`，不需要把控制口暴露到局域网。

给 Windows 工具的输入/输出路径使用 `C:\…`、`D:\…` 或已验证可用的 UNC；在 WSL 中查看产物再用 `/mnt/c/…` 或实际挂载路径。`/home/…` 必须先转换成 Windows 可访问路径或另行准备输入；不能以路径字符串存在为由假设对方可读写。

本环境 `/mnt/c` 对 WSL 是只读挂载，但 Windows 导出进程可写自身的临时目录。这是本机验证结果，不应推广成其他主机固定规则。检查产物时区分执行进程权限和观察端权限。
