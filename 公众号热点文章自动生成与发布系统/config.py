# 配置文件

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',
    'database': 'weibo_articles',
    'charset': 'utf8mb4'
}

# 微博API配置
WEIBO_CONFIG = {
    'app_key': 'your_app_key',  # 替换为您的微博开放平台应用密钥
    'app_secret': 'your_app_secret',  # 替换为您的微博开放平台应用密钥
    'redirect_uri': 'your_redirect_uri',  # 回调地址
    'access_token': 'your_access_token',  # 访问令牌
    # 热门话题获取数量
    'topic_count': 10,
    # 每个话题下获取的热门微博数量
    'weibo_count_per_topic': 5,
    # 抓取时间间隔(秒)
    'crawl_interval': 3600
}

# 文本生成模型配置
AI_MODEL_CONFIG = {
    'model_type': 'openai',  # 可选: 'openai', 'baidu', 'local'
    'api_key': 'your_api_key',  # API密钥
    'model_name': 'gpt-3.5-turbo',  # 模型名称
    'temperature': 0.7,  # 创造性参数
    'max_tokens': 2000,  # 最大生成长度
    # 文章生成间隔(秒)
    'generation_interval': 1800
}

# 微信公众号配置
WECHAT_CONFIG = {
    'app_id': 'your_app_id',  # 公众号AppID
    'app_secret': 'your_app_secret',  # 公众号AppSecret
    'upload_interval': 3600,  # 上传间隔(秒)
}

# 文件路径配置
PATH_CONFIG = {
    'data_dir': './data',  # 数据存储目录
    'prompt_dir': './prompts',  # 提示词文件目录
    'article_dir': './articles',  # 生成文章存储目录
    'log_dir': './logs'  # 日志目录
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}