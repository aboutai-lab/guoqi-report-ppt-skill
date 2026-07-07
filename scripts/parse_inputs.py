#!/usr/bin/env python3
"""Parse uploaded/source materials into materials_text and an input manifest."""

from __future__ import annotations

from workflow_common import OUTPUT, discover_inputs, dump_json, ensure_dirs, write, cli_paths


def main() -> None:
    args = cli_paths()
    ensure_dirs()
    manifest = discover_inputs(args.paths)
    combined = []
    for item in manifest["materials"]:
        combined.append(f"## {item['path']}\n\n{item['text']}")
    write(OUTPUT / "materials_text.md", "\n\n".join(combined) or "未发现可解析文字资料。")
    dump_json(OUTPUT / "input_manifest.json", manifest)
    print(f"Parsed {len(manifest['materials'])} text materials and {len(manifest['visual_reference_files'])} visual references.")


if __name__ == "__main__":
    main()
