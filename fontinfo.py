import argparse
import glob
import os
from fontTools.ttLib import TTFont # pip install fonttools
from typing import List, Tuple

# nameID 对应的名称映射表（中英文）
NAMEID_MAP = {
    0: "版权/Copyright",
    1: "字体族/Font Family",
    2: "字体子族/Font Subfamily",
    3: "唯一子族标识/Unique Subfamily Identification",
    4: "全名/Full Font Name",
    5: "版本/Version",
    6: "PostScript 名称/PostScript Name",
    7: "商标/Trademark",
    8: "制造商/Manufacturer",
    9: "设计师/Designer",
    10: "描述/Description",
    11: "厂商网址/Vendor URL",
    12: "设计师网址/Designer URL",
    13: "许可描述/License Description",
    14: "许可信息网址/License Info URL",
    15: "保留/Reserved",
    16: "排版字体族/Typographic Family",
    17: "排版字体子族/Typographic Subfamily",
    18: "兼容全名/Compatible Full",
    19: "示例文本/Sample Text",
    20: "PostScript CID Findfont 名称/PostScript CID Findfont Name",
    21: "WWS 字体族/WWS Family Name",
    22: "WWS 字体子族/WWS Subfamily Name",
    23: "浅色背景调色板/Light Background Palette",
    24: "深色背景调色板/Dark Background Palette",
    25: "变体 PostScript 名称前缀/Variations PostScript Name Prefix",
    # 26-255: 保留或未定义/Reserved or undefined
}

def get_font_info(file_path: str) -> dict:
    """提取所有 nameID 信息"""
    try:
        font = TTFont(file_path)
        name_table = font['name'].names
        nameid_info = {}
        for entry in name_table:
            try:
                value = entry.toUnicode()
            except Exception:
                value = entry.string.decode(errors="replace")
            nameid_info.setdefault(entry.nameID, set()).add(value)
        # 将集合转为字符串，便于输出
        nameid_info = {k: "; ".join(sorted(v)) for k, v in nameid_info.items()}
        return nameid_info
    except Exception as e:
        return {"error": "Invalid Font"}

def main():
    parser = argparse.ArgumentParser(description="读取字体文件所有 nameID 信息")
    parser.add_argument("files", nargs="*", help="字体文件路径（支持通配符）")
    args = parser.parse_args()

    # 处理通配符和默认路径
    if args.files:
        file_list = []
        for pattern in args.files:
            file_list.extend(glob.glob(pattern, recursive=True))
    else:
        file_list = glob.glob("*.ttf") + glob.glob("*.otf") + glob.glob("*.woff*")

    # 去重并过滤非文件项
    file_list = list(set([f for f in file_list if os.path.isfile(f)]))

    for file_path in file_list:
        print(f"\n文件: {os.path.basename(file_path)}")
        nameid_info = get_font_info(file_path)
        if "error" in nameid_info:
            print("  读取失败")
        else:
            for nameid, value in sorted(nameid_info.items()):
                nameid_name = NAMEID_MAP.get(nameid, "Unknown")
                print(f"  nameID {nameid:<2} ({nameid_name}): {value}")

if __name__ == "__main__":
    main()
