import argparse
import glob
import os
from fontTools.ttLib import TTFont # pip install fonttools
from typing import List, Tuple

def get_font_info(file_path: str) -> Tuple[str, str]:
    """提取字体名和版本信息"""
    try:
        font = TTFont(file_path)
        name_table = font['name'].names
        font_name, version = "", ""
        
        for entry in name_table:
            if entry.nameID == 4:  # 全名（Full name）
                font_name = entry.toUnicode()
            elif entry.nameID == 5:  # 版本（Version）
                version = entry.toUnicode()
        
        return font_name, version
    except Exception as e:
        return ("Invalid Font", "N/A")

def main():
    parser = argparse.ArgumentParser(description="读取字体文件信息")
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

    # 输出表头
    print(f"{'文件名':<30} | {'字体名':<40} | {'版本':<15}")
    print("-" * 90)

    # 遍历文件并输出信息
    for file_path in file_list:
        font_name, version = get_font_info(file_path)
        print(f"{os.path.basename(file_path):<30} | {font_name:<40} | {version:<15}")

if __name__ == "__main__":
    main()
