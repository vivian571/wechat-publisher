# 花了3个小时，我用AI开发了一个markdown文档编辑器

> "老师，有没有简单好用的Markdown编辑器推荐？市面上的要么太复杂，要么功能不全..."

这是最近收到的一条留言。

确实，找一个称心如意的Markdown编辑器不容易。

要么功能太简单，写起长文档来捉襟见肘。

要么功能太复杂，界面堆满了按钮，用起来像在驾驶宇宙飞船。

于是我想：为什么不自己做一个呢？

正好最近AI编程工具这么强大，何不试试看？

说干就干，我花了3个小时，用AI辅助开发了一个简洁实用的Markdown编辑器。

下面就和大家分享我的开发过程和成果，保证让你看完后直呼："原来用AI开发这么简单！"

## 一、为什么要自己开发Markdown编辑器？

![Markdown编辑器效果图](https://raw.githubusercontent.com/microsoft/vscode-docs/main/docs/images/markdown/preview.png)

市面上的Markdown编辑器要么太简陋，要么太臃肿。

简陋的只有基本编辑功能，缺乏实时预览、代码高亮等实用特性。

臃肿的则塞满了各种你可能一辈子都用不到的功能，界面复杂得像飞机驾驶舱。

我想要的很简单：
- 界面干净整洁
- 实时预览
- 支持常用Markdown语法
- 代码块高亮
- 一键导出HTML/PDF
- 自动保存

最重要的是，我希望它完全按照我的使用习惯来设计。

## 二、AI辅助开发的惊人效率

![AI编程助手](https://miro.medium.com/max/1400/1*Gh5PS4R_A5drl5eHfr6dyA.png)

以前，开发这样一个应用可能需要一周甚至更长时间。

但有了AI编程助手（我用的是GitHub Copilot和ChatGPT），整个过程快得惊人！

我只需要：
1. 描述我想要的功能
2. 审查AI生成的代码
3. 进行必要的调整
4. 测试和完善

整个过程就像和一个资深程序员结对编程，但这个"程序员"不会累，不会抱怨，也不会要求加薪。

## 三、技术选型：简单但够用

![技术栈](https://miro.medium.com/max/1400/1*aTYOTFS4Vh4dXGboFDHwYw.png)

在AI的建议下，我选择了以下技术栈：

- **前端框架**：React（轻量级且生态丰富）
- **Markdown解析**：Marked.js（高效且易于扩展）
- **代码高亮**：Highlight.js（支持200+编程语言）
- **CSS框架**：Tailwind CSS（快速构建UI）
- **构建工具**：Vite（超快的热重载）

这个组合既简单又强大，完全能满足我的需求。

最棒的是，AI对这些技术都非常熟悉，能生成高质量的代码。

## 四、开发过程：与AI的完美配合

### 第一步：项目初始化（30分钟）

首先，我让AI帮我生成了项目的基本结构和配置文件。

```bash
# AI建议的项目初始化命令
npm create vite@latest md-editor -- --template react
cd md-editor
npm install marked highlight.js tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

然后，AI生成了Tailwind CSS的配置文件和基本的项目结构。

这一步最让我惊讶的是，AI不仅生成了代码，还解释了每个依赖包的作用，帮我避开了可能的兼容性问题。

### 第二步：编辑器核心功能（1小时）

接下来是最关键的部分：实现Markdown编辑和预览功能。

我向AI描述了我想要的功能，它立刻生成了核心组件的代码：

```jsx
import { useState, useEffect } from 'react';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

// 配置marked使用highlight.js进行代码高亮
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true
});

function MarkdownEditor() {
  const [markdown, setMarkdown] = useState('# 欢迎使用Markdown编辑器\n\n开始输入...');
  const [html, setHtml] = useState('');
  
  // 当markdown内容变化时，更新预览
  useEffect(() => {
    setHtml(marked(markdown));
  }, [markdown]);
  
  // 自动保存功能
  useEffect(() => {
    const savedContent = localStorage.getItem('markdown-content');
    if (savedContent) {
      setMarkdown(savedContent);
    }
    
    // 每5秒自动保存一次
    const saveInterval = setInterval(() => {
      localStorage.setItem('markdown-content', markdown);
    }, 5000);
    
    return () => clearInterval(saveInterval);
  }, [markdown]);
  
  return (
    <div className="flex h-screen">
      {/* 编辑区 */}
      <div className="w-1/2 p-4 border-r">
        <textarea
          className="w-full h-full p-2 font-mono text-sm outline-none resize-none"
          value={markdown}
          onChange={(e) => setMarkdown(e.target.value)}
          placeholder="输入Markdown内容..."
        ></textarea>
      </div>
      
      {/* 预览区 */}
      <div className="w-1/2 p-4 overflow-auto">
        <div 
          className="markdown-preview prose max-w-none"
          dangerouslySetInnerHTML={{ __html: html }}
        ></div>
      </div>
    </div>
  );
}

export default MarkdownEditor;
```

这段代码实现了：
- 分屏编辑和预览
- Markdown实时渲染
- 代码高亮
- 自动保存到本地存储

AI甚至考虑到了性能优化，使用useEffect确保渲染不会造成性能问题。

### 第三步：添加工具栏（45分钟）

为了提高编辑效率，我决定添加一个工具栏，包含常用的Markdown格式化按钮。

AI很快生成了工具栏组件：

```jsx
function Toolbar({ editor, onAction }) {
  const tools = [
    { icon: '# ', title: '标题', action: () => onAction('heading') },
    { icon: '**B**', title: '粗体', action: () => onAction('bold') },
    { icon: '*I*', title: '斜体', action: () => onAction('italic') },
    { icon: '- [ ]', title: '任务列表', action: () => onAction('task') },
    { icon: '`代码`', title: '行内代码', action: () => onAction('inlineCode') },
    { icon: '```', title: '代码块', action: () => onAction('codeBlock') },
    { icon: '[链接]()', title: '链接', action: () => onAction('link') },
    { icon: '![图片]()', title: '图片', action: () => onAction('image') },
    { icon: '> ', title: '引用', action: () => onAction('quote') },
    { icon: '- ', title: '列表', action: () => onAction('list') },
    { icon: '---', title: '分割线', action: () => onAction('divider') },
    { icon: '导出', title: '导出HTML', action: () => onAction('export') },
  ];
  
  return (
    <div className="flex p-2 bg-gray-100 border-b">
      {tools.map((tool, index) => (
        <button
          key={index}
          className="px-2 py-1 mx-1 text-sm rounded hover:bg-gray-200"
          title={tool.title}
          onClick={tool.action}
        >
          {tool.icon}
        </button>
      ))}
    </div>
  );
}
```

然后，AI还实现了每个按钮的具体功能，比如插入标题、粗体、列表等。

最让我惊喜的是，AI还主动提出了一个我没想到的功能：根据选中文本的位置自动定位光标，大大提升了编辑体验。

### 第四步：完善功能和UI（45分钟）

在基本功能完成后，我又和AI一起完善了一些细节：

1. **主题切换**：添加了明暗两种主题
2. **导出功能**：支持导出为HTML和PDF
3. **字数统计**：实时显示文档字数和预计阅读时间
4. **自定义样式**：允许用户调整编辑器字体大小和行高
5. **快捷键支持**：添加常用操作的键盘快捷键

这些功能AI都能快速实现，而且代码质量很高，几乎不需要我做太多修改。

## 五、成果展示：简洁而不简单

![最终成果](https://miro.medium.com/max/1400/1*2N6XkqZGK3Ksna-yyQxMUQ.png)

经过3个小时的开发，我的Markdown编辑器终于完成了！

它拥有以下特点：

- **界面简洁**：分为工具栏、编辑区和预览区三部分
- **实时预览**：编辑内容立即在预览区显示效果
- **语法高亮**：支持多种编程语言的代码高亮
- **自动保存**：定期保存内容到本地，防止意外丢失
- **一键导出**：支持导出为HTML和PDF格式
- **响应式设计**：在手机和平板上也能正常使用

最重要的是，整个应用只有不到500行代码，轻量级且高效。

## 六、使用AI开发的经验总结

![AI开发经验](https://miro.medium.com/max/1400/1*8wNWIYHkr8hFHGG5SuKxCQ.png)

通过这次开发，我总结了几点使用AI辅助编程的经验：

### 1. 清晰描述需求

AI不是读心术，你需要尽可能清晰地描述你想要的功能。

比如不要只说"我想要一个按钮"，而应该说"我想要一个导出PDF的按钮，点击后将当前编辑器内容转换为PDF并下载"。

### 2. 分步骤开发

将大任务分解为小步骤，逐步实现。

每完成一个功能就测试一下，这样更容易发现和修复问题。

### 3. 理解生成的代码

不要盲目复制粘贴AI生成的代码，要花时间理解它的工作原理。

这不仅能帮你发现潜在问题，还能提升你的编程技能。

### 4. 善用AI的专业知识

AI了解最新的库和最佳实践，不要犹豫向它请教技术问题。

比如我在选择Markdown解析库时，AI推荐了Marked.js而不是我原本打算用的库，理由是它更轻量且维护更活跃。

### 5. 迭代改进

第一版代码通常不是最好的。

不断向AI提出改进建议，比如"这段代码如何优化性能"或"如何让这个UI更美观"。

## 七、源码分享

我已经将这个项目开源在GitHub上，感兴趣的小伙伴可以自由下载使用：

```
https://github.com/yourusername/simple-markdown-editor
```

你可以直接克隆项目并按照README中的说明运行：

```bash
git clone https://github.com/yourusername/simple-markdown-editor
cd simple-markdown-editor
npm install
npm run dev
```

欢迎提交Issues和Pull Requests，一起让这个编辑器变得更好！

## 互动环节

你平时用什么工具写Markdown文档？

有没有遇到过让你特别头疼的问题？

如果让你给这个编辑器添加一个功能，你最想添加什么？

欢迎在评论区分享你的想法和建议！

下期预告：我将分享如何用AI在一天内开发一个完整的个人博客系统，敬请期待！

---

PS：如果你对AI辅助编程感兴趣，别忘了点赞、收藏和转发这篇文章。让我们一起探索AI时代的编程新方式！
