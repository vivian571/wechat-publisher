# Python 自动化实战：5 个脚本帮你告别 90% 重复性工作

嘿，小伙伴们！是不是每天都在做大量的重复性工作，感觉自己像个没有感情的复制粘贴机器？

别担心，今天我就要教你如何用 Python 这把「**懒人神器**」，轻松搞定那些烦人的重复任务，让你的工作效率直接起飞！

相信我，掌握了这 5 个自动化脚本，你能轻松告别 **90%** 的重复性工作，每天多出几个小时来喝咖啡、刷剧，或者——摸鱼（老板不在的时候才能看这句哦）。

## 一、文件整理小能手：一键搞定文件分类

每次下载文件后，桌面乱得像狗窝？各种文档、图片、视频混在一起，找起来眼睛都花了？

试试这个「**文件整理小能手**」脚本，它能自动识别文件类型，并将它们分门别类地放入对应文件夹，让你的桌面焕然一新！

```python
import os
import shutil
from datetime import datetime

def organize_files(directory):
    # 创建分类文件夹
    categories = {
        '文档': ['.doc', '.docx', '.pdf', '.txt', '.xlsx', '.ppt', '.pptx'],
        '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
        '视频': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'],
        '音频': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
        '压缩包': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        '其他': []
    }
    
    # 确保分类文件夹存在
    for category in categories:
        category_path = os.path.join(directory, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
    
    # 遍历目录中的所有文件
    file_count = 0
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # 跳过文件夹
        if os.path.isdir(file_path):
            continue
        
        # 获取文件扩展名
        file_ext = os.path.splitext(filename)[1].lower()
        
        # 确定文件类别
        target_category = '其他'
        for category, extensions in categories.items():
            if file_ext in extensions:
                target_category = category
                break
        
        # 移动文件到对应分类文件夹
        target_path = os.path.join(directory, target_category, filename)
        shutil.move(file_path, target_path)
        file_count += 1
    
    return file_count

# 使用示例
if __name__ == "__main__":
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    count = organize_files(desktop_path)
    print(f"整理完成！共处理了 {count} 个文件。")
```

只需运行一次这个脚本，你的桌面就会变得井井有条，再也不用为找文件而抓狂了！

## 二、自动备份大师：数据安全有保障

数据丢失的痛苦，相信很多人都体会过——辛辛苦苦写的报告突然消失，重要的照片找不到了，这种感觉简直比失恋还难受！

有了这个「**自动备份大师**」，你可以设置定期自动备份重要文件夹，再也不用担心数据丢失的风险。

```python
import os
import time
import zipfile
import schedule
from datetime import datetime

def backup_folder(source_folder, backup_dir):
    # 确保备份目录存在
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 创建备份文件名（使用当前时间）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"backup_{os.path.basename(source_folder)}_{timestamp}.zip"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # 创建ZIP文件
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历源文件夹中的所有文件和子文件夹
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # 将文件添加到ZIP文件中，保持相对路径
                arcname = os.path.relpath(file_path, os.path.dirname(source_folder))
                zipf.write(file_path, arcname)
    
    print(f"备份完成：{backup_path}")
    return backup_path

# 设置定期备份任务
def setup_scheduled_backup(source_folder, backup_dir, interval='daily'):
    if interval == 'daily':
        schedule.every().day.at("18:00").do(backup_folder, source_folder, backup_dir)
    elif interval == 'weekly':
        schedule.every().monday.at("18:00").do(backup_folder, source_folder, backup_dir)
    elif interval == 'hourly':
        schedule.every().hour.do(backup_folder, source_folder, backup_dir)
    
    print(f"已设置{interval}备份任务，源文件夹：{source_folder}")
    
    # 保持程序运行以执行计划任务
    while True:
        schedule.run_pending()
        time.sleep(60)

# 使用示例
if __name__ == "__main__":
    # 设置要备份的文件夹和备份存储位置
    documents_folder = os.path.join(os.path.expanduser("~"), "Documents")
    backup_location = os.path.join(os.path.expanduser("~"), "Backups")
    
    # 立即执行一次备份
    backup_folder(documents_folder, backup_location)
    
    # 设置定期备份（取消注释以启用）
    # setup_scheduled_backup(documents_folder, backup_location, 'daily')
```

这个脚本不仅能立即备份你的重要文件，还能设置定期自动备份，让你的数据安全万无一失！

## 三、Excel数据处理王：批量处理不费力

每天要处理几十个Excel文件，复制粘贴到怀疑人生？数据统计分析让你头大？

别急，这个「**Excel数据处理王**」能帮你批量处理Excel文件，自动合并、统计、筛选数据，省时又省力！

```python
import os
import pandas as pd
import glob

def process_excel_files(input_dir, output_file, sheet_name='Sheet1'):
    # 获取所有Excel文件
    excel_files = glob.glob(os.path.join(input_dir, "*.xlsx")) + \
                 glob.glob(os.path.join(input_dir, "*.xls"))
    
    if not excel_files:
        print(f"在 {input_dir} 中没有找到Excel文件")
        return False
    
    # 读取并合并所有Excel文件
    all_data = []
    for file in excel_files:
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            # 添加文件名列，便于追踪数据来源
            df['来源文件'] = os.path.basename(file)
            all_data.append(df)
            print(f"已处理: {file}")
        except Exception as e:
            print(f"处理 {file} 时出错: {e}")
    
    if not all_data:
        print("没有成功处理任何文件")
        return False
    
    # 合并所有数据
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # 保存合并后的数据
    combined_data.to_excel(output_file, index=False)
    print(f"所有数据已合并并保存到: {output_file}")
    
    # 生成简单的数据统计
    stats_file = os.path.splitext(output_file)[0] + "_统计.xlsx"
    
    # 对数值列进行统计
    numeric_columns = combined_data.select_dtypes(include=['number']).columns
    if not numeric_columns.empty:
        stats = combined_data[numeric_columns].describe()
        stats.to_excel(stats_file)
        print(f"数据统计已保存到: {stats_file}")
    
    return True

# 使用示例
if __name__ == "__main__":
    # 设置输入文件夹和输出文件
    input_directory = os.path.join(os.path.expanduser("~"), "Excel文件")
    output_excel = os.path.join(os.path.expanduser("~"), "合并结果.xlsx")
    
    # 处理所有Excel文件
    process_excel_files(input_directory, output_excel)
```

有了这个脚本，你可以轻松合并多个Excel文件，自动生成数据统计报告，再也不用手动复制粘贴了！

## 四、网页监控助手：价格变动早知道

想买的商品一直在等降价？关注的网站内容更新了想第一时间知道？

这个「**网页监控助手**」能定期检查网页变化，当发现价格下降或内容更新时，立即通过邮件通知你，让你不错过任何重要信息！

```python
import requests
import time
import smtplib
import hashlib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class WebMonitor:
    def __init__(self, url, check_interval=3600, email_config=None):
        self.url = url
        self.check_interval = check_interval  # 检查间隔（秒）
        self.last_content_hash = None
        self.email_config = email_config
    
    def get_page_content(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(self.url, headers=headers)
        response.raise_for_status()
        return response.text
    
    def extract_price(self, html_content):
        # 这里需要根据具体网站调整选择器
        soup = BeautifulSoup(html_content, 'html.parser')
        # 示例：提取价格（需要根据实际网站调整）
        price_element = soup.select_one('.price-box .price')
        if price_element:
            price_text = price_element.text.strip()
            # 提取数字部分
            import re
            price_match = re.search(r'\d+(\.\d+)?', price_text)
            if price_match:
                return float(price_match.group())
        return None
    
    def send_notification(self, subject, message):
        if not self.email_config:
            print("未配置邮件信息，无法发送通知")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = self.email_config['sender']
        msg['To'] = self.email_config['receiver']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        try:
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            print("通知邮件已发送")
            return True
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
    
    def check_for_changes(self):
        try:
            current_content = self.get_page_content()
            current_hash = hashlib.md5(current_content.encode()).hexdigest()
            
            # 首次运行，保存当前内容哈希值
            if self.last_content_hash is None:
                self.last_content_hash = current_hash
                print(f"首次检查完成，监控已启动: {self.url}")
                return
            
            # 检查内容是否变化
            if current_hash != self.last_content_hash:
                print("检测到网页内容变化！")
                
                # 提取并比较价格（如果是商品页面）
                try:
                    current_price = self.extract_price(current_content)
                    if current_price is not None:
                        print(f"当前价格: {current_price}")
                        
                        # 发送价格变化通知
                        subject = f"价格更新通知: {self.url}"
                        message = f"您监控的网页价格已更新！\n\n当前价格: {current_price}\n\n网址: {self.url}"
                        self.send_notification(subject, message)
                except Exception as e:
                    print(f"提取价格失败: {e}")
                    
                    # 发送一般变化通知
                    subject = f"网页更新通知: {self.url}"
                    message = f"您监控的网页内容已更新！\n\n网址: {self.url}"
                    self.send_notification(subject, message)
                
                # 更新哈希值
                self.last_content_hash = current_hash
            else:
                print(f"网页内容未变化: {self.url}")
                
        except Exception as e:
            print(f"检查网页时出错: {e}")
    
    def start_monitoring(self):
        print(f"开始监控网页: {self.url}")
        print(f"检查间隔: {self.check_interval} 秒")
        
        try:
            while True:
                self.check_for_changes()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("监控已停止")

# 使用示例
if __name__ == "__main__":
    # 配置邮件信息
    email_settings = {
        'sender': 'your_email@gmail.com',  # 发件人邮箱
        'password': 'your_password',        # 邮箱密码或应用专用密码
        'receiver': 'your_email@gmail.com', # 收件人邮箱
        'smtp_server': 'smtp.gmail.com',    # SMTP服务器
        'smtp_port': 587                    # SMTP端口
    }
    
    # 创建监控实例（每小时检查一次）
    monitor = WebMonitor(
        url="https://www.example.com/product/12345",
        check_interval=3600,  # 每小时检查一次
        email_config=email_settings
    )
    
    # 开始监控
    monitor.start_monitoring()
```

这个脚本能帮你监控商品价格变化，网站内容更新，让你第一时间获取重要信息，再也不会错过任何优惠！

## 五、日常任务提醒器：告别拖延症

总是忘记重要日期？工作任务经常拖延到最后一刻？

这个「**日常任务提醒器**」能帮你管理日程，自动发送提醒，让你的工作生活更有条理！

```python
import time
import json
import os
from datetime import datetime, timedelta
import schedule
from plyer import notification

class TaskReminder:
    def __init__(self, tasks_file="tasks.json"):
        self.tasks_file = tasks_file
        self.tasks = self.load_tasks()
    
    def load_tasks(self):
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载任务文件失败: {e}")
                return []
        return []
    
    def save_tasks(self):
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def add_task(self, title, description, deadline, remind_before=24):
        """添加新任务
        
        Args:
            title: 任务标题
            description: 任务描述
            deadline: 截止日期（格式：YYYY-MM-DD HH:MM）
            remind_before: 提前多少小时提醒
        """
        task = {
            'id': len(self.tasks) + 1,
            'title': title,
            'description': description,
            'deadline': deadline,
            'remind_before': remind_before,
            'completed': False,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        self.tasks.append(task)
        self.save_tasks()
        print(f"任务已添加: {title}")
        return task
    
    def complete_task(self, task_id):
        """将任务标记为已完成"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                self.save_tasks()
                print(f"任务已完成: {task['title']}")
                return True
        print(f"未找到ID为 {task_id} 的任务")
        return False
    
    def list_tasks(self, show_completed=False):
        """列出所有任务"""
        pending_tasks = []
        completed_tasks = []
        
        for task in self.tasks:
            if task['completed']:
                completed_tasks.append(task)
            else:
                pending_tasks.append(task)
        
        print("\n待完成任务:")
        if pending_tasks:
            for task in pending_tasks:
                deadline = datetime.strptime(task['deadline'], "%Y-%m-%d %H:%M")
                remaining = deadline - datetime.now()
                print(f"[{task['id']}] {task['title']} - 截止日期: {task['deadline']} (剩余 {remaining.days} 天 {remaining.seconds//3600} 小时)")
        else:
            print("没有待完成的任务")
        
        if show_completed and completed_tasks:
            print("\n已完成任务:")
            for task in completed_tasks:
                print(f"[{task['id']}] {task['title']} - 完成时间: {task['completed_at'] if 'completed_at' in task else '未知'}")
    
    def check_reminders(self):
        """检查是否有需要提醒的任务"""
        now = datetime.now()
        
        for task in self.tasks:
            if task['completed']:
                continue
                
            deadline = datetime.strptime(task['deadline'], "%Y-%m-%d %H:%M")
            remind_time = deadline - timedelta(hours=task['remind_before'])
            
            # 如果当前时间已过提醒时间但在截止时间之前
            if remind_time <= now < deadline:
                remaining = deadline - now
                hours_remaining = remaining.days * 24 + remaining.seconds // 3600
                
                # 避免重复提醒，这里简单处理：只在整点提醒
                if now.minute < 5:  # 每小时前5分钟检查一次
                    self.send_notification(
                        title=f"任务提醒: {task['title']}",
                        message=f"截止时间还剩 {hours_remaining} 小时\n{task['description']}"
                    )
            
            # 如果已过截止时间但未完成
            elif now >= deadline and not task.get('overdue_notified', False):
                self.send_notification(
                    title=f"任务已逾期: {task['title']}",
                    message=f"任务已经逾期！\n{task['description']}"
                )
                # 标记为已通知逾期，避免重复提醒
                task['overdue_notified'] = True
                self.save_tasks()
    
    def send_notification(self, title, message):
        """发送桌面通知"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="任务提醒器",
                timeout=10
            )
            print(f"已发送通知: {title}")
        except Exception as e:
            print(f"发送通知失败: {e}")
    
    def start(self):
        """启动提醒服务"""
        print("任务提醒器已启动...")
        
        # 每小时检查一次提醒
        schedule.every(1).hours.do(self.check_reminders)
        # 也可以设置更频繁的检查
        # schedule.every(15).minutes.do(self.check_reminders)
        
        # 立即检查一次
        self.check_reminders()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("提醒服务已停止")

# 使用示例
if __name__ == "__main__":
    reminder = TaskReminder()
    
    # 添加示例任务
    # reminder.add_task(
    #     title="完成季度报告",
    #     description="准备Q2季度销售数据分析报告",
    #     deadline="2023-06-30 17:00",
    #     remind_before=48  # 提前48小时提醒
    # )
    
    # 列出所有任务
    reminder.list_tasks()
    
    # 启动提醒服务
    reminder.start()
```

有了这个脚本，你可以轻松管理日常任务，再也不会错过重要截止日期，工作生活更有条理！

## 总结：Python自动化，解放你的双手和大脑

看完这5个实用脚本，是不是感觉Python自动化真的很**强大**？

从文件整理、数据备份、Excel处理到网页监控、任务提醒，Python几乎可以自动化你生活和工作中的任何重复性任务。

最棒的是，这些脚本都不需要很深的编程知识，即使你是**编程小白**，照着示例稍作修改就能用起来。

想象一下，当这些脚本帮你完成90%的重复性工作后，你将有更多时间专注于**创造性**的工作，或者享受生活的乐趣。

如果你对Python自动化感兴趣，不妨从这5个脚本开始尝试，相信你很快就会爱上这种**高效**的工作方式！

你平时有哪些重复性工作最让你头疼？或者你已经用Python解决了哪些烦人的任务？欢迎在评论区分享你的经验和想法！

下期预告：我们将深入探讨如何将这些自动化脚本打包成可执行文件，让不懂编程的同事也能轻松使用。敬请期待！