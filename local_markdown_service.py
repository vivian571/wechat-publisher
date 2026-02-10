#!/usr/bin/env python3
"""
本地Markdown转图片服务
替代md2 API的解决方案
"""
import os
import sys
import json
import base64
from pathlib import Path
from io import BytesIO
import logging
from flask import Flask, request, jsonify
from enhanced_markdown_converter import EnhancedMarkdownToImageConverter
from quick_tech_blood import SimpleTechBloodConverter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class LocalMarkdownService:
    """本地Markdown转图片服务"""
    
    def __init__(self):
        self.converter = EnhancedMarkdownToImageConverter()
        self.tech_converter = SimpleTechBloodConverter()  # 热血技术风格转换器
        self.temp_dir = Path("/tmp/md_images")
        self.temp_dir.mkdir(exist_ok=True)
    
    def convert_markdown_to_base64(self, markdown_content):
        """将Markdown转换为base64图片"""
        try:
            # 生成临时文件名
            import uuid
            temp_filename = f"md_{uuid.uuid4().hex}.png"
            temp_path = self.temp_dir / temp_filename
            
            # 检测是否为技术风格内容
            if self._is_tech_content(markdown_content):
                logger.info("检测到技术风格内容，使用热血技术风格转换器")
                # 使用热血技术风格转换器
                success = self.tech_converter.create_simple_tech_image(
                    markdown_content, 
                    str(temp_path)
                )
            else:
                logger.info("使用标准转换器")
                # 使用标准转换器
                success = self.converter.convert_markdown_to_image(
                    markdown_content, 
                    str(temp_path)
                )
            
            if not success:
                return None, "转换失败"
            
            # 读取图片并转换为base64
            with open(temp_path, 'rb') as img_file:
                img_data = img_file.read()
                base64_data = base64.b64encode(img_data).decode('utf-8')
            
            # 清理临时文件
            try:
                temp_path.unlink()
            except:
                pass
            
            return base64_data, None
            
        except Exception as e:
            logger.error(f"转换过程出错: {e}")
            return None, str(e)
    
    def _is_tech_content(self, markdown_content):
        """检测是否为技术风格内容"""
        content_lower = markdown_content.lower()
        
        # 技术关键词检测
        tech_keywords = [
            'docker', 'github', '开源', '监控', 'api', '代码', '编程',
            '服务器', '部署', '配置', 'bash', 'python', 'linux',
            '免费', '神器', '火了', '技术', '开发', '工具'
        ]
        
        # 热血风格关键词
        blood_keywords = [
            '🔥', '⚡', '🚀', '💻', '🎯', '💰', '🔒', '⚙️',
            '别再', '付费', '慌了', '火了', '神器', '推荐'
        ]
        
        # 检查是否包含技术或热血关键词
        has_tech = any(keyword in content_lower for keyword in tech_keywords)
        has_blood = any(keyword in markdown_content for keyword in blood_keywords)
        
        # 如果包含热血风格emoji或强烈的技术内容，使用热血风格
        return has_blood or (has_tech and len(markdown_content) > 100)
    
    def convert_markdown_to_file(self, markdown_content, output_path):
        """将Markdown转换为图片文件"""
        try:
            success = self.converter.convert_markdown_to_image(
                markdown_content, 
                output_path
            )
            return success, None if success else "转换失败"
            
        except Exception as e:
            logger.error(f"转换过程出错: {e}")
            return False, str(e)

# 初始化服务
service = LocalMarkdownService()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "local-markdown-converter",
        "version": "1.0.0"
    })

@app.route('/convert', methods=['POST'])
def convert_markdown():
    """Markdown转换接口"""
    try:
        data = request.get_json()
        
        if not data or 'markdown' not in data:
            return jsonify({
                "code": 400,
                "msg": "缺少markdown参数"
            }), 400
        
        markdown_content = data['markdown']
        theme = data.get('theme', 'default')
        
        logger.info(f"收到转换请求，主题: {theme}, 内容长度: {len(markdown_content)}")
        
        # 转换为base64图片
        base64_image, error = service.convert_markdown_to_base64(markdown_content)
        
        if base64_image:
            return jsonify({
                "code": 200,
                "msg": "转换成功",
                "data": {
                    "image": f"data:image/png;base64,{base64_image}",
                    "format": "png",
                    "theme": theme
                }
            })
        else:
            return jsonify({
                "code": 500,
                "msg": f"转换失败: {error}"
            }), 500
            
    except Exception as e:
        logger.error(f"转换接口出错: {e}")
        return jsonify({
            "code": 500,
            "msg": f"服务器错误: {str(e)}"
        }), 500

@app.route('/convert/file', methods=['POST'])
def convert_to_file():
    """转换并保存为文件"""
    try:
        data = request.get_json()
        
        if not data or 'markdown' not in data or 'output_path' not in data:
            return jsonify({
                "code": 400,
                "msg": "缺少必要参数"
            }), 400
        
        markdown_content = data['markdown']
        output_path = data['output_path']
        
        logger.info(f"收到文件转换请求，输出路径: {output_path}")
        
        # 转换并保存为文件
        success, error = service.convert_markdown_to_file(markdown_content, output_path)
        
        if success:
            return jsonify({
                "code": 200,
                "msg": "转换成功",
                "data": {
                    "file_path": output_path
                }
            })
        else:
            return jsonify({
                "code": 500,
                "msg": f"转换失败: {error}"
            }), 500
            
    except Exception as e:
        logger.error(f"文件转换接口出错: {e}")
        return jsonify({
            "code": 500,
            "msg": f"服务器错误: {str(e)}"
        }), 500

def main():
    """启动服务"""
    port = int(os.environ.get('PORT', 8081))
    host = os.environ.get('HOST', 'localhost')
    
    logger.info(f"启动本地Markdown转换服务...")
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"健康检查: http://{host}:{port}/health")
    logger.info(f"转换接口: POST http://{host}:{port}/convert")
    
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    main()