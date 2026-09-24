#!/usr/bin/env python3
"""Extract a lightweight color report from a PowerPoint master/template.

The tool is intentionally read-only and dependency-free. It reads the PPTX zip
directly, collects theme colors, samples srgb fill colors from masters/layouts,
and applies optional overrides from templates/brand-spec.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from collections import Counter
from xml.etree import ElementTree as ET


NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
ROLES = ("primary", "secondary", "accent", "background", "text")
THEME_ROLE_SLOTS = {
    "primary": "accent1",
    "secondary": "accent2",
    "accent": "accent3",
    "background": "lt1",
    "text": "dk1",
}
BRAND_ROLE_PATTERNS = {
    "primary": ("主色", "primary"),
    "secondary": ("辅色", "secondary"),
    "accent": ("强调", "accent"),
    "background": ("背景", "background"),
    "text": ("正文", "text"),
}
HEX_RE = re.compile(r"#?([0-9a-fA-F]{6})")


def normalize_hex(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().lstrip("#").upper()
    if re.fullmatch(r"[0-9A-F]{6}", value):
        return "#" + value
    return None


def color_from_scheme_node(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    srgb = node.find(".//a:srgbClr", NS)
    if srgb is not None:
        return normalize_hex(srgb.get("val"))
    sys_clr = node.find(".//a:sysClr", NS)
    if sys_clr is not None:
        return normalize_hex(sys_clr.get("lastClr"))
    return None


def read_theme(pptx_path: str) -> tuple[dict[str, str], dict[str, str]]:
    colors: dict[str, str] = {}
    fonts: dict[str, str] = {}
    with zipfile.ZipFile(pptx_path) as zf:
        theme_names = [n for n in zf.namelist() if n.startswith("ppt/theme/") and n.endswith(".xml")]
        if not theme_names:
            return colors, fonts
        xml = zf.read(sorted(theme_names)[0])
    root = ET.fromstring(xml)
    scheme = root.find(".//a:clrScheme", NS)
    if scheme is not None:
        for child in list(scheme):
            tag = child.tag.rsplit("}", 1)[-1]
            color = color_from_scheme_node(child)
            if color:
                colors[tag] = color
    font_scheme = root.find(".//a:fontScheme", NS)
    if font_scheme is not None:
        for key, path in (
            ("major_latin", ".//a:majorFont/a:latin"),
            ("major_ea", ".//a:majorFont/a:ea"),
            ("minor_latin", ".//a:minorFont/a:latin"),
            ("minor_ea", ".//a:minorFont/a:ea"),
        ):
            node = font_scheme.find(path, NS)
            if node is not None and node.get("typeface"):
                fonts[key] = node.get("typeface", "")
    return colors, fonts


def parse_brand_spec(path: str | None) -> dict[str, str]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    overrides: dict[str, str] = {}
    for line in text.splitlines():
        lower = line.lower()
        if "待填" in line:
            continue
        match = HEX_RE.search(line)
        if not match:
            continue
        color = normalize_hex(match.group(1))
        if not color:
            continue
        for role, patterns in BRAND_ROLE_PATTERNS.items():
            if any(pattern.lower() in lower for pattern in patterns):
                overrides[role] = color
                break
    return overrides


def sample_layout_colors(pptx_path: str) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    with zipfile.ZipFile(pptx_path) as zf:
        names = [
            name
            for name in zf.namelist()
            if (
                name.startswith("ppt/slideLayouts/")
                or name.startswith("ppt/slideMasters/")
            )
            and name.endswith(".xml")
        ]
        for name in names:
            text = zf.read(name).decode("utf-8", errors="ignore")
            for raw in re.findall(r"<a:srgbClr[^>]*\bval=\"([0-9A-Fa-f]{6})\"", text):
                color = "#" + raw.upper()
                if color not in ("#000000", "#FFFFFF"):
                    counter[color] += 1
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def luminance(color: str) -> float:
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def saturation_span(color: str) -> int:
    color = color.lstrip("#")
    channels = (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
    return max(channels) - min(channels)


def pick_sampled_background(samples: list[tuple[str, int]]) -> str | None:
    if not samples:
        return None
    light = [
        color
        for color, _ in samples
        if luminance(color) >= 150 and saturation_span(color) >= 25
    ]
    if light:
        return light[0]
    light = [color for color, _ in samples if luminance(color) >= 150]
    return light[0] if light else samples[0][0]


def build_report(pptx_path: str, brand_spec: str | None) -> dict:
    warnings: list[str] = []
    theme_colors, theme_fonts = read_theme(pptx_path)
    brand_overrides = parse_brand_spec(brand_spec)
    sampled = sample_layout_colors(pptx_path)

    colors: dict[str, dict[str, str | None]] = {}
    for role in ROLES:
        if role in brand_overrides:
            colors[role] = {"value": brand_overrides[role], "source": "brand_spec"}
            continue

        slot = THEME_ROLE_SLOTS[role]
        value = theme_colors.get(slot)
        source = f"theme:ppt/theme/theme1.xml:{slot}" if value else None

        if role == "background":
            sampled_background = pick_sampled_background(sampled)
            if sampled_background:
                value = sampled_background
                source = "layout_sample"

        if not value:
            warnings.append(f"unresolved color role: {role}")

        colors[role] = {"value": value, "source": source}

    report = {
        "pptx": pptx_path,
        "colors": colors,
        "warnings": warnings,
    }
    if theme_fonts:
        report["fonts"] = theme_fonts
    if sampled:
        report["sampled_colors"] = [
            {"value": color, "count": count} for color, count in sampled[:12]
        ]
    if brand_spec:
        report["brand_spec"] = brand_spec
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract theme colors from a PPTX master.")
    parser.add_argument("pptx", help="Path to the PPTX master/template")
    parser.add_argument(
        "--brand-spec",
        default="templates/brand-spec.md",
        help="Optional brand-spec override markdown file",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not os.path.exists(args.pptx):
        print(f"ERROR: pptx not found: {args.pptx}", file=sys.stderr)
        return 2
    if not args.pptx.lower().endswith(".pptx"):
        print(f"ERROR: not a pptx file: {args.pptx}", file=sys.stderr)
        return 2
    try:
        report = build_report(args.pptx, args.brand_spec)
    except zipfile.BadZipFile:
        print(f"ERROR: invalid pptx zip: {args.pptx}", file=sys.stderr)
        return 2
    except ET.ParseError as exc:
        print(f"ERROR: invalid pptx XML: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
