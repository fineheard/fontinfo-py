import argparse
import glob
import os
from fontTools.ttLib import TTFont
from pathlib import Path
import fnmatch

# 定义 nameID 对应的中英文名称映射表
NAMEID_MAP = {
    0: "版权声明 / Copyright Notice",
    1: "字体家族 / Font Family",
    2: "字体样式 / Font Subfamily",
    3: "唯一标识符 / Unique Identifier",
    4: "完整字体名 / Full Font Name",
    5: "版本信息 / Version",
    6: "PostScript名称 / PostScript Name",
    7: "商标声明 / Trademark",
    8: "厂商名称 / Manufacturer Name",
    9: "设计师名称 / Designer Name",
    10: "说明描述 / Description",
    11: "厂商网址 / Vendor URL",
    12: "设计师网址 / Designer URL",
    13: "许可说明 / License Description",
    14: "许可网址 / License URL",
    16: "典型家族 / Typographic Family",
    17: "典型子族 / Typographic Subfamily",
    18: "Mac兼容全名 / Compatible Full (Macintosh)",
    19: "示例文本 / Sample Text",
    20: "PostScript CID名称 / PostScript CID findfont Name",
    21: "WWS家族名 / WWS Family Name",
    22: "WWS子族名 / WWS Subfamily Name",
    23: "光背景调色板 / Light Background Palette",
    24: "暗背景调色板 / Dark Background Palette",
    25: "变体PS前缀 / Variations PostScript Name Prefix",
}

def get_all_name_ids(font_path):
    """获取字体文件中的所有 nameID 信息，仅针对 Windows 平台，按 nameID 排序"""
    font = TTFont(font_path)
    name_records = {}
    for record in font['name'].names:
        if record.platformID != 3:  # 仅处理 Windows 平台
            continue
        try:
            value = record.string.decode(record.getEncoding())
        except Exception:
            value = record.string.decode('utf-8', errors='ignore')
        if record.nameID not in name_records:  # 避免重复
            name_id_name = NAMEID_MAP.get(record.nameID, f"未知ID / Unknown ID {record.nameID}")
            name_records[record.nameID] = (name_id_name, value)
    # 按 nameID 排序
    return dict(sorted(name_records.items()))

def get_all_stylistic_sets(font_path):
    """获取字体文件中的所有 Stylistic Sets (ssXX)"""
    font = TTFont(font_path)
    stylistic_sets = []
    if 'GSUB' in font:
        gsub = font['GSUB'].table
        featureList = getattr(gsub, 'FeatureList', None)
        if featureList:
            for featureRecord in featureList.FeatureRecord:
                tag = featureRecord.FeatureTag
                if tag.startswith('ss') and tag[2:].isdigit():
                    name = None
                    feature = featureRecord.Feature
                    params = getattr(feature, 'FeatureParams', None)
                    if params and hasattr(params, 'UINameID'):
                        nameID = params.UINameID
                        for record in font['name'].names:
                            if record.nameID == nameID:
                                try:
                                    name = record.string.decode(record.getEncoding())
                                except Exception:
                                    name = record.string.decode('utf-8', errors='ignore')
                                break
                    stylistic_sets.append((tag, name or '无名称'))
    return stylistic_sets

def list_font_properties(font_paths):
    """输出字体文件的所有属性"""
    for font_path in font_paths:
        print(f"\n字体文件: {Path(font_path).name}")
        print("所有 nameID 信息:")
        name_ids = get_all_name_ids(font_path)
        for name_id, (name_id_name, value) in name_ids.items():
            print(f"  {name_id} ({name_id_name}): {value}")
        
        print("\n所有 Stylistic Sets (ssXX):")
        stylistic_sets = get_all_stylistic_sets(font_path)
        if stylistic_sets:
            for tag, name in stylistic_sets:
                print(f"  {tag}: {name}")
        else:
            print("  无")

def find_fonts_by_name_pattern(font_dir, name_pattern=None):
    """查找字体文件并按文件名排序"""
    font_files = []
    for ext in ('*.ttf', '*.otf', '*.ttc'):
        font_files.extend(glob.glob(os.path.join(font_dir, ext)))
    font_files.sort(key=lambda x: Path(x).name.lower())
    if not name_pattern:
        return font_files
    return [f for f in font_files if fnmatch.fnmatch(Path(f).name, name_pattern)]

def main():
    parser = argparse.ArgumentParser(description="输出字体文件的所有属性，包括 nameID 和 Stylistic Sets")
    parser.add_argument('--name', help='字体文件名通配符（如 *Mono*）')
    parser.add_argument('--dir', default='.', help='字体文件所在目录，默认为当前目录')
    args = parser.parse_args()

    font_paths = find_fonts_by_name_pattern(args.dir, args.name)
    if not font_paths:
        print("未找到匹配的字体文件。")
        return

    list_font_properties(font_paths)

if __name__ == "__main__":
    main()