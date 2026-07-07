#!/usr/bin/env python3
"""Generate output/00_visual_style_brief.md."""

from __future__ import annotations

from workflow_common import (
    DEFAULT_GUOQI_STYLE_NAME,
    DEFAULT_GUOQI_STYLE_PROFILE,
    OUTPUT,
    explicit_style,
    load_json,
    materials_text,
    project_name,
    write,
    now,
)


def main() -> None:
    text = materials_text()
    manifest = load_json(OUTPUT / "input_manifest.json", {})
    refs = manifest.get("visual_reference_files", [])
    user_style = explicit_style(text)
    style_desc = user_style or DEFAULT_GUOQI_STYLE_NAME
    if refs:
        source = "用户上传参考图/参考文件"
        fallback_note = "已检测到参考图/参考文件；如参考资料无法识别明确风格，则以国企汇报默认风格作为底座。"
    elif user_style:
        source = "用户文字描述"
        fallback_note = "已检测到用户自定义风格描述；以用户描述优先。"
    else:
        source = "默认风格"
        fallback_note = "未检测到用户参考图、历史 PPT、品牌规范或自定义风格描述，已自动启用国企汇报默认风格。"
    ref_lines = "\n".join(f"- `{ref}`" for ref in refs) if refs else "- 未检测到用户参考图，直接采用国企汇报默认风格。"
    profile_lines = "\n".join(f"- {item}" for item in DEFAULT_GUOQI_STYLE_PROFILE)
    content = f"""# 视觉风格说明

- 生成时间：{now()}
- 项目名称：{project_name(text)}
- 风格来源：{source}
- 当前风格：{style_desc}
- 默认规则：{fallback_note}

## 参考资料

{ref_lines}

## 默认国企汇报风格底座

{profile_lines}

## 风格定位

稳重、正式、专业、克制，适合央国企、政企、运营商、数字化项目、AI赋能、信息化建设、项目立项、总办会和上会决策场景。

## 视觉规范

1. 页面比例：16:9 横版。
2. 主色：深蓝、国企蓝、蓝灰。
3. 辅助色：浅灰白、浅蓝灰、低饱和蓝。
4. 背景：白底或极浅蓝灰底，避免复杂纹理。
5. 标题区：左上强标题，标题下方可使用细蓝线或政务蓝标题栏。
6. 信息承载：模块卡片、流程图、架构图、指标卡、矩阵图、时间轴。
7. 图标风格：线性图标、低装饰、统一蓝色系。
8. 字体气质：黑体/雅黑/思源黑体类，层级清晰，不使用花体。
9. 图文比例：以信息图和结构化文字为主，图片仅用于真实素材或必要视觉示意。
10. 信息密度：正式汇报中高密度，但每页必须有明确核心结论。
11. 留白：结构清楚、边距统一，不做海报式大留白。
12. 常用版式：目录导航、问题矩阵、目标体系、分层架构、流程链路、实施路线、价值矩阵、风险措施矩阵。

## 禁止偏离

- 避免营销海报风、科技展板风、咨询公司广告页。
- 避免过度炫光、蓝紫霓虹、3D 大脑、机器人堆砌。
- 禁止伪造真实 Logo、产品截图或外部素材。
- 禁止每页随机换配色或版式风格。
"""
    write(OUTPUT / "00_visual_style_brief.md", content)
    print("Wrote output/00_visual_style_brief.md")


if __name__ == "__main__":
    main()
