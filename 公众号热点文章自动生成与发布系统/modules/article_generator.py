# 文章生成模块
# 负责根据微博热点话题和相关微博内容生成文章

import os
import json
import logging
import requests
from datetime import datetime

class ArticleGenerator:
    def __init__(self, config, path_config):
        self.config = config
        self.path_config = path_config
        self.logger = logging.getLogger('article_generator')
        
        # 确保文章存储目录和提示词目录存在
        os.makedirs(path_config['article_dir'], exist_ok=True)
        os.makedirs(path_config['prompt_dir'], exist_ok=True)
        
        # 初始化默认提示词模板
        self._init_default_prompts()
    
    def _init_default_prompts(self):
        """初始化默认提示词模板"""
        default_prompt_file = os.path.join(self.path_config['prompt_dir'], 'default_prompt.json')
        
        # 如果默认提示词文件不存在，则创建
        if not os.path.exists(default_prompt_file):
            default_prompt = {
                'system': "你是一位专业的新媒体文章撰写专家，擅长将热点话题转化为有深度、有见解的文章。",
                'article_template': """请根据以下微博热点话题及相关微博内容，撰写一篇有深度的分析文章：

话题：{topic_name}

相关微博内容：
{weibo_contents}

要求：
1. 文章标题需要吸引人，能够引起读者的阅读兴趣
2. 文章需要包含引言、主体和结论三部分
3. 引言部分需要简要介绍话题背景和引起读者的兴趣
4. 主体部分需要分析话题的多个角度，包括原因分析、现状描述、影响评估等
5. 结论部分需要给出你的观点和建议
6. 文章风格要专业、客观，但也要有温度，能引起读者的共鸣
7. 文章长度在1500-2000字之间
8. 请确保文章有清晰的段落划分，可读性强
9. 返回格式为JSON，包含title和content两个字段"""
            }
            
            # 写入默认提示词文件
            with open(default_prompt_file, 'w', encoding='utf-8') as f:
                json.dump(default_prompt, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"已创建默认提示词模板: {default_prompt_file}")
    
    def _load_prompt_template(self, topic_category=None):
        """加载提示词模板，可以根据话题类别加载不同的模板"""
        # 如果指定了话题类别，尝试加载对应的提示词模板
        if topic_category:
            category_prompt_file = os.path.join(self.path_config['prompt_dir'], f'{topic_category}_prompt.json')
            if os.path.exists(category_prompt_file):
                try:
                    with open(category_prompt_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    self.logger.error(f"加载话题类别提示词模板失败: {str(e)}")
        
        # 加载默认提示词模板
        default_prompt_file = os.path.join(self.path_config['prompt_dir'], 'default_prompt.json')
        try:
            with open(default_prompt_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载默认提示词模板失败: {str(e)}")
            
            # 返回硬编码的默认提示词
            return {
                'system': "你是一位专业的新媒体文章撰写专家，擅长将热点话题转化为有深度、有见解的文章。",
                'article_template': "请根据微博热点话题及相关微博内容，撰写一篇有深度的分析文章。"
            }
    
    def _categorize_topic(self, topic_name):
        """简单的话题分类，可以根据关键词判断话题类别"""
        # 这里是一个简单的实现，实际应用中可以使用更复杂的分类算法
        topic_lower = topic_name.lower()
        
        if any(kw in topic_lower for kw in ['ai', '人工智能', '机器学习', '深度学习', 'chatgpt']):
            return 'technology'
        elif any(kw in topic_lower for kw in ['经济', '金融', '股市', '理财', '投资']):
            return 'finance'
        elif any(kw in topic_lower for kw in ['教育', '学校', '学生', '考试', '升学']):
            return 'education'
        elif any(kw in topic_lower for kw in ['健康', '医疗', '疾病', '养生', '保健']):
            return 'health'
        elif any(kw in topic_lower for kw in ['娱乐', '明星', '电影', '音乐', '综艺']):
            return 'entertainment'
        
        return None
    
    def _call_openai_api(self, system_prompt, user_prompt):
        """调用OpenAI API生成文章"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.config['model_name'],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": self.config['temperature'],
                "max_tokens": self.config['max_tokens']
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            return result['choices'][0]['message']['content']
        except Exception as e:
            self.logger.error(f"调用OpenAI API失败: {str(e)}")
            return None
    
    def _call_baidu_api(self, system_prompt, user_prompt):
        """调用百度文心一言API生成文章"""
        try:
            # 这里是百度文心一言API的调用实现
            # 实际应用中需要根据百度文心一言的API文档进行实现
            self.logger.warning("百度文心一言API调用尚未实现，返回模拟数据")
            
            # 返回模拟数据
            return json.dumps({
                "title": "模拟生成的文章标题",
                "content": "这是一篇由模拟的百度文心一言API生成的文章内容。\n\n这里是第一段落...\n\n这里是第二段落..."
            }, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"调用百度文心一言API失败: {str(e)}")
            return None
    
    def _call_local_model(self, system_prompt, user_prompt):
        """调用本地模型生成文章"""
        try:
            # 这里是本地模型的调用实现
            # 实际应用中需要根据本地模型的接口进行实现
            self.logger.warning("本地模型调用尚未实现，返回模拟数据")
            
            # 返回模拟数据
            return json.dumps({
                "title": "模拟生成的文章标题",
                "content": "这是一篇由模拟的本地模型生成的文章内容。\n\n这里是第一段落...\n\n这里是第二段落..."
            }, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"调用本地模型失败: {str(e)}")
            return None
    
    def _call_model_api(self, system_prompt, user_prompt):
        """根据配置调用不同的模型API"""
        model_type = self.config['model_type'].lower()
        
        if model_type == 'openai':
            return self._call_openai_api(system_prompt, user_prompt)
        elif model_type == 'baidu':
            return self._call_baidu_api(system_prompt, user_prompt)
        elif model_type == 'local':
            return self._call_local_model(system_prompt, user_prompt)
        else:
            self.logger.error(f"不支持的模型类型: {model_type}")
            return None
    
    def generate_article(self, topic, weibos):
        """根据话题和微博内容生成文章"""
        try:
            self.logger.info(f"开始为话题 '{topic['topic_name']}' 生成文章")
            
            # 获取话题类别
            topic_category = self._categorize_topic(topic['topic_name'])
            
            # 加载提示词模板
            prompt_template = self._load_prompt_template(topic_category)
            
            # 准备微博内容
            weibo_contents = "\n\n".join([f"用户 {weibo['user_name']} 发布：{weibo['content']}" for weibo in weibos])
            
            # 准备用户提示词
            user_prompt = prompt_template['article_template'].format(
                topic_name=topic['topic_name'],
                weibo_contents=weibo_contents
            )
            
            # 调用模型API生成文章
            response = self._call_model_api(prompt_template['system'], user_prompt)
            
            if not response:
                self.logger.error(f"为话题 '{topic['topic_name']}' 生成文章失败")
                return None
            
            # 解析响应
            try:
                # 尝试解析JSON格式的响应
                article_data = json.loads(response)
                title = article_data.get('title', f"关于「{topic['topic_name']}」的分析")
                content = article_data.get('content', "")
            except json.JSONDecodeError:
                # 如果不是JSON格式，则尝试从文本中提取标题和内容
                lines = response.strip().split('\n')
                title = lines[0].strip().replace('#', '').strip() if lines else f"关于「{topic['topic_name']}」的分析"
                content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else response
            
            # 保存文章到文件
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{topic['id']}.md"
            file_path = os.path.join(self.path_config['article_dir'], filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n{content}")
            
            self.logger.info(f"成功为话题 '{topic['topic_name']}' 生成文章，保存至 {file_path}")
            
            # 返回文章数据
            return {
                'topic_id': topic['id'],
                'title': title,
                'content': content,
                'file_path': file_path
            }
            
        except Exception as e:
            self.logger.error(f"生成文章过程中发生错误: {str(e)}")
            return None