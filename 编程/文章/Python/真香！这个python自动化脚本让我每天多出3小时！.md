# 真香！这个Python自动化脚本让我每天多出3小时！

嘿，小伙伴们！

还在为每天重复的工作烦恼吗？

敲键盘敲到手抽筋？

复制粘贴到怀疑人生？

我曾经也是这样，直到发现了Python自动化这个**神器**，彻底改变了我的工作方式！

现在，我每天能**<font color='red'>多出整整3小时</font>**的时间！

可以用来喝咖啡、刷剧，甚至——偷偷摸鱼（老板不在的时候才能看这句哦）。

今天就来掏心窝子分享一个让我直呼**<font color='orange'>“真香”</font>**的Python自动化脚本。

保证让你也能告别繁琐工作，效率直接起飞！

## 痛点！那些年我们浪费的时间

先来回忆一下，你是不是经常遇到这些场景？

每天上班第一件事，打开N个文件夹，把各种来源的文件（邮件附件、下载文件、同事发的）整理到对应的项目目录里。

文件名乱七八糟，有的是日期，有的是项目名，有的是“未命名”，找个文件像大海捞针。

手动分类、重命名，一不小心就弄错，还得返工。

或者，你需要定期从某个网站下载报表，然后手动复制粘贴数据到Excel里。

网站结构一变，或者数据格式稍微有点不同，之前的操作就全白费。

还有，每天要处理一堆邮件，筛选重要信息，回复固定模板的邮件。

这些看似不起眼的小事，**<font color='red'>日积月累</font>**，不知不觉就偷走了我们大把的时间和精力！

说多了都是泪啊！

## 救星来了！Python自动化脚本登场！

就在我快要被这些重复工作逼疯的时候，我遇到了**Python**！

一开始我也觉得编程很难，但Python真的**<font color='green'>太简单</font>**了！

语法像说话一样自然，几行代码就能干大事。

而且Python社区**<font color='blue'>超级活跃</font>**，有海量的库（就像工具箱里的各种工具），你想干啥几乎都能找到现成的轮子。

针对上面说的文件整理痛点，我就写了下面这个脚本。

## 实战！文件自动归类整理脚本

想象一下，你只需要运行一下这个脚本，电脑桌面或者下载文件夹里杂乱无章的文件，就能**<font color='purple'>自动</font>**按照你设定的规则，跑到它们该去的文件夹里，并且**<font color='purple'>自动</font>**改好名字！

是不是很酷？

来，上代码！

```python
import os
import shutil
import datetime

# --- 配置区 --- 你只需要修改这里！ ---

# 1. 要整理的文件夹路径 (比如你的下载文件夹)
SOURCE_FOLDER = r'C:\Users\你的用户名\Downloads'

# 2. 文件归类的目标文件夹路径 (你想把文件放到哪里)
DESTINATION_BASE_FOLDER = r'D:\工作文件'

# 3. 文件分类规则 (根据文件后缀名)
# 格式：'目标子文件夹名称': ['.后缀1', '.后缀2']
FILE_CATEGORIES = {
    '文档': ['.docx', '.doc', '.pdf', '.pptx', '.ppt', '.txt'],
    '表格': ['.xlsx', '.xls', '.csv'],
    '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
    '压缩包': ['.zip', '.rar', '.7z'],
    '代码': ['.py', '.java', '.html', '.css', '.js'],
    # 你可以继续添加更多分类
    '其他': [] # 其他未匹配到的文件会放到这里
}

# 4. 是否按日期创建子文件夹 (True 或 False)
CREATE_DATE_SUBFOLDER = True

# 5. 日期格式 (如果 CREATE_DATE_SUBFOLDER 为 True)
# %Y: 年份 (e.g., 2023)
# %m: 月份 (01-12)
# %d: 日期 (01-31)
DATE_FORMAT = '%Y-%m-%d' # 例如：创建像 '2023-10-27' 这样的文件夹

# --- 脚本核心逻辑 --- 一般不需要修改下面 --- 

def organize_files():
    print(f"开始整理文件夹：{SOURCE_FOLDER}")
    moved_count = 0
    skipped_count = 0

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(SOURCE_FOLDER):
        source_file_path = os.path.join(SOURCE_FOLDER, filename)

        # 确保是文件而不是文件夹
        if os.path.isfile(source_file_path):
            try:
                # 获取文件后缀名
                _, file_extension = os.path.splitext(filename)
                file_extension = file_extension.lower() # 转小写方便匹配

                # 确定文件类别
                category_folder_name = '其他' # 默认为其他
                for folder_name, extensions in FILE_CATEGORIES.items():
                    if file_extension in extensions:
                        category_folder_name = folder_name
                        break
                
                # 构建目标文件夹路径
                destination_folder = os.path.join(DESTINATION_BASE_FOLDER, category_folder_name)

                # 如果需要按日期创建子文件夹
                if CREATE_DATE_SUBFOLDER:
                    today_str = datetime.datetime.now().strftime(DATE_FORMAT)
                    destination_folder = os.path.join(destination_folder, today_str)

                # 创建目标文件夹 (如果不存在)
                os.makedirs(destination_folder, exist_ok=True)

                # 构建完整的目标文件路径
                destination_file_path = os.path.join(destination_folder, filename)

                # --- 处理文件名冲突 --- 
                counter = 1
                original_filename = filename
                while os.path.exists(destination_file_path):
                    # 如果目标文件已存在，在文件名后加上序号
                    name, ext = os.path.splitext(original_filename)
                    destination_file_path = os.path.join(destination_folder, f"{name}_{counter}{ext}")
                    counter += 1
                    if counter > 1: # 第一次冲突时打印提示
                         print(f"  文件名冲突：'{original_filename}' -> '{os.path.basename(destination_file_path)}'")
                # --- 文件名冲突处理结束 ---

                # 移动文件
                shutil.move(source_file_path, destination_file_path)
                print(f"  移动 '{filename}' 到 '{destination_folder}'")
                moved_count += 1

            except Exception as e:
                print(f"  处理 '{filename}' 时出错: {e}")
                skipped_count += 1
        else:
            # print(f"  跳过文件夹: {filename}") # 如果需要可以取消注释
            pass

    print("\n整理完成！")
    print(f"成功移动文件数：{moved_count}")
    print(f"跳过或处理失败文件数：{skipped_count}")

# --- 运行脚本 ---
if __name__ == "__main__":
    organize_files()
```

## 脚本怎么用？超简单！

别被代码吓到，用起来**<font color='red'>超级简单</font>**！

**第一步：安装Python**

如果你电脑还没装Python，去官网（python.org）下载安装包，一路点“下一步”就行。

记得勾选“Add Python to PATH”这个选项，省去后面配置环境变量的麻烦。

**第二步：复制代码**

把上面那段Python代码，**<font color='blue'>完整复制</font>**下来。

打开你电脑上的任何文本编辑器（记事本、VS Code、Sublime Text都行）。

粘贴代码，然后保存文件。

文件名可以随便取，但后缀名必须是 `.py`，比如 `file_organizer.py`。

**第三步：修改配置**

这是**<font color='red'>最关键</font>**的一步！

找到代码里 `--- 配置区 ---` 这部分。

你需要修改以下几个地方：

1.  `SOURCE_FOLDER`: 把 `C:\Users\你的用户名\Downloads` 换成你**<font color='green'>实际</font>**想要整理的文件夹路径。
    *   **注意**：路径里的反斜杠 `\` 要用**<font color='red'>两个</font>**！或者用单正斜杠 `/` 也可以，比如 `'D:/我的下载'`。
2.  `DESTINATION_BASE_FOLDER`: 把 `D:\工作文件` 换成你希望文件**<font color='green'>最终</font>**存放的基础路径。
3.  `FILE_CATEGORIES`: 这是分类规则的核心！
    *   你可以**<font color='blue'>修改</font>**现有的分类名（比如把“文档”改成“学习资料”）。
    *   你可以**<font color='blue'>修改</font>**每个分类包含的文件后缀名（比如把 `.txt` 从“文档”移到“代码”分类）。
    *   你可以**<font color='blue'>添加</font>**新的分类和对应的后缀名列表。
    *   **<font color='red'>重要</font>**：后缀名要用**<font color='red'>小写</font>**，并且前面带个点 `.`。
4.  `CREATE_DATE_SUBFOLDER`: 如果你想让脚本在每个分类文件夹下，再按**<font color='orange'>当天日期</font>**创建一个子文件夹（比如 `D:\工作文件\文档\2023-10-27`），就保持 `True`。
    *   如果不需要按日期分类，就改成 `False`。
5.  `DATE_FORMAT`: 如果 `CREATE_DATE_SUBFOLDER` 是 `True`，这里可以定义日期文件夹的格式。
    *   `'%Y-%m-%d'` 会生成 `2023-10-27` 这样的格式。
    *   `'%Y%m%d'` 会生成 `20231027` 这样的格式。
    *   你可以根据喜好调整。

**第四步：运行脚本**

打开你电脑的“命令提示符”或“终端”。

用 `cd` 命令切换到你保存 `file_organizer.py` 文件的那个目录。

比如，如果你保存在 `D:\脚本` 目录下，就输入：

```bash
cd D:\脚本
```

然后敲回车。

接着，输入以下命令来运行脚本：

```bash
python file_organizer.py
```

敲回车！

然后，见证奇迹的时刻到了！

脚本会自动扫描你指定的源文件夹，把文件嗖嗖嗖地移动到目标文件夹对应的分类（和日期子文件夹）里。

屏幕上会显示每个文件的移动情况。

搞定！

## 效果炸裂！时间回来了！

自从用了这个脚本，我再也不用手动整理下载文件夹了！

每天下班前运行一下，所有文件**<font color='green'>井井有条</font>**。

找文件也变得**<font color='orange'>超级快</font>**！

粗略估计，光是整理文件这一项，每天至少帮我省下**<font color='red'>半小时</font>**！

这还只是一个简单的例子！

Python自动化能做的远不止这些！

比如：

*   **自动备份重要文件**到网盘或U盘。
*   **批量处理图片**：调整大小、加水印、转换格式。
*   **自动抓取网页信息**：监控商品价格、获取新闻资讯。
*   **自动操作Excel**：合并表格、提取数据、生成图表。
*   **定时发送邮件/微信消息**。

只要是你在电脑上**<font color='purple'>重复</font>**做的、有**<font color='purple'>规律</font>**可循的操作，大概率都能用Python自动化！

## 总结：拥抱自动化，解放生产力！

别再让重复性工作消耗你的时间和热情了！

花一点点时间学习Python自动化，就能换来**<font color='red'>长期</font>**的效率提升。

这个文件整理脚本只是冰山一角。

当你掌握了Python这个**<font color='blue'>强大武器</font>**，你会发现一个全新的、高效的世界！

每天多出来的那**<font color='red'>3小时</font>**（甚至更多！），你可以用来学习新技能、陪伴家人，或者，就是单纯地放松一下。

**<font color='green'>行动起来吧！</font>**

从这个简单的脚本开始，尝试用Python解决你工作中的一个小痛点。

相信我，一旦你体验到自动化的甜头，你会**<font color='orange'>彻底爱上</font>**它！

## 互动一下

你现在每天被哪些**<font color='purple'>重复性</font>**工作困扰？

或者你有什么**<font color='blue'>自动化</font>**的小妙招？

欢迎在评论区留言分享！

**<font color='red'>下期预告</font>**：想不想让这个脚本更智能？比如自动识别图片内容进行分类？或者自动解压压缩包？关注我，下期带来更**<font color='orange'>进阶</font>**的玩法！