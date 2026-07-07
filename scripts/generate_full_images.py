#!/usr/bin/env python3
"""Generate full page images only after sample confirmation."""

from __future__ import annotations

import sys

from workflow_common import IMAGES, OUTPUT, cli_paths, image_model_available, load_slide_content, write


def main() -> None:
    args = cli_paths()
    slides = load_slide_content()
    IMAGES.mkdir(parents=True, exist_ok=True)
    if not args.confirmed:
        write(OUTPUT / "full_generation_status.md", """# 全量图片生成状态

- 状态：未执行
- 原因：尚未收到小样确认。请在用户确认后使用 `--confirmed`。
""")
        print("Full generation blocked: sample confirmation required.")
        sys.exit(0)
    if not image_model_available():
        write(OUTPUT / "full_generation_status.md", f"""# 全量图片生成状态

- 状态：未生成全量图片
- 原因：当前未配置真实图片生成模型命令。
- 页数：{len(slides)}
- 提示词目录：`output/image_prompts/`
""")
        print("Image model not configured; full images skipped.")
        return
    write(OUTPUT / "full_generation_status.md", "图片生成命令已配置，但需要接入具体图片生成 CLI/API 后执行。")
    print("Image generation hook detected but not implemented.")


if __name__ == "__main__":
    main()
