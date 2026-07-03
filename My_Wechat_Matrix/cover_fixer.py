#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号封面修复工具
将任意比例图片裁剪为微信封面标准的 2.35:1 比例

使用方式:
  1. 直接运行：python cover_fixer.py，然后拖入图片路径
  2. 作为模块导入：from cover_fixer import fix_wechat_cover
  3. 命令行参数：python cover_fixer.py "path/to/image.jpg"
"""

from PIL import Image
import os
from pathlib import Path


def fix_wechat_cover(image_path: str, output_path: str = None, target_ratio: float = 2.35) -> str:
    """
    将图片强制整形为微信封面的 2.35:1 比例
    防止微信后台弹出裁剪框和转圈圈。
    
    Args:
        image_path: 输入图片路径
        output_path: 输出图片路径（可选，默认在原文件名后加 _fixed）
        target_ratio: 目标宽高比，默认 2.35:1
        
    Returns:
        输出文件路径，失败返回 None
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        original_ratio = width / height
        
        print(f"📐 原始尺寸: {width} x {height} (比例: {original_ratio:.2f}:1)")
        print(f"🎯 目标比例: {target_ratio}:1")
        
        # 计算理想的高度 (以宽度为基准)
        target_height = int(width / target_ratio)
        
        # 如果原图太高（比如正方形），就裁剪高度
        if height > target_height:
            # 计算裁剪区域（取中间部分，丢弃上下多余的）
            top = (height - target_height) // 2
            bottom = top + target_height
            # 裁剪框: (left, top, right, bottom)
            crop_box = (0, top, width, bottom)
            img = img.crop(crop_box)
            print(f"✂️  检测到图片过高，已切除上下多余部分")
            print(f"   裁剪区域: 顶部移除 {top}px, 底部移除 {height - bottom}px")
            
        # 如果原图太宽（虽然少见，但也处理一下），就裁剪宽度
        elif height < target_height:
            target_width = int(height * target_ratio)
            left = (width - target_width) // 2
            right = left + target_width
            crop_box = (left, 0, right, height)
            img = img.crop(crop_box)
            print(f"✂️  检测到图片过宽，已切除左右多余部分")
            print(f"   裁剪区域: 左侧移除 {left}px, 右侧移除 {width - right}px")
            
        else:
            print(f"✨ 完美！原图比例已经是 {target_ratio}:1，无需裁剪")

        # 生成输出路径
        if output_path is None:
            file_name, ext = os.path.splitext(image_path)
            output_path = f"{file_name}_fixed{ext}"
        
        # 强制转换为 RGB (防止 PNG 透明度导致的兼容问题)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            print(f"🔄 已将 {img.mode} 模式转换为 RGB")
        
        # 保存
        img.save(output_path, quality=95)
        
        new_width, new_height = img.size
        print(f"\n✅ 处理完成！")
        print(f"   新尺寸: {new_width} x {new_height}")
        print(f"   新比例: {new_width/new_height:.2f}:1")
        print(f"   输出到: {output_path}")
        print(f"\n>>> 请使用这张新图上传，微信后台将无法拒绝。")
        
        return output_path

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def batch_fix_covers(image_paths: list, output_dir: str = None) -> list:
    """
    批量处理多张图片
    
    Args:
        image_paths: 图片路径列表
        output_dir: 输出目录（可选，默认在原位置生成）
        
    Returns:
        成功处理的输出文件路径列表
    """
    results = []
    total = len(image_paths)
    
    print(f"\n{'='*60}")
    print(f"🚀 批量处理模式，共 {total} 张图片")
    print(f"{'='*60}\n")
    
    for i, path in enumerate(image_paths, 1):
        print(f"\n--- [{i}/{total}] 处理中 ---")
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.basename(path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(output_dir, f"{name}_fixed{ext}")
        else:
            output_path = None
            
        result = fix_wechat_cover(path, output_path)
        if result:
            results.append(result)
    
    print(f"\n{'='*60}")
    print(f"✅ 批量处理完成: {len(results)}/{total} 成功")
    print(f"{'='*60}\n")
    
    return results


def ensure_cover_ratio(image_path: str) -> str:
    """
    确保图片符合微信封面比例的快捷方法
    用于自动发布流程中的预处理
    
    Args:
        image_path: 输入图片路径
        
    Returns:
        处理后的图片路径（可能与输入相同，如果已符合比例）
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        current_ratio = width / height
        target_ratio = 2.35
        
        # 允许 5% 的误差
        if abs(current_ratio - target_ratio) / target_ratio < 0.05:
            print(f"✅ 封面图片比例合格: {current_ratio:.2f}:1")
            return image_path
        else:
            print(f"⚠️  封面图片比例不符 ({current_ratio:.2f}:1)，自动修复中...")
            return fix_wechat_cover(image_path)
            
    except Exception as e:
        print(f"❌ 检查封面比例失败: {e}")
        return image_path


# === 命令行入口 ===
if __name__ == "__main__":
    import sys
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🖼️  微信公众号封面修复工具  🖼️                      ║
║                                                              ║
║  将任意图片裁剪为标准的 2.35:1 微信封面比例                  ║
║  保留图片中间最核心的内容，丢弃上下/左右多余部分             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 如果有命令行参数，直接处理
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
        if len(paths) == 1:
            fix_wechat_cover(paths[0])
        else:
            batch_fix_covers(paths)
    else:
        # 交互模式
        target_image = input("📂 请把图片路径拖进来（或输入路径），然后按回车：").strip().strip('"').strip("'")
        
        if target_image:
            fix_wechat_cover(target_image)
        else:
            print("❌ 未提供图片路径，退出")
