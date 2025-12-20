# 【太强了】Python邮件自动发送程序，5分钟搞定老板交代的100封邮件！

**<font color='red'>不用再熬夜手动发邮件了！这个Python小程序让你躺着完成工作！</font>**

![邮件自动化](https://images.unsplash.com/photo-1596526131083-e8c633c948d2?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

## 先看效果，绝对震撼！

**<font color='blue'>只需几行代码，就能实现：</font>**

**批量发送个性化邮件！**

**定时自动发送报表！**

**邮件附件自动添加！**

**自定义邮件模板！**

**一键群发不同内容！**

## 完整代码，复制就能用！

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pandas as pd
import time
from datetime import datetime

class EmailSender:
    def __init__(self, sender_email, password, smtp_server="smtp.163.com", smtp_port=25):
        """初始化邮件发送器
        
        参数:
            sender_email: 发件人邮箱
            password: 邮箱授权码（不是登录密码）
            smtp_server: SMTP服务器地址
            smtp_port: SMTP服务器端口
        """
        self.sender_email = sender_email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
    def send_email(self, receiver_email, subject, body, attachments=None):
        """发送单封邮件
        
        参数:
            receiver_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文
            attachments: 附件列表，格式为[(文件名, 文件路径)]
        """
        # 创建邮件对象
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        
        # 添加邮件正文
        msg.attach(MIMEText(body, "html"))
        
        # 添加附件
        if attachments:
            for attachment_name, attachment_path in attachments:
                with open(attachment_path, "rb") as file:
                    part = MIMEApplication(file.read())
                    part.add_header("Content-Disposition", "attachment", filename=attachment_name)
                    msg.attach(part)
        
        # 发送邮件
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # 启用TLS加密
            server.login(self.sender_email, self.password)
            server.send_message(msg)
            server.quit()
            print(f"邮件已成功发送至 {receiver_email}")
            return True
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            return False
    
    def send_batch_emails(self, data_file, template, attachments=None, delay=1):
        """批量发送邮件
        
        参数:
            data_file: 包含收件人信息的Excel文件路径
            template: 邮件模板，使用{变量名}作为占位符
            attachments: 附件列表，格式为[(文件名, 文件路径)]
            delay: 每封邮件之间的延迟时间（秒）
        """
        # 读取收件人数据
        try:
            df = pd.read_excel(data_file)
        except Exception as e:
            print(f"读取数据文件失败: {str(e)}")
            return
        
        success_count = 0
        fail_count = 0
        
        # 遍历每一行数据发送邮件
        for index, row in df.iterrows():
            # 确保必要的字段存在
            if "email" not in row or "subject" not in row:
                print(f"第{index+1}行数据缺少必要字段")
                fail_count += 1
                continue
            
            # 替换模板中的占位符
            personalized_body = template
            for column in df.columns:
                if column in row and isinstance(row[column], str):
                    personalized_body = personalized_body.replace("{" + column + "}", row[column])
            
            # 发送邮件
            if self.send_email(row["email"], row["subject"], personalized_body, attachments):
                success_count += 1
            else:
                fail_count += 1
            
            # 添加延迟，避免被邮件服务器识别为垃圾邮件
            time.sleep(delay)
        
        print(f"批量发送完成！成功: {success_count}, 失败: {fail_count}")
    
    def schedule_email(self, receiver_email, subject, body, attachments=None, send_time=None):
        """定时发送邮件
        
        参数:
            receiver_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文
            attachments: 附件列表
            send_time: 发送时间，格式为"YYYY-MM-DD HH:MM:SS"，如果为None则立即发送
        """
        if send_time:
            # 解析发送时间
            send_datetime = datetime.strptime(send_time, "%Y-%m-%d %H:%M:%S")
            current_datetime = datetime.now()
            
            # 计算等待时间
            wait_seconds = (send_datetime - current_datetime).total_seconds()
            
            if wait_seconds > 0:
                print(f"邮件将在 {send_time} 发送，等待 {wait_seconds} 秒...")
                time.sleep(wait_seconds)
            else:
                print("指定的发送时间已过，立即发送邮件")
        
        # 发送邮件
        return self.send_email(receiver_email, subject, body, attachments)

# 使用示例
if __name__ == "__main__":
    # 初始化邮件发送器
    sender = EmailSender(
        sender_email="your_email@163.com",  # 替换为你的邮箱
        password="your_auth_code",  # 替换为你的授权码
        smtp_server="smtp.163.com",  # 邮箱服务器
        smtp_port=25  # 服务器端口
    )
    
    # 示例1：发送单封邮件
    sender.send_email(
        receiver_email="receiver@example.com",
        subject="Python自动邮件测试",
        body="<h1>这是一封测试邮件</h1><p>Hello，这是使用Python自动发送的邮件！</p>",
        attachments=[("测试文档.pdf", "path/to/document.pdf")]
    )
    
    # 示例2：批量发送邮件
    template = """
    <html>
    <body>
        <h2>亲爱的{name}：</h2>
        <p>感谢您参与我们的{event}活动！</p>
        <p>您的订单号是：<strong>{order_id}</strong></p>
        <p>如有任何问题，请随时联系我们。</p>
        <p>祝好，<br>团队</p>
    </body>
    </html>
    """
    
    sender.send_batch_emails(
        data_file="contacts.xlsx",  # Excel文件包含email, subject, name, event, order_id等列
        template=template,
        attachments=[("活动说明.pdf", "path/to/event_guide.pdf")],
        delay=2  # 每封邮件间隔2秒
    )
    
    # 示例3：定时发送邮件
    tomorrow = (datetime.now().date() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    sender.schedule_email(
        receiver_email="boss@example.com",
        subject="每日销售报告",
        body="<h2>每日销售报告</h2><p>请查收附件中的销售数据。</p>",
        attachments=[("销售报告.xlsx", "path/to/sales_report.xlsx")],
        send_time=f"{tomorrow} 09:00:00"  # 明天早上9点发送
    )
```

## 保姆级教程，手把手教你用！

**<font color='green'>第一步：准备工作</font>**

**安装必要的库：**

```bash
pip install pandas openpyxl
```

**<font color='green'>第二步：获取邮箱授权码</font>**

![邮箱设置](https://images.unsplash.com/photo-1563986768609-322da13575f3?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**不知道啥是授权码？看这里：**

1. **登录你的邮箱网页版**

2. **找到设置或账户管理**

3. **找到"POP3/SMTP服务"并开启**

4. **获取授权码（不是你的登录密码！）**

**<font color='purple'>不同邮箱操作略有不同，但基本类似！</font>**

**<font color='green'>第三步：准备收件人数据</font>**

**创建Excel文件，必须包含这些列：**

**email（收件人邮箱）**

**subject（邮件主题）**

**其他你需要的个性化字段（如name、order_id等）**

![Excel数据](https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color='green'>第四步：修改代码中的关键信息</font>**

**替换以下内容：**

**sender_email：你的邮箱地址**

**password：你的邮箱授权码**

**smtp_server和smtp_port：根据你的邮箱服务商设置**

**<font color='red'>常见邮箱SMTP设置：</font>**

**网易163：smtp.163.com，端口25或465(SSL)**

**QQ邮箱：smtp.qq.com，端口587或465(SSL)**

**Gmail：smtp.gmail.com，端口587(TLS)或465(SSL)**

**<font color='green'>第五步：运行程序</font>**

**保存代码为email_sender.py，然后运行：**

```bash
python email_sender.py
```

## 进阶玩法，解锁更多功能！

**<font color='orange'>添加HTML邮件模板</font>**

![精美模板](https://images.unsplash.com/photo-1555421689-491a97ff2040?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**想发精美邮件？使用HTML模板！**

**可以添加图片、表格、按钮等元素！**

**<font color='orange'>自动生成并发送报表</font>**

**结合pandas生成数据分析报表**

**自动生成图表并作为邮件内容**

**定期发送给团队或领导**

**<font color='orange'>与其他系统集成</font>**

**连接数据库自动获取数据**

**与企业CRM系统集成**

**作为自动化工作流的一部分**

## 常见问题解答

**<font color='red'>问：为什么我的邮件发不出去？</font>**

**答：检查以下几点：**

**1. 邮箱和授权码是否正确**

**2. SMTP服务器和端口是否正确**

**3. 邮箱是否开启了POP3/SMTP服务**

**4. 是否触发了邮箱服务商的反垃圾邮件机制**

**<font color='red'>问：如何避免邮件被当成垃圾邮件？</font>**

**答：几个小技巧：**

**1. 添加适当的发送延迟**

**2. 避免使用大量特殊符号和敏感词**

**3. 使用正规的邮件格式和结构**

**4. 不要一次性发送太多邮件**

**<font color='red'>问：如何保护邮箱密码安全？</font>**

**答：最佳实践：**

**1. 使用环境变量存储敏感信息**

**2. 不要将密码硬编码在代码中**

**3. 使用专门的授权码而非登录密码**

## 总结

**<font color='purple'>Python邮件自动发送程序，真的太强了！</font>**

**解放双手，提高效率！**

**从此告别繁琐的手动发邮件！**

**轻松应对各种邮件发送需求！**

**学会了这个技能，工作效率直接提升200%！**

**赶紧动手试试吧！**

![成功](https://images.unsplash.com/photo-1552581234-26160f608093?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)