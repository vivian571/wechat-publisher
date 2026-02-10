# <font color='OrangeRed'>【保姆级】OpenRouter 终极教程：白嫖最新 AI 大模型，API 调用 很简单！</font>

## <font color='DeepSkyBlue'>引言：AI 圈又炸了！你还在用老掉牙的模型？</font>

**嘿，兄弟们！**

最近是不是感觉 AI 圈一天一个样？

各种新模型层出不穷，看得眼花缭乱？

想尝鲜最新的 **<font color='red'>GPT-4o</font>**？想试试 **<font color='red'>Claude 3 Opus</font>**？

但是！

官方 API 要么 **<font color='purple'>贵</font>**，要么 **<font color='purple'>申请麻烦</font>**，要么 **<font color='purple'>网络卡顿</font>**？

**<font color='green'>别慌！</font>**

今天，老司机就带你上高速！

隆重介绍一个 **<font color='OrangeRed'>神器</font>** —— **<font color='OrangeRed'>OpenRouter</font>**！

让你 **<font color='green'>轻松白嫖</font>** 各路顶尖 AI 大模型！

还能 **<font color='green'>丝滑调用 API</font>**！

甚至可能在你的 **<font color='green'>聊天软件里免费用</font>**！

**<font color='blue'>准备好了吗？发车！</font>** 🚗💨

---

## <font color='DeepSkyBlue'>第一站：OpenRouter 是个啥？凭啥这么牛？</font>

**简单粗暴地说：**

OpenRouter 就是一个 **<font color='red'>AI 模型聚合平台</font>** + **<font color='red'>API 中转站</font>**。

**<font color='green'>想象一下：</font>**

你想吃麦当劳，又想喝星巴克，还想来份肯德基。

以前你得跑三家店。

现在！

OpenRouter 就是那个 **<font color='OrangeRed'>超级外卖平台</font>**！

**<font color='blue'>一个账号，一个 API Key</font>**，就能点到 **<font color='red'>几乎所有主流 AI 大模型</font>** 的“外卖”！

**<font color='green'>它的牛逼之处在于：</font>**

*   **<font color='OrangeRed'>模型超多！</font>** GPT 系列、Claude 系列、Google 的 Gemini、开源的 Llama、Mistral...应有尽有！你想用的，它基本都有！**（选择困难症犯了没？😂）**
*   **<font color='OrangeRed'>价格透明！</font>** 不同模型明码标价，按量计费，童叟无欺。甚至还有 **<font color='red'>免费额度</font>** 和 **<font color='red'>低价模型</font>** 让你薅羊毛！**（白嫖党的福音！🎉）**
*   **<font color='OrangeRed'>API 统一！</font>** 不管你用哪个模型，API 接口格式基本一致，遵循 OpenAI 的标准。切换模型？改个模型名字就行！**（开发者的最爱！💖）**
*   **<font color='OrangeRed'>速度可能更快！</font>** OpenRouter 有自己的服务器中转，有时候比直连官方还快！**（告别卡顿！🚀）**
*   **<font color='OrangeRed'>注册简单！</font>** 不需要国外手机号，邮箱就能搞定！**（门槛超低！👍）**

**<font color='blue'>总之，OpenRouter 就是帮你打破壁垒，让你更方便、更便宜地玩转各种 AI 大模型的利器！</font>**

---

## <font color='DeepSkyBlue'>第二站：三步搞定 OpenRouter 账号和 API Key</font>

**<font color='green'>别眨眼，操作极其简单！</font>**

**第一步：打开官网，光速注册！**

浏览器输入：`https://openrouter.ai`

点击 **<font color='blue'>"Sign Up"</font>**。

可以用 Google 账号、邮箱等方式注册。

**<font color='red'>推荐用邮箱</font>**，简单直接。

填个邮箱，设个密码，点一下验证邮件里的链接，**<font color='green'>搞定！</font>** 👌

**第二步：进入后台，找到 API Key！**

登录成功后，点击右上角的 **<font color='blue'>头像/用户名</font>**。

在下拉菜单里找到 **<font color='blue'>"Keys"</font>** 或者 **<font color='blue'>"API Keys"</font>**。

点击 **<font color='blue'>"Create Key"</font>**。

给你的 Key 起个名字（方便管理，比如 "MyAwesomeApp"）。

**<font color='OrangeRed'>重点来了！</font>**

你会看到一长串 **<font color='red'>以 `sk-or-v1-` 开头的神秘代码</font>**。

**<font color='purple'>这就是你的 API Key！</font>**

**<font color='red'>立刻！马上！复制它！</font>**

**<font color='red'>并且！找个安全的地方存好！</font>**

**<font color='red'>因为这个 Key 只会显示一次！关掉就没了！</font>** （丢了就只能重新创建一个了）

**第三步：充点小钱，激活账户（可选但推荐）**

虽然 OpenRouter 有些免费模型，但很多强大的模型还是要收费的。

点击左侧菜单的 **<font color='blue'>"Credits"</font>** 或 **<font color='blue'>"Billing"</font>**。

你可以绑定信用卡或者用加密货币充值。

**<font color='green'>建议先充个 5 美元或 10 美元试试水。</font>**

放心，按量计费，用多少扣多少，不用不扣钱。

**<font color='blue'>好了！三步走完，你已经拥有了打开 AI 新世界大门的钥匙！</font>** 🔑

---

## <font color='DeepSkyBlue'>第三站：Show Time！用 Python 调用 OpenRouter API</font>

**<font color='green'>理论讲完了，上代码！</font>**

我们用 Python 来演示如何调用 OpenRouter API。

**<font color='red'>前提：你需要安装 OpenAI 的 Python 库。</font>**

为啥是 OpenAI 的库？因为 OpenRouter 兼容它的 API 格式！方便！

打开你的终端（命令行），输入：

```bash
pip install openai
```

**<font color='green'>装好了？开始写代码！</font>**

```python
# 导入必要的库
import os
from openai import OpenAI

# 关键步骤：配置 API Key 和 Base URL
# 强烈建议使用环境变量存储 API Key，更安全！
# 你可以手动设置： os.environ['OPENROUTER_API_KEY'] = '你的 sk-or-v1-... 开头的 API Key'
# 或者直接在代码里写（但不推荐，容易泄露）:
# api_key = "你的 sk-or-v1-... 开头的 API Key"

# 从环境变量读取 API Key
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("错误：请先设置 OPENROUTER_API_KEY 环境变量！")
    # 或者在这里直接赋值你的 Key (仅作演示，不推荐)
    # api_key = "你的 sk-or-v1-... 开头的 API Key"
    # if not api_key: exit()
    exit()

# 初始化 OpenAI 客户端，指向 OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1", # OpenRouter 的 API 地址
    api_key=api_key, # 你的 OpenRouter API Key
)

# 定义你要调用的模型和你的问题
model_name = "openai/gpt-3.5-turbo" # 试试免费的 GPT-3.5 Turbo
# model_name = "anthropic/claude-3-haiku" # 或者试试 Claude 3 Haiku (可能需要付费)
# model_name = "google/gemini-flash-1.5" # 或者 Google 的 Gemini Flash (可能需要付费)
# 更多模型可以在 OpenRouter 官网 Models 页面找到！

user_prompt = "你好！给我讲个关于程序员的冷笑话吧。"

print(f"正在使用模型: {model_name}")
print(f"你的问题: {user_prompt}")

# 发起 API 请求
try:
    completion = client.chat.completions.create(
        model=model_name, # 指定模型
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        # 可选参数：
        # max_tokens=150, # 最大生成字数
        # temperature=0.7, # 创造性程度 (0-2, 越高越随机)
        # stream=False, # 是否流式输出 (True 的话需要不同处理方式)
    )

    # 提取并打印 AI 的回答
    ai_response = completion.choices[0].message.content
    print("\nAI 的回答:")
    print(ai_response)

    # 打印一些额外信息 (可选)
    # print("\n--- 调试信息 ---")
    # print(f"模型实际使用: {completion.model}")
    # print(f"花费 Tokens: {completion.usage.total_tokens}")

except Exception as e:
    print(f"\n出错了 T_T: {e}")

```

**<font color='blue'>代码解释：</font>**

1.  **<font color='green'>导入 `openai` 库。</font>**
2.  **<font color='OrangeRed'>设置 `api_key`</font>**：**<font color='red'>强烈建议</font>** 把你的 OpenRouter API Key 设置成环境变量 `OPENROUTER_API_KEY`，这样代码里就不用明文写 Key 了，更安全。如果图省事，也可以直接在代码里赋值（但不推荐）。
3.  **<font color='OrangeRed'>初始化 `OpenAI` 客户端</font>**：
    *   `base_url` **<font color='red'>必须</font>** 设置为 `https://openrouter.ai/api/v1`。
    *   `api_key` 就是你刚刚获取的 OpenRouter Key。
4.  **<font color='green'>指定 `model_name`</font>**：去 OpenRouter 官网的 "Models" 页面找你喜欢的模型名字，比如 `openai/gpt-3.5-turbo`、`anthropic/claude-3-opus` 等。
5.  **<font color='green'>准备 `messages`</font>**：这是一个列表，里面包含对话历史。最简单的就是放一个 `role` 为 `user` 的字典，`content` 是你的问题。
6.  **<font color='green'>调用 `client.chat.completions.create()`</font>**：把模型名字和消息传进去，发起请求。
7.  **<font color='green'>处理 `completion`</font>**：返回结果在 `completion.choices[0].message.content` 里。
8.  **<font color='red'>错误处理</font>**：用 `try...except` 包裹起来，防止网络问题或 API 错误导致程序崩溃。

**<font color='blue'>运行一下试试！</font>**

把你的 API Key 填进去（或者设置好环境变量），然后运行这个 Python 脚本。

看看 AI 是不是给你讲了个冷笑话？😄

**<font color='OrangeRed'>是不是很简单？！</font>**

你可以随便换 `model_name` 和 `user_prompt` 来玩！

---

## <font color='DeepSkyBlue'>第四站：进阶玩法 & 省钱妙招</font>

**<font color='green'>掌握了基本操作，我们来点高级的！</font>**

*   **<font color='OrangeRed'>模型选择困难？看这里！</font>**
    *   **<font color='blue'>免费/低价优先：</font>** `openai/gpt-3.5-turbo`, `anthropic/claude-3-haiku`, `google/gemini-flash-1.5`, `mistralai/mistral-7b-instruct` 等，性价比超高！适合日常聊天、简单任务。
    *   **<font color='blue'>追求最强性能：</font>** `openai/gpt-4o`, `anthropic/claude-3-opus`, `google/gemini-pro-1.5`。贵是贵了点，但效果顶尖！适合复杂推理、高质量内容生成。
    *   **<font color='blue'>特定领域模型：</font>** 有些模型擅长编码、有些擅长创意写作，可以去 OpenRouter 官网看模型的详细介绍和评分。
    *   **<font color='red'>小技巧：</font>** OpenRouter 网站上模型列表可以按价格排序！先找便宜的试试！

*   **<font color='OrangeRed'>API 参数微调，效果大不同！</font>**
    *   `temperature`：控制输出的随机性。**<font color='blue'>值越高越“放飞自我”</font>**，适合创意写作；**<font color='blue'>值越低越“一本正经”</font>**，适合需要精确答案的场景。默认一般是 0.7 左右。
    *   `max_tokens`：限制 AI 回答的最大长度（按 token 计算，不是字数）。防止话痨 AI 停不下来，也帮你省钱！
    *   `stream=True`：流式输出。AI 会一个字一个字地返回结果，就像打字机一样。适合做实时聊天界面，用户体验更好。（代码处理会稍微复杂一点，需要循环接收数据）

*   **<font color='OrangeRed'>省钱！省钱！省钱！</font>**
    *   **<font color='red'>善用免费/低价模型！</font>** 不是所有任务都需要 GPT-4o，杀鸡焉用牛刀？
    *   **<font color='red'>优化 Prompt！</font>** 清晰、简洁的 Prompt 能让 AI 更快理解你的意图，减少不必要的对话轮次和 token 消耗。
    *   **<font color='red'>限制 `max_tokens`！</font>** 给 AI 的回答长度设个上限。
    *   **<font color='red'>监控花费！</font>** 经常去 OpenRouter 后台看看你的 Credits 余额和消费明细，做到心中有数。

*   **<font color='OrangeRed'>在聊天软件里用？</font>**
    *   很多第三方 AI 聊天软件或客户端（比如 LobeChat, ChatBox, NextChat 等）都支持 **<font color='blue'>自定义 API Endpoint</font>** 和 **<font color='blue'>API Key</font>**。
    *   你只需要把它们的 API 地址设置为 OpenRouter 的 `https://openrouter.ai/api/v1`，再填入你的 OpenRouter API Key。
    *   然后就可以在这些软件里选择 OpenRouter 提供的各种模型来聊天了！
    *   **<font color='green'>相当于用一个软件，就能和几十个不同的 AI 大模型对话！</font>**
    *   **<font color='red'>注意：</font>** 这种方式本质上还是通过你的 OpenRouter 账号调用 API，该付费的模型还是要扣你的 Credits 哦！但确实方便了很多！

---

## <font color='DeepSkyBlue'>第五站：总结 & 下一步去哪儿？</font>

**<font color='green'>恭喜你！</font>**

你已经成功解锁了 OpenRouter 这个强大的 AI 工具！

**<font color='blue'>回顾一下：</font>**

*   我们知道了 OpenRouter 是个 **<font color='red'>模型聚合</font>** + **<font color='red'>API 中转</font>** 神器。
*   我们学会了 **<font color='red'>注册账号</font>**、**<font color='red'>获取 API Key</font>**。
*   我们用 Python **<font color='red'>成功调用</font>** 了 OpenRouter API。
*   我们了解了 **<font color='red'>模型选择</font>**、**<font color='red'>参数调整</font>** 和 **<font color='red'>省钱技巧</font>**。
*   我们还知道了如何在 **<font color='red'>聊天软件</font>** 里接入 OpenRouter。

**<font color='OrangeRed'>现在，你可以：</font>**

*   尽情 **<font color='green'>体验</font>** 各种最新的 AI 大模型！
*   把 OpenRouter API **<font color='green'>集成</font>** 到你自己的项目里！
*   开发出 **<font color='green'>酷炫</font>** 的 AI 应用！

**<font color='purple'>但是！</font>**

关于 OpenRouter，还有更多有趣的玩法和细节值得探索！

比如：

*   如何处理 **<font color='blue'>流式输出 (stream=True)</font>** 的 API 响应？
*   如何更精细地 **<font color='blue'>控制成本</font>** 和 **<font color='blue'>监控用量</font>**？
*   OpenRouter 上那些 **<font color='blue'>小众但有趣</font>** 的模型怎么玩？
*   遇到 API 调用 **<font color='blue'>报错</font>** 怎么办？

**<font color='red'>想知道答案吗？</font>** 😉

---

## <font color='DeepSkyBlue'>互动环节：你的下一个 AI 项目是？</font>

**<font color='green'>老铁们！</font>**

学会了 OpenRouter，你最想用它来做什么？

是想打造一个 **<font color='blue'>超级 AI 聊天助手</font>**？

还是想开发一个 **<font color='blue'>AI 绘画工具</font>**？（虽然 OpenRouter 主要是文本模型，但思路可以借鉴嘛）

或者只是想 **<font color='blue'>白嫖各种模型</font>**，和 AI 吹牛聊天？😂

**<font color='OrangeRed'>在评论区告诉我你的想法吧！</font>** 👇

**<font color='red'>点赞、在看、转发</font>** 三连，下次带你解锁更多 AI 黑科技！✨

**<font color='purple'>敬请期待下一期！</font>** 😉

#ai时代 #工具分享 #openrouter #ai资讯 #前沿科技 #api调用 #python #保姆级教程