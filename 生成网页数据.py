# 把口红库导出给普通网页用。改完 口红数据.py / 购买链接.py 后运行：
# python 生成网页数据.py

import json
from pathlib import Path

from 口红数据 import 获取口红库

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
print(f"已写出 kouhong.json，共 {len(库)} 支")
