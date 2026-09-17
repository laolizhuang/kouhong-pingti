# 会员：用户先扫收款码付款，再把截图发给客服微信；
# 你确认到账后，把 开通口令.txt 里一个「未使用」口令发给她，她才能解锁。
# 网页看不到微信有没有付钱，所以不能只靠点按钮开通。

from datetime import datetime, timedelta
from pathlib import Path
import os
import secrets

根目录 = Path(__file__).parent
图片目录 = 根目录 / "口红图片"
口令文件 = 根目录 / "开通口令.txt"

客服微信 = "ye20mxzm"
月卡价格 = 9.9
月卡天数 = 30
月卡说明 = "30 天内看试色对比图、全库平替、AI 查询"
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


def _解析一行(一行):
    一行 = 一行.strip()
    if not 一行 or 一行.startswith("#"):
        return None
    部分 = 一行.replace(",", " ").split()
    if not 部分:
        return None
    状态 = 部分[1] if len(部分) >= 2 else "未使用"
    return {"码": 部分[0].strip().upper(), "状态": 状态}


def 读取口令(额外文本=""):
    记录 = []
    if 口令文件.exists():
        for 一行 in 口令文件.read_text(encoding="utf-8").splitlines():
            项 = _解析一行(一行)
            if 项:
                记录.append(项)
    环境 = os.environ.get("UNLOCK_PASSWORD", "")
    for 来源 in (额外文本, 环境):
        if not 来源:
            continue
        for 一行 in str(来源).splitlines():
            项 = _解析一行(一行)
            if 项:
                记录.append(项)
    return 记录


def 保存口令(记录):
    行 = ["# 付款确认后发给顾客。格式：口令  未使用/已使用", "# 不要把这个文件发到网上"]
    for 一项 in 记录:
        行.append(f"{一项['码']}  {一项['状态']}")
    口令文件.write_text("\n".join(行) + "\n", encoding="utf-8")


def 生成口令(数量=10):
    记录 = 读取口令()
    新码 = []
    for _ in range(数量):
        码 = "MISE-" + secrets.token_hex(2).upper()
        记录.append({"码": 码, "状态": "未使用"})
        新码.append(码)
    保存口令(记录)
    return 新码


def 校验口令(用户输入, 额外文本=""):
    用户输入 = (用户输入 or "").strip().upper()
    if not 用户输入:
        return False, "请输入客服发给你的开通口令", None
    记录 = 读取口令(额外文本)
    for 一项 in 记录:
        if 一项["码"] != 用户输入:
            continue
        if 一项["状态"] != "未使用":
            return False, "这个口令已经用过了，请再向客服要一个", None
        一项["状态"] = "已使用"
        try:
            本地 = 读取口令()
            改过 = False
            for x in 本地:
                if x["码"] == 用户输入 and x["状态"] == "未使用":
                    x["状态"] = "已使用"
                    改过 = True
            if 改过:
                保存口令(本地)
        except Exception:
            pass
        会员 = 开通会员()
        到期 = 会员["到期"].strftime("%Y-%m-%d")
        return True, f"已开通会员，有效期至 {到期}", 会员
    return False, "口令不对。请先付款，并把截图发给客服微信", None


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
