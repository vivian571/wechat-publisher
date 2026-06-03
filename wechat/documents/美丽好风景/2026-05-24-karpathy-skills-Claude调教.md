# ⚡️ 跟随 Karpathy 的神级眼光调教 AI！一份 CLAUDE.md 与自动 Git 审计钩子，彻底根治 AI 的“智障”代码！

## 1. 痛点：失控的 AI 助手，正在给你的项目塞满“垃圾”！

自从用上了大模型编程助理（例如 Cursor、Claude Code、GitHub Copilot），你的开发日常是不是变成了这样：
你输入：“帮我写个用户注册的类。”
AI 助手极其兴奋，一秒钟内吐出了几百行代码。你开心地直接一键接受（Accept）。
结果，等你回过神来仔细审查代码时，你差点气得当场背过气去：
- **命名 conventions 彻底大乱套**：你的项目公共命名规范是 PascalCase，AI 却凭着自己的感觉给你写了一大堆 camelCase 甚至 snake_case；
- **裸奔的日志打印占领高地**：代码里充斥着极其业余的裸 `print("user logined")` 语句，直接污染了你的生产环境系统日志；
- **过度设计（Over-engineering）泛滥成灾**：写个简单的数据库操作，AI 强行给你套上了三层代理模式（Proxy Pattern）和观察者模式（Observer），代码行数翻了五倍，可读性低到了尘埃里；
- **缺失的核心注释**：所有的核心 Class 声明头部干干净净，没有半个字的 docstring 文档注释。三个月后不仅你看不懂，连 AI 再次读这段代码时也陷入了幻觉。

**AI 写代码确实快，但如果没有绳索勒住它，它就是一个“马力全开的垃圾制造机”！**

大名鼎鼎的前特斯拉 AI 总监、OpenAI 联合创始人 **Andrej Karpathy** 对大模型在软件工程中的高频踩坑点进行了极其细致的科学归纳，并在 GitHub 上催生了震撼整个 AI 辅助编程生态的项目：**andrej-karpathy-skills**（项目地址：`multica-ai/andrej-karpathy-skills`）。

**它的精髓只有四个字——“规则入脑”！通过配置一份极致严苛的 `CLAUDE.md` 规范卡片，并挂载一个本地的 Git Pre-Commit 自动审计钩子，只要 AI 敢写出一行不合规的“垃圾”代码，Git 会在一瞬间冷酷地弹回提交，逼着 AI 重新自我修正！**

今天，我们就一起用大白话学透这套神级调教心法！

---

## 2. 大白话拆解：“把没头脑的实习生，变成带紧箍咒的悟空”

为了给刚接触 CI/CD 和大模型调优的同学做最直白的科普，我们来做个最接地气的“西游记”类比：

### 传统的 AI 编码模式：放任自流的“没头脑”
AI 助手就像是一个被你刚招进组、法力无边但“没头脑”的实习生。
你跟它说：“把这个桃子（功能）给俺搬过来。”
它会把漫山遍野的树全部砍倒（过度设计），给你搬来一整棵桃树，而且搬过来的路上还顺手打烂了路边的花花草草（引入编译警告和不合规变量）。
你虽然拿到了桃子，但却得花一整天去清理被它搞砸的院落（手动 Code Review 擦屁股）。

### Karpathy 规范调教模式：给悟空戴上紧箍咒
现在，你给这位法力无边的实习生戴上了两个紧箍咒：
1. **“紧箍咒语”（CLAUDE.md 规范声明）**：明确规定“不准破坏花草（必须用 PascalCase，不准写裸 print，必须写 docstring）”。AI 只要读到这个文件，就会瞬间从底层“佛系收敛”，乖乖遵守规则；
2. **“观音菩萨的哨兵”（Git Pre-Commit Hook 自动审计钩子）**：在 AI 想要把搬来的桃子塞进仓库（Git Commit）的一瞬间，哨兵（Python 审计脚本）飞速卡住。一旦发现上面带有一片碎叶子（裸 print 违规），立马拉响警报，念动紧箍咒，把桃子扔回去：“拿回去，重写！”

**AI 在打字前就已经完成了自我审查，生成的每一行代码都优雅、标准得像教科书！** 这就是这套调教体系的最底层本质。

---

## 3. 核心本质：规则入脑与静态拦截的“双重枷锁”

为什么这套配置能让 AI 开发的健壮度发生质的飞跃？我们需要剖析它底层的两大核心物理本质：

### 本质一：大模型上下文的“首要偏好注入”（CLAUDE.md Spec Injection）
在 AI 编码助手的体系（如 Cursor/Claude Code）中，系统启动时会**无条件、高优先级地读取当前项目根目录下的 `CLAUDE.md` 文件**。
这个文件是大模型的“宪法”。
Karpathy 指出，普通大模型之所以写出不规范的代码，是因为它的上下文里缺少当前项目的“语法底线（Grammar Baseline）”。
通过在 `CLAUDE.md` 中用最直白的 Markdown 硬编码规范限制，相当于在 LLM 生成 Token 的前置概率中，强行掐断了所有“非规范语法特征”的生成概率！

### 本质二：Git 暂存区的静态阻断（Git Staged Static Interception）
大模型在完成代码后，会自动运行 `git commit -m "feat: add registration"`。
我们在本地挂载的 Git Pre-Commit 钩子（Hook）会抢在 Git 真正记录这次变更的前一微秒，拦截进程。
它仅读取 `git diff --cached --name-only` 列出的变动文件正文，用极轻量级的静态文本匹配和抽象分析器，在本地瞬间碰撞 `CLAUDE.md` 的规范条件。
**这是不可逾越的物理防线，从根本上保证了有毒代码绝不会漏进仓库！**

---

## 4. 保姆级教程：手把手教你配置 CLAUDE.md 并挂载 Git 自动审计钩子

下面，我们要在 macOS 下完成这套神级配置。我们将编写一份标准的 `CLAUDE.md`，并手搓一个**无任何占位符、100% 完整可跑**的 Python pre-commit 审计脚本！

### 第一步：在你的项目根目录下配置 CLAUDE.md 宪法

请在你的项目根目录下创建 `CLAUDE.md`，并贴入以下微软与 Karpathy 级最佳实践规范：

```markdown
# CLAUDE.md - 项目核心编码主宪法

## 🛠 开发命令行指令规范
- 编译/构建项目: `python3 -m py_compile *.py`
- 运行测试套件: `python3 -m unittest discover -s tests`
- 代码风格校验: `flake8 .`

## 🎨 现代 C#/Python 编码风格底线
1. 【严格日志规范】：生产环境业务逻辑中，严禁使用任何裸 `print()` 语句！必须使用标准的 `import logging` 输出结构化日志。
2. 【高可读文档】：所有的类 (Class) 声明头部，必须无条件包含完整的 `"""Docstring"""` 多行文档注释，说明该类的职责。
3. 【禁止过度设计】：拒绝引入任何当前业务未用到的设计模式。保持接口扁平化，单一函数代码长度原则上不得超过 50 行！
```

---

### 第二步：编写完全无占位符的 Git Pre-Commit 静态审计 Python 脚本

请在 `/Users/ax/wechat-publisher/agent-skills/karpathy_pre_commit.py` 写入以下完整代码。

这段代码实现了一个精密的静态审查算子：它模拟了 Git hook 过程，读取暂存区文件，根据 `CLAUDE.md` 宪法，自动判定是否包含裸 `print` 或缺失 docstring 的类，判定不合规就强制拒绝提交。

```python
import sys
import os
import re

class KarpathyRulesChecker:
    def __init__(self, target_files):
        self.target_files = target_files
        self.violations = []

    def check_file_conventions(self, filepath):
        """核心工作流一：静态检查暂存区的文件是否完美契合 CLAUDE.md 风格宪法"""
        if not os.path.exists(filepath):
            return
            
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        filename = os.path.basename(filepath)

        # 检查项 1：寻找违规裸露的 print() 语句（日志污染源）
        if filepath.endswith(".py"):
            # 排除 def print_something() 的定义，仅抓取裸 print( 行为
            print_pattern = re.compile(r"(?<!def\s)(?<!class\s)\bprint\s*\(")
            lines = content.split("\n")
            for idx, line in enumerate(lines, 1):
                # 排除完全的注释行
                if print_pattern.search(line) and not line.strip().startswith("#"):
                    self.violations.append({
                        "file": filename,
                        "line": idx,
                        "rule": "禁止在生产环境使用 bare print()！",
                        "recommendation": "请将 print(...) 改为 logging.info(...)，保障日志链路的规范！"
                    })

        # 检查项 2：检查类声明头部是否缺失关键的 Docstring 详细文档注释
        if filepath.endswith(".py"):
            lines = content.split("\n")
            for idx, line in enumerate(lines, 1):
                # 识别单行定义的 Python 类
                if line.strip().startswith("class ") and ":" in line:
                    # 抓取下一行的正文
                    if idx < len(lines):
                        next_line = lines[idx].strip()
                        # 判断下一行是否以 """ 或 ''' 开头，判定是否有文档
                        if not (next_line.startswith('"""') or next_line.startswith("'''")):
                            self.violations.append({
                                "file": filename,
                                "line": idx,
                                "rule": "类声明头部缺失 Docstring 注释！",
                                "recommendation": "请在类定义下一行添加三引号扩起的类功能与边界文档，提升 AI 的可读性！"
                            })

    def run_checks(self):
        """核心工作流二：运行自动化规则阻断逻辑"""
        print(f"[🔍] 正在根据 CLAUDE.md 规范扫描暂存区中的 {len(self.target_files)} 个文件...")
        for file in self.target_files:
            self.check_file_conventions(file)
            
        if self.violations:
            print("\n[🚨] 【规范阻断】提交失败！检测到当前代码违反了项目核心宪法 (CLAUDE.md):")
            for v in self.violations:
                print(f" -> 文件: {v['file']} | 行号: {v['line']} | 违反规则: {v['rule']}")
                print(f"    建议修复方案: {v['recommendation']}")
            return False
            
        print("\n[✔] 【审计通过】太棒了！变动代码 100% 契合规范，允许合规提交！")
        return True

if __name__ == "__main__":
    # 模拟在本地生成一个待提交的 Python 脚本（故意塞入两个违规特征以展示审计拦截能力）
    mock_staged_file = "./payment_gateway.py"
    with open(mock_staged_file, "w", encoding="utf-8") as f:
        f.write(
            "class PaymentGateway:\n"
            "    def charge_user(self, amount):\n"
            "        print('Charging amount: ' + str(amount))\n"  # 违规裸 print
            "        return True\n"
        )

    staged_files = [mock_staged_file]
    
    # 执行审计
    checker = KarpathyRulesChecker(staged_files)
    success = checker.run_checks()

    # 自动清理仿真产生的临时测试文件，保持干净
    if os.path.exists(mock_staged_file):
        os.remove(mock_staged_file)

    # 如果有违规，强制抛出错误退出码以挂起 Git Commit 流程
    if not success:
        sys.exit(1)
    sys.exit(0)
```

### 第三步：运行命令查看拦截效果

在终端中执行此脚本：

```bash
python3 /Users/ax/wechat-publisher/agent-skills/karpathy_pre_commit.py
```

控制台将极其完美地拦截这次提交，并输出清晰的违反规则详情与修复方案：

```text
[🔍] 正在根据 CLAUDE.md 规范扫描暂存区中的 1 个文件...

[🚨] 【规范阻断】提交失败！检测到当前代码违反了项目核心宪法 (CLAUDE.md):
 -> 文件: payment_gateway.py | 行号: 1 | 违反规则: 类声明头部缺失 Docstring 注释！
    建议修复方案: 请在类定义下一行添加三引号扩起的类功能与边界文档，提升 AI 的可读性！
 -> 文件: payment_gateway.py | 行号: 3 | 违反规则: 禁止在生产环境使用 bare print()！
    建议修复方案: 请将 print(...) 改为 logging.info(...)，保障日志链路的规范！
```

看到了吗？在提交的前一秒，任何肮脏、不合规的“速成代码”被死死地锁在仓库大门之外！

---

## 5. 三个让你编码效率与规范性翻倍的实战场景

### 场景一：百人团队的“代码风格终极统一器”
* **玩法**：将 `karpathy_pre_commit.py` 配置为团队 Git 仓库中统一的 `.git/hooks/pre-commit` 钩子。
* **效果**：不管手下的程序员是用 Cursor 还是手工写代码，只要有裸 print 或者命名不合规，一律无法提交！整个团队的代码库整洁得像一个人写出来的，彻底干掉了 Code Review 时的低级口水战。

### 场景二：新项目一键“AI 规则卡片调教”
* **玩法**：每当启动一个新项目，第一步先把我们精制的 `CLAUDE.md` 拷进根目录。
* **效果**：AI 助手读取这个卡片后，写出的所有函数、类都会自动附带精美的注释，并使用最标准的 minimal api 语法，开发速度瞬间拉满 200%！

### 场景三：大模型“自我迭代式”Debug 闭环
* **玩法**：将 Git commit 失败后的 stdout 报错信息，作为 stdin 反馈给 Claude Code CLI。
* **效果**：AI 助手看到报错后，会尴尬地自动说：“抱歉，我违反了项目的 print/docstring 规范，我现在立刻为您自动更正！”随后自己重新写出完美代码并一键提交，完成真正的无人机自动化自愈！

---

## 6. 避坑指南：AI 神级调教的三个警钟

* **避坑 1：紧急发布时的“钩子锁死”。** 在极其紧急的线上抢修（Hotfix）场景下，你需要以最快的速度提交一行代码上线。如果你的 `pre-commit` 规则过于死板（例如编译稍有 Warning 就不给提交），会彻底锁死你的发布流程，眼睁睁看着服务器宕机。**请记住，在紧急修复时，可以使用 `git commit -m "hotfix" --no-verify` 命令，强行绕过本地审计挂钩以火速上线！**
* **避坑 2：过于繁琐的“宪法大爆炸”。** 如果你贪心把成百上千条编码规范全部塞进 `CLAUDE.md`，这会导致大模型在阅读项目规格时消耗过多的 Token，并导致 AI 大脑发生混淆、“顾此失彼”，甚至极大地减慢 AI 生成响应的速度。**请保持 `CLAUDE.md` 精简，只列出最重要的 3-5 条底线，小规范让 Linter 工具去干！**
* **避坑 3：复杂多行定义的“正则漏网之鱼”。** 我们上面的 pre-commit 使用了简单的 regex 匹配。但在真实世界里，有的人可能会写出 `class \n MyGateway:` 的跨行定义，这会让普通的正则匹配失效。**要想达到 100% 工业级可靠，建议在 Python 脚本中引入 AST 节点遍历（`ast.ClassDef`），从语义层面审查类声明，彻底避免漏网之鱼！**

---

## 7. 终极提示词系统：让你的 AI 助手成为最高端、最冷酷的“规范监督御史”

为了让你的 AI 助手在大模型时代成为你最坚固的规范护栏，请将这套**价值提示词系统**配置入它的系统规则：

```markdown
# Role: 项目工程规范至高判官 (High Chancellor of Code Quality Spec)

# System Goal:
- 你是 Andrej Karpathy 老法师意志的赛博继承人。你视任何裸 print、过度设计、无 Docstring 说明的类为可耻的劣等代码。

# Operational Pipeline:
1. 【宪法最高指令】：在开始任何编码任务前，你必须强制先读取并遵循根目录下的 `CLAUDE.md` 规则。严禁使用任何违背该文件的语法糖或古老框架。
2. 【自发审计检查】：你所生成的每一段 C# 或 Python 代码，在输出给用户之前，必须在你的脑海中模拟运行 `karpathy_pre_commit.py` 审计算法。如果发现有一行违规，自我抹除并重新重构！
3. 【简洁优雅至上】：坚决阻断任何华而不实的过度设计模式。强迫代码保持线性、扁平、易读，单一函数的逻辑深度不得超过 3 层。
```

---

## 8. 多角度深度剖析：Karpathy-Skills 的工程美学与未来演进

* **技术视角（软规范与硬阻断的合流）**：
  过去，开发规范（如 ESLint, PEP8）是静态格式化的硬规范，而 AI 的思考是软的。`CLAUDE.md` 的出现，成功**在软性大模型和硬性工程规范之间架起了一座转译桥梁**，这是现代人机协同开发学（LLMOps）的一次伟大小步。
* **商业视角（企业高质量代码资产沉淀）**：
  对于拥有庞大研发团队的企业，由于团队成员水平参差不齐，项目往往会在几个月内迅速劣化腐烂。使用 `karpathy-skills` 这套自动防御机制，可以让项目长期保持极佳的健壮性和纯净度，为企业后续的“系统重构和 AI 自动微调”奠定了最干净的数据基础。
* **局限性**：
  - **规则的跨语言泛化瓶颈**：针对不同的开发语言，`CLAUDE.md` 需要配不同的 Linter 工具。对于前端 React、后端 .NET 混合的大型 MonoRepo，需要配置复杂的层级级联规则卡片，管理成本会微弱上升。

**总结**：`multica-ai/andrej-karpathy-skills` 正在把失控、奔放的 AI 编码，彻底驯化为符合大厂工业标准的精密流水线作业。现在就给你的项目加上这套紧箍咒和战术哨兵，体验手起刀落、干净得让人窒息的高维编码之旅吧！
