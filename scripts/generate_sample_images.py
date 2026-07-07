#!/usr/bin/env python3
"""Generate first 3-5 sample images when a real image generation command is configured."""

from __future__ import annotations

from workflow_common import IMAGE_PROMPTS, OUTPUT, SAMPLE_IMAGES, image_model_available, load_slide_content, write


def main() -> None:
    slides = load_slide_content()[:5]
    SAMPLE_IMAGES.mkdir(parents=True, exist_ok=True)
    if not image_model_available():
        write(OUTPUT / "sample_review.md", f"""# 小样生成报告

- 状态：未生成图片小样
- 原因：当前未配置真实图片生成模型命令。
- 已准备：前 {len(slides)} 页提示词位于 `output/image_prompts/`。
- 建议：复制 `slide_01.txt` 至 `slide_{len(slides):02d}.txt` 到 GPT-Image-2 或其他图片模型生成小样。

## 用户需要确认

1. 视觉风格是否符合参考图或默认风格。
2. 页面结构是否符合汇报逻辑。
3. 每页信息密度是否合适。
4. 是否需要调整配色、图标、标题风格或版式。
""")
        print("Image model not configured; sample images skipped.")
        return
    write(OUTPUT / "sample_review.md", """# 小样生成报告

图片生成命令已配置，但此脚本需要接入具体图片生成 CLI/API 后执行。当前不会伪造图片文件。
""")
    print("Image generation command hook detected but not implemented in this repository.")


if __name__ == "__main__":
    main()
