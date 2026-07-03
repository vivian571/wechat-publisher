# <font color='OrangeRed'><b>Python一键自动发布抖音视频！小白也能学会的保姆级教程</b></font>

<font color='Purple'><b>不想看长篇大论？直接拿走这段代码，一键发布抖音视频！</b></font>

```python
# 抖音视频自动发布工具
import requests
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DouyinPublisher:
    def __init__(self, cookie_path=None):
        self.cookies_path = cookie_path or "douyin_cookies.json"
        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_argument("--start-maximized")
        # 无头模式，可选
        # self.browser_options.add_argument("--headless")
        self.driver = None
        
    def login(self, auto_save=True):
        """登录抖音创作者平台"""
        print("🚀 正在启动浏览器...")
        self.driver = webdriver.Chrome(options=self.browser_options)
        self.driver.get("https://creator.douyin.com/")
        
        # 尝试加载已保存的cookies
        if os.path.exists(self.cookies_path):
            print("📂 发现已保存的登录信息，尝试自动登录...")
            try:
                with open(self.cookies_path, "r") as f:
                    cookies = json.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.refresh()
                time.sleep(3)
                
                # 检查是否成功登录
                if "创作者" in self.driver.title:
                    print("✅ 自动登录成功！")
                    return True
                else:
                    print("❌ 自动登录失败，请手动登录...")
            except Exception as e:
                print(f"❌ 加载cookies失败: {e}")
        
        # 手动登录
        print("👉 请在60秒内完成手动登录...")
        wait = WebDriverWait(self.driver, 60)
        wait.until(EC.title_contains("创作者"))
        
        if auto_save:
            # 保存cookies
            cookies = self.driver.get_cookies()
            with open(self.cookies_path, "w") as f:
                json.dump(cookies, f)
            print("💾 已保存登录信息，下次可自动登录")
        
        return True
    
    def publish_video(self, video_path, title, tags=None):
        """发布视频到抖音"""
        if not self.driver:
            raise Exception("请先调用login()方法登录")
            
        # 进入发布页面
        print("🎬 准备发布视频...")
        self.driver.get("https://creator.douyin.com/creator-micro/content/upload")
        time.sleep(3)
        
        # 上传视频
        print("📤 正在上传视频...")
        upload_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        upload_input.send_keys(os.path.abspath(video_path))
        
        # 等待视频上传完成
        wait = WebDriverWait(self.driver, 120)
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".upload-progress")))  
        print("✅ 视频上传完成！")
        
        # 填写标题
        print("📝 正在填写视频信息...")
        title_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".DraftEditor-root")))
        title_input.click()
        title_input.send_keys(title)
        
        # 添加标签
        if tags:
            tag_input = self.driver.find_element(By.CSS_SELECTOR, ".tag-input")
            for tag in tags:
                tag_input.click()
                tag_input.send_keys(tag)
                tag_input.send_keys("\n")
                time.sleep(0.5)
        
        # 点击发布按钮
        print("🚀 正在发布视频...")
        publish_btn = self.driver.find_element(By.CSS_SELECTOR, ".publish-btn")
        publish_btn.click()
        
        # 等待发布完成
        wait.until(EC.url_contains("content/manage"))
        print("🎉 视频发布成功！")
        return True
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None

# 使用示例
if __name__ == "__main__":
    # 创建发布器实例
    publisher = DouyinPublisher()
    
    try:
        # 登录
        publisher.login()
        
        # 发布视频
        video_path = input("请输入视频文件路径: ")
        title = input("请输入视频标题: ")
        tags_input = input("请输入标签(用逗号分隔): ")
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else None
        
        publisher.publish_video(video_path, title, tags)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        publisher.close()
```

![](https://images.pexels.com/photos/7014337/pexels-photo-7014337.jpeg)

<font color='DeepSkyBlue'><b>每天手动发抖音太麻烦？</b></font>

<font color='DeepSkyBlue'><b>想批量发布视频却不知道怎么操作？</b></font>

<font color='DeepSkyBlue'><b>Python小白也能看懂的抖音自动发布教程来了！</b></font>

![](https://images.pexels.com/photos/4050315/pexels-photo-4050315.jpeg)

## <font color='Purple'><b>一、为什么要用Python自动发布抖音视频？</b></font>

<font color='Green'><b>省时省力，一键发布几十个视频！</b></font>

<font color='Green'><b>定时发布，让你的账号保持活跃度！</b></font>

<font color='Green'><b>批量管理，再也不用手忙脚乱！</b></font>

<font color='Green'><b>解放双手，躺着也能当自媒体！</b></font>

![](https://images.pexels.com/photos/7256897/pexels-photo-7256897.jpeg)

## <font color='DeepSkyBlue'><b>二、准备工作：只需这几样东西</b></font>

<font color='Orange'><b>1. 一台电脑（Windows/Mac都行）</b></font>

<font color='Orange'><b>2. Python环境（不会装？往下看！）</b></font>

<font color='Orange'><b>3. Chrome浏览器</b></font>

<font color='Orange'><b>4. 抖音账号（创作者）</b></font>

<font color='Orange'><b>5. 要发布的视频文件</b></font>

![](https://images.pexels.com/photos/4050288/pexels-photo-4050288.jpeg)

## <font color='DeepSkyBlue'><b>三、环境安装：超简单三步走</b></font>

<font color='Purple'><b>第一步：安装Python</b></font>

去Python官网(https://www.python.org/downloads/)下载最新版本。

安装时记得勾选「Add Python to PATH」！

<font color='Purple'><b>第二步：安装必要的库</b></font>

打开命令提示符（Windows）或终端（Mac），输入：

```bash
pip install selenium requests webdriver-manager
```

<font color='Purple'><b>第三步：安装Chrome浏览器</b></font>

如果还没有Chrome浏览器，去官网下载安装一个。

![](https://images.pexels.com/photos/4050290/pexels-photo-4050290.jpeg)

## <font color='DeepSkyBlue'><b>四、代码详解：看这一篇就够了</b></font>

### <font color='Purple'><b>1. 整体思路</b></font>

<font color='Green'><b>我们用Selenium模拟真人操作抖音创作者平台。</b></font>

<font color='Green'><b>自动完成登录、上传视频、填写信息、点击发布等操作。</b></font>

<font color='Green'><b>还能保存登录状态，下次使用不用重复登录！</b></font>

### <font color='Purple'><b>2. 代码结构</b></font>

<font color='Blue'><b>DouyinPublisher类：核心功能类</b></font>

<font color='Blue'><b>login方法：处理登录逻辑</b></font>

<font color='Blue'><b>publish_video方法：发布视频</b></font>

<font color='Blue'><b>close方法：关闭浏览器</b></font>

### <font color='Purple'><b>3. 关键代码解析</b></font>

<font color='Orange'><b>自动登录功能：</b></font>

```python
def login(self, auto_save=True):
    """登录抖音创作者平台"""
    print("🚀 正在启动浏览器...")
    self.driver = webdriver.Chrome(options=self.browser_options)
    self.driver.get("https://creator.douyin.com/")
    
    # 尝试加载已保存的cookies
    if os.path.exists(self.cookies_path):
        print("📂 发现已保存的登录信息，尝试自动登录...")
        try:
            with open(self.cookies_path, "r") as f:
                cookies = json.load(f)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            time.sleep(3)
            
            # 检查是否成功登录
            if "创作者" in self.driver.title:
                print("✅ 自动登录成功！")
                return True
            else:
                print("❌ 自动登录失败，请手动登录...")
        except Exception as e:
            print(f"❌ 加载cookies失败: {e}")
    
    # 手动登录
    print("👉 请在60秒内完成手动登录...")
    wait = WebDriverWait(self.driver, 60)
    wait.until(EC.title_contains("创作者"))
    
    if auto_save:
        # 保存cookies
        cookies = self.driver.get_cookies()
        with open(self.cookies_path, "w") as f:
            json.dump(cookies, f)
        print("💾 已保存登录信息，下次可自动登录")
    
    return True
```

<font color='Orange'><b>视频发布功能：</b></font>

```python
def publish_video(self, video_path, title, tags=None):
    """发布视频到抖音"""
    if not self.driver:
        raise Exception("请先调用login()方法登录")
        
    # 进入发布页面
    print("🎬 准备发布视频...")
    self.driver.get("https://creator.douyin.com/creator-micro/content/upload")
    time.sleep(3)
    
    # 上传视频
    print("📤 正在上传视频...")
    upload_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    upload_input.send_keys(os.path.abspath(video_path))
    
    # 等待视频上传完成
    wait = WebDriverWait(self.driver, 120)
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".upload-progress")))  
    print("✅ 视频上传完成！")
    
    # 填写标题
    print("📝 正在填写视频信息...")
    title_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".DraftEditor-root")))
    title_input.click()
    title_input.send_keys(title)
    
    # 添加标签
    if tags:
        tag_input = self.driver.find_element(By.CSS_SELECTOR, ".tag-input")
        for tag in tags:
            tag_input.click()
            tag_input.send_keys(tag)
            tag_input.send_keys("\n")
            time.sleep(0.5)
    
    # 点击发布按钮
    print("🚀 正在发布视频...")
    publish_btn = self.driver.find_element(By.CSS_SELECTOR, ".publish-btn")
    publish_btn.click()
    
    # 等待发布完成
    wait.until(EC.url_contains("content/manage"))
    print("🎉 视频发布成功！")
    return True
```

![](https://images.pexels.com/photos/4050312/pexels-photo-4050312.jpeg)

## <font color='DeepSkyBlue'><b>五、使用方法：傻瓜式操作</b></font>

### <font color='Purple'><b>1. 基础使用</b></font>

<font color='Green'><b>把上面的完整代码保存为douyin_publisher.py</b></font>

<font color='Green'><b>打开命令提示符，进入代码所在目录</b></font>

<font color='Green'><b>运行命令：python douyin_publisher.py</b></font>

<font color='Green'><b>按提示输入视频路径、标题和标签</b></font>

<font color='Green'><b>首次使用需要手动登录，之后会自动登录</b></font>

### <font color='Purple'><b>2. 批量发布</b></font>

想批量发布多个视频？试试这个增强版代码：

```python
# 批量发布示例
if __name__ == "__main__":
    # 创建发布器实例
    publisher = DouyinPublisher()
    
    try:
        # 登录
        publisher.login()
        
        # 批量发布视频
        videos_folder = input("请输入视频文件夹路径: ")
        
        # 获取文件夹中所有视频文件
        video_files = [f for f in os.listdir(videos_folder) 
                      if f.endswith(('.mp4', '.mov', '.avi'))]
        
        print(f"找到{len(video_files)}个视频文件，准备批量发布...")
        
        for i, video_file in enumerate(video_files):
            video_path = os.path.join(videos_folder, video_file)
            title = f"自动发布视频 #{i+1} - {os.path.splitext(video_file)[0]}"
            tags = ["自动发布", "Python脚本"]
            
            print(f"\n[{i+1}/{len(video_files)}] 正在发布: {video_file}")
            publisher.publish_video(video_path, title, tags)
            
            # 避免频繁发布被限制
            if i < len(video_files) - 1:
                wait_time = 60  # 每个视频间隔60秒
                print(f"等待{wait_time}秒后发布下一个视频...")
                time.sleep(wait_time)
        
        print("\n🎉 所有视频发布完成！")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        publisher.close()
```

### <font color='Purple'><b>3. 定时发布</b></font>

想在特定时间发布视频？加上这段代码：

```python
# 定时发布示例
import schedule

def scheduled_publish():
    publisher = DouyinPublisher()
    try:
        publisher.login()
        video_path = "your_video.mp4"  # 设置视频路径
        title = "定时发布的视频"  # 设置标题
        tags = ["定时发布", "自动化"]  # 设置标签
        publisher.publish_video(video_path, title, tags)
    except Exception as e:
        print(f"❌ 发布失败: {e}")
    finally:
        publisher.close()

# 每天早上9点发布
schedule.every().day.at("09:00").do(scheduled_publish)

print("定时发布器已启动，等待执行...")
while True:
    schedule.run_pending()
    time.sleep(1)
```

![](https://images.pexels.com/photos/4050321/pexels-photo-4050321.jpeg)

## <font color='DeepSkyBlue'><b>六、常见问题解答</b></font>

<font color='Orange'><b>问：为什么第一次使用需要手动登录？</b></font>

<font color='Green'><b>答：抖音有验证码和人脸识别，无法完全自动化，但登录一次后会保存状态。</b></font>

<font color='Orange'><b>问：会被抖音检测到是机器人吗？</b></font>

<font color='Green'><b>答：正常使用不会，但频繁发布可能会被限制，建议设置合理间隔。</b></font>

<font color='Orange'><b>问：代码中的CSS选择器可能失效怎么办？</b></font>

<font color='Green'><b>答：抖音更新界面后可能需要更新选择器，可以用浏览器开发者工具查看最新的。</b></font>

<font color='Orange'><b>问：能自动生成视频内容吗？</b></font>

<font color='Green'><b>答：本脚本只负责发布，可以结合AI视频生成工具实现全自动化。</b></font>

![](https://images.pexels.com/photos/4050299/pexels-photo-4050299.jpeg)

## <font color='DeepSkyBlue'><b>七、进阶玩法：打造全自动内容工厂</b></font>

<font color='Purple'><b>结合AI生成视频</b></font>

<font color='Green'><b>用AI生成视频内容，再用本脚本自动发布，躺着赚流量！</b></font>

<font color='Purple'><b>多账号管理</b></font>

<font color='Green'><b>修改代码支持多账号切换，一键管理多个抖音号！</b></font>

<font color='Purple'><b>数据分析</b></font>

<font color='Green'><b>爬取视频数据，分析哪类内容效果好，再针对性发布！</b></font>

<font color='Purple'><b>评论互动</b></font>

<font color='Green'><b>扩展脚本功能，实现自动回复评论，提高账号活跃度！</b></font>

![](https://images.pexels.com/photos/4050319/pexels-photo-4050319.jpeg)

## <font color='DeepSkyBlue'><b>八、行动起来，一分钟搞定你的第一个自动发布！</b></font>

现在，你已经掌握了抖音视频自动发布的全部技能！

<font color='Purple'><b>第一步：复制本文提供的代码</b></font>

<font color='Purple'><b>第二步：安装必要的环境</b></font>

<font color='Purple'><b>第三步：准备好要发布的视频</b></font>

<font color='Purple'><b>第四步：运行脚本，坐等视频上线</b></font>

就这么简单！

还在等什么？现在就行动起来，让Python帮你自动发布抖音视频吧！

<font color='Orange'><b>你有什么想用Python自动化的创意？欢迎在评论区分享！</b></font>

---

<font color='Green'><b>完整代码下载链接：关注公众号，回复"抖音自动发布"获取</b></font>

<font color='Blue'><b>更多Python自动化教程，请持续关注我们！</b></font>