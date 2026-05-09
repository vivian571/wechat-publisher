#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查当前机器的真实出口 IP 地址
用于排查微信公众平台 IP 白名单问题
"""

import requests
import socket

def get_local_ip():
    """获取本机局域网 IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"获取失败: {e}"

def get_public_ip():
    """获取公网出口 IP（不使用代理）"""
    services = [
        'https://api.ipify.org?format=json',
        'https://ifconfig.me/ip',
        'https://api.ip.sb/ip',
        'http://ip-api.com/json/',
    ]
    
    # 创建一个不使用代理的 session
    session = requests.Session()
    session.proxies = {'http': None, 'https': None}
    session.trust_env = False
    
    for service in services:
        try:
            print(f"正在尝试 {service}...")
            response = session.get(service, timeout=5)
            if response.status_code == 200:
                if 'json' in service or 'ip-api' in service:
                    data = response.json()
                    ip = data.get('ip') or data.get('query')
                else:
                    ip = response.text.strip()
                print(f"✓ 成功获取 IP: {ip}")
                return ip
        except Exception as e:
            print(f"✗ 失败: {e}")
            continue
    
    return "无法获取公网 IP"

def main():
    print("=" * 60)
    print("微信公众平台 IP 白名单诊断工具")
    print("=" * 60)
    print()
    
    print("1. 本机局域网 IP:")
    local_ip = get_local_ip()
    print(f"   {local_ip}")
    print()
    
    print("2. 公网出口 IP (这是您需要添加到微信白名单的 IP):")
    public_ip = get_public_ip()
    print(f"   {public_ip}")
    print()
    
    print("=" * 60)
    print("操作步骤:")
    print("=" * 60)
    print(f"1. 复制上面的公网 IP: {public_ip}")
    print("2. 登录微信公众平台: https://mp.weixin.qq.com")
    print("3. 进入 [设置与开发] → [基本配置] → [IP白名单]")
    print(f"4. 添加 IP 地址: {public_ip}")
    print("5. 保存并等待 1-2 分钟生效")
    print()
    print("注意:")
    print("- 如果您使用的是动态 IP，每次 IP 变化都需要重新添加")
    print("- 白名单最多支持 20 个 IP 地址")
    print("- 如果使用云服务器，请添加服务器的公网 IP")
    print("=" * 60)

if __name__ == "__main__":
    main()
