"""
Project N - 主程序入口
基于 ADB 的手机自动化控制系统
"""

import json
import time
import logging
from pathlib import Path
from skills.hand_v2 import HandCore
from skills.eye_v2 import EyeCore
from skills.brain_v2 import BrainCore
from skills.video_v2 import VideoCore

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/project_n.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProjectN:
    """Project N 主控制器"""
    
    def __init__(self):
        """初始化系统"""
        logger.info("=" * 50)
        logger.info("Project N 系统启动中...")
        logger.info("=" * 50)
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化核心模块
        self.hand = HandCore()
        self.eye = EyeCore()
        self.brain = BrainCore()
        self.video = VideoCore()
        
        # 检查 ADB 连接
        if not self.hand.check_connection():
            logger.error("❌ ADB 连接失败,请检查设备连接!")
            raise ConnectionError("无法连接到 ADB 设备")
        
        logger.info("✅ 所有模块初始化完成")
    
    def _load_config(self):
        """加载配置文件"""
        config_path = Path("configs/manifest.json")
        if not config_path.exists():
            logger.warning("⚠️ 配置文件不存在,使用默认配置")
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"📋 加载配置: {config.get('project_name')} v{config.get('version')}")
        return config
    
    def auto_browse_videos(self, duration_minutes=10):
        """
        自动刷视频模式
        
        Args:
            duration_minutes: 运行时长(分钟)
        """
        logger.info(f"🎬 开始自动刷视频模式,运行时长: {duration_minutes} 分钟")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        video_count = 0
        
        try:
            while time.time() < end_time:
                video_count += 1
                logger.info(f"\n--- 第 {video_count} 个视频 ---")
                
                # 1. 截取屏幕
                screenshot = self.eye.capture_screen()
                
                # 2. 分析内容
                analysis = self.brain.analyze(screenshot)
                logger.info(f"📊 内容分析: {analysis}")
                
                # 3. 决策: 是否观看完整视频
                watch_duration = self.brain.decide_watch_duration(analysis)
                logger.info(f"⏱️ 观看时长: {watch_duration} 秒")
                
                # 4. 等待观看
                time.sleep(watch_duration)
                
                # 5. 滑动到下一个视频
                self.hand.swipe_up()
                logger.info("👆 滑动到下一个视频")
                
                # 6. 短暂等待加载
                time.sleep(2)
        
        except KeyboardInterrupt:
            logger.info("\n⏸️ 用户中断操作")
        
        except Exception as e:
            logger.error(f"❌ 运行出错: {e}", exc_info=True)
        
        finally:
            elapsed = (time.time() - start_time) / 60
            logger.info(f"\n📊 运行统计:")
            logger.info(f"   - 总时长: {elapsed:.1f} 分钟")
            logger.info(f"   - 观看视频: {video_count} 个")
            logger.info(f"   - 平均速度: {video_count/elapsed:.1f} 个/分钟")
    
    def test_mode(self):
        """测试模式: 验证各个模块功能"""
        logger.info("\n🧪 进入测试模式\n")
        
        # 测试 1: 手部操作
        logger.info("测试 1: 点击屏幕中央")
        self.hand.tap(500, 1000)
        time.sleep(1)
        
        # 测试 2: 滑动操作
        logger.info("测试 2: 上滑操作")
        self.hand.swipe_up()
        time.sleep(1)
        
        # 测试 3: 截图功能
        logger.info("测试 3: 截取屏幕")
        screenshot = self.eye.capture_screen()
        if screenshot:
            logger.info(f"✅ 截图成功: {screenshot}")
        
        # 测试 4: 视频识别
        logger.info("测试 4: 视频状态检测")
        is_playing = self.video.is_video_playing()
        logger.info(f"视频播放状态: {is_playing}")
        
        logger.info("\n✅ 所有测试完成!")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Project N - 手机自动化控制系统')
    parser.add_argument('--mode', choices=['auto', 'test'], default='test',
                        help='运行模式: auto=自动刷视频, test=测试模式')
    parser.add_argument('--duration', type=int, default=10,
                        help='自动模式运行时长(分钟), 默认 10 分钟')
    
    args = parser.parse_args()
    
    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)
    
    # 初始化系统
    try:
        system = ProjectN()
        
        if args.mode == 'test':
            system.test_mode()
        elif args.mode == 'auto':
            system.auto_browse_videos(duration_minutes=args.duration)
    
    except Exception as e:
        logger.error(f"❌ 系统启动失败: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
