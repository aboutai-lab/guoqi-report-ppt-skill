#!/usr/bin/env python3
"""Run structured checks for the image-first PPT workflow."""

from __future__ import annotations

from workflow_common import CHECKS, IMAGE_PROMPTS, IMAGES, OUTPUT, SAMPLE_IMAGES, EXTERNAL, load_slide_content, read, write


def status(ok: bool) -> str:
    return "PASS" if ok else "RISK"


def main() -> None:
    slides = load_slide_content()
    prompts = sorted(IMAGE_PROMPTS.glob("slide_*.txt"))
    sample_images = sorted(SAMPLE_IMAGES.glob("slide_*.png"))
    full_images = sorted(IMAGES.glob("slide_*.png"))
    style = read(OUTPUT / "00_visual_style_brief.md")
    outline = read(OUTPUT / "01_ppt_outline.md")
    content = read(OUTPUT / "02_slide_content.md")
    prompt_md = read(OUTPUT / "03_image_prompts.md")
    asset_plan = read(EXTERNAL / "asset_plan.md")
    bullet_sets = [tuple(s.get("bullets", [])) for s in slides]
    repeated_bullets = len(set(bullet_sets)) != len(bullet_sets)
    prompt_sections = ["全局总控", "选择页面模板", "输入页面内容", "生成后自检"]
    prompt_has_sections = all(section in prompt_md for section in prompt_sections)
    prompt_is_rich = bool(prompts) and all(len(read(path)) >= 2800 for path in prompts)
    prompt_locks_header = all(term in prompt_md for term in ["正文页页眉锁定规范", "文字型Logo", "2px纯直线", "统一无衬线字体"])

    write(CHECKS / "structure_check.md", f"""# PPT 结构自检

- {status(bool(outline))}：已生成总体提纲。
- {status(len(slides) >= 5)}：页数为 {len(slides)}。
- {status(all(s.get('headline') for s in slides))}：每页具备核心结论字段。
- 风险项：结构合理性仍需结合用户真实业务材料人工复核。
""")
    repeated_titles = len({s.get("title") for s in slides}) != len(slides)
    write(CHECKS / "content_check.md", f"""# 每页详细内容自检

- {status(bool(content))}：已生成每页详细内容。
- {status(not repeated_titles)}：页面标题未发现重复。
- {status(not repeated_bullets)}：页面正文要点未发现整页重复。
- {status(all(s.get('bullets') for s in slides))}：每页具备正文要点。
- 风险项：当前脚本为规则化生成，复杂行业材料建议进一步人工/模型精修。
""")
    write(CHECKS / "prompt_check.md", f"""# 生图提示词自检

- {status(bool(prompt_md))}：已生成总提示词文档。
- {status(len(prompts) == len(slides))}：提示词数量 {len(prompts)} / 页面数量 {len(slides)}。
- {status('16:9' in prompt_md)}：提示词包含页面比例。
- {status(prompt_has_sections)}：提示词包含“全局总控 / 页面模板 / 页面内容 / 生成后自检”等完整段落。
- {status(prompt_is_rich)}：单页提示词已达到较高信息密度，不是简短薄提示词。
- {status(prompt_locks_header)}：提示词已锁定正文页标题字体、字号、横线和文字型Logo规范。
- {status('不要出现页码' in prompt_md)}：提示词包含禁止页码要求。
- {status('不要编造' in prompt_md)}：提示词包含禁止无来源数据要求。
- 风险项：真实 Logo / 产品截图需后期叠加官方素材，不建议交给图片模型幻觉生成。
""")
    write(CHECKS / "visual_calibration.md", f"""# 视觉智能校准与优化

## 通过项

- {status(bool(style))}：已生成视觉风格说明。
- {status(bool(prompts))}：提示词继承统一视觉风格。

## 风险项

- 当前未实际生成小样图片时，无法进行图像结果级校准。
- 若用户上传参考图，应人工比较前 3-5 页小样与参考图，确认是否继续全量生成。

## 是否建议继续全量生成

{"建议先生成并确认小样后再继续。" if not sample_images else "可根据用户确认继续全量生成。"}
""")
    write(CHECKS / "external_assets_check.md", f"""# 真实外部素材使用自检

- {status(bool(asset_plan))}：已生成素材计划。
- 风险项：未联网时不得伪造下载；真实 Logo 和截图必须保持官方原貌。
""")
    write(CHECKS / "image_generation_check.md", f"""# 图片生成结果自检

- 小样图片数量：{len(sample_images)}
- 全量图片数量：{len(full_images)}
- {status(bool(sample_images) or bool(read(OUTPUT / 'sample_review.md')))}：已生成小样或明确记录跳过原因。
- 风险项：无图片时不得声称视觉已通过。
""")
    write(CHECKS / "pdf_packaging_check.md", f"""# PDF 打包自检

- 全量图片数量：{len(full_images)}
- PDF 文件：{'存在' if (OUTPUT / 'slides_preview.pdf').exists() else '不存在'}
- 风险项：只有在全量图片存在时才应打包 PDF。
""")
    write(OUTPUT / "05_review_checklist.md", """# 交付前检查清单

1. 视觉风格说明是否符合参考图或用户描述。
2. PPT 提纲是否有清晰主线。
3. 每页核心结论是否明确。
4. 每页提示词是否可直接复制。
5. 前 3-5 页小样是否已让用户确认。
6. 真实 Logo / 截图是否来自官方素材并保持原貌。
7. 未生成图片时，是否明确说明未生成而不是伪造结果。
8. 全量图片生成前是否已获得用户确认。
""")
    print("Wrote structured checks under output/checks/.")


if __name__ == "__main__":
    main()
