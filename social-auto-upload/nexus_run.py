import os
import sys
import subprocess
import argparse
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [NEXUS] - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("NexusTerminal")

# 强制 stdout 使用 UTF-8 (支持 Emoji)
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')


# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

PATHS = {
    "wechat_matrix": os.path.join(PROJECT_ROOT, "My_Wechat_Matrix"),
    "omnipublish": os.path.join(PROJECT_ROOT, "OmniPublish"),
    "fanqie": os.path.join(PROJECT_ROOT, "番茄xiaoshuoyouhua.py"),
    "temp_api": os.path.join(PROJECT_ROOT, "temp"),
    "social_upload": BASE_DIR
}

def run_command(command, cwd=None, description="task"):
    """在指定目录执行命令并流式输出结果"""
    logger.info(f"Starting {description}...")
    logger.info(f"Command: {command}")
    logger.info(f"Working Directory: {cwd or os.getcwd()}")
    
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='gbk', # 读取 Windows 子进程输出 (通常是 GBK)
            errors='replace'
        )
        
        # 实时打印输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"[LOG] {output.strip()}")
                
        # 打印错误（如果有）
        stderr = process.communicate()[1]
        if stderr:
             print(f"\n[ERROR] {stderr.strip()}")
             
        if process.returncode == 0:
            logger.info(f"{description} completed successfully. ✨")
        else:
            logger.error(f"{description} failed with return code {process.returncode}. ❌")
            
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")

def handle_wechat(args_list):
    """
    处理微信矩阵任务
    Usage:
      wechat all              -> Post all
      wechat [account]        -> Post specific account
      wechat gen all          -> Generate all
      wechat gen [account]    -> Generate specific account
      wechat auto all         -> Generate and Post all
      wechat auto [account]   -> Generate and Post specific account
    """
    
    # 解析参数
    mode = "post" # default
    target = "all"
    
    if not args_list:
        pass # use defaults
    elif args_list[0] in ["gen", "generate"]:
        mode = "gen"
        if len(args_list) > 1:
            target = args_list[1]
    elif args_list[0] in ["auto"]:
        mode = "auto"
        if len(args_list) > 1:
            target = args_list[1]
    else:
        # 假设第一个参数就是 target (account 或 all)
        target = args_list[0]
        
    logger.info(f"WeChat Handler - Mode: {mode}, Target: {target}")

    # 自动发现账号
    accounts_dir = os.path.join(PATHS["wechat_matrix"], "accounts")
    available_accounts = []
    if os.path.exists(accounts_dir):
        available_accounts = [d for d in os.listdir(accounts_dir) if os.path.isdir(os.path.join(accounts_dir, d))]
    
    # 确定要执行的账号列表
    tasks = []
    if target == "all":
        tasks = available_accounts
    elif target in available_accounts:
        tasks = [target]
    elif target == "check":
         logger.info(f"Available accounts: {available_accounts}")
         return
    else:
        logger.error(f"Invalid target: {target}")
        logger.info(f"Available accounts: all, {', '.join(available_accounts)}")
        return

    if not tasks:
        logger.warning("No tasks to execute.")
        return

    # 根据模式执行
    if mode == "gen":
        script_path = os.path.join(PATHS["wechat_matrix"], "generator.py")
        if not os.path.exists(script_path):
             logger.error(f"Generator script not found: {script_path}")
             return
             
        for account in tasks:
            logger.info(f"📝 Generating content for: {account}")
            cmd = f"python generator.py --account {account}"
            run_command(cmd, cwd=PATHS["wechat_matrix"], description=f"WeChat Generator ({account})")

    elif mode == "auto":
        script_path = os.path.join(PATHS["wechat_matrix"], "auto_matrix.py")
        if not os.path.exists(script_path):
             logger.error(f"Auto Matrix script not found: {script_path}")
             return
             
        for account in tasks:
            logger.info(f"🚀 Auto-Pilot (Gen+Post) for: {account}")
            cmd = f"python auto_matrix.py --account {account}"
            run_command(cmd, cwd=PATHS["wechat_matrix"], description=f"WeChat Auto Pilot ({account})")
            
    else: # mode == "post"
        script_path = os.path.join(PATHS["wechat_matrix"], "wechat_auto_post.py")
        if not os.path.exists(script_path):
            logger.error(f"Post script not found: {script_path}")
            return

        for account in tasks:
            logger.info(f"📤 Posting content for: {account}")
            cmd = f"python wechat_auto_post.py --account {account}"
            run_command(cmd, cwd=PATHS["wechat_matrix"], description=f"WeChat Auto Post ({account})")



def handle_fanqie(args):
    """处理番茄小说自动化"""
    script_path = PATHS["fanqie"]
    if not os.path.exists(script_path):
        logger.error(f"Script not found: {script_path}")
        return
        
    if not args.url:
        logger.warning("No URL provided. Usage: fanqie https://fanqienovel.com/page/...")
        # 即使没有 URL，我们也可以运行脚本(此时脚本会 fallback 到 input)，但在非交互式 Web 终端中这会卡住。
        # 所以这里我们强制要求提供 URL，或者提供一个更友好的交互提示。
        return

    logger.info(f"Starting Fanqie Novel automation for: {args.url}")
    # 传递 URL 参数
    # 注意引号包裹 URL 防止特殊字符问题
    cmd = f"python \"{script_path}\" \"{args.url}\""
    run_command(cmd, cwd=PROJECT_ROOT, description="Fanqie Novel Downloader")

def handle_omnipublish(args):
    """处理 OmniPublish 国际发布"""
    target = args.target # dev, hashnode, or all
    logger.info(f"Deploying content to {target.upper()} via OmniPublish...")
    
    # 这里需要根据 OmniPublish 的具体 CLI 逻辑来调用
    # 假设它是通过 main.py 运行的
    script_dir = PATHS["omnipublish"]
    # 示例命令，需根据实际情况调整
    cmd = "python main.py" 
    run_command(cmd, cwd=script_dir, description=f"OmniPublish ({target})")

def handle_temp_api(args):
    """处理 Temp API 多账号发布"""
    account = args.account
    logger.info(f"Switching to Temp API Account: {account}")
    
    cwd = PATHS["temp_api"]
    # 假设 temp 目录下有对应账号的脚本，例如 account1.py
    # 或者有一个主脚本接收账号参数
    # 这里做一个模拟调用
    cmd = f"python main.py --account {account}"
    run_command(cmd, cwd=cwd, description=f"Temp API Publish ({account})")

def main():
    parser = argparse.ArgumentParser(description="Nexus Terminal Unified Dispatcher")
    subparsers = parser.add_subparsers(dest="command", help="Available modules")

    # WeChat Matrix Module
    wechat_parser = subparsers.add_parser("wechat", help="My_Wechat_Matrix automation")
    wechat_parser.add_argument("args", nargs="*", help="[gen|auto] [account|all] - default is post", default=[])
    
    # Fanqie Module
    fanqie_parser = subparsers.add_parser("fanqie", help="Fanqie Novel automation")
    fanqie_parser.add_argument("url", help="Novel URL (optional)", nargs="?")

    # OmniPublish Module
    omni_parser = subparsers.add_parser("publish", help="OmniPublish International")
    omni_parser.add_argument("target", choices=["dev", "hashnode", "all"], help="Target platform")
    
    # Temp API Module
    temp_parser = subparsers.add_parser("run", help="Temp API Multi-Account")
    temp_parser.add_argument("account", help="Account identifier (e.g., acc1, acc2)")

    args = parser.parse_args()

    if args.command == "wechat":
        handle_wechat(args.args)
    elif args.command == "fanqie":
        handle_fanqie(args)
    elif args.command == "publish":
        handle_omnipublish(args)
    elif args.command == "run":
        handle_temp_api(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    print("\033[1;33m") # Amber color
    print(r"""
    _   _ ________   ___   _ ___ 
   | \ | |  ____\ \ / / | | / __|
   |  \| | |__   \ V /| | | \__ \
   | . ` |  __|   > < | |_| |___/
   |_| \_|_____| /_/ \_\___/|___/
                                 
    Island Nexus System Online
    """)
    print("\033[0m")
    main()
