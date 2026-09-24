<!-- @AI_GENERATED -->
# image-mcp · 本地图片读取 MCP Server

让支持视觉的模型（agent）"看"到本地图片文件（PNG/JPG/…），用于 PPT 出片截图、可视化检查等。由 Kiro 通过 `.kiro/settings/mcp.json` **自动拉起，无需手动运行**。

## 依赖

- Python 3.x
- `mcp`（FastMCP server SDK，提供 `mcp.server.fastmcp` / `mcp.types`）
- `Pillow`（PIL，图片读取与等比缩放）

安装：

```
pip install mcp pillow
# Windows 上若 python 不在 PATH：
py -m pip install mcp pillow
```

## 提供的工具

- `read_image(path, max_edge=1600)` — 读取单张图片并以 MCP image 内容返回；超过 `max_edge` 像素时自动等比缩小以控制 token 体积。
- `list_images(directory)` — 列出目录下的图片文件，便于挑选。

支持格式：PNG / JPG / JPEG / GIF / BMP / WEBP / TIFF。

## mcp.json 配置

在 `.kiro/settings/mcp.json` 的 `mcpServers` 中注册本 server（命令/路径按实际环境调整，与仓库现有 `mcp.json` 保持一致）：

```json
{
  "mcpServers": {
    "local-image-reader": {
      "command": "py",
      "args": ["deliverable-tools/image-mcp/image_server.py"]
    }
  }
}
```

> `command` 用 `py` 还是 `python` 取决于本机 Python 启动器；若已有条目，以现有 `mcp.json` 为准，不要重复注册。
<!-- @AI_GENERATED: end -->
