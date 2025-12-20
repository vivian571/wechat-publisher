from wechat import WeChatAPI
import markdown_processor

def publish_article(md_path):
    # 初始化微信接口
    wx = WeChatAPI(app_id=config.APP_ID, 
                  app_secret=config.APP_SECRET)
    
    # 转换Markdown
    content = markdown_processor.convert(md_path)
    
    # 上传素材
    media_id = wx.upload_media(content.images)
    
    # 发布文章
    return wx.create_draft(
        title=content.title,
        content=content.body,
        cover_media_id=media_id
    )