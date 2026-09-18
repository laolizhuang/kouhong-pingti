# ============================================
# 觅色：口红平替查询（全库版：所有口红都能点、能搜）
# 运行：streamlit run 口红平替工具.py
# ============================================

from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from pathlib import Path
import smtplib

import streamlit as st
import streamlit.components.v1 as components

from 口红数据 import 获取口红库

st.set_page_config(page_title="觅色", page_icon="💄", layout="wide")

# 建议箱会发到这个 QQ 邮箱；授权码不要写进代码，写在 邮箱授权码.txt
收件邮箱 = "2833909485@qq.com"

图片目录 = Path(__file__).parent / "口红图片"
建议文件 = Path(__file__).parent / "建议箱.txt"
授权码文件 = Path(__file__).parent / "邮箱授权码.txt"
口红库 = 获取口红库()


@st.cache_resource
def 全局建议():
    return []

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@600;700&display=swap');

    .stApp {
        background: linear-gradient(180deg, #f8ebe4 0%, #fdf8f5 280px, #fffaf7 100%);
        font-family: "Noto Sans SC", sans-serif;
        color: #3b2a2a;
    }
    .block-container { padding-top: 3.4rem; max-width: 1180px; }

    h1, h2, h3 { font-family: "Noto Serif SC", serif !important; color: #4a2c2c !important; }

    .hero-caption {
        margin-top: -8px;
        margin-bottom: 18px;
        color: #8a5a5a;
        letter-spacing: 0.12em;
        font-size: 0.92rem;
        text-align: center;
    }
    .hero-title {
        text-align: center;
        font-family: "Noto Serif SC", serif;
        font-size: 2.3rem;
        margin: 8px 0 4px 0;
        color: #4a2c2c;
    }

    div[data-testid="stImage"] img {
        border-radius: 18px;
        box-shadow: 0 12px 30px rgba(120, 60, 60, 0.12);
    }

    .swatch {
        width: 100%;
        height: 14px;
        border-radius: 999px;
        margin: 6px 0 10px 0;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.4);
    }
    .price {
        color: #c45c5c;
        font-weight: 700;
        font-size: 1.15rem;
    }
    .meta { color: #8a6a6a; font-size: 0.9rem; }
    .ad {
        color: #9a6a6a;
        font-size: 0.78rem;
        margin: 4px 0 8px 0;
    }
    .count {
        text-align: center;
        color: #8a5a5a;
        margin-bottom: 12px;
    }

    .stButton > button {
        background: linear-gradient(90deg, #c45c5c, #d47a6a);
        color: white;
        border: 0;
        border-radius: 999px;
        height: 2.6rem;
        padding: 0 1.4rem;
        font-weight: 600;
        font-size: 0.85rem;
        white-space: nowrap;
    }
    .stButton > button:hover { background: linear-gradient(90deg, #b34e4e, #c96b5c); color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)


def 图片路径(文件名):
    路径 = 图片目录 / 文件名
    if 路径.exists():
        return str(路径)
    return str(图片目录 / "tomato.png")


def 试色图路径(色系, 种类="涂好"):
    if 种类 == "未涂":
        文件 = 图片目录 / "试色模特" / f"素唇_{色系}.png"
    elif 种类 == "涂抹":
        文件 = 图片目录 / "试色模特" / f"涂抹_{色系}.png"
    else:
        文件 = 图片目录 / "试色模特" / f"{色系}.png"
    if 文件.exists():
        return str(文件)
    return 图片路径("tomato.png")


def 妆效匹配(妆效, 偏好):
    if 偏好 == "不限":
        return True
    if 偏好 == "哑光/雾面":
        return 妆效 in ("哑光", "雾面")
    if 偏好 == "润泽/水光":
        return 妆效 in ("润泽", "水光")
    return 妆效 == 偏好


def 按id查找(口红id):
    for 口红 in 口红库:
        if 口红["id"] == 口红id:
            return 口红
    return None


def 找平替(当前, 预算, 妆效偏好, 只看更便宜):
    结果 = []
    for 口红 in 口红库:
        if 口红["id"] == 当前["id"]:
            continue
        if 口红["色系"] != 当前["色系"]:
            continue
        if not 妆效匹配(口红["妆效"], 妆效偏好):
            continue
        if 只看更便宜 and 口红["价格"] > 预算:
            continue
        结果.append(口红)
    结果.sort(key=lambda x: x["价格"])
    return 结果


def 取QQ授权码():
    try:
        码 = (st.secrets.get("qq_auth_code", "") or "").strip()
        if 码:
            return 码
    except Exception:
        pass
    if 授权码文件.exists():
        for 一行 in 授权码文件.read_text(encoding="utf-8").splitlines():
            一行 = 一行.strip()
            if 一行 and not 一行.startswith("#"):
                return 一行
    return ""


def 发到QQ邮箱(内容):
    授权码 = 取QQ授权码()
    if not 授权码:
        return False, "还没设置QQ邮箱授权码"
    邮件 = MIMEText(内容, "plain", "utf-8")
    邮件["From"] = 收件邮箱
    邮件["To"] = 收件邮箱
    邮件["Subject"] = Header("【觅色】建议箱新留言", "utf-8")
    try:
        with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=20) as smtp:
            smtp.login(收件邮箱, 授权码)
            smtp.sendmail(收件邮箱, [收件邮箱], 邮件.as_string())
        return True, "已发到QQ邮箱"
    except Exception as e:
        return False, str(e)


def 收下建议(内容):
    内容 = (内容 or "").strip()
    if not 内容:
        return False, "请先写下你想找的口红"
    一条 = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}  {内容}"
    全局建议().append(一条)
    try:
        with 建议文件.open("a", encoding="utf-8") as f:
            f.write(一条 + "\n")
    except Exception:
        pass
    发出去, _说明 = 发到QQ邮箱(一条)
    if 发出去:
        return True, "收到啦，已经发到站长的QQ邮箱。"
    return True, "收到啦，已记下。邮箱稍后会再试着发过去。"


def 画出建议箱():
    if st.session_state.pop("清空建议", False):
        st.session_state["suggestion_box"] = ""
    st.markdown("### 建议箱")
    st.caption("全库没有你要的色号？写在这里，我们后面补进去。")
    内容 = st.text_area(
        "你想找的口红",
        placeholder="例如：YSL 小金条 21、香奈儿 58、某支豆沙色",
        key="suggestion_box",
    )
    if st.button("投进建议箱", type="primary"):
        成功, 说明 = 收下建议(内容)
        if 成功:
            st.session_state["建议结果"] = 说明
            st.session_state["清空建议"] = True
            st.rerun()
        else:
            st.warning(说明)
    if st.session_state.get("建议结果"):
        st.success(st.session_state.pop("建议结果"))


def 选中口红(口红id):
    st.session_state["选中id"] = 口红id
    st.session_state["页面"] = "介绍"
    st.session_state.pop("平替介绍id", None)
    st.rerun()


def 展示卡片(列表, 放下面=False):
    if not 列表:
        st.warning("按当前条件没有筛到。试试放宽品牌、色系或预算，或去下面建议箱留言。")
        return
    for 起始 in range(0, len(列表), 3):
        列 = st.columns(3, gap="large")
        for i, 口红 in enumerate(列表[起始:起始 + 3]):
            with 列[i]:
                st.image(图片路径(口红["图片"]), use_container_width=True)
                st.markdown(
                    f'<div class="swatch" style="background:{口红["色卡"]};"></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{口红['全名']}**")
                st.caption(f"{口红['色系']}  ·  {口红['妆效']}")
                st.markdown(f'<div class="price">¥ {口红["价格"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">{口红["说明"]}</div>', unsafe_allow_html=True)
                if st.button("查看介绍", key=f"card_{口红['id']}", use_container_width=True):
                    if 放下面:
                        st.session_state["平替介绍id"] = 口红["id"]
                        st.session_state["滚到平替介绍"] = True
                        st.rerun()
                    else:
                        选中口红(口红["id"])


def 画出购买(当前):
    if 当前.get("有佣金"):
        st.markdown('<div class="ad">广告 · 点击购买可能产生佣金</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="ad">广告 · 将跳转淘宝搜索该色号。联盟推广链接填上后才会有佣金</div>',
            unsafe_allow_html=True,
        )
    st.link_button("去购买", 当前["购买链接"], type="primary")
    if 当前.get("淘口令"):
        st.caption("淘口令，复制后打开淘宝")
        st.code(当前["淘口令"], language=None)


def 画出详细介绍(当前, 标题=None):
    st.markdown(f"### {标题 or 当前['全名']}")
    st.caption("色号图、试色，以及这支口红的真实上嘴情况")
    图列 = st.columns(4, gap="large")
    with 图列[0]:
        st.image(图片路径(当前["图片"]), use_container_width=True, caption="色号图")
    with 图列[1]:
        st.image(试色图路径(当前["色系"], "未涂"), use_container_width=True, caption="未涂")
    with 图列[2]:
        st.image(试色图路径(当前["色系"], "涂抹"), use_container_width=True, caption="涂抹中")
    with 图列[3]:
        st.image(试色图路径(当前["色系"], "涂好"), use_container_width=True, caption="涂好")
    st.markdown(
        f'<div class="swatch" style="background:{当前["色卡"]}; width:160px;"></div>',
        unsafe_allow_html=True,
    )
    st.write(
        f"{当前['品牌']} · {当前['名称']} · {当前['色号']}　｜　"
        f"{当前['色系']} · {当前['妆效']}　｜　参考价 ¥{当前['价格']}"
    )
    st.markdown(f'<div class="intro">{当前["介绍"]}</div>', unsafe_allow_html=True)
    画出购买(当前)


def 画出平替(当前):
    st.markdown("### 同色系平替")
    c1, c2 = st.columns(2)
    with c1:
        预算 = st.slider("最高预算（元）", min_value=30, max_value=500, value=150, step=10)
    with c2:
        妆效偏好 = st.selectbox("妆效", ["不限", "哑光/雾面", "丝绒", "润泽/水光"])
    只看更便宜 = st.checkbox("只看不超过预算的平替", value=True)
    平替们 = 找平替(当前, 预算, 妆效偏好, 只看更便宜)
    if 平替们:
        st.caption(f"找到 {len(平替们)} 支和「{当前['全名']}」同色系的平替，点查看介绍会在下面展开")
        展示卡片(平替们, 放下面=True)
    else:
        st.info("这支暂时没有合适平替，可以把需求写到最下面的建议箱。")
    平替当前 = 按id查找(st.session_state.get("平替介绍id"))
    if 平替当前:
        st.markdown("---")
        st.markdown("### 这支平替的介绍")
        画出详细介绍(平替当前)
        if st.session_state.pop("滚到平替介绍", False):
            components.html(
                """
                <script>
                const doc = window.parent.document;
                const heads = [...doc.querySelectorAll('h3')];
                const el = heads.reverse().find(h => h.innerText.includes('这支平替的介绍'));
                if (el) el.scrollIntoView({behavior: 'smooth', block: 'start'});
                </script>
                """,
                height=0,
            )


def 画出口红介绍(当前):
    st.markdown("<div style='height: 1.2rem'></div>", unsafe_allow_html=True)
    if st.button("← 返回全库"):
        st.session_state["页面"] = "全库"
        st.session_state.pop("平替介绍id", None)
        st.rerun()
    画出详细介绍(当前)
    st.markdown("---")
    画出平替(当前)


if st.session_state.get("页面") == "介绍":
    当前 = 按id查找(st.session_state.get("选中id"))
    if 当前:
        画出口红介绍(当前)
    else:
        st.session_state["页面"] = "全库"
        st.rerun()
else:
    st.image(图片路径("banner.png"), use_container_width=True)
    st.markdown('<div class="hero-title">觅色</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-caption">全库 {len(口红库)} 支 · 点一支，进入介绍</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### 先学怎么涂")
    教学步骤 = [
        ("01.png", "1. 打底保湿", "先涂薄薄一层润唇膏"),
        ("02.png", "2. 勾勒唇峰", "从唇峰两点开始画轮廓"),
        ("03.png", "3. 填满上唇", "沿着唇线往中间填色"),
        ("04.png", "4. 填满下唇", "从下唇中央向外推开"),
        ("05.png", "5. 抿匀修角", "轻轻抿一下，修齐嘴角"),
        ("06.png", "6. 完成", "左右对称就可以出门了"),
    ]
    教学目录 = 图片目录 / "口红教学"
    for 起始 in range(0, len(教学步骤), 3):
        列 = st.columns(3, gap="large")
        for i, (文件, 标题, 说明) in enumerate(教学步骤[起始:起始 + 3]):
            with 列[i]:
                图 = 教学目录 / 文件
                if 图.exists():
                    st.image(str(图), use_container_width=True)
                st.markdown(f"**{标题}**")
                st.caption(说明)
    st.caption("对照每张图做一遍，就不会花、不会歪。")

    st.subheader("口红全库")
    品牌列表 = ["全部品牌"] + sorted({x["品牌"] for x in 口红库})
    色系列表 = ["全部色系"] + sorted({x["色系"] for x in 口红库})

    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        搜索词 = st.text_input("搜索口红（品牌 / 色号 / 色系）", placeholder="例如：405、Chili、豆沙、完美日记")
    with f2:
        选中品牌 = st.selectbox("品牌", 品牌列表)
    with f3:
        选中色系 = st.selectbox("色系", 色系列表)

    展示列表 = []
    for 口红 in 口红库:
        if 选中品牌 != "全部品牌" and 口红["品牌"] != 选中品牌:
            continue
        if 选中色系 != "全部色系" and 口红["色系"] != 选中色系:
            continue
        if 搜索词.strip():
            拼 = f"{口红['全名']} {口红['色系']} {口红['说明']}"
            if 搜索词.strip().lower() not in 拼.lower():
                continue
        展示列表.append(口红)

    st.markdown(
        f'<div class="count">当前显示 {len(展示列表)} / {len(口红库)} 支，点击色号进入介绍</div>',
        unsafe_allow_html=True,
    )
    if 搜索词.strip() and not 展示列表:
        st.info("全库暂时没有这个关键词，可以把色号写到最下面的建议箱。")

    每行 = 6
    for 起始 in range(0, len(展示列表), 每行):
        一行 = 展示列表[起始:起始 + 每行]
        列 = st.columns(每行)
        for i, 口红 in enumerate(一行):
            with 列[i]:
                st.image(图片路径(口红["图片"]), use_container_width=True)
                st.markdown(
                    f'<div class="swatch" style="background:{口红["色卡"]};"></div>',
                    unsafe_allow_html=True,
                )
                if st.button(口红["简称"], key=f"pick_{口红['id']}", use_container_width=True):
                    选中口红(口红["id"])

    st.markdown(
        '<div class="hint">点开任意口红进入介绍页。屏幕有色差，下手前请对照试色。没收录的名字可以投进最下面的建议箱。</div>',
        unsafe_allow_html=True,
    )

画出建议箱()
