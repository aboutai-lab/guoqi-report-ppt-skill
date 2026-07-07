#!/usr/bin/env python3
"""Search/download external assets only when explicitly enabled."""

from __future__ import annotations

from workflow_common import EXTERNAL, network_enabled, now, read, write


def main() -> None:
    plan = read(EXTERNAL / "asset_plan.md")
    if not network_enabled():
        write(EXTERNAL / "source_log.md", f"""# 外部素材来源日志

- 时间：{now()}
- 状态：已跳过下载
- 原因：当前未启用联网下载。设置 `ALLOW_NETWORK_DOWNLOADS=1` 后才允许搜索和下载。
- 要求：不得伪造素材下载结果；请按 `asset_plan.md` 中建议来源人工确认素材。

## 待确认素材计划

{plan}
""")
        print("Network download disabled; wrote source_log.md with skip status.")
        return
    write(EXTERNAL / "source_log.md", f"""# 外部素材来源日志

- 时间：{now()}
- 状态：联网下载入口已启用，但当前脚本不内置搜索 API。
- 处理建议：由执行环境调用官方站点搜索/下载工具后，把素材保存到 `output/external_assets/`，并在本文件补充来源 URL、用途页码和授权风险。
""")
    print("External asset download requires a search/download integration; wrote source_log.md.")


if __name__ == "__main__":
    main()
