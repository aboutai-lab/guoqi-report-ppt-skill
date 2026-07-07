#!/usr/bin/env python3
"""Build slides_preview.pdf from generated images when they exist."""

from __future__ import annotations

from workflow_common import IMAGES, OUTPUT, write


def main() -> None:
    images = sorted(IMAGES.glob("slide_*.png"))
    if not images:
        write(OUTPUT / "pdf_packaging_status.md", """# 图片合集 PDF 打包状态

- 状态：未生成 PDF
- 原因：`output/images/` 中没有全量页面 PNG。
- 处理：确认小样并生成全量图片后再执行本脚本。
""")
        print("No full images found; PDF packaging skipped.")
        return
    try:
        from PIL import Image
    except Exception:
        write(OUTPUT / "pdf_packaging_status.md", "未安装 Pillow，无法将图片打包为 PDF。")
        print("Pillow not installed; PDF packaging skipped.")
        return
    pil_images = [Image.open(p).convert("RGB") for p in images]
    first, rest = pil_images[0], pil_images[1:]
    out = OUTPUT / "slides_preview.pdf"
    first.save(out, save_all=True, append_images=rest)
    write(OUTPUT / "pdf_packaging_status.md", f"# 图片合集 PDF 打包状态\n\n- 状态：已生成\n- 文件：`{out}`\n- 页数：{len(images)}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
