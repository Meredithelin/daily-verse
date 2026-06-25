#!/usr/bin/env python3
# 将工作流产出的名言/名句 + 本地唐诗宋词，合并注入 index.html 的 DATA 块。
import json, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = "/private/tmp/claude-501/-Users-Apple/d1220dee-41c2-4b18-9cfd-646c828ddca0/tasks/wfifh4gko.output"

wf = json.load(open(OUTPUT, encoding="utf-8"))
content = wf["result"]["content"]
cn = content["cnQuotes"]
en = content["enQuotes"]
lines = content["lines"]

# --- 人工复核修正 ---
# 1) 「知识就是力量」误标《沉思录》(实为马可·奥勒留之书)，清空出处
for q in en:
    if q["quote"].startswith("知识就是力量"):
        q["source"] = ""
# 2) 删除托名卢梭、无出处的可疑伪托句
en = [q for q in en if not q["quote"].startswith("我们登山")]

# 合并名言，标注中/外来源
quotes = [dict(q, origin="中") for q in cn] + [dict(q, origin="外") for q in en]

# 唐诗宋词
poems = json.load(open(os.path.join(HERE, "poems_data.json"), encoding="utf-8"))

data = {"poems": poems, "quotes": quotes, "lines": lines}
block = "window.DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"

path = os.path.join(HERE, "index.html")
html = open(path, encoding="utf-8").read()
pat = re.compile(r"(/\* === DATA:BEGIN === \*/\n).*?(\n/\* === DATA:END === \*/)", re.S)
new_html, n = pat.subn(lambda m: m.group(1) + block + m.group(2), html)
assert n == 1, f"DATA 标记替换失败 (matched {n})"
open(path, "w", encoding="utf-8").write(new_html)

print(f"注入完成: 诗词 {len(poems)} 首, 名言 {len(quotes)} 条 (中{len(cn)}/外{len(en)}), 名句 {len(lines)} 条")
print(f"总卡片数: {len(poems)+len(quotes)+len(lines)}")
