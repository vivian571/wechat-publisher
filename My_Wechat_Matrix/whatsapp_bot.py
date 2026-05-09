#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Matrix WhatsApp Integration
通过 WhatsApp 消息触发公众号文章生成和发布

使用方法:
1. 在 WhatsApp 发送: "公众号生成全部"
2. 在 WhatsApp 发送: "公众号生成 Account_A_CrossBorder AI提示词技巧"
3. 在 WhatsApp 发送: "公众号状态"
4. 在 WhatsApp 发送: "启动发布代理"
"""

import os
import sys
import subprocess
from pathlib import Path


class WeChatMatrixWhatsAppBot:
    """WhatsApp 集成机器人"""
    
    def __init__(self):
        self.project_dir = Path("/Users/ax/wechat-publisher/My_Wechat_Matrix")
        self.cli_path = self.project_dir / "scripts" / "wechat-matrix"
    
    def handle_message(self, message: str) -> str:
        """
        处理 WhatsApp 消息并返回响应
        
        Args:
            message: WhatsApp 消息内容
            
        Returns:
            响应消息
        """
        message = message.strip()
        
        # 生成全部
        if "公众号生成全部" in message or "generate all" in message.lower():
            return self._generate_all()
        
        # 生成指定账号
        if "公众号生成" in message or "generate" in message.lower():
            return self._generate_specific(message)
        
        # 查看状态
        if "公众号状态" in message or "status" in message.lower():
            return self._get_status()
        
        # 启动代理
        if "启动发布代理" in message or "start agent" in message.lower():
            return self._start_agent()
        
        # 停止代理
        if "停止发布代理" in message or "stop agent" in message.lower():
            return self._stop_agent()
        
        # 查看日志
        if "查看日志" in message or "logs" in message.lower():
            return self._get_logs()
        
        # 帮助
        if "帮助" in message or "help" in message.lower():
            return self._get_help()
        
        return "❓ 未识别的命令。发送 '帮助' 查看可用命令。"
    
    def _run_cli(self, *args) -> tuple[int, str]:
        """运行 CLI 命令"""
        try:
            result = subprocess.run(
                [str(self.cli_path)] + list(args),
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return 1, "❌ 命令执行超时"
        except Exception as e:
            return 1, f"❌ 执行失败: {e}"
    
    def _generate_all(self) -> str:
        """生成所有账号文章"""
        returncode, output = self._run_cli("generate-all")
        
        if returncode == 0:
            return f"✅ 已为所有 4 个账号生成文章！\n\n{output}"
        else:
            return f"❌ 生成失败\n\n{output}"
    
    def _generate_specific(self, message: str) -> str:
        """生成指定账号文章"""
        # 解析消息
        # 格式: "公众号生成 Account_A_CrossBorder AI提示词技巧"
        parts = message.split()
        
        if len(parts) < 3:
            return "❌ 格式错误。正确格式: 公众号生成 <账号名> <主题>"
        
        account = parts[1]
        topic = " ".join(parts[2:])
        
        returncode, output = self._run_cli(
            "generate",
            "--account", account,
            "--topic", topic
        )
        
        if returncode == 0:
            return f"✅ 已为账号 {account} 生成文章！\n主题: {topic}\n\n{output}"
        else:
            return f"❌ 生成失败\n\n{output}"
    
    def _get_status(self) -> str:
        """获取状态"""
        returncode, output = self._run_cli("status")
        return output
    
    def _start_agent(self) -> str:
        """启动代理"""
        returncode, output = self._run_cli("start-agent")
        
        if returncode == 0:
            return f"✅ 自动发布代理已启动！\n\n{output}"
        else:
            return f"❌ 启动失败\n\n{output}"
    
    def _stop_agent(self) -> str:
        """停止代理"""
        returncode, output = self._run_cli("stop-agent")
        
        if returncode == 0:
            return f"✅ 自动发布代理已停止\n\n{output}"
        else:
            return f"❌ 停止失败\n\n{output}"
    
    def _get_logs(self) -> str:
        """获取最近的日志"""
        log_file = self.project_dir / "auto_publish_agent.log"
        
        if not log_file.exists():
            return "📋 暂无日志"
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-20:]  # 最近 20 行
                return "📋 最近的日志:\n\n" + "".join(recent_lines)
        except Exception as e:
            return f"❌ 读取日志失败: {e}"
    
    def _get_help(self) -> str:
        """获取帮助信息"""
        return """
📖 WeChat Matrix WhatsApp 机器人

可用命令:

1️⃣ 生成文章
   • 公众号生成全部
   • 公众号生成 <账号名> <主题>
   
   示例:
   公众号生成全部
   公众号生成 Account_A_CrossBorder AI提示词技巧

2️⃣ 代理管理
   • 启动发布代理
   • 停止发布代理
   • 公众号状态

3️⃣ 查看信息
   • 查看日志
   • 帮助

账号列表:
   • Account_A_CrossBorder (AI提示词)
   • Account_B_English (英语学习)
   • Account_C_Life (生活感悟)
   • Account_D_Tech (编程技术)
"""


def main():
    """主函数 - 用于测试"""
    bot = WeChatMatrixWhatsAppBot()
    
    print("WeChat Matrix WhatsApp Bot - 测试模式")
    print("输入消息测试响应 (输入 'quit' 退出):\n")
    
    while True:
        try:
            message = input(">>> ")
            if message.lower() in ['quit', 'exit', 'q']:
                break
            
            response = bot.handle_message(message)
            print(f"\n{response}\n")
        
        except KeyboardInterrupt:
            print("\n\n再见！")
            break


if __name__ == "__main__":
    main()
