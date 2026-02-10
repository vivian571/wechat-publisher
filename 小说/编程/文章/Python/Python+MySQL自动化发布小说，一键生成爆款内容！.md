# <font color='OrangeRed'>Python+MySQL自动化发布小说，一键生成爆款内容！</font>

**<font color='purple'>不会写小说？没关系！</font>**

**<font color='green'>不懂技术？也没问题！</font>**

今天教你用Python+MySQL打造自己的小说自动发布系统！

只需几行代码，就能自动生成、存储、发布小说，再也不用担心没内容更新了！

![创意写作](https://images.unsplash.com/photo-1455390582262-044cdead277a?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

## <font color='DeepSkyBlue'>一、先看看成果</font>

我们要实现的是什么？

**<font color='red'>一个完整的小说自动化系统！</font>**

这个系统能做到：

1. 自动生成小说内容（大纲+章节）
2. 将小说存入MySQL数据库
3. 一键发布到网站
4. 定时更新，吸引读者

![数据库管理](https://images.unsplash.com/photo-1544383835-bda2bc66a55d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

## <font color='DeepSkyBlue'>二、准备工作</font>

开始前，你需要准备这些：

**<font color='purple'>必备工具：</font>**

1. Python 3.6+
2. MySQL数据库
3. OpenAI API密钥

**<font color='green'>安装必要的库：</font>**

```python
pip install openai python-dotenv mysql-connector-python schedule
```

**<font color='red'>数据库准备：</font>**

1. 安装MySQL（官网下载安装包）
2. 创建数据库和表（后面有代码）

![编程准备](https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

## <font color='DeepSkyBlue'>三、数据库设计</font>

我们需要设计一个简单的数据库结构：

**<font color='purple'>novels表：</font>** 存储小说基本信息

**<font color='green'>chapters表：</font>** 存储小说章节内容

**<font color='red'>publishing表：</font>** 记录发布状态

![数据库设计](https://images.unsplash.com/photo-1489875347897-49f64b51c1f8?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

## <font color='DeepSkyBlue'>四、完整代码实现</font>

下面是完整的Python代码，包含了所有功能：

```python
import os
import openai
import mysql.connector
from dotenv import load_dotenv
import time
import schedule
import random
from datetime import datetime

# 加载环境变量
load_dotenv()

# 设置OpenAI API密钥
openai.api_key = os.getenv("OPENAI_API_KEY")

class NovelPublishingSystem:
    def __init__(self):
        # 连接MySQL数据库
        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "novel_system")
        )
        self.cursor = self.conn.cursor()
        self.novel = {}
        self.current_chapter = 1
        self.initialize_database()
    
    def initialize_database(self):
        """初始化数据库表结构"""
        # 创建novels表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS novels (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(100) NOT NULL,
            type VARCHAR(50),
            theme VARCHAR(255),
            main_character TEXT,
            setting TEXT,
            outline TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('draft', 'publishing', 'completed') DEFAULT 'draft'
        )
        """)
        
        # 创建chapters表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS chapters (
            id INT AUTO_INCREMENT PRIMARY KEY,
            novel_id INT,
            chapter_number INT,
            title VARCHAR(255),
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (novel_id) REFERENCES novels(id)
        )
        """)
        
        # 创建publishing表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS publishing (
            id INT AUTO_INCREMENT PRIMARY KEY,
            novel_id INT,
            chapter_id INT,
            platform VARCHAR(50),
            publish_time TIMESTAMP,
            status ENUM('pending', 'published', 'failed') DEFAULT 'pending',
            FOREIGN KEY (novel_id) REFERENCES novels(id),
            FOREIGN KEY (chapter_id) REFERENCES chapters(id)
        )
        """)
        
        self.conn.commit()
    
    def create_outline(self, novel_type, theme, main_character, setting):
        """创建小说大纲"""
        prompt = f"""
        你是一位专业的{novel_type}小说作家。请为以下设定创建一个10章的小说大纲：
        - 主题：{theme}
        - 主角：{main_character}
        - 背景设定：{setting}
        
        请提供每章的标题和简短的内容概述。格式如下：
        第1章：[标题]
        [内容概述]
        
        第2章：[标题]
        [内容概述]
        
        以此类推...
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        outline = response.choices[0].message.content
        self.novel["outline"] = outline
        return outline
    
    def write_chapter(self, chapter_number, writing_style=""):
        """写小说章节"""
        # 获取大纲中对应章节的信息
        outline_lines = self.novel["outline"].split("\n")
        chapter_title = ""
        chapter_outline = ""
        
        for i, line in enumerate(outline_lines):
            if line.startswith(f"第{chapter_number}章"):
                chapter_title = line.replace(f"第{chapter_number}章：", "").strip()
                if i + 1 < len(outline_lines) and not outline_lines[i + 1].startswith("第"):
                    chapter_outline = outline_lines[i + 1].strip()
        
        style_prompt = ""
        if writing_style:
            style_prompt = f"请模仿{writing_style}的写作风格。"
        
        prompt = f"""
        你是一位专业小说作家。{style_prompt}请根据以下大纲写一个精彩的小说章节：
        
        章节标题：{chapter_title}
        章节概要：{chapter_outline}
        
        请写一个完整的章节，字数在2000-3000字之间。注重情节发展、人物刻画和环境描写。
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        chapter_content = response.choices[0].message.content
        self.novel[f"chapter_{chapter_number}"] = chapter_content
        return chapter_title, chapter_content
    
    def save_novel_to_database(self, title, author, novel_type, theme, main_character, setting):
        """保存小说信息到数据库"""
        # 插入小说基本信息
        self.cursor.execute("""
        INSERT INTO novels (title, author, type, theme, main_character, setting, outline, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, author, novel_type, theme, main_character, setting, self.novel["outline"], "draft"))
        
        self.conn.commit()
        novel_id = self.cursor.lastrowid
        return novel_id
    
    def save_chapter_to_database(self, novel_id, chapter_number, title, content):
        """保存章节到数据库"""
        self.cursor.execute("""
        INSERT INTO chapters (novel_id, chapter_number, title, content)
        VALUES (%s, %s, %s, %s)
        """, (novel_id, chapter_number, title, content))
        
        self.conn.commit()
        chapter_id = self.cursor.lastrowid
        return chapter_id
    
    def schedule_publishing(self, novel_id, chapter_id, platform, publish_time):
        """安排发布计划"""
        self.cursor.execute("""
        INSERT INTO publishing (novel_id, chapter_id, platform, publish_time, status)
        VALUES (%s, %s, %s, %s, %s)
        """, (novel_id, chapter_id, platform, publish_time, "pending"))
        
        self.conn.commit()
    
    def publish_chapter(self, publishing_id):
        """发布章节到指定平台"""
        # 获取发布信息
        self.cursor.execute("""
        SELECT p.id, p.novel_id, p.chapter_id, p.platform, n.title as novel_title, 
               c.chapter_number, c.title as chapter_title, c.content
        FROM publishing p
        JOIN novels n ON p.novel_id = n.id
        JOIN chapters c ON p.chapter_id = c.id
        WHERE p.id = %s AND p.status = 'pending'
        """, (publishing_id,))
        
        result = self.cursor.fetchone()
        if not result:
            return False
        
        pub_id, novel_id, chapter_id, platform, novel_title, chapter_number, chapter_title, content = result
        
        # 这里实现实际的发布逻辑，例如调用平台API
        # 这里只是模拟发布
        print(f"正在发布《{novel_title}》第{chapter_number}章：{chapter_title} 到 {platform}平台...")
        time.sleep(2)  # 模拟发布过程
        
        # 更新发布状态
        self.cursor.execute("""
        UPDATE publishing SET status = 'published' WHERE id = %s
        """, (pub_id,))
        
        self.conn.commit()
        return True
    
    def check_pending_publications(self):
        """检查待发布的内容"""
        current_time = datetime.now()
        
        # 查找应该发布的内容
        self.cursor.execute("""
        SELECT id FROM publishing 
        WHERE status = 'pending' AND publish_time <= %s
        """, (current_time,))
        
        pending_pubs = self.cursor.fetchall()
        for pub in pending_pubs:
            self.publish_chapter(pub[0])
    
    def generate_complete_novel(self, title, author, novel_type, theme, main_character, setting, chapters=5, writing_style="", platforms=["网站", "微信公众号"]):
        """生成完整小说并安排发布"""
        # 创建大纲
        self.create_outline(novel_type, theme, main_character, setting)
        time.sleep(2)  # 避免API限制
        
        # 保存小说信息到数据库
        novel_id = self.save_novel_to_database(title, author, novel_type, theme, main_character, setting)
        
        # 生成发布时间表（每天一章）
        publish_dates = []
        start_date = datetime.now()
        for i in range(chapters):
            # 每天同一时间发布
            next_date = start_date.replace(day=start_date.day + i)
            publish_dates.append(next_date)
        
        # 生成章节并安排发布
        for i in range(1, chapters + 1):
            # 写章节
            chapter_title, chapter_content = self.write_chapter(i, writing_style)
            self.current_chapter = i + 1
            time.sleep(2)  # 避免API限制
            
            # 保存章节到数据库
            chapter_id = self.save_chapter_to_database(novel_id, i, chapter_title, chapter_content)
            
            # 为每个平台安排发布
            for platform in platforms:
                self.schedule_publishing(novel_id, chapter_id, platform, publish_dates[i-1])
        
        # 更新小说状态
        self.cursor.execute("""
        UPDATE novels SET status = 'publishing' WHERE id = %s
        """, (novel_id,))
        self.conn.commit()
        
        return f"小说《{title}》创作完成并安排发布！"
    
    def start_publishing_scheduler(self):
        """启动发布调度器"""
        # 每小时检查一次是否有需要发布的内容
        schedule.every(1).hour.do(self.check_pending_publications)
        
        print("发布调度器已启动，按Ctrl+C停止...")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("发布调度器已停止")
    
    def close(self):
        """关闭数据库连接"""
        self.cursor.close()
        self.conn.close()

# 使用示例
if __name__ == "__main__":
    system = NovelPublishingSystem()
    
    # 设置小说参数
    title = "时间的囚徒"
    author = "AI作家"
    novel_type = "科幻"
    theme = "时间旅行者的困境"
    main_character = "李时，一位物理学教授，发现了时间旅行的秘密"
    setting = "2035年的中国，科技高度发达"
    writing_style = "刘慈欣"  # 可以为空
    platforms = ["网站", "微信公众号", "起点中文网"]
    
    # 生成小说并安排发布
    result = system.generate_complete_novel(
        title=title,
        author=author,
        novel_type=novel_type,
        theme=theme,
        main_character=main_character,
        setting=setting,
        chapters=5,  # 生成5章
        writing_style=writing_style,
        platforms=platforms
    )
    
    print(result)
    
    # 启动发布调度器
    system.start_publishing_scheduler()
    
    # 完成后关闭连接
    system.close()
```

![代码实现](https://images.unsplash.com/photo-1517694712202-14dd9538aa97?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

## <font color='DeepSkyBlue'>五、系统功能详解</font>

**<font color='purple'>1. 小说生成功能</font>**

系统会根据你设定的类型、主题、人物和背景，自动生成一个完整的小说大纲。

然后根据大纲，逐章生成小说内容，可以模仿特定作家的风格！

**<font color='green'>2. 数据库存储功能</font>**

所有生成的内容都会存入MySQL数据库，方便管理和查询。

三张表分别存储：小说信息、章节内容、发布计划。

**<font color='red'>3. 自动发布功能</font>**

系统会按照设定的时间表，自动将小说章节发布到指定平台。

支持多平台发布，比如自建网站、微信公众号、小说网站等。

![自动化发布](https://images.unsplash.com/photo-1563986768609-322da13575f3?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

## <font color='DeepSkyBlue'>六、使用步骤</font>

**<font color='purple'>第一步：环境配置</font>**

1. 安装Python和MySQL
2. 安装必要的库
3. 创建`.env`文件，添加配置：

```
OPENAI_API_KEY=你的OpenAI密钥
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=你的密码
DB_NAME=novel_system
```

**<font color='green'>第二步：运行系统</font>**

1. 运行Python脚本
2. 设置小说参数
3. 系统会自动生成内容并存入数据库

**<font color='red'>第三步：启动发布调度器</font>**

1. 系统会按照设定的时间表自动发布内容
2. 你可以随时查看发布状态

![使用步骤](https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

## <font color='DeepSkyBlue'>七、进阶功能</font>

想让系统更强大？

**<font color='purple'>可以添加这些功能：</font>**

1. 读者评论收集和分析
2. 根据读者反馈调整后续章节
3. 自动生成宣传文案和封面图片
4. 销量统计和收益分析

![进阶功能](https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

## <font color='DeepSkyBlue'>八、总结</font>

**<font color='red'>Python+MySQL自动化发布小说，就是这么简单！</font>**

只需要：

1. 设置好参数
2. 运行脚本
3. 启动调度器

系统就会自动帮你：生成内容、存储管理、定时发布！

**<font color='green'>再也不用担心没内容更新了！</font>**

**<font color='purple'>动手试试吧，说不定下一个网文大神就是你！</font>**

![总结](https://images.unsplash.com/photo-1499750310107-5fef28a66643?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)