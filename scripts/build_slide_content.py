#!/usr/bin/env python3
"""Build detailed slide content for image-prompt generation."""

from __future__ import annotations

from workflow_common import OUTPUT, clean_markdown_text, dump_json, load_json, materials_text, split_points, write


LAYOUT_BY_ROLE = {
    "cover": "strong cover hierarchy with main title and restrained project metadata",
    "toc": "modular numbered agenda navigation",
    "review_items": "three-column approval page with reasons, construction direction, and review items",
    "background": "necessity driver diagram with left narrative and right drivers",
    "problem": "five-problem diagnosis matrix",
    "objectives": "four-objective system diagram around central goal",
    "solution": "overall solution diagram with platform, process, data, and governance modules",
    "architecture": "five-layer horizontal architecture diagram with right-side governance columns",
    "process": "horizontal closed-loop process with capability mapping cards",
    "capabilities": "capability chain or capability matrix",
    "implementation": "phased roadmap with milestones and outputs",
    "budget": "three-column investment boundary, cost structure, and pricing strategy",
    "value": "value matrix with metrics and management value",
    "risk": "risk-measure matrix",
    "summary": "decision items and next-step action statement",
    "back_cover": "formal closing page with deep blue gradient and restrained digital motif",
}

ROLE_BULLETS = {
    "cover": ["明确项目名称、汇报对象和材料属性", "突出项目定位和建设主题", "保留单位、日期和审议场景信息"],
    "toc": ["建设背景与必要性", "现状问题与建设目标", "总体方案与核心能力", "实施路径、价值成效与保障措施"],
    "review_items": ["说明事项缘由", "明确建设方向", "列出提请审议事项", "形成会议决策建议"],
    "background": ["业务协同事项持续增加", "传统人工流转效率和追踪能力不足", "数字化平台建设具备现实必要性", "AI能力可支撑流程和数据治理升级"],
    "problem": ["入口分散导致多头登记", "任务派办依赖经验判断", "过程状态难以及时掌握", "数据沉淀不足影响复盘分析"],
    "objectives": ["形成统一入口和统一流转", "提升事项派办和协同处置效率", "强化全过程留痕和闭环管控", "沉淀数据资产支撑管理决策"],
    "solution": ["构建统一事务协同平台", "打通事项登记、派办、处置、销项流程", "引入语义识别和智能推荐能力", "建设驾驶舱支撑运行态势可视化"],
    "architecture": ["构建用户层、应用层、AI能力层、数据层和基础设施层", "右侧贯穿安全、运维和标准保障体系", "支撑事项流、数据流、模型流和管理流协同"],
    "process": ["串联事项上报、智能识别、登记派办、处置销项和简报分析", "通过流程引擎实现全过程在线流转", "通过留痕归档支撑审计追溯"],
    "capabilities": ["智能登记提取事项要素", "智能派办推荐责任单元", "协同处置跟踪过程进度", "数据分析形成管理视图"],
    "implementation": ["先完成需求确认和边界梳理", "再开展方案设计和原型验证", "分阶段推进系统建设和联调试运行", "通过验收培训完成推广交付"],
    "budget": ["明确软件开发与AI能力建设边界", "拆分开发、集成、实施和运维成本", "在预算约束下形成报价和风险预留策略"],
    "value": ["减少重复录入和线下沟通成本", "提升事项办理效率和透明度", "增强过程管控和风险预警能力", "形成可持续运营和复盘机制"],
    "risk": ["组织协同风险需明确责任机制", "数据质量风险需统一口径规则", "系统安全风险需落实权限审计", "运营持续风险需建立复盘机制"],
    "summary": ["明确审议事项和决策边界", "确认建设范围和推进节奏", "落实牵头部门和协同责任", "形成后续实施计划"],
    "back_cover": ["以敬请审议收束", "保留项目名称和汇报信息", "保持与封面一致的深蓝数字化风格"],
}


def section_points(section: str, limit: int = 8) -> list[str]:
    candidates: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("##", "###", "---", ">")):
            continue
        stripped = stripped.strip("-* ")
        stripped = stripped.lstrip("0123456789.、 ")
        stripped = clean_markdown_text(stripped, 90)
        if 8 <= len(stripped) <= 90 and stripped not in candidates:
            candidates.append(stripped)
        if len(candidates) >= limit:
            break
    if len(candidates) < 4:
        for point in split_points(section, limit):
            if point not in candidates:
                candidates.append(point)
            if len(candidates) >= limit:
                break
    return candidates[:limit]


def body_for(page: dict, points: list[str]) -> dict:
    idx = page["slide_no"] - 1
    selected = section_points(page.get("section_text", ""), 8) or points[idx * 2: idx * 2 + 4] or points[:4]
    role_defaults = ROLE_BULLETS.get(page["page_role"], ["结合用户资料进一步补充关键事实", "保持正式克制的结构化表达"])
    merged = []
    for item in selected + role_defaults:
        item = item.strip(" 。；;")
        if item and item not in merged:
            merged.append(item)
        if len(merged) >= 4:
            break
    bullets = [p[:42] for p in merged]
    return {
        **page,
        "headline": page["core_message"],
        "layout_intent": page.get("recommended_layout") or LAYOUT_BY_ROLE.get(page["page_role"], "structured PPT information layout"),
        "bullets": bullets,
        "content_excerpt": clean_markdown_text(page.get("section_text", ""), 1200),
        "speaker_note": "本页用于形成清晰审议判断，不堆砌原文。",
    }


def main() -> None:
    outline = load_json(OUTPUT / "outline.json", {})
    text = materials_text()
    points = split_points(text, 50)
    slides = [body_for(page, points) for page in outline.get("slides", [])]
    lines = ["# 每页详细内容", ""]
    for slide in slides:
        lines.append(f"## {slide['slide_no']:02d}. {slide['title']}")
        lines.append(f"- 页面角色：{slide['page_role']}")
        lines.append(f"- 核心结论：{slide['headline']}")
        lines.append(f"- 推荐版式：{slide['layout_intent']}")
        lines.append("- 正文要点：")
        lines.extend(f"  - {b}" for b in slide["bullets"])
        lines.append("")
    write(OUTPUT / "02_slide_content.md", "\n".join(lines))
    dump_json(OUTPUT / "slide_content.json", {"slides": slides})
    print("Wrote output/02_slide_content.md and output/slide_content.json")


if __name__ == "__main__":
    main()
