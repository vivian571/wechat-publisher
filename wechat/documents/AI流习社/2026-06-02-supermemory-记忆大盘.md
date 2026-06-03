# 智能体记忆大盘与轻量化语义向量检索网关：手搓 TF-IDF 文本能谱分析、余弦相似度计算与离线记忆索引数据库

### AI 记性比你还好，它怎么做到的？

你有没有遇到过这种情况：
早上刚看的一篇高价值干货，下午想用时，怎么也想不起来关键词；
或者，跟 AI 聊天聊到一半，它突然把你前三句话的设定给“忘干净了”！
**记忆力断层，不管是人类还是智能体，都是致命硬伤！**
智能体（Agent）要真正融入我们的工作流，就必须拥有一颗坚不可摧的“数字记忆大脑”。
今天，我们就来手搓一个纯本地、轻量级、绝对离线的**智能体记忆大盘与语义检索网关**。
不用部署重型向量数据库（如 Pinecone 或 Milvus），不需要繁琐地申请第三方 OpenAI Embedding API 密钥。
直接使用经典的物理特征能谱——**TF-IDF（词频-逆文档频率）**与**高维余弦相似度算法**，在 macOS 上手搓一个秒级语义检索的智能体记忆中心！

---

### 底层大白话：什么是语义的“能谱地图”？

有同学会问：“老师，计算机只认得 0 和 1，它是怎么理解两句话‘意思相近’的呢？”
其实，这就是数学上的**空间夹角**！
我们可以用一个非常通俗的类比：**每一篇记忆日记，都是空气中漂浮的一颗星星；而星星所在的坐标，是由它里面的词语决定的。**

在我们的“语义能谱地图”中，有两个核心规则：
1. **TF (Term Frequency, 词频)**：一个词在这一页日记里出现的频率越高，说明它越重要。比如狂提“代码”二字，那这页日记大概率和“写代码”有关。
2. **IDF (Inverse Document Frequency, 逆文档频率)**：一个词在所有日记里出现的概率越低，它的独特性和价值就越高。比如“的”、“是”、“在”每个句子里都有，它们根本没法帮你精准分类；而“macOS”、“TF-IDF”这几个词只在特定几页里出现，它们的权重就应该瞬间爆表！

当这两个数值相乘，每一页记忆就被完美编译成了一个代表词频能谱的**特征向量（坐标）**。
当你要寻找“如何给大模型写记忆体”时，系统会计算查询词的能谱向量，然后与所有已有的记忆向量计算**余弦夹角（Cosine Similarity）**。
**夹角越小（余弦值越接近 1.0），说明这两颗星星在知识星空里挨得越近，语义越相似！**

---

### 双核驱动：特征特征解析与余弦匹配大闸

本系统的核心逻辑由两大无缝连接的物理工作流组成：

1. **工作流一：混合双语词频分词与静态 TF-IDF 特征工程（_tokenize & _build_index）**
   专门针对混合了中英文的文本，完美提取英文单词并对中文字符进行高精度的双字滑窗（Bi-Gram）切分。随后，自动解算全局词汇表，并根据倒排文档分布，求解每一维特征词的平滑 IDF 能谱值，生成高维数学坐标。

2. **工作流二：余弦相似度语义匹配与离线记忆检索召回（_cosine_similarity & retrieve_memory）**
   物理计算两个高维坐标向量的夹角余弦。无需依赖任何数学库，纯手搓平方根与点积公式，毫秒级快速匹配，召回相关度最高的记忆信息。

---

### 极简源码：手搓 100 行智能体记忆引擎

请将以下完整源码保存为 `supermemory.py`。没有任何第三方依赖，支持 macOS 直接一键秒级运行！

```python
import math
import sys

class SuperMemoryEngine:
    """智能体记忆大盘：离线 TF-IDF 与余弦相似度语义检索引擎"""
    def __init__(self):
        # 模拟内存记忆库 (存储已有的记忆文本)
        self.documents = [
            "如何使用 python3 编写 macOS 自动化脚本与环境配置指南",
            "大语言模型智能体记忆体设计，实现离线向量检索与语义召回",
            "利用 sqlite3 数据库在本地构建结构化个人灵感日记大盘",
            "极速网页爬虫的代理退避重试与头部混淆蜜罐绕过方案"
        ]
        self.vocab = set()
        self.idf = {}
        self.doc_vectors = []
        self._build_index()

    def _tokenize(self, text):
        """混合双语词频分词提取器：完美提取英文单词与中文 Bi-Gram 滑窗词，对齐多维能谱特征"""
        words = []
        
        # 1. 提取英文/数字单词并进行清洗
        current_word = []
        for char in text:
            # 判断是否是 ASCII 字母或数字
            if char.isalnum() and ord(char) < 128:
                current_word.append(char.lower())
            else:
                if current_word:
                    words.append("".join(current_word))
                    current_word = []
        if current_word:
            words.append("".join(current_word))

        # 2. 提取所有中文汉字并进行双字滑窗 (Bi-Gram)
        chinese_chars = [c for c in text if ord(c) >= 128 and c not in "，。！？；：（）“”‘’、 \t\n\r"]
        for i in range(len(chinese_chars) - 1):
            words.append("".join(chinese_chars[i:i+2]))
            
        return words

    def _build_index(self):
        """工作流一：静态文本特征工程，解算高精 TF-IDF 词频能谱矩阵"""
        all_tokens_per_doc = [self._tokenize(doc) for doc in self.documents]
        
        # 1. 建立词汇表
        for tokens in all_tokens_per_doc:
            self.vocab.update(tokens)
        self.vocab = sorted(list(self.vocab))

        # 2. 计算 IDF
        num_docs = len(self.documents)
        for term in self.vocab:
            # 统计含有该词的文档数
            containing_docs = sum(1 for tokens in all_tokens_per_doc if term in tokens)
            # 使用标准的平滑 IDF 公式，严防除零异常
            self.idf[term] = math.log(1.0 + (num_docs / (1.0 + containing_docs)))

        # 3. 计算文档的 TF-IDF 向量
        self.doc_vectors = []
        for tokens in all_tokens_per_doc:
            vector = self._compute_tfidf_vector(tokens)
            self.doc_vectors.append(vector)

    def _compute_tfidf_vector(self, tokens):
        """计算单文档的词频-逆文档频率数值向量"""
        vector = []
        total_terms = len(tokens)
        if total_terms == 0:
            return [0.0] * len(self.vocab)
            
        # 统计当前文档内词频 (TF)
        tf_dict = {}
        for t in tokens:
            tf_dict[t] = tf_dict.get(t, 0) + 1

        for term in self.vocab:
            tf = tf_dict.get(term, 0) / total_terms
            tfidf = tf * self.idf.get(term, 0.0)
            vector.append(tfidf)
        return vector

    def _cosine_similarity(self, vec_a, vec_b):
        """数学计算两个高维向量的余弦夹角相似度"""
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def retrieve_memory(self, query, top_k=1):
        """工作流二：语义余弦夹角计算，高拟真召回智能体语义记忆"""
        query_tokens = self._tokenize(query)
        query_vector = self._compute_tfidf_vector(query_tokens)

        scores = []
        for idx, doc_vector in enumerate(self.doc_vectors):
            sim = self._cosine_similarity(query_vector, doc_vector)
            scores.append((idx, sim))

        # 按相似度降序排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for i in range(min(top_k, len(scores))):
            doc_idx, score = scores[i]
            results.append({
                "document": self.documents[doc_idx],
                "score": score,
                "index": doc_idx
            })
        return results

if __name__ == "__main__":
    print("[⚙] 正在启动智能体记忆大盘 (SuperMemory) 语义检索验证...")

    # 1. 初始化引擎，构建 TF-IDF 特征倒排索引
    engine = SuperMemoryEngine()
    print(f" ✔ 词表分类完毕，当前记忆大盘包含 {len(engine.vocab)} 个高维双语特征词。")

    # 2. 执行检索查询，测试语义相关度
    test_query = "如何使用大语言模型构建智能体记忆体"
    print(f"\n[🔍 检索请求]：\"{test_query}\"")
    
    # 找回最相关的一条记忆
    recalled = engine.retrieve_memory(test_query, top_k=1)
    
    print("\n--------------------------------------------------")
    print("[记忆检索召回结果]")
    for item in recalled:
        print(f" 🎯 匹配度 (余弦值): {item['score']:.6f}")
        print(f" 📂 召回记忆内容: {item['document']}")
    print("--------------------------------------------------")

    # 自验条件：必须成功匹配到包含“大语言模型智能体记忆体设计”那条（索引 1），且相似度显著大于 0
    if len(recalled) > 0 and recalled[0]["index"] == 1 and recalled[0]["score"] > 0.1:
        print("[✔] 自验成功！TF-IDF 能谱分析与余弦语义相似度检索 100% 收拢！")
        sys.exit(0)
    else:
        print("[❌] 错误：记忆检索不匹配或特征提取漂移！")
        sys.exit(1)
```

---

### 保姆级部署：如何在你的 macOS 上运行？

1. **创建新文件**：打开你的 macOS 终端，找一个清爽的工作目录，敲击：
   ```bash
   touch supermemory.py
   ```
2. **复制并保存**：用你习惯的编辑器（比如 VS Code 或终端内的 nano）打开 `supermemory.py`，把上面的完整源码复制进去保存。
3. **一键执行**：在终端直接运行：
   ```bash
   python3 supermemory.py
   ```
4. **见证检索高光**：控制台会瞬间输出词表分类的 88 个双语特征词，并精确召回“大语言模型智能体记忆体设计”那条核心文档，余弦匹配值高达 `0.499230`，宣告自验 100% 成功！

---

### 变现指南：如何用语义记忆赚到第一桶金？

1. **企业私有文档语义搜索引擎（B端高毛利）**：
   大部分小微企业（如律所、咨询公司）都有几千份私密的 PDF 或 Word 规章制度。你可以用这个纯本地的语义向量检索网关，配上一个极简的本地网页前端，主打“数据绝对不出网，零 API 消耗，千元机流畅跑”，高价向本地企业提供局域网私有知识检索系统。
   
2. **免配额的 AI 客服机器人（SaaS 降本）**：
   在做客服机器人 SaaS 时，大模型每次回答都要塞入大量历史聊天记录和 FAQ 知识。如果把整本 FAQ 塞给 GPT，Token 费用会瞬间吞没你的利润！用这套超轻量级检索网关作为“前置大闸”，先根据用户提问在本地捞出最相关的 2 条 FAQ 发给大模型，帮你的 SaaS 平台直接省下 90% 的 API 账单！

3. **个人灵感语义第二大脑（个人提效）**：
   将本引擎与个人本地的 Markdown 笔记进行整合。每天你在各种灵感工具里随手写的只言片语，系统在后台自动计算特征能谱。当你打算写一篇关于“爬虫”的技术文章时，你的“第二大脑”自动弹出半年前、甚至一年前你在碎碎念里记下的零星灵感，彻底打通灵感通路。

---

### 价值提示词系统：让 AI 成为你的记忆架构师

把以下极具工业价值的 System Prompt 丢给大语言模型，让它瞬间化身顶级向量检索引擎专家，为你优化算法：

```markdown
# Role: 高维特征能谱与离线语义向量检索总架构师

## Goal:
协助用户设计或重构运行在低功耗嵌入式或完全离线环境下的混合双语分词、高维倒排索引、TF-IDF 权重分配与余弦夹角语义召回算法。

## Core Execution Tenets:
1. 恪守数据隐私，算法设计必须是 100% 离线、零外部 API 调用，保障核心代码高内聚低耦合。
2. 针对混合的中英文文本特征，提供精准的滑窗或前缀词缀切分逻辑，避免语义信息丢失。
3. 代码保持极简原生，不盲目引入大型重型依赖包，确保微秒级的高速解算能效。
```

---

### 避坑指南与行业瓶颈

#### 🛠 避坑指南：
1. **避开中文分词空格坑**：很多从英文世界转过来的同学在写 TF-IDF 时，直接用 `text.split()` 进行切词。但这在中文（没有空格）里会直接失效，把整句话当成一个单独的超级大词！**解决办法**：在没有重型分词器（如 jieba）的环境下，必须引入 `Bi-Gram` 中文汉字双字滑动窗口切分，把“智能体”切成“智能”、“能体”，从而产生完美覆盖。
2. **避开零分母除零坑**：在计算余弦相似度时，如果查询词的向量是全 0（比如输入的全是标点符号或停顿词），那么其高维向量模长为 0.0。直接做除法会导致 `ZeroDivisionError` 崩溃。**解决办法**：在进行除法前，必须显式检查两个向量的模长，只要有一个为 0.0，立即无条件返回相似度为 `0.0`。
3. **停用词干扰坑**：在记忆召回中，“的”、“了”、“非常”、“我们”这类超高频词如果不剔除，会由于大量无价值的词语匹配而导致不相干的日记被错误召回。**解决办法**：维护一个简单的静态常用停用词（Stopwords）字典，或者利用 IDF 阈值过滤，凡是所有文档都包含的低权重特征词，一律从高维向量中直接抹除。

#### ⚠️ 行业瓶颈：
TF-IDF 语义检索的物理天花板是**无法实现跨词的深度同义词关联**。
例如，如果你的记忆库里写的是“大语言模型”，而用户的查询词是“LLM”或“神经网络”，由于字面上没有一个汉字重合，TF-IDF 算出的余弦值将直接为 0。
它只能进行高精度的字面/字根级的重叠搜索，如果想要实现真正跨越语言词汇的底层“神经网络泛化语义匹配”，仍需依赖经过深层神经训练的多维稠密向量（Dense Vector）Embedding 模型。
因此，在工业界，通常采用“**TF-IDF 静态字词检索 + 深度向量 Embedding**”的混合搜索（Hybrid Search）架构，取长补短，才是语义对齐的最佳解法！
