#!/usr/bin/env python3
"""Plan real external assets such as logos, screenshots, app icons, and product images."""

from __future__ import annotations

import re

from workflow_common import EXTERNAL, load_slide_content, md_table, write


KEYWORDS = ["logo", "Logo", "品牌", "产品", "平台", "系统", "软件", "App", "网站", "官网", "截图", "界面", "硬件", "设备", "看板"]


def needs_asset(slide: dict) -> bool:
    text = " ".join([slide.get("title", ""), slide.get("headline", ""), " ".join(slide.get("bullets", []))])
    return any(k in text for k in KEYWORDS)


def asset_type(slide: dict) -> str:
    text = slide.get("title", "") + " " + " ".join(slide.get("bullets", []))
    if re.search(r"Logo|logo|品牌", text):
        return "官方 Logo"
    if re.search(r"截图|界面|看板|系统|软件|平台", text):
        return "官方界面截图 / 产品截图"
    if re.search(r"设备|硬件", text):
        return "官方硬件产品图"
    return "真实外部素材"


def main() -> None:
    slides = load_slide_content()
    rows = []
    for slide in slides:
        if needs_asset(slide):
            atype = asset_type(slide)
            rows.append([
                f"{slide['slide_no']:02d}",
                "建议补充" if atype != "官方 Logo" else "如涉及真实品牌则必须补充",
                atype,
                "品牌官网 / 产品官网 / 官方新闻稿 / 官方文档 / 用户上传素材",
                "增强真实可信度，避免图片模型伪造真实界面或标识",
                "标题区、产品界面区、能力示意区或案例页",
                "是",
                "如无授权素材，先生成无真实素材底图，后期手动叠加。",
            ])
    if not rows:
        rows.append(["-", "暂未识别必须使用的真实外部素材", "-", "-", "-", "-", "-", "如用户补充品牌或产品信息，需要重新规划。"])
    content = "# 外部素材使用计划\n\n" + md_table(
        ["页面编号", "需要素材", "素材类型", "建议来源", "用途", "放置位置", "是否必须保持官方原貌", "备注"],
        rows,
    )
    write(EXTERNAL / "asset_plan.md", content)
    print("Wrote output/external_assets/asset_plan.md")


if __name__ == "__main__":
    main()
