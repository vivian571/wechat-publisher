import os
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(base_dir, 'web_reader')
os.makedirs(web_dir, exist_ok=True)

files = [
    "00_世界观与大纲设定.md",
    "01_第一卷_第一章_薄荷糖路由卡壳事件.md",
    "02_第一卷_第二章_做吃山空的恐慌度量.md",
    "03_第一卷_第三章_冒充者综合征.md",
    "04_第一卷_第四章_资本共谋的免费馅饼.md",
    "05_第一卷_第五章_开源灵巧手选型清单.md"
]

chapters = []
for f in files:
    path = os.path.join(base_dir, f)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            title = f.replace('.md', '')
            chapters.append({
                "id": f,
                "title": title,
                "content": content
            })

js_content = "const novelData = " + json.dumps(chapters, ensure_ascii=False, indent=2) + ";"
output_path = os.path.join(web_dir, 'data.js')
with open(output_path, 'w', encoding='utf-8') as out:
    out.write(js_content)
print(f"Successfully built {output_path}")
