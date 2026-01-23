#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def truncate_by_bytes(text, max_bytes, encoding='utf-8'):
    """按字节数截断字符串"""
    if not text:
        return text
        
    encoded = text.encode(encoding)
    if len(encoded) <= max_bytes:
        return text
    
    truncated = text
    while len(truncated.encode(encoding)) > max_bytes:
        truncated = truncated[:-1]
    
    return truncated

# 测试
title = "Gemini CLI：谷歌送给开发者的新年礼物，免费又能打"
print(f"原标题: {title}")
print(f"原字节数: {len(title.encode('utf-8'))} bytes")
print()

truncated_title = truncate_by_bytes(title, 60)
print(f"截断后标题: {truncated_title}")
print(f"截断后字节数: {len(truncated_title.encode('utf-8'))} bytes")
print()

print("✓ 符合微信限制 (64 bytes)" if len(truncated_title.encode('utf-8')) <= 64 else "✗ 仍然超限")
