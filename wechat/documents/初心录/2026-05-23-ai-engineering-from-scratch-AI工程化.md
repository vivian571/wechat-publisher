# ⚡️ 拒绝调包！从零手搓 BPE 分词与 Transformer 多头注意力，找回 AI 工程化的初心

## 1. 痛点：被 API 喂养废掉的“调包工程师”

如今的 AI 工程师是幸福的，也是不幸的。
幸福的是，你只需要三行代码调用 OpenAI 的接口，或者直接 `import langchain`，就能搭建起一个看起来很厉害的智能对话系统。
不幸的是，一旦接口报了错，或者系统遇到了高并发和严重的延迟问题，绝大多数人就只能干瞪眼。

为什么？
因为大家都在当**“赛博微波炉厨师”**——只管买速冻食品（API）往微波炉里一放，却根本不知道面包是怎么发酵的，面粉是怎么磨出来的。
如果你只知道 `from transformers import AutoModel`，你将永远无法理解：
- 为什么有些中文字符在分词时会吞掉双倍的 Token？
- 为什么多头注意力机制（Multi-Head Attention）的计算复杂度是序列长度的平方级别？
- 为什么向量检索在高维空间里会发生“维度灾难”？

就在今天，GitHub 热榜上冲出了一股清流：**ai-engineering-from-scratch**（项目地址：`rohitg00/ai-engineering-from-scratch`）。
它不讲花里胡哨的框架，只教你一件极其硬核的事：
**用最底层的 Python 和数学公式，把 Transformer、BPE 分词器、向量数据库和 RAG 引擎“手搓”出来！**
今天，我们就来找回初心，亲自动手解剖大模型的两个底层心脏！

---

## 2. 这个项目到底在“搓”什么？

用大白话来说，`ai-engineering-from-scratch` 就是一个**“AI 基础原理的积木拼图”**。

它把当今最复杂的 LLM（大语言模型）拆解为一个个最基本的单元，比如：
1. **Tokenization（分词）**：大模型是怎么把人类的文字切碎成一串数字编码的？
2. **Embeddings & Attention（嵌入与注意力）**：这串数字怎么变成高维空间里的向量？它们之间又是怎么产生语义关联的？
3. **Inference & Search（推理与检索）**：模型又是如何预测下一个词的？

这个项目不使用任何重型框架，只用最基础的 Python 标准库和 NumPy。看完它的源码，你会发现，大模型底层那套看似高深莫测的“魔法”，本质上就是一系列巧妙的矩阵乘法和统计概率！

---

## 3. 为什么每个想要进阶的开发者都该阅读它？

在没有手搓过代码之前，你对 AI 的理解永远是抽象的。它的多元功能覆盖教你直接掌握两大核心底层逻辑：

1. **掌握“Token 经济学”的本质**：
   通过手写 BPE（字节对编码）合并算法，你会彻底明白为什么大模型会计费、为什么有些词会被切成无意义的乱码。
2. **直面 Transformer 的数学核心**：
   用 NumPy 矩阵运算手搓自注意力，比在 PyTorch 里调库能让你更清晰地看懂 Q（Query）、K（Key）、V（Value）在空间里是如何做点积运算的。
3. **理解 RAG 的检索物理边界**：
   不调 Milvus 或 Pinecone，只用 NumPy 的余弦相似度（Cosine Similarity）去暴力检索，能让你看清向量在高维空间的投影本质。

---

## 4. 手搓教程：从零实现 BPE 分词与多头注意力

下面我们完全抛弃大框架，用最纯粹的 Python 和 NumPy 代码，在你的 macOS 终端里跑通这两个底层核心！

### 第一步：准备基础环境

我们只需要安装一个数学计算库 `numpy` 即可：

```bash
pip install numpy
```

### 第二步：手搓工作流一 - 纯 Python 编写 BPE（Byte Pair Encoding）分词器

大模型的第一步是把文本转成数字。BPE 算法就是统计并合并出现频率最高的字符对。
请将以下完全无占位符的代码写入 `/Users/ax/wechat-publisher/agent-skills/my_bpe.py`：

```python
import re
from collections import defaultdict

class SimpleBPETokenizer:
    def __init__(self):
        self.vocab = {}
        self.merges = {}

    def get_stats(self, ids):
        counts = defaultdict(int)
        for pair in zip(ids, ids[1:]):
            counts[pair] += 1
        return counts

    def merge_ids(self, ids, pair, idx):
        new_ids = []
        i = 0
        while i < len(ids):
            if i < len(ids) - 1 and ids[i] == pair[0] and ids[i+1] == pair[1]:
                new_ids.append(idx)
                i += 2
            else:
                new_ids.append(ids[i])
                i += 1
        return new_ids

    def train(self, text, num_merges):
        # 初始化词表：单个字节
        tokens = list(text.encode("utf-8"))
        ids = list(tokens)
        
        vocab = {i: bytes([i]) for i in range(256)}
        
        for i in range(num_merges):
            stats = self.get_stats(ids)
            if not stats:
                break
            # 找到出现次数最多的字符对
            best_pair = max(stats, key=stats.get)
            new_idx = 256 + i
            ids = self.merge_ids(ids, best_pair, new_idx)
            self.merges[best_pair] = new_idx
            vocab[new_idx] = vocab[best_pair[0]] + vocab[best_pair[1]]
            
        self.vocab = vocab
        print(f"BPE 训练完成。新词表大小: {len(self.vocab)}")

    def encode(self, text):
        tokens = list(text.encode("utf-8"))
        while len(tokens) >= 2:
            stats = self.get_stats(tokens)
            # 找出可以合并的字符对里在 merges 中序号最小的（即最先训练合并的）
            pairs = [pair for pair in stats if pair in self.merges]
            if not pairs:
                break
            pair_to_merge = min(pairs, key=lambda p: self.merges[p])
            idx = self.merges[pair_to_merge]
            tokens = self.merge_ids(tokens, pair_to_merge, idx)
        return tokens

if __name__ == "__main__":
    text = "hello world, this is a simple bpe test. hello world, learn from scratch!"
    tokenizer = SimpleBPETokenizer()
    tokenizer.train(text, num_merges=10)
    
    encoded = tokenizer.encode("hello world, simple test!")
    print("编码结果 IDs:", encoded)
```

跑一下这个脚本，体验大模型最初的分词训练：

```bash
python3 /Users/ax/wechat-publisher/agent-skills/my_bpe.py
```

### 第三步：手搓工作流二 - 纯 NumPy 实现 Transformer 缩放点积注意力

接下来，我们要用数学公式把向量之间的关系串联起来。
请将以下无占位符的代码写入 `/Users/ax/wechat-publisher/agent-skills/my_attention.py`：

```python
import numpy as np

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    计算 Attention 公式: Softmax(Q K^T / sqrt(d_k)) V
    """
    d_k = Q.shape[-1]
    
    # 1. 计算注意力得分: Q * K 的转置
    scores = np.matmul(Q, K.swapaxes(-2, -1)) / np.sqrt(d_k)
    
    # 2. 如果有掩码（例如在解码器中防止看到未来的词），将其加上极小值
    if mask is not None:
        scores += (mask * -1e9)
        
    # 3. Softmax 归一化
    # np.exp(x) / sum(np.exp(x))
    exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
    
    # 4. 点乘权重与 Value 矩阵得到最终输出
    output = np.matmul(attention_weights, V)
    
    return output, attention_weights

if __name__ == "__main__":
    # 假设我们有 3 个单词，每个单词的维度是 4
    # Batch size = 1, Seq len = 3, Dim = 4
    np.random.seed(42)
    Q = np.random.randn(1, 3, 4)
    K = np.random.randn(1, 3, 4)
    V = np.random.randn(1, 3, 4)
    
    output, weights = scaled_dot_product_attention(Q, K, V)
    print("注意力输出矩阵:\n", output)
    print("\n注意力权重分布矩阵（和为1）:\n", weights)
```

在终端里运行：

```bash
python3 /Users/ax/wechat-publisher/agent-skills/my_attention.py
```

你会清晰地看到，原本随机分布的 Query 和 Key，是如何通过矩阵转置相乘和 Softmax 计算，变成一张完美的概率相关性分布表，并最终加权输出 Value 向量的。这就是大模型智能的物理源头！

---

## 5. 大白话拆解：多头注意力的“底层逻辑本质”

对于不爱看公式的同学，我们用一个**“赛博非诚勿扰”**的故事来通俗解释 Query、Key 和 Value 的关系：

### 1. 每个人手里的“求偶小纸条”（Query/Key/Value）
假设在相亲现场（大模型的一句话里），有 3 个男嘉宾（单词）。
- **Query（查询向量）**：每个男嘉宾写在小纸条上的“我想要的择偶标准”。
- **Key（键向量）**：每个男嘉宾挂在胸前的“我的自身标签”。
- **Value（值向量）**：每个男嘉宾兜里揣着的“如果选我，我能提供的实际情绪价值”。

### 2. 配对打分（Scaled Dot-Product）
台上的月老（Attention 机制）把 1 号嘉宾的 `Query`（择偶标准）拿去和所有人的 `Key`（自身标签）做一个点积（Dot Product）打分，然后除以 `sqrt(d_k)`（防止数值太大爆表），再过一遍 Softmax（归一化为百分比权重）。
比如 1 号男嘉宾和自己配对度 10%，和 2 号嘉宾配对度 80%，和 3 号嘉宾配对度 10%。

### 3. 带走价值（Output）
最后，1 号男嘉宾会按照这套权重去分配他的注意力，融合 80% 的 2 号嘉宾的 `Value`（情绪价值）加上 10% 的 1 号和 3 号的 Value。
这样，1 号单词在脑海里就融合了 2 号单词的语义。这就是**上下文理解**的本质！

---

## 6. 三个让你直呼“卧槽”的实用案例

### 案例一：自定义极客小语种分词器
* **玩法**：如果你在做一个物联网系统，设备之间传输的是一堆类似 `CMD_SYNC_001_DATA_OK` 的特殊紧凑指令。直接用 OpenAI 的 Tokenizer 会切得很碎，极度费钱。
* **效果**：用此项目里的 BPE 算法在你的历史日志上训练 10 分钟，生成一个专门针对你公司协议的 Tokenizer。传输效率直接提高 5 倍，且完全离线运行在边缘网关上。

### 案例二：完全可控的“防穿透”敏感词检索
* **玩法**：利用 NumPy 暴力实现向量余弦相似度，不依赖任何云端数据库。
* **效果**：对于本地 1000 条敏感词文档，AI 检索只在内存中用 NumPy 一行矩阵相乘完成。极快、无延迟，且绝对没有数据上传泄露风险。

### 案例三：单卡微缩 Transformer 从头训练
* **玩法**：在本地手写一个仅有三层的极简 GPT 模型，用红楼梦的文本片段训练它。
* **效果**：在没有 PyTorch 显卡加持的情况下，让 CPU 在一小时内学会仿照曹雪芹的风格“预测下一个汉字”，作为少儿编程的终极科普项目。

---

## 7. 终极奥义：手搓 AI 系统“价值提示词”

为了让你的 AI 助手（如 Claude/GPT-4）能够在没有外部库的情况下，自动把复杂的深度学习论文公式翻译成手搓代码，你可以在 Prompt 中加入以下指令：

```markdown
# Role: 纯 Python 深度学习翻译官 (Zero-Framework Deep Learning Translator)

# System Goal:
- 你的职责是将学术论文中的深度学习模型和数学公式，翻译成不依赖 PyTorch/HuggingFace 的纯 Python + NumPy 实现。

# Constraints:
1. 【严格禁入包装】：严禁导入 `torch`, `tensorflow`, `transformers` 或 `langchain`。只允许使用 `numpy` 和 `math`。
2. 【公式明线映射】：在代码注释中，必须用 ASCII 字符或者 LaTeX 写出对应的数学公式（例如 `# Output = Softmax(Q K^T / sqrt(d_k)) V`），并把代码里的矩阵乘法与之逐一对应。
3. 【无省略完整运行】：写出的类必须包含完整的初始化、前向传播（forward）方法，并且附带一个使用 np.random.randn 生成的 Mock 数据运行实例，确保复制即可在终端运行。
```

---

## 8. 避坑指南与行业冷思考

我们必须冷静地指出手搓代码在实际生产中的局限性：

* **避坑指南 1：数值溢出（Overflow）**。在手搓 Attention 的 Softmax 时，如果你的 Q 和 K 点积结果太大，直接用 `np.exp` 会抛出 `nan`（非数）。**请务必像我刚才写的代码一样，在计算 exp 之前，减去每行的最大值（`scores - np.max(scores)`），这叫稳定 Softmax 算法！**
* **避坑指南 2：BPE 编码死循环**。如果你的训练文本非常短，但你设置的 `num_merges` 大于了可能的字符对组合数，BPE 在统计时会遇到最大统计为 0 的情况。**请务必加入 `if not stats: break` 的边界校验，防止程序卡死！**
* **避坑指南 3：NumPy 广播机制误伤**。NumPy 的三维矩阵乘法在进行 Q 和 K 转置乘法时，非常容易把 Batch 维度和 Sequence 维度搞混。**请不要使用简写的 `.T`，必须使用精确的 `.swapaxes(-2, -1)` 或 `.transpose(0, 1, 3, 2)` 进行轴交换！**

**总结**：`rohitg00/ai-engineering-from-scratch` 让我们从漫天飞舞的“高级框架”里冷静下来，重新用手触摸数学与逻辑的真实质感。想成为真正的 AI 架构师，先从放下调包、拿起手搓开始吧！
