# 国央企 PPT Image-First Skill 使用说明

本 Skill 用于根据用户提供的 PPT 相关资料、文档、图片、PDF、网页文字或简单需求，生成一套面向国央企/政企汇报场景的 PPT 生产资料。

它的核心交付不是直接生成可编辑 PPTX，而是生成：

- PPT 提纲
- 逐页内容稿
- 每页高质量视觉生成提示词
- 外部素材计划
- 小样/全量图片生成说明
- PDF 打包说明
- 质量自检报告

如果用户没有提供参考图片或自定义风格，系统会自动使用默认“国央企正式汇报风格”。

## 1. 适用场景

适合用于：

- 国央企数字化项目汇报
- 项目立项上会材料
- 信息化建设方案
- AI 赋能建设方案
- 工作总结与成果汇报
- 经营分析、风险评估、建设规划
- 产品方案、培训课件、营销方案等需要 PPT 化表达的材料

不适合用于：

- 直接生成可编辑 PPTX
- 把图片反向转换为可编辑 PPT
- 自动仿制真实公司 Logo 或真实系统截图
- 在没有图片模型的情况下声称已经生成图片

## 2. 目录说明

```text
guoqi-report-ppt-skill/
├── SKILL.md                         # Agent 使用的核心规则
├── README.md                        # 简要说明
├── USAGE.md                         # 使用说明
├── input/materials.md               # 默认输入资料
├── examples/ai_empowerment/input.md # 示例输入
├── output/                          # 运行产物目录
└── scripts/                         # 工作流脚本
```

`output/` 是运行产物目录，交付版默认为空。每次运行后，结果会写入该目录。

## 3. 准备输入资料

将用户资料放入 `input/` 目录，推荐先使用：

```text
input/materials.md
```

资料中建议写清楚：

- 项目名称
- 汇报对象
- 汇报场景
- 期望页数
- 是否需要封面和封底
- 主要章节
- 每页已有内容
- 视觉风格要求
- 禁止事项
- 是否有真实 Logo、截图、产品图等官方素材

支持读取的常见资料类型包括：

- `.md`
- `.txt`
- `.csv`
- `.json`
- `.html`
- `.docx`
- `.pptx`
- `.pdf`
- `.png` / `.jpg` / `.jpeg` / `.webp`

图片文件会被识别为视觉参考，不会被当作正文 OCR 内容。

## 4. 一键运行文本工作流

在 skill 目录下执行：

```bash
python3 scripts/parse_inputs.py
python3 scripts/detect_visual_style.py
python3 scripts/build_outline.py
python3 scripts/build_slide_content.py
python3 scripts/build_image_prompts.py
python3 scripts/plan_external_assets.py
python3 scripts/search_and_download_assets.py
python3 scripts/generate_sample_images.py
python3 scripts/run_checks.py
```

运行完成后查看：

```text
output/
├── 00_visual_style_brief.md
├── 01_ppt_outline.md
├── 02_slide_content.md
├── 03_image_prompts.md
├── 04_generation_guide.md
├── 05_review_checklist.md
├── image_prompts/
├── external_assets/
└── checks/
```

## 5. 每个输出文件怎么看

### `00_visual_style_brief.md`

说明本次 PPT 采用什么视觉风格。

如果用户没有上传参考图或指定风格，会默认使用国央企正式汇报风格，包括：

- 16:9 横版
- 深蓝/政务蓝主色
- 白底或浅蓝灰底
- 左上强标题
- 细蓝线标题系统
- 浅色圆角卡片
- 正式、克制、适合上会

### `01_ppt_outline.md`

整套 PPT 的页面大纲。

用于确认：

- 页数是否合适
- 页面顺序是否符合汇报逻辑
- 是否覆盖背景、问题、目标、方案、实施、成效、风险、决策事项等关键内容

### `02_slide_content.md` / `slide_content.json`

逐页详细内容。

用于后续生成提示词、人工编辑或复制到其他 PPT 工具中。

### `03_image_prompts.md` / `image_prompts/slide_XX.txt`

每页独立的高密度生图提示词。

提示词不是简单风格描述，而是包含：

- 全局风格控制
- 页面类型
- 主视觉结构
- 页面内容
- 字体、标题线、卡片、Logo、图标要求
- 禁止事项
- 生成后自检项

可将单页提示词复制到 GPT-Image-2 或其他图片模型中生成视觉参考图。

### `external_assets/asset_plan.md`

列出本次 PPT 可能需要的官方素材，例如：

- Logo
- 产品截图
- 官方界面图
- 设备照片
- 品牌图标
- 真实数据图表

如果无法联网下载，脚本会写明建议检索来源，不会伪造素材。

### `checks/*.md`

自检报告，用于确认：

- 结构是否完整
- 内容是否重复
- 提示词是否足够具体
- 是否有图片生成风险
- PDF 打包是否具备条件
- 是否可以进入全量生成

## 6. 生成图片小样

默认流程只准备前 3-5 页小样生成说明。

如果当前环境没有接入真实图片生成模型，`generate_sample_images.py` 不会伪造图片，只会生成 `output/sample_review.md`，提示用户把 `output/image_prompts/` 下的提示词复制到图片模型中生成。

建议先生成这些页面作为小样：

1. 封面
2. 目录
3. 背景/必要性
4. 问题分析
5. 目标/总体方案

用户确认小样风格后，再进入全量生成。

## 7. 用户反馈后如何优化

如果用户对小样或内容提出修改意见，可将反馈写入一个文本文件，例如：

```text
input/feedback.md
```

然后执行：

```bash
python3 scripts/optimize_after_feedback.py --feedback input/feedback.md
python3 scripts/build_image_prompts.py
python3 scripts/run_checks.py
```

常见反馈包括：

- 标题字号不统一
- Logo 不统一
- 标题线粗细不统一
- 某几页文字太多
- 页面缺少决策感
- 风格太像科技展板
- 卡片堆叠过多
- 某一页需要改成架构图、矩阵图或时间轴

## 8. 全量图片与 PDF

只有在用户确认小样后，才建议执行全量图片生成：

```bash
python3 scripts/generate_full_images.py --confirmed
python3 scripts/build_pdf_from_images.py
python3 scripts/run_checks.py
```

如果没有配置真实图片生成能力，脚本会写明“未生成图片”，不会生成假的 PNG。

如果已经有全量图片并放在：

```text
output/images/slide_XX.png
```

则可以使用 PDF 打包脚本生成：

```text
output/slides_preview.pdf
```

## 9. 默认风格规则

没有参考图时，默认使用“国央企正式汇报风格”：

- 页面比例：16:9
- 背景：白色或极浅蓝灰
- 主色：深蓝、政务蓝、蓝灰
- 强调：少量科技蓝或红蓝细线
- 字体：现代中文无衬线风格
- 标题：左上强标题，标题下细蓝线
- 内容：卡片、流程、矩阵、架构、时间轴、表格等信息图
- 气质：正式、稳重、清晰、克制

禁止默认生成：

- 互联网营销风
- 科技展板风
- 咨询广告风
- 古风装饰
- 复杂炫光背景
- 夸张 3D 机器人
- 虚假 Logo
- 虚假截图
- 未确认的具体数据

## 10. 推荐使用流程

```text
准备资料
↓
放入 input/
↓
运行 parse_inputs.py
↓
生成视觉风格 brief
↓
生成提纲
↓
生成逐页内容
↓
生成每页视觉提示词
↓
生成小样或手动复制提示词出图
↓
用户确认或反馈
↓
优化提示词与内容
↓
确认后生成全量图片
↓
打包 PDF
↓
运行自检
```

## 11. 交付给客户时应说明

需要明确告诉客户：

- 本 Skill 生成的是 PPT 设计生产资料和视觉提示词。
- 若未接入图片模型，系统不会自动生成 PNG。
- 若需要图片版 PPT，可将 `output/image_prompts/slide_XX.txt` 复制到图片模型生成。
- 若需要可编辑 PPTX，需要另行进入 PPTX 制作或 HTML/PPT 转换流程。
- 官方 Logo、真实系统截图、真实产品图应由客户提供或从官方渠道获取。

## 12. 常见问题

### 没有参考图能不能用？

可以。系统会自动使用默认国央企正式汇报风格。

### 为什么没有生成图片？

因为当前交付包不内置图片模型 API，也不包含任何私有 Key。未配置图片模型时，只生成提示词和小样说明。

### 为什么不直接生成 PPTX？

本 Skill 当前定位是 image-first PPT 生产资料，不以可编辑 PPTX 为主输出。

### 输出内容在哪里？

所有运行产物都在：

```text
output/
```

### 能不能用于非国企场景？

可以，但默认风格是国央企/政企汇报风。如果用于营销、培训、产品介绍等场景，建议在 `input/materials.md` 中明确写出目标风格。

## 13. 最小测试

交付后可用默认示例快速测试：

```bash
python3 scripts/parse_inputs.py
python3 scripts/detect_visual_style.py
python3 scripts/build_outline.py
python3 scripts/build_slide_content.py
python3 scripts/build_image_prompts.py
python3 scripts/run_checks.py
```

测试通过后，应至少看到：

```text
output/00_visual_style_brief.md
output/01_ppt_outline.md
output/02_slide_content.md
output/03_image_prompts.md
output/image_prompts/
output/checks/
```
