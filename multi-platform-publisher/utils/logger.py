import logging
import sys
from typing import Optional

class DefaultAccountFilter(logging.Filter):
    """为没有 account_name 的日志记录提供默认值"""
    def filter(self, record):
        if not hasattr(record, 'account_name'):
            record.account_name = 'System'
        return True

class AccountLogFilter(logging.Filter):
    """用于为日志记录添加特定的账户名"""
    def __init__(self, account_name):
        super().__init__()
        self.account_name = account_name
    
    def filter(self, record):
        record.account_name = self.account_name
        return True

LOGGING_CONFIGURED = False

def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None):
    """
    配置日志系统
    
    Args:
        level: 日志级别，默认为INFO
        log_file: 日志文件路径，如果为None则只输出到控制台
    """
    global LOGGING_CONFIGURED
    if LOGGING_CONFIGURED:
        return

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(account_name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 移除所有现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台处理器
    default_filter = DefaultAccountFilter()
    
    # 创建一个包装器函数来处理控制台输出的编码问题
    class UnicodeStreamHandler(logging.StreamHandler):
        def emit(self, record):
            try:
                msg = self.format(record)
                stream = self.stream
                # 尝试使用控制台编码，如果失败则使用utf-8
                try:
                    stream.write(msg + self.terminator)
                except UnicodeEncodeError:
                    stream.buffer.write((msg + self.terminator).encode('utf-8'))
                    stream.flush()
                self.flush()
            except Exception:
                self.handleError(record)
    
    # 使用自定义的StreamHandler
    console_handler = UnicodeStreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(default_filter)
    root_logger.addHandler(console_handler)
    
    # 如果需要，添加文件处理器
    if log_file:
        try:
            import os
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 使用 utf-8 编码写入日志文件
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.addFilter(default_filter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"创建日志文件处理器时出错: {e}", file=sys.stderr)
    
    
    # 配置第三方库的日志级别
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('markdown').setLevel(logging.WARNING)

    LOGGING_CONFIGURED = True

def get_logger(name: str, account_name: str = 'System') -> logging.Logger:
    """
    获取带有账户名称的日志记录器
    
    Args:
        name: 日志记录器名称
        account_name: 账户名称
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    # 注意：不再手动添加处理器，因为它们会从根记录器继承。
    # 我们只为这个特定的 logger 实例的上下文添加一个过滤器。
    # 但由于过滤器是应用在处理器上的，更好的方式是在 BasePublisher 中动态添加/移除过滤器
    # 或者在日志消息中通过 extra 参数传递 account_name。
    # 为简单起见，我们依赖根记录器的处理器和过滤器。
    # 如果需要为特定 logger 设置不同的过滤器，需要更复杂的逻辑。
    # 目前，BasePublisher 中的实现（为每个实例的 logger 添加过滤器）是有效的。 

    
    return logger
