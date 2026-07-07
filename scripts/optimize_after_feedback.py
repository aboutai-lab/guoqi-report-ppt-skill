#!/usr/bin/env python3
"""Record user feedback and append optimization guidance to prompts."""

from __future__ import annotations

from workflow_common import IMAGE_PROMPTS, OUTPUT, cli_paths, now, read, write


def main() -> None:
    args = cli_paths()
    feedback = read(__import__("pathlib").Path(args.feedback)) if args.feedback else ""
    if not feedback.strip():
        write(OUTPUT / "feedback_optimization.md", "# 反馈优化记录\n\n未提供反馈文件。")
        print("No feedback provided.")
        return
    note = f"""# 反馈优化记录

- 时间：{now()}
- 反馈来源：{args.feedback}

## 用户反馈

{feedback}

## 执行要求

- 重新审视视觉风格、页面内容和提示词。
- 对用户指定页面重新生成小样，不直接进入全量生成。
- 如用户上传新参考图，应重新运行 `detect_visual_style.py`。
"""
    write(OUTPUT / "feedback_optimization.md", note)
    for prompt in IMAGE_PROMPTS.glob("slide_*.txt"):
        existing = read(prompt)
        write(prompt, existing + "\n\nAdditional user feedback to apply:\n" + feedback.strip())
    print("Recorded feedback and appended it to existing prompts.")


if __name__ == "__main__":
    main()
