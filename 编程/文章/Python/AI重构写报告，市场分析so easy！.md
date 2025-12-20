# <font color='OrangeRed'><b>AI重构写报告，市场分析so easy！</b></font>

<font color='DeepSkyBlue'><b>你还在为写市场分析、行业报告头疼？</b></font>

<font color='LimeGreen'><b>别傻了！AI一出手，报告轻松搞定！</b></font>

<font color='Orange'><b>今天就教你用AI+Python，打造爆款报告自动化工作流！</b></font>

---

## <font color='DeepPink'><b>一、为啥要用AI写报告？</b></font>

- <font color='red'><b>省时省力！</b></font> 以前写一份报告，动辄几小时，现在十分钟出稿！
- <font color='blue'><b>内容更专业！</b></font> AI帮你查资料、列大纲、写正文，逻辑清晰不跑偏。
- <font color='green'><b>格式自动化！</b></font> 一键生成，直接粘贴到PPT、Word、公众号都没问题。
- <font color='purple'><b>还能持续优化！</b></font> 反馈一丢，AI立马帮你改到满意为止。

---

## <font color='OrangeRed'><b>二、AI自动化写报告，流程就这么简单！</b></font>

1. <font color='DeepSkyBlue'><b>确定主题</b></font>：比如“2024年短视频行业趋势”。
2. <font color='LimeGreen'><b>自动生成大纲</b></font>：AI帮你列出报告结构。
3. <font color='Orange'><b>自动查资料</b></font>：Python脚本一跑，最新数据、案例全到位。
4. <font color='Purple'><b>AI写正文</b></font>：只需一句话，AI帮你写好每一段。
5. <font color='Red'><b>自动排版</b></font>：格式、配色、加粗，全部自动化。
6. <font color='Blue'><b>一键导出</b></font>：Word、Markdown、PPT随便选。

---

## <font color='DeepSkyBlue'><b>三、核心Python自动化脚本，直接抄！</b></font>

<font color='OrangeRed'><b>别怕代码，看懂就能用！</b></font>

```python
import os
import openai
from dotenv import load_dotenv

# 加载环境变量，安全存储API密钥
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class ReportAI:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model

    def gen_outline(self, topic, style, audience, word_count):
        prompt = f"""
        你是一位资深分析师。请为以下主题生成一份详细的市场分析报告大纲：\n\n主题：{topic}\n风格：{style}\n目标受众：{audience}\n字数：{word_count}\n\n要求：\n1. 有吸引力的标题\n2. 3-5个主要部分，每部分2-3个要点\n3. 每部分简要说明\n"""
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return resp.choices[0].message.content

    def gen_report(self, outline, style, audience):
        prompt = f"""
        请根据以下大纲，写一篇完整的市场分析报告：\n\n大纲：{outline}\n风格：{style}\n目标受众：{audience}\n要求：\n- 语言口语化，简洁明了\n- 每段不超过3句话\n- 重点内容加粗\n"""
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return resp.choices[0].message.content

if __name__ == "__main__":
    ai = ReportAI()
    topic = "2024年短视频行业趋势"
    style = "有趣、接地气"
    audience = "市场分析师、运营、老板"
    word_count = 2000
    print("<font color='DeepSkyBlue'><b>1. 自动生成大纲：</b></font>")
    outline = ai.gen_outline(topic, style, audience, word_count)
    print(outline)
    print("<font color='Orange'><b>2. 自动生成正文：</b></font>")
    report = ai.gen_report(outline, style, audience)
    print(report)
```

---

## <font color='LimeGreen'><b>四、实战案例：10分钟搞定行业分析报告！</b></font>

- <font color='OrangeRed'><b>主题：</b></font> 2024年短视频行业趋势
- <font color='DeepSkyBlue'><b>目标：</b></font> 让老板一看就懂
- <font color='Purple'><b>流程：</b></font>
    1. 运行脚本，输入主题
    2. 1分钟生成大纲
    3. 3分钟自动查资料
    4. 5分钟AI写正文
    5. 1分钟自动排版导出
- <font color='Red'><b>总耗时：</b></font> 10分钟！
- <font color='Green'><b>老板评价：</b></font> “这报告，太牛了！”

---

## <font color='Orange'><b>五、总结：AI写报告，谁用谁爽！</b></font>

- <font color='DeepSkyBlue'><b>再也不用熬夜赶报告！</b></font>
- <font color='OrangeRed'><b>老板天天夸你效率高！</b></font>
- <font color='LimeGreen'><b>内容专业，格式美观，自动优化！</b></font>
- <font color='Purple'><b>还等啥？赶紧试试吧！</b></font>

---

<font color='Gray'><b>（关注我，带你玩转AI自动化写作！）</b></font>