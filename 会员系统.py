# 会员与卡密：本地用 会员卡密.txt；上网后把同样的码填进 Streamlit Secrets
# 改价格、客服微信，只改下面这几行

from datetime import datetime, timedelta
from pathlib import Path
import os
import secrets

根目录 = Path(__file__).parent
卡密文件 = 根目录 / "会员卡密.txt"

客服微信 = "ye20mxzm"
套餐 = {
    "月卡": {"价格": 9.9, "天数": 30, "说明": "30 天内看全部视频、全库平替、AI 查询"},
    "永久": {"价格": 29.9, "天数": 3650, "说明": "一次买断，全部功能长期可用"},
}
免费可看支数 = 12
免费平替条数 = 1


def 现在():
    return datetime.now()


def _解析一行(一行):
    一行 = 一行.strip()
    if not 一行 or 一行.startswith("#"):
        return None
    一行 = 一行.replace(",", " ")
    部分 = 一行.split()
    if len(部分) < 2:
        return None
    状态 = 部分[2] if len(部分) >= 3 else "未使用"
    return {"码": 部分[0], "套餐": 部分[1], "状态": 状态}


def 读取卡密(额外文本=""):
    记录 = []
    if 卡密文件.exists():
        for 一行 in 卡密文件.read_text(encoding="utf-8").splitlines():
            项 = _解析一行(一行)
            if 项:
                记录.append(项)
    环境 = os.environ.get("MEMBER_CODES", "")
    for 来源 in (额外文本, 环境):
        if not 来源:
            continue
        for 一行 in str(来源).splitlines():
            项 = _解析一行(一行)
            if 项:
                记录.append(项)
    return 记录


def 保存卡密(记录):
    行 = ["# 格式：兑换码  套餐  状态", "# 状态：未使用 / 已使用"]
    for 一项 in 记录:
        行.append(f"{一项['码']}  {一项['套餐']}  {一项['状态']}")
    卡密文件.write_text("\n".join(行) + "\n", encoding="utf-8")


def 生成卡密(套餐名, 数量=5):
    if 套餐名 not in 套餐:
        raise ValueError("套餐只能是 月卡 或 永久")
    记录 = 读取卡密()
    新码 = []
    for _ in range(数量):
        码 = "LIP-" + secrets.token_hex(2).upper() + "-" + secrets.token_hex(2).upper()
        记录.append({"码": 码, "套餐": 套餐名, "状态": "未使用"})
        新码.append(码)
    保存卡密(记录)
    return 新码


def 兑换(兑换码, 额外文本=""):
    兑换码 = (兑换码 or "").strip().upper()
    if not 兑换码:
        return False, "请输入兑换码", None
    记录 = 读取卡密(额外文本)
    for 一项 in 记录:
        if 一项["码"].upper() != 兑换码:
            continue
        if 一项["状态"] != "未使用":
            return False, "这张卡密已经用过了", None
        套餐名 = 一项["套餐"]
        if 套餐名 not in 套餐:
            return False, "卡密套餐无效", None
        天数 = 套餐[套餐名]["天数"]
        到期 = 现在() + timedelta(days=天数)
        一项["状态"] = "已使用"
        try:
            只含文件 = [x for x in 读取卡密() if x["码"].upper() == 兑换码]
            if 只含文件:
                全部 = 读取卡密()
                for x in 全部:
                    if x["码"].upper() == 兑换码:
                        x["状态"] = "已使用"
                保存卡密(全部)
        except Exception:
            pass
        会员 = {"套餐": 套餐名, "卡密": 一项["码"], "到期": 到期}
        return True, f"已开通{套餐名}，有效期至 {到期.strftime('%Y-%m-%d')}", 会员
    return False, "兑换码不正确", None


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
    return f"{会员信息['套餐']}会员 · 至 {日期}"
