#!/usr/bin/env python3
# -*- coding: utf-8 -*-

title = "Gemini CLI：谷歌送给开发者的新年礼物，免费又能打"
print(f"标题: {title}")
print(f"字符数: {len(title)}")
print(f"字节数: {len(title.encode('utf-8'))} bytes")
print()
print("微信限制: 64 bytes")
print(f"是否超限: {'是' if len(title.encode('utf-8')) > 64 else '否'}")
