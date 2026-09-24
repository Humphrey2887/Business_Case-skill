# -*- coding: utf-8 -*-
# @AI_GENERATED
"""
本地图片读取 MCP Server。
作用：把磁盘上的图片文件(PNG/JPG/...)读出来，以 MCP 的 image 内容返回，
让支持视觉的模型(agent)能够"看"到本地图片，用于 PPT/截图等可视化检查。

提供两个工具：
- read_image(path):  返回单张图片（过大时自动等比缩小到 max_edge 像素）
- list_images(dir):  列出目录下的图片文件，便于挑选

运行方式（由 Kiro 通过 mcp.json 自动拉起，无需手动运行）：
    python image_server.py
"""
import base64
import io
import os
from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent, TextContent
from PIL import Image

mcp = FastMCP("local-image-reader")

MAX_EDGE = 1600          # 返回前最长边像素上限，控制 token 体积
SUPPORTED = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}


def _encode(path: str, max_edge: int = MAX_EDGE):
    img = Image.open(path)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    w, h = img.size
    scale = max_edge / max(w, h)
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    return data, img.size


@mcp.tool()
def read_image(path: str, max_edge: int = MAX_EDGE) -> list:
    """读取本地图片文件并以图像形式返回。
    path: 图片绝对路径(如 D:\\...\\slide-01.png)。
    max_edge: 返回图最长边像素上限(默认 1600)，越小 token 越省。"""
    if not os.path.exists(path):
        return [TextContent(type="text", text="ERROR: file not found: %s" % path)]
    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED:
        return [TextContent(type="text", text="ERROR: unsupported image type: %s" % ext)]
    try:
        data, (w, h) = _encode(path, max_edge)
    except Exception as e:
        return [TextContent(type="text", text="ERROR: %s: %s" % (type(e).__name__, e))]
    return [
        TextContent(type="text", text="%s (%dx%d)" % (os.path.basename(path), w, h)),
        ImageContent(type="image", mimeType="image/png", data=data),
    ]


@mcp.tool()
def list_images(directory: str) -> str:
    """列出目录下的图片文件名(便于挑选要看的图)。"""
    if not os.path.isdir(directory):
        return "ERROR: not a directory: %s" % directory
    files = [f for f in sorted(os.listdir(directory))
             if os.path.splitext(f)[1].lower() in SUPPORTED]
    if not files:
        return "(no images in %s)" % directory
    return "\n".join(files)


if __name__ == "__main__":
    mcp.run()
# @AI_GENERATED: end
