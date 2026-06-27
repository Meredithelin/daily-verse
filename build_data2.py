#!/usr/bin/env python3
# 第二版：把扩充工作流产出的新内容并入 index.html 现有数据，去重后重新注入，并把 sw.js 缓存版本 +1。
import json, re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT2 = "/private/tmp/claude-501/-Users-Apple/d1220dee-41c2-4b18-9cfd-646c828ddca0/tasks/wkit7qfn3.output"

INDEX = os.path.join(HERE, "index.html")
html = open(INDEX, encoding="utf-8").read()
m = re.search(r"/\* === DATA:BEGIN === \*/\n(.*?)\n/\* === DATA:END === \*/", html, re.S)
assert m, "找不到 DATA 标记"
cur = json.loads(m.group(1).strip().removeprefix("window.DATA =").strip().rstrip(";"))

wf = json.load(open(OUTPUT2, encoding="utf-8"))
new = wf["result"]["content"]

def norm(s):
    return re.sub(r"[\s，。、；：？！,.;:?!\"'·…—《》〔〕()（）]", "", s or "")

def keyset(items, field):
    return {norm(it.get(field, ""))[:18] for it in items}

# 现有去重键
poem_keys = {norm(p.get("content",""))[:18] for p in cur["poems"]} | {norm(p.get("title","")+p.get("author","")) for p in cur["poems"]}
quote_keys = keyset(cur["quotes"], "quote")
line_keys = keyset(cur["lines"], "line")

added = {"tang":0,"song":0,"cnQuotes":0,"enQuotes":0,"lines":0,"dupes":0}

# 唐诗 / 宋词 → poems
for k, typ in (("tang","诗"),("song","词")):
    for p in new.get(k, []):
        ck = norm(p.get("content",""))[:18]
        tk = norm(p.get("title","")+p.get("author",""))
        if ck in poem_keys or (tk and tk in poem_keys):
            added["dupes"] += 1; continue
        poem_keys.add(ck); poem_keys.add(tk)
        p["type"] = typ
        cur["poems"].append(p)
        added[k] += 1

# 名言 → quotes
for k, origin in (("cnQuotes","中"),("enQuotes","外")):
    for q in new.get(k, []):
        qk = norm(q.get("quote",""))[:18]
        if qk in quote_keys:
            added["dupes"] += 1; continue
        quote_keys.add(qk)
        q["origin"] = origin
        cur["quotes"].append(q)
        added[k] += 1

# 名句 → lines
for l in new.get("lines", []):
    lk = norm(l.get("line",""))[:18]
    if lk in line_keys:
        added["dupes"] += 1; continue
    line_keys.add(lk)
    cur["lines"].append(l)
    added["lines"] += 1

# 重新注入
block = "window.DATA = " + json.dumps(cur, ensure_ascii=False, separators=(",", ":")) + ";"
new_html, n = re.subn(r"(/\* === DATA:BEGIN === \*/\n).*?(\n/\* === DATA:END === \*/)",
                      lambda mm: mm.group(1) + block + mm.group(2), html, flags=re.S)
assert n == 1
open(INDEX, "w", encoding="utf-8").write(new_html)

# sw.js 缓存版本 +1
SW = os.path.join(HERE, "sw.js")
sw = open(SW, encoding="utf-8").read()
mv = re.search(r"shijian-v(\d+)", sw)
if mv:
    nv = int(mv.group(1)) + 1
    sw = re.sub(r"shijian-v\d+", f"shijian-v{nv}", sw)
    open(SW, "w", encoding="utf-8").write(sw)
    print(f"sw.js 缓存版本 -> shijian-v{nv}")

tot = len(cur["poems"]) + len(cur["quotes"]) + len(cur["lines"])
print(f"新增: 唐诗{added['tang']} 宋词{added['song']} 中名言{added['cnQuotes']} 外名言{added['enQuotes']} 名句{added['lines']} (去重跳过{added['dupes']})")
print(f"现总计: 诗词{len(cur['poems'])} 名言{len(cur['quotes'])} 名句{len(cur['lines'])} = {tot} 条")
