# 会员：扫收款码付款后，在网页里点「我已付款」开通月卡
# 改价格、客服微信、有效天数，只改下面这几行

from datetime import datetime, timedelta
from pathlib import Path

根目录 = Path(__file__).parent
图片目录 = 根目录 / "口红图片"

客服微信 = "ye20mxzm"
月卡价格 = 9.9
月卡天数 = 30
月卡说明 = "30 天内看全部视频、全库平替、AI 查询"
免费可看支数 = 12
免费平替条数 = 1


def 现在():
    return datetime.now()


def 收款码路径():
    for 名 in ("收款码.png", "收款码.jpg", "收款码.jpeg", "收款码.webp"):
        路径 = 图片目录 / 名
        if 路径.exists():
            return 路径
    return None


def 开通会员():
    到期 = 现在() + timedelta(days=月卡天数)
    return {"套餐": "月卡", "到期": 到期}


def 会员仍有效(会员信息):
    if not 会员信息:
        return None
    到期 = 会员信息.get("到期")
    if 到期 is None:
        return None
    if 到期 < 现在():
        return None
    return 会员信息


def 会员文案(会员信息):
    if not 会员信息:
        return "未开通"
    日期 = 会员信息["到期"].strftime("%Y-%m-%d")
    return f"会员 · 至 {日期}"
