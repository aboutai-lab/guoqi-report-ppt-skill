# guoqi-report-ppt-skill

面向国央企、政企、数字化项目汇报的 image-first PPT 生产 Skill。

本 Skill 的交付重点是先生成高质量 PPT 设计生产资料，再由图片模型或人工设计工具继续出图、排版或打包。它不把“可编辑 PPTX”作为第一阶段主交付。

完整用户使用说明见：[USAGE.md](USAGE.md)。

## 交付内容

运行后核心产物写入 `output/`：

- `00_visual_style_brief.md`：视觉风格简报
- `01_ppt_outline.md`：PPT 提纲
- `02_slide_content.md` / `slide_content.json`：逐页内容
- `03_image_prompts.md` / `image_prompts/slide_XX.txt`：逐页高密度生图提示词
- `04_generation_guide.md`：生成说明
- `05_review_checklist.md`：审查清单
- `external_assets/asset_plan.md`：外部素材计划
- `checks/*.md`：结构、内容、提示词、图片与 PDF 自检报告

## 运行主流程

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

如果用户没有上传参考图、历史 PPT、品牌手册或自定义风格描述，流程会直接使用默认“国央企/政企正式汇报风格”，无需反复要求用户补充视觉参考。

## Prompt Richness

`scripts/build_image_prompts.py` generates long-form prompts using the built-in modern SOE/government-enterprise reporting style rules.

Each page prompt includes:

- global design-control prompt
- style source and default-style fallback
- page template and main visual structure
- page content and module-level instructions
- typography, title line, card, logo, icon and spacing rules
- prohibited items
- generation self-check list

The expected prompt is not a short English style sentence. It should be detailed enough to directly drive a GPT-Image-2 style page rendering while keeping the whole deck visually consistent.

## Sample Then Full Generation

The default workflow stops at the first 3-5 sample pages. Continue to full image generation only after the user confirms the sample direction or explicitly asks for one-pass full generation.

```bash
python3 scripts/generate_full_images.py --confirmed
python3 scripts/build_pdf_from_images.py
python3 scripts/run_checks.py
```

If no real image generation model is configured, image scripts write skip notes and do not fabricate PNG files.

## External Assets

Run:

```bash
python3 scripts/plan_external_assets.py
python3 scripts/search_and_download_assets.py
```

When network access is unavailable, the downloader writes recommended official search sources instead of pretending assets were downloaded.

## 交付包说明

本仓库不包含任何私有 API Key。若需要自动调用图片模型，请在使用方环境中自行配置图片生成能力；未配置时，Skill 仍会稳定生成完整提示词与审查材料。

`output/` 属于运行产物目录，交付版默认保持为空。
