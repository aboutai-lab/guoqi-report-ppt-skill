#!/usr/bin/env python3
"""Shared helpers for the image-first PPT workflow."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
CHECKS = OUTPUT / "checks"
EXTERNAL = OUTPUT / "external_assets"
IMAGE_PROMPTS = OUTPUT / "image_prompts"
SAMPLE_IMAGES = OUTPUT / "sample_images"
IMAGES = OUTPUT / "images"

TEXT_EXTS = {".md", ".txt", ".csv", ".tsv", ".html", ".htm", ".json"}
DOC_EXTS = {".docx", ".pptx", ".pdf"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

DEFAULT_GUOQI_STYLE_NAME = "国企汇报默认风格"
DEFAULT_GUOQI_STYLE_PROFILE = [
    "16:9 横版",
    "白底或极浅蓝灰底",
    "深蓝/国企蓝主色",
    "红蓝细线强调",
    "左上强标题",
    "浅色圆角信息卡片",
    "问题矩阵、目标体系、分层架构、流程链路、实施路线、价值矩阵",
    "正式、稳重、克制、适合上会决策",
]


def ensure_dirs() -> None:
    for path in [OUTPUT, CHECKS, EXTERNAL, IMAGE_PROMPTS, SAMPLE_IMAGES, IMAGES]:
        path.mkdir(parents=True, exist_ok=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read(path: Path, default: str = "") -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else default


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_xml_text(xml: str) -> str:
    try:
        root = ET.fromstring(xml)
        parts = [node.text for node in root.iter() if node.text and node.text.strip()]
        return "\n".join(parts)
    except Exception:
        return re.sub(r"<[^>]+>", " ", xml)


def extract_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist() if n.startswith("word/") and n.endswith(".xml")]
        return "\n".join(strip_xml_text(zf.read(n).decode("utf-8", errors="ignore")) for n in names)


def extract_pptx(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        names = sorted(n for n in zf.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml"))
        slides = []
        for index, name in enumerate(names, 1):
            text = strip_xml_text(zf.read(name).decode("utf-8", errors="ignore")).strip()
            if text:
                slides.append(f"[PPT slide {index}]\n{text}")
        return "\n\n".join(slides)


def extract_pdf(path: Path) -> tuple[str, str | None]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except Exception:
            return "", "PDF text extraction skipped: install pypdf or PyPDF2 for direct PDF parsing."
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages), None


def extract_text(path: Path) -> tuple[str, str | None]:
    suffix = path.suffix.lower()
    try:
        if suffix in {".md", ".txt", ".csv", ".tsv", ".html", ".htm", ".json"}:
            text = read(path)
            if suffix in {".html", ".htm"}:
                text = re.sub(r"<[^>]+>", " ", text)
            return text, None
        if suffix == ".docx":
            return extract_docx(path), None
        if suffix == ".pptx":
            return extract_pptx(path), None
        if suffix == ".pdf":
            return extract_pdf(path)
    except Exception as exc:
        return "", f"Failed to parse {path.name}: {exc}"
    return "", f"Unsupported file type: {path.suffix}"


def discover_inputs(extra_paths: list[str] | None = None) -> dict:
    roots: list[Path] = []
    input_dir = ROOT / "input"
    if input_dir.exists():
        roots.append(input_dir)
    demo = ROOT / "examples" / "ai_empowerment" / "input.md"
    if not roots and demo.exists():
        roots.append(demo)
    if extra_paths:
        roots.extend(Path(p).expanduser().resolve() for p in extra_paths)

    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(p for p in root.rglob("*") if p.is_file() and not p.name.startswith("."))

    materials = []
    visual_refs = []
    warnings = []
    for path in sorted(set(files)):
        suffix = path.suffix.lower()
        if suffix in IMAGE_EXTS:
            visual_refs.append(str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path))
            continue
        if suffix in TEXT_EXTS or suffix in DOC_EXTS:
            text, warning = extract_text(path)
            if text.strip():
                materials.append({
                    "path": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
                    "chars": len(text),
                    "text": text.strip(),
                })
            if warning:
                warnings.append(warning)
        else:
            warnings.append(f"Skipped unsupported input: {path.name}")

    return {
        "generated_at": now(),
        "materials": materials,
        "visual_reference_files": visual_refs,
        "warnings": warnings,
    }


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def materials_text() -> str:
    manifest = load_json(OUTPUT / "input_manifest.json", {})
    if not manifest:
        return read(OUTPUT / "materials_text.md")
    parts = []
    for item in manifest.get("materials", []):
        parts.append(f"## {item.get('path')}\n\n{item.get('text', '')}")
    return "\n\n".join(parts).strip()


def project_name(text: str) -> str:
    candidates = re.findall(r"([^\n。；;]{4,40}(?:建设方案|项目|平台|系统|汇报|材料))", text)
    if candidates:
        return candidates[0].strip(" #：:")
    return "现代国企数字化项目汇报材料"


def audience(text: str) -> str:
    for key in ["总办会", "党委会", "省公司领导", "集团领导", "管理层", "上会"]:
        if key in text:
            return key
    return "项目审议与管理决策对象"


def explicit_style(text: str) -> str:
    match = re.search(r"(?:视觉风格|风格|参考风格)[:：]?\s*([^\n。；;]{3,40})", text)
    return match.group(1).strip() if match else ""


def target_slide_count(text: str) -> int:
    combined = re.search(r"封面\s*\+\s*(\d{1,2})\s*页正文\s*\+\s*封底", text)
    if combined:
        return max(5, min(30, int(combined.group(1)) + 2))
    match = re.search(r"(\d{1,2})\s*页", text)
    if match:
        return max(5, min(30, int(match.group(1))))
    return 10


def markdown_field(section: str, field: str) -> str:
    pattern = rf"^###\s+{re.escape(field)}\s*\n(?P<body>.*?)(?=^###\s+|\Z)"
    match = re.search(pattern, section, flags=re.M | re.S)
    if not match:
        return ""
    body = match.group("body").strip()
    body = re.sub(r"\n{2,}", "\n", body)
    return body.strip()


def clean_markdown_text(text: str, limit: int = 500) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^---+$", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+[.、]\s*", "", text, flags=re.M)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def role_from_title(heading: str, title: str) -> str:
    joined = f"{heading} {title}"
    if "封面" in heading:
        return "cover"
    if "封底" in heading:
        return "back_cover"
    if "目录" in joined or "材料结构" in joined:
        return "toc"
    if "上会事项" in joined or "审议事项" in joined:
        return "review_items"
    if "背景" in joined or "必要性" in joined:
        return "background"
    if "痛点" in joined or "问题" in joined:
        return "problem"
    if "目标" in joined:
        return "objectives"
    if "建设内容" in joined or "建设内容总览" in joined:
        return "solution"
    if "架构" in joined:
        return "architecture"
    if "流程" in joined or "闭环" in joined:
        return "process"
    if "登记" in joined or "派办" in joined:
        return "capabilities"
    if "处置" in joined or "销项" in joined:
        return "capabilities"
    if "数据协同" in joined or "智能填报" in joined:
        return "capabilities"
    if "可视化" in joined or "简报" in joined:
        return "capabilities"
    if "实施" in joined or "计划" in joined:
        return "implementation"
    if "投资" in joined or "预算" in joined or "报价" in joined:
        return "budget"
    if "风险" in joined or "保障" in joined or "收益" in joined:
        return "risk"
    return "summary"


def explicit_pages_from_markdown(text: str) -> list[dict]:
    page_heading = re.compile(r"^##\s+(封面|封底|P\d{1,2}[｜|].+?)\s*$", flags=re.M)
    matches = list(page_heading.finditer(text))
    pages: list[dict] = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        top_level = re.search(r"^#\s+", section, flags=re.M)
        if top_level:
            section = section[:top_level.start()].strip()
        title = clean_markdown_text(markdown_field(section, "页面标题"), 80)
        if not title:
            title = re.sub(r"^P\d{1,2}[｜|]", "", heading).strip()
        headline = clean_markdown_text(markdown_field(section, "说明句"), 220)
        if not headline:
            headline = clean_markdown_text(markdown_field(section, "内容定位") or markdown_field(section, "设计建议"), 220)
        if not headline:
            headline = "明确本页汇报重点，支撑会议审议和管理决策。"
        recommended = clean_markdown_text(markdown_field(section, "推荐版式") or markdown_field(section, "设计建议"), 260)
        conclusion = clean_markdown_text(markdown_field(section, "轻量结论"), 180)
        pages.append({
            "slide_no": len(pages) + 1,
            "source_heading": heading,
            "page_role": role_from_title(heading, title),
            "title": title,
            "core_message": headline,
            "recommended_layout": recommended,
            "light_conclusion": conclusion,
            "section_text": section,
        })
    if pages:
        covers = [page for page in pages if page["page_role"] == "cover"]
        tocs = [page for page in pages if page["page_role"] == "toc"]
        backs = [page for page in pages if page["page_role"] == "back_cover"]
        middle = [page for page in pages if page["page_role"] not in {"cover", "toc", "back_cover"}]
        pages = covers[:1] + tocs + middle + backs[:1]
        for index, page in enumerate(pages, 1):
            page["slide_no"] = index
    return pages


def split_points(text: str, limit: int = 30) -> list[str]:
    raw = re.split(r"[\n。；;]+|(?:\d+[.、])", text)
    points = []
    for item in raw:
        item = re.sub(r"\s+", "", item).strip("#-：:")
        if not item or "/" in item or item.lower().endswith((".md", ".txt", ".pdf", ".pptx")):
            continue
        if item.startswith(("##", "examples", "input")):
            continue
        if re.fullmatch(r"[A-Za-z0-9_./-]+", item):
            continue
        if 10 <= len(item) <= 90 and item not in points:
            points.append(item)
        if len(points) >= limit:
            break
    return points


def outline_pages(text: str, count: int | None = None) -> list[dict]:
    count = count or target_slide_count(text)
    base = [
        ("cover", "封面", "明确汇报主题、对象与项目定位。"),
        ("toc", "目录", "建立汇报主线和章节导航。"),
        ("background", "建设背景与必要性", "说明为什么现在需要启动建设。"),
        ("problem", "现状问题诊断", "归纳制约效率、管控和数据价值的问题。"),
        ("objectives", "建设目标与总体思路", "明确目标、路径和管理闭环。"),
        ("solution", "总体方案与核心设计", "呈现平台、流程、数据和智能能力方案。"),
        ("capabilities", "核心能力建设", "拆解关键能力模块和应用场景。"),
        ("implementation", "实施路径与里程碑", "明确阶段计划、交付成果和责任协同。"),
        ("value", "预期成效与管理价值", "说明效率、管控、数据和运营价值。"),
        ("risk", "风险与保障措施", "识别风险并提出责任化应对措施。"),
        ("summary", "审议事项与下一步计划", "形成需要确认的决策事项和后续安排。"),
    ]
    pages = base[:count]
    while len(pages) < count:
        pages.append(("appendix", f"补充页{len(pages) + 1}", "承载用户指定补充信息。"))
    return [
        {"slide_no": i + 1, "page_role": role, "title": title, "core_message": msg}
        for i, (role, title, msg) in enumerate(pages)
    ]


def load_slide_content() -> list[dict]:
    data = load_json(OUTPUT / "slide_content.json", {})
    return data.get("slides", []) if isinstance(data, dict) else []


def image_model_available() -> bool:
    return os.environ.get("IMAGE_GENERATION_ENABLED", "").lower() in {"1", "true", "yes"} and bool(os.environ.get("IMAGE_GENERATION_COMMAND"))


def network_enabled() -> bool:
    return os.environ.get("ALLOW_NETWORK_DOWNLOADS", "").lower() in {"1", "true", "yes"}


def base_prompt_style(style_text: str) -> str:
    style_name_match = re.search(r"当前风格[:：]\s*([^\n]+)", style_text)
    style_name = style_name_match.group(1).strip() if style_name_match else ""
    style_bits = []
    for key in ["稳重", "正式", "专业", "克制", "深蓝", "国企蓝", "蓝灰", "浅灰白", "16:9"]:
        if key in style_text and key not in style_bits:
            style_bits.append(key)
    if not style_name:
        style_name = DEFAULT_GUOQI_STYLE_NAME
    style_summary = f"{style_name}; " + ", ".join(style_bits or ["formal", "restrained", "deep navy", "pale blue"])
    return (
        "16:9 PowerPoint slide, high-end but formal, clean grid alignment, clear report conclusion, "
        "professional information design, no logo hallucination, no watermark, no photo unless explicitly provided, "
        f"visual style: {style_summary}"
    )


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
        *["| " + " | ".join(str(c).replace("\n", "<br>") for c in row) + " |" for row in rows],
    ])


def cli_paths() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", help="Optional input files or directories.")
    parser.add_argument("--confirmed", action="store_true", help="Allow full image/PDF stages after sample approval.")
    parser.add_argument("--feedback", default="", help="Feedback text file for optimization.")
    return parser.parse_args()
