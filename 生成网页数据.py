# 把口红库导出给普通网页用。改完 口红数据.py / 购买链接.py 后运行：
# python 生成网页数据.py

import json
import re
from html import escape
from pathlib import Path
from urllib.parse import quote

from 口红数据 import 获取口红库

站点 = "https://laolizhuang.github.io/kouhong-pingti"
首页 = Path("index.html")
产品目录 = Path("p")


def 截简介(文, 最长=80):
    文 = re.sub(r"\s+", " ", (文 or "").strip())
    if len(文) <= 最长:
        return 文
    return 文[:最长].rstrip() + "…"


库 = []
for x in 获取口红库():
    色 = x["色系"]
    库.append(
        {
            "id": x["id"],
            "品牌": x["品牌"],
            "名称": x["名称"],
            "色号": x["色号"],
            "全名": x["全名"],
            "简称": x["简称"],
            "价格": x["价格"],
            "妆效": x["妆效"],
            "色系": 色,
            "色卡": x["色卡"],
            "说明": x["说明"],
            "介绍": x["介绍"],
            "图片": "口红图片/" + x["图片"],
            "未涂": f"口红图片/试色模特/素唇_{色}.png",
            "涂抹": f"口红图片/试色模特/涂抹_{色}.png",
            "涂好": f"口红图片/试色模特/{色}.png",
            "佣金渠道": x.get("佣金渠道") or "",
            "购买链接": x.get("购买链接") or "",
            "淘口令": x.get("淘口令") or "",
        }
    )

Path("kouhong.json").write_text(
    json.dumps(库, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)

Path("robots.txt").write_text(
    "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {站点}/sitemap.xml",
            "",
        ]
    ),
    encoding="utf-8",
)

地图 = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    f"  <url><loc>{站点}/</loc></url>",
]
for x in 库:
    地图.append(f"  <url><loc>{站点}/p/{quote(x['id'])}.html</loc></url>")
地图.append("</urlset>")
Path("sitemap.xml").write_text("\n".join(地图) + "\n", encoding="utf-8")

产品目录.mkdir(exist_ok=True)
for 旧 in 产品目录.glob("*.html"):
    旧.unlink()

for x in 库:
    页 = f"{站点}/p/{quote(x['id'])}.html"
    标题 = f"{x['全名']} 介绍与同色平替 | 觅色"
    简介 = (
        截简介(x.get("介绍") or x.get("说明"))
        + " 图为示意图。广告：点购买或用淘口令进店，结算后可能有佣金。"
    )
    口令 = (
        f'<p>淘口令（复制后打开淘宝 APP 粘贴）：</p><p>{escape(x["淘口令"])}</p>'
        if x.get("淘口令")
        else ""
    )
    购买 = (
        f'<p><a href="{escape(x["购买链接"])}" rel="noopener noreferrer">去购买</a></p>'
        if x.get("购买链接")
        else ""
    )
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(标题)}</title>
  <meta name="description" content="{escape(简介)}">
  <link rel="canonical" href="{escape(页)}">
  <meta property="og:title" content="{escape(标题)}">
  <meta property="og:description" content="{escape(简介)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{escape(页)}">
  <meta property="og:image" content="{站点}/{quote(x['图片'])}">
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <div class="wechat-tip">微信里常常打不开本页。请点右上角「…」，选「在浏览器打开」；或复制淘口令到淘宝 APP。</div>
  <div class="wrap" id="app">
    <p><a href="../index.html">← 返回全库</a></p>
    <h1>{escape(x["全名"])}</h1>
    <p>{escape(x["品牌"])} · {escape(x["名称"])} · {escape(x["色号"])} ｜ {escape(x["色系"])} · {escape(x["妆效"])} ｜ 参考价 ¥{x["价格"]}</p>
    <p>下面是示意图，不是实拍保证。屏幕有色差，下手前请对照实物试色。</p>
    <p>{escape(x["介绍"])}</p>
    <p>广告 · 点购买或用淘口令进店，下单并结算后可能产生佣金</p>
    {购买}
    {口令}
    <p><img src="../{escape(x["图片"])}" alt="{escape(x["全名"])} 色号示意图"></p>
  </div>
  <script>window.MISE_PRESELECT = {json.dumps(x["id"], ensure_ascii=False)};</script>
  <script src="../app.js"></script>
</body>
</html>
"""
    (产品目录 / f"{x['id']}.html").write_text(html, encoding="utf-8")

首页文 = 首页.read_text(encoding="utf-8")
目录 = "\n".join(
    f'    <li><a href="p/{escape(x["id"])}.html">{escape(x["全名"])} — {escape(x["说明"])}</a></li>'
    for x in 库
)
seo = f"<!--MISE-SEO-START-->\n    <ul class=\"seo-list\">\n{目录}\n    </ul>\n    <!--MISE-SEO-END-->"
if "<!--MISE-SEO-START-->" not in 首页文:
    raise SystemExit("index.html 缺少 MISE-SEO 标记，无法写入色号目录")
首页文 = re.sub(
    r"<!--MISE-SEO-START-->.*?<!--MISE-SEO-END-->",
    seo,
    首页文,
    count=1,
    flags=re.S,
)
ld = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "觅色口红全库",
    "url": 站点 + "/",
    "numberOfItems": len(库),
    "itemListElement": [
        {
            "@type": "ListItem",
            "position": i + 1,
            "url": f"{站点}/p/{quote(x['id'])}.html",
            "name": x["全名"],
        }
        for i, x in enumerate(库)
    ],
}
ld_block = (
    "<!--MISE-JSONLD-START-->\n"
    f'  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>\n'
    "  <!--MISE-JSONLD-END-->"
)
if "<!--MISE-JSONLD-START-->" not in 首页文:
    raise SystemExit("index.html 缺少 MISE-JSONLD 标记")
首页文 = re.sub(
    r"<!--MISE-JSONLD-START-->.*?<!--MISE-JSONLD-END-->",
    ld_block,
    首页文,
    count=1,
    flags=re.S,
)
首页.write_text(首页文, encoding="utf-8")

print(f"已写出 kouhong.json、sitemap.xml、robots.txt，以及 p/ 下 {len(库)} 个介绍页")
