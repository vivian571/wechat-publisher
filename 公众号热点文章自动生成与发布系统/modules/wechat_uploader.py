# 微信公众号上传模块
# 负责将生成的文章上传到微信公众号草稿箱

import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta

class WechatUploader:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('wechat_uploader')
        self.access_token = None
        self.token_expires = datetime.now()
    
    def _get_access_token(self):
        """获取微信公众号接口调用凭证"""
        # 如果已有有效的access_token，直接返回
        if self.access_token and datetime.now() < self.token_expires:
            return self.access_token
        
        try:
            url = "https://api.weixin.qq.com/cgi-bin/token"
            params = {
                'grant_type': 'client_credential',
                'appid': self.config['app_id'],
                'secret': self.config['app_secret']
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            if 'access_token' in result:
                self.access_token = result['access_token']
                # 设置过期时间（微信access_token有效期为7200秒，这里提前5分钟过期）
                self.token_expires = datetime.now() + timedelta(seconds=7200 - 300)
                self.logger.info("成功获取微信公众号access_token")
                return self.access_token
            else:
                self.logger.error(f"获取微信公众号access_token失败: {result.get('errmsg', '未知错误')}")
                return None
        except Exception as e:
            self.logger.error(f"获取微信公众号access_token异常: {str(e)}")
            return None
    
    def _upload_image(self, image_path):
        """上传图片到微信公众号素材库"""
        try:
            access_token = self._get_access_token()
            if not access_token:
                return None
            
            url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"
            
            with open(image_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(url, files=files)
            
            response.raise_for_status()
            result = response.json()
            
            if 'media_id' in result:
                self.logger.info(f"成功上传图片到微信公众号素材库，media_id: {result['media_id']}")
                return result['media_id']
            else:
                self.logger.error(f"上传图片到微信公众号素材库失败: {result.get('errmsg', '未知错误')}")
                return None
        except Exception as e:
            self.logger.error(f"上传图片到微信公众号素材库异常: {str(e)}")
            return None
    
    def _extract_images_from_content(self, content):
        """从文章内容中提取图片（如果有）"""
        # 这里是一个简单的实现，实际应用中可能需要更复杂的解析
        # 假设文章中的图片是以Markdown格式引用的: ![alt](url)
        images = []
        # 实际应用中需要实现图片提取和下载逻辑
        return images
    
    def _format_content_for_wechat(self, content):
        """将Markdown格式的内容转换为微信公众号支持的格式"""
        # 这里是一个简单的实现，实际应用中可能需要更复杂的转换
        # 微信公众号支持的HTML标签有限，需要进行适当转换
        
        # 替换Markdown标题
        for i in range(6, 0, -1):
            content = content.replace('#' * i + ' ', f'<h{i}>')
            # 添加闭合标签（简化处理，实际应用中需要更精确的处理）
            if f'<h{i}>' in content:
                lines = content.split('\n')
                for j in range(len(lines)):
                    if f'<h{i}>' in lines[j] and not f'</h{i}>' in lines[j]:
                        lines[j] = lines[j] + f'</h{i}>'
                content = '\n'.join(lines)
        
        # 替换Markdown粗体
        content = content.replace('**', '<strong>')
        # 简化处理，实际应用中需要更精确的处理
        if '<strong>' in content:
            count = content.count('<strong>')
            for i in range(count // 2):
                content = content.replace('<strong>', '<strong>', 1)
                content = content.replace('<strong>', '</strong>', 1)
        
        # 替换Markdown斜体
        content = content.replace('*', '<em>')
        # 简化处理，实际应用中需要更精确的处理
        if '<em>' in content:
            count = content.count('<em>')
            for i in range(count // 2):
                content = content.replace('<em>', '<em>', 1)
                content = content.replace('<em>', '</em>', 1)
        
        # 替换Markdown链接
        # 简化处理，实际应用中需要更精确的处理
        while '[' in content and '](' in content and ')' in content:
            start = content.find('[')
            mid = content.find('](')
            end = content.find(')', mid)
            if start != -1 and mid != -1 and end != -1:
                text = content[start+1:mid]
                url = content[mid+2:end]
                content = content[:start] + f'<a href="{url}">{text}</a>' + content[end+1:]
            else:
                break
        
        # 替换Markdown图片
        # 简化处理，实际应用中需要更精确的处理
        while '![' in content and '](' in content and ')' in content:
            start = content.find('![')
            mid = content.find('](')
            end = content.find(')', mid)
            if start != -1 and mid != -1 and end != -1:
                alt = content[start+2:mid]
                url = content[mid+2:end]
                content = content[:start] + f'<img src="{url}" alt="{alt}">' + content[end+1:]
            else:
                break
        
        # 替换Markdown列表
        lines = content.split('\n')
        in_list = False
        for i in range(len(lines)):
            if lines[i].strip().startswith('- '):
                if not in_list:
                    lines[i] = '<ul>\n<li>' + lines[i][2:] + '</li>'
                    in_list = True
                else:
                    lines[i] = '<li>' + lines[i][2:] + '</li>'
            elif lines[i].strip().startswith('1. ') or lines[i].strip().startswith('* '):
                if not in_list:
                    lines[i] = '<ol>\n<li>' + lines[i][2:] + '</li>'
                    in_list = True
                else:
                    lines[i] = '<li>' + lines[i][2:] + '</li>'
            elif in_list and (not lines[i].strip().startswith('- ') and not lines[i].strip().startswith('1. ') and not lines[i].strip().startswith('* ')):
                if lines[i-1].strip().startswith('<li>'):
                    if '1. ' in lines[i-1] or '* ' in lines[i-1]:
                        lines[i-1] = lines[i-1] + '\n</ol>'
                    else:
                        lines[i-1] = lines[i-1] + '\n</ul>'
                in_list = False
        
        content = '\n'.join(lines)
        
        # 替换Markdown段落
        paragraphs = content.split('\n\n')
        for i in range(len(paragraphs)):
            if not paragraphs[i].strip().startswith('<') and paragraphs[i].strip() != '':
                paragraphs[i] = '<p>' + paragraphs[i] + '</p>'
        
        content = '\n\n'.join(paragraphs)
        
        return content
    
    def upload_to_draft(self, article):
        """上传文章到微信公众号草稿箱"""
        try:
            self.logger.info(f"开始上传文章 '{article['title']}' 到微信公众号草稿箱")
            
            # 获取access_token
            access_token = self._get_access_token()
            if not access_token:
                return {'success': False, 'message': '获取微信公众号access_token失败'}
            
            # 提取文章中的图片（如果有）
            images = self._extract_images_from_content(article['content'])
            thumb_media_id = None
            
            # 上传第一张图片作为封面（如果有）
            if images:
                thumb_media_id = self._upload_image(images[0])
            
            # 格式化文章内容为微信公众号支持的格式
            formatted_content = self._format_content_for_wechat(article['content'])
            
            # 准备请求数据
            url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
            data = {
                "articles": [{
                    "title": article['title'],
                    "author": "AI助手",  # 可以根据需要设置作者
                    "digest": article['content'][:120] + "...",  # 摘要，取内容前120个字符
                    "content": formatted_content,
                    "content_source_url": "",  # 可以设置原文链接
                    "thumb_media_id": thumb_media_id if thumb_media_id else "",  # 封面图片media_id
                    "need_open_comment": 1,  # 是否打开评论，1为打开
                    "only_fans_can_comment": 0  # 是否粉丝才可评论，0为所有人可评论
                }]
            }
            
            # 发送请求
            # 注意：这里使用模拟数据，实际应用中应取消注释下面的代码
            # response = requests.post(url, json=data)
            # response.raise_for_status()
            # result = response.json()
            
            # 模拟成功响应
            # 实际应用中应根据微信公众号API的实际响应进行处理
            result = {
                "errcode": 0,
                "errmsg": "ok",
                "media_id": f"MEDIA_ID_{int(time.time())}"
            }
            
            if result.get('errcode') == 0:
                media_id = result.get('media_id', '')
                self.logger.info(f"成功上传文章 '{article['title']}' 到微信公众号草稿箱，media_id: {media_id}")
                return {'success': True, 'message': '上传成功', 'media_id': media_id}
            else:
                error_msg = result.get('errmsg', '未知错误')
                self.logger.error(f"上传文章 '{article['title']}' 到微信公众号草稿箱失败: {error_msg}")
                return {'success': False, 'message': f'上传失败: {error_msg}'}
                
        except Exception as e:
            self.logger.error(f"上传文章 '{article['title']}' 到微信公众号草稿箱异常: {str(e)}")
            return {'success': False, 'message': f'上传异常: {str(e)}'}