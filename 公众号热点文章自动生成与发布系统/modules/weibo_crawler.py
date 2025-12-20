# 微博爬虫模块
# 负责从微博平台获取热点话题和相关微博内容

import requests
import logging
import time
from datetime import datetime
from urllib.parse import quote

class WeiboCrawler:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('weibo_crawler')
        self.access_token = config['access_token']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        
    def get_hot_topics(self):
        """获取微博热门话题"""
        try:
            self.logger.info("开始获取微博热门话题")
            
            # 使用微博开放平台API获取热门话题
            # 实际应用中应使用微博开放平台的正式API
            # 以下为模拟实现
            
            # 热搜接口URL (实际应用中替换为真实API)
            url = "https://api.weibo.com/2/trends/hot.json"
            params = {
                'access_token': self.access_token,
                'count': self.config['topic_count']
            }
            
            # 发送请求
            # 注意：这里使用模拟数据，实际应用中应取消注释下面的代码
            # response = requests.get(url, params=params, headers=self.headers)
            # response.raise_for_status()
            # data = response.json()
            # topics = data.get('trends', [])
            
            # 模拟数据
            topics = self._get_mock_hot_topics()
            
            # 处理结果
            result = []
            for i, topic in enumerate(topics):
                result.append({
                    'topic_name': topic['name'],
                    'read_count': topic.get('read_count', 0),
                    'discussion_count': topic.get('discussion_count', 0),
                    'rank_index': i + 1
                })
            
            self.logger.info(f"成功获取 {len(result)} 个热门话题")
            return result
            
        except Exception as e:
            self.logger.error(f"获取微博热门话题失败: {str(e)}")
            return []
    
    def get_hot_weibos_by_topic(self, topic_name, count=None):
        """获取指定话题下的热门微博"""
        if count is None:
            count = self.config['weibo_count_per_topic']
            
        try:
            self.logger.info(f"开始获取话题 '{topic_name}' 下的热门微博")
            
            # 使用微博开放平台API获取话题下的热门微博
            # 实际应用中应使用微博开放平台的正式API
            # 以下为模拟实现
            
            # 话题搜索接口URL (实际应用中替换为真实API)
            url = "https://api.weibo.com/2/search/topics.json"
            params = {
                'access_token': self.access_token,
                'q': quote(topic_name),
                'count': count
            }
            
            # 发送请求
            # 注意：这里使用模拟数据，实际应用中应取消注释下面的代码
            # response = requests.get(url, params=params, headers=self.headers)
            # response.raise_for_status()
            # data = response.json()
            # weibos = data.get('statuses', [])
            
            # 模拟数据
            weibos = self._get_mock_weibos_by_topic(topic_name, count)
            
            # 处理结果
            result = []
            for weibo in weibos:
                result.append({
                    'weibo_id': weibo['id'],
                    'user_name': weibo['user']['name'],
                    'content': weibo['text'],
                    'publish_time': datetime.strptime(weibo['created_at'], '%a %b %d %H:%M:%S %z %Y'),
                    'like_count': weibo.get('attitudes_count', 0),
                    'repost_count': weibo.get('reposts_count', 0),
                    'comment_count': weibo.get('comments_count', 0)
                })
            
            self.logger.info(f"成功获取话题 '{topic_name}' 下的 {len(result)} 条热门微博")
            return result
            
        except Exception as e:
            self.logger.error(f"获取话题 '{topic_name}' 下的热门微博失败: {str(e)}")
            return []
    
    def _get_mock_hot_topics(self):
        """获取模拟的热门话题数据（仅用于开发测试）"""
        return [
            {
                'name': '#ChatGPT掀起AI热潮#',
                'read_count': 1200000,
                'discussion_count': 35000
            },
            {
                'name': '#年轻人为什么不愿意进工厂#',
                'read_count': 980000,
                'discussion_count': 28000
            },
            {
                'name': '#如何看待大学生就业难问题#',
                'read_count': 850000,
                'discussion_count': 22000
            },
            {
                'name': '#元宇宙是炒作还是未来#',
                'read_count': 760000,
                'discussion_count': 19000
            },
            {
                'name': '#数字人民币试点扩大#',
                'read_count': 680000,
                'discussion_count': 15000
            },
            {
                'name': '#如何平衡工作与生活#',
                'read_count': 620000,
                'discussion_count': 18000
            },
            {
                'name': '#电动汽车的未来发展#',
                'read_count': 580000,
                'discussion_count': 14000
            },
            {
                'name': '#直播带货新规实施#',
                'read_count': 520000,
                'discussion_count': 12000
            },
            {
                'name': '#中小学生减负政策效果#',
                'read_count': 490000,
                'discussion_count': 13000
            },
            {
                'name': '#远程办公是否会成为常态#',
                'read_count': 450000,
                'discussion_count': 11000
            }
        ]
    
    def _get_mock_weibos_by_topic(self, topic_name, count):
        """获取模拟的微博数据（仅用于开发测试）"""
        # 根据不同话题返回不同的模拟数据
        mock_data = {
            '#ChatGPT掀起AI热潮#': [
                {
                    'id': '4735291234567890',
                    'user': {'name': '科技前沿讨论'},
                    'text': 'ChatGPT的出现让我们看到了AI的巨大潜力，它不仅能写文章、编程，还能进行复杂的推理。这可能是继互联网之后最重要的技术革命！#ChatGPT掀起AI热潮#',
                    'created_at': 'Mon May 15 12:30:45 +0800 2023',
                    'attitudes_count': 3500,
                    'reposts_count': 1200,
                    'comments_count': 800
                },
                {
                    'id': '4735298765432109',
                    'user': {'name': 'AI研究员张明'},
                    'text': '作为AI领域的研究者，我认为ChatGPT的成功在于它的大规模预训练和人类反馈强化学习。但我们也要警惕AI可能带来的问题，如版权、隐私和伦理挑战。#ChatGPT掀起AI热潮#',
                    'created_at': 'Mon May 15 14:20:33 +0800 2023',
                    'attitudes_count': 2800,
                    'reposts_count': 950,
                    'comments_count': 620
                },
                {
                    'id': '4735302345678901',
                    'user': {'name': '互联网分析师'},
                    'text': 'ChatGPT已经引发了新一轮AI创业热潮，据统计，今年第一季度全球AI相关创业公司融资额同比增长了150%。大家都在思考：下一个颠覆性的AI应用会是什么？#ChatGPT掀起AI热潮#',
                    'created_at': 'Mon May 15 15:45:12 +0800 2023',
                    'attitudes_count': 2200,
                    'reposts_count': 780,
                    'comments_count': 520
                },
                {
                    'id': '4735309876543210',
                    'user': {'name': '教育创新者'},
                    'text': 'ChatGPT正在改变教育领域。一方面它可以作为个性化学习助手，另一方面也带来了学术诚信的挑战。我们需要重新思考考核评价方式。#ChatGPT掀起AI热潮#',
                    'created_at': 'Mon May 15 17:10:28 +0800 2023',
                    'attitudes_count': 1800,
                    'reposts_count': 650,
                    'comments_count': 480
                },
                {
                    'id': '4735315432109876',
                    'user': {'name': '普通网友小李'},
                    'text': '刚刚用ChatGPT帮我写了一份工作报告，效率提高了不少！不过我还是会进行修改和个性化，毕竟AI生成的内容还是有些公式化。#ChatGPT掀起AI热潮#',
                    'created_at': 'Mon May 15 18:30:55 +0800 2023',
                    'attitudes_count': 1500,
                    'reposts_count': 320,
                    'comments_count': 280
                }
            ],
            '#年轻人为什么不愿意进工厂#': [
                {
                    'id': '4736291234567890',
                    'user': {'name': '社会观察员'},
                    'text': '年轻人不愿进工厂，核心问题是性价比太低。长时间、高强度的体力劳动，却只有很低的薪资回报，没有职业发展空间，谁会愿意？#年轻人为什么不愿意进工厂#',
                    'created_at': 'Tue May 16 09:30:45 +0800 2023',
                    'attitudes_count': 4200,
                    'reposts_count': 1500,
                    'comments_count': 980
                },
                {
                    'id': '4736298765432109',
                    'user': {'name': '制造业从业者'},
                    'text': '作为一名在工厂工作了10年的人，我想说工厂工作环境确实在改善，但薪资增长跟不上物价和房价。年轻人有更多选择，自然会用脚投票。#年轻人为什么不愿意进工厂#',
                    'created_at': 'Tue May 16 10:20:33 +0800 2023',
                    'attitudes_count': 3800,
                    'reposts_count': 1200,
                    'comments_count': 850
                }
            ]
        }
        
        # 如果没有该话题的模拟数据，返回通用模拟数据
        if topic_name not in mock_data:
            return [
                {
                    'id': f'47360000{i}',
                    'user': {'name': f'用户{i}'},
                    'text': f'关于「{topic_name}」的模拟微博内容 {i}。这是一条测试数据，用于系统开发阶段。',
                    'created_at': 'Wed May 17 12:00:00 +0800 2023',
                    'attitudes_count': 1000 - i * 100,
                    'reposts_count': 500 - i * 50,
                    'comments_count': 300 - i * 30
                } for i in range(1, count + 1)
            ]
        
        # 返回指定话题的模拟数据
        return mock_data[topic_name][:count]