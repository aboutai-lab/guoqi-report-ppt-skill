#!/usr/bin/env python3
"""Build output/01_ppt_outline.md from parsed materials."""

from __future__ import annotations

from workflow_common import (
    OUTPUT,
    audience,
    dump_json,
    explicit_pages_from_markdown,
    materials_text,
    outline_pages,
    project_name,
    target_slide_count,
    write,
)


def main() -> None:
    text = materials_text()
    pages = explicit_pages_from_markdown(text) or outline_pages(text, target_slide_count(text))
    lines = [
        "# PPT 总体提纲",
        "",
        f"- 项目名称：{project_name(text)}",
        f"- 汇报对象：{audience(text)}",
        f"- 建议页数：{len(pages)}",
        "- 结构原则：背景—问题—目标—方案—能力—路径—价值—保障—审议。",
        "",
        "## 页面安排",
        "",
    ]
    for page in pages:
        lines.append(f"### {page['slide_no']:02d}. {page['title']}")
        lines.append(f"- 页面角色：{page['page_role']}")
        lines.append(f"- 核心结论：{page['core_message']}")
        if page.get("recommended_layout"):
            lines.append(f"- 推荐版式：{page['recommended_layout']}")
        lines.append("")
    write(OUTPUT / "01_ppt_outline.md", "\n".join(lines))
    dump_json(OUTPUT / "outline.json", {"project_name": project_name(text), "audience": audience(text), "slides": pages})
    print("Wrote output/01_ppt_outline.md")


if __name__ == "__main__":
    main()
