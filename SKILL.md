---
name: guoqi-report-ppt-skill
description: Generate image-first PPT planning deliverables from user PPT/PDF/doc/image/web/text materials: visual style brief, PPT outline, detailed slide content, rich per-slide image-generation prompts, sample-image workflow, external asset plan, image/PDF packaging guidance, and structured self-check reports. Use for SOE/government-enterprise reports, project approval decks, AI/digital transformation materials, product decks, tutorials, marketing decks, and other PPT-image or PDF-image deliverables. If no visual reference is provided, use the default formal SOE/government-enterprise report style. This skill does not target editable PPTX as the main output.
---

# Guoqi Image-First PPT Skill

## Positioning

This skill turns user-uploaded PPT-related materials, images, PDFs, documents, web notes, or text requirements into an image-first PPT production package.

Primary outputs:

- `output/00_visual_style_brief.md`
- `output/01_ppt_outline.md`
- `output/02_slide_content.md`
- `output/03_image_prompts.md`
- `output/04_generation_guide.md`
- `output/05_review_checklist.md`
- `output/checks/*.md`
- `output/external_assets/asset_plan.md`

Optional outputs, only when a real image generation or image/PDF packaging capability is available:

- `output/sample_images/slide_01.png` to `slide_05.png`
- `output/images/slide_XX.png`
- `output/slides_preview.pdf`

Do not claim images, external assets, or PDFs were generated when the runtime cannot actually generate or download them.

## Workflow

Run stages in order:

1. `scripts/parse_inputs.py`: collect user materials and write `output/materials_text.md` plus `output/input_manifest.json`.
2. `scripts/detect_visual_style.py`: create `output/00_visual_style_brief.md` from reference images/PPT/PDF/brand material or the user’s style description. Default to modern SOE approval-report style if no style is supplied.
3. `scripts/build_outline.py`: create `output/01_ppt_outline.md`.
4. `scripts/build_slide_content.py`: create `output/02_slide_content.md` and `output/slide_content.json`.
5. `scripts/build_image_prompts.py`: create `output/03_image_prompts.md` and `output/image_prompts/slide_XX.txt`.
6. `scripts/plan_external_assets.py`: create `output/external_assets/asset_plan.md`.
7. `scripts/search_and_download_assets.py`: download official assets only when network is available and sources are reliable; otherwise write a skip log.
8. `scripts/generate_sample_images.py`: generate only the first 3-5 page samples when a real image model is configured; otherwise write a clear skip note.
9. Wait for user confirmation or feedback. Do not generate all pages unless the user confirms samples or explicitly asks for one-pass full generation.
10. `scripts/optimize_after_feedback.py`: apply user feedback to style, content, prompts, or selected pages.
11. `scripts/generate_full_images.py`: generate all page images only after confirmation or explicit full-generation instruction.
12. `scripts/build_pdf_from_images.py`: package generated images into `output/slides_preview.pdf`.
13. `scripts/run_checks.py`: write structure, content, prompt, visual calibration, asset, image, and PDF checks.

## Visual Style Confirmation

Before detailed production, establish a visual style:

- If the user uploaded reference images, PPT, PDF, brand manuals, screenshots, or historical decks, treat them as visual references.
- Extract style positioning, aspect ratio, main/secondary colors, background style, title zone, card style, icon style, font tone, image/text ratio, information density, whitespace, common layouts, and non-negotiable visual traits.
- If the user only describes a style, convert that description into a visual style brief.
- If the user provides neither reference images nor a custom style, do not block or ask for more material. Immediately use the default SOE/government-enterprise report style:
  - 16:9 landscape
  - restrained, formal, professional
  - deep blue, SOE blue, blue-gray, pale gray/white
  - clear report logic and explicit conclusion per page
  - information diagrams such as cards, process diagrams, architecture diagrams, metrics, matrices, and timelines
  - avoid marketing poster style, technology exhibition-board style, consulting-ad style, excessive neon/3D/robot imagery
- Treat this default as a valid production style, not a temporary placeholder. Only override it when the user provides explicit visual references or a style requirement.

Always write `output/00_visual_style_brief.md`.

## Image Prompt Standard

Generate dense, production-grade page prompts. Do not output short generic prompts.

Each `output/image_prompts/slide_XX.txt` must follow this structure:

1. `第一段：全局总控`: full modern SOE/government-enterprise design control prompt.
2. `第二段：当前设计风格来源`: explain whether the style comes from user references, user text, or the default SOE report style.
3. `第三段：选择页面模板`: page type, body structure, layout rules, visual hierarchy.
4. `第四段：输入页面内容`: project name, page theme, subtitle, module content, bottom hint, data rules.
5. `第五段：版式与细节要求`: title, title line, logo, cards, icons, footer hint, density rules.
6. `第六段：生成限制`: forbidden visual/content elements.
7. `第七段：生成后自检`: title, title line, logo, card, icon, style consistency checks.

Use the built-in modern SOE/government-enterprise reporting style rules as the default design system source.

Prompts must specify page-level structure, not just style adjectives. For example, use patterns such as `中心归因 + 五项痛点卡片`, `四项目标卡片 + 中央目标闭环图`, `五层横向架构图 + 右侧贯穿保障体系`, `横向阶段时间轴 + 里程碑说明 + 保障机制`, and `风险识别与应对矩阵`.

## Sample Confirmation

Do not generate a full deck of images immediately unless the user explicitly requests it.

First sample set usually includes:

1. Cover
2. Agenda
3. Background/necessity
4. Problem/current-state analysis
5. Objectives/overall solution

Write `output/sample_review.md` when sample images are generated or skipped. It must explain the chosen style, page design intent, source fit, reference fit, pending confirmations, and what the user should review.

If the user is dissatisfied, regenerate selected pages or the sample set after applying feedback. Do not continue to full generation until confirmation.

## External Asset Rules

When the content involves real brands, products, platforms, companies, software, hardware, websites, apps, devices, logos, or screenshots:

- Create `output/external_assets/asset_plan.md`.
- Prefer official sources: brand site, product site, official press kit, official docs, app store, official GitHub, trusted media, then user-uploaded assets.
- Keep official logos, screenshots, icons, and product images in their original appearance.
- Do not recolor, redraw, restyle, stretch, or invent approximate logos.
- If image models cannot reliably embed real logos/screenshots, generate the page background without them and recommend adding official assets manually afterward.
- If no network is available, do not fabricate downloads. List recommended search sources instead.

## Self-Checks

Run `scripts/run_checks.py` before delivery. Required reports:

- `output/checks/structure_check.md`
- `output/checks/content_check.md`
- `output/checks/prompt_check.md`
- `output/checks/visual_calibration.md`
- `output/checks/external_assets_check.md`
- `output/checks/image_generation_check.md`
- `output/checks/pdf_packaging_check.md`

Checks must identify passed items, risks, pages needing optimization, and whether to proceed to full generation.

## Prohibited

- Do not target editable PPTX as the main artifact.
- Do not claim images exist when no image model generated them.
- Do not claim assets were downloaded when network/search was unavailable.
- Do not generate full images before sample confirmation unless explicitly requested.
- Do not use internet marketing language for SOE/government-enterprise decks.
- Do not use highly repetitive prompts, repeated slide content, meaningless pages, or blank pages.
- Do not let an image model hallucinate official logos or screenshots.
