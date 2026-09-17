# ============================================
# 觅色：口红平替查询（全库版：所有口红都能点、能搜）
# 运行：streamlit run 口红平替工具.py
# ============================================

from datetime import datetime
from pathlib import Path

import streamlit as st

from 口红数据 import 获取口红库

st.set_page_config(page_title="觅色", page_icon="💄", layout="wide")

图片目录 = Path(__file__).parent / "口红图片"
建议文件 = Path(__file__).parent / "建议箱.txt"
口红库 = 获取口红库()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@600;700&display=swap');

    .stApp {
        background: linear-gradient(180deg, #f8ebe4 0%, #fdf8f5 280px, #fffaf7 100%);
        font-family: "Noto Sans SC", sans-serif;
        color: #3b2a2a;
    }
    .block-container { padding-top: 1.2rem; max-width: 1180px; }

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
    .hint { color: #9a7a7a; font-size: 0.82rem; text-align: center; margin-top: 28px; }
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
        font-weight: 600;
        font-size: 0.85rem;
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


def 按名字查找(文字):
    文字 = 文字.strip().lower()
    命中 = []
    for 口红 in 口红库:
        拼 = f"{口红['全名']} {口红['简称']} {口红['色系']}".lower()
        if 文字 and 文字 in 拼:
            命中.append(口红)
    return 命中


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


def 收下建议(内容):
    内容 = (内容 or "").strip()
    if not 内容:
        return False, "请先写下你想找的口红"
    一行 = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}  {内容}\n"
    try:
        with 建议文件.open("a", encoding="utf-8") as f:
            f.write(一行)
    except Exception:
        pass
    return True, "收到啦，我们会尽量补进全库。"


def 画出建议箱():
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
            st.success(说明)
        else:
            st.warning(说明)


def 展示卡片(列表):
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


# ---------- 顶部海报 ----------
st.image(图片路径("banner.png"), use_container_width=True)
st.markdown('<div class="hero-title">觅色</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="hero-caption">全库 {len(口红库)} 支 · 点一支，遇见同色平替</div>',
    unsafe_allow_html=True,
)

画出建议箱()

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

# ---------- 全库筛选 ----------
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
    f'<div class="count">当前显示 {len(展示列表)} / {len(口红库)} 支，点击下方色号即可选中</div>',
    unsafe_allow_html=True,
)
if 搜索词.strip() and not 展示列表:
    st.info("全库暂时没有这个关键词，可以把色号写到上面的建议箱。")

if "选中id" not in st.session_state:
    st.session_state["选中id"] = 口红库[0]["id"]

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
                st.session_state["选中id"] = 口红["id"]

# ---------- 当前选择 + 平替条件 ----------
st.markdown("### 为这支找平替")
查询方式 = st.radio("怎么查？", ["从上面全库点选", "自己输入名字"], horizontal=True)

c1, c2 = st.columns(2)
with c1:
    预算 = st.slider("最高预算（元）", min_value=30, max_value=500, value=150, step=10)
with c2:
    妆效偏好 = st.selectbox("妆效", ["不限", "哑光/雾面", "丝绒", "润泽/水光"])

只看更便宜 = st.checkbox("只看不超过预算的平替", value=True)

当前 = 按id查找(st.session_state["选中id"])
目标口红 = ""
if 查询方式 == "从上面全库点选":
    目标口红 = 当前["全名"]
    a, b, c = st.columns(3, gap="large")
    with a:
        st.image(试色图路径(当前["色系"], "未涂"), use_container_width=True, caption="未涂")
    with b:
        st.image(试色图路径(当前["色系"], "涂抹"), use_container_width=True, caption="涂抹中")
    with c:
        st.image(试色图路径(当前["色系"], "涂好"), use_container_width=True, caption="涂好")
    st.markdown(f"#### {当前['全名']}")
    st.markdown(
        f'<div class="swatch" style="background:{当前["色卡"]}; width:160px;"></div>',
        unsafe_allow_html=True,
    )
    st.write(f"{当前['色系']} · {当前['妆效']} · ¥{当前['价格']}")
    st.caption(当前["说明"])
else:
    目标口红 = st.text_input("输入口红名字（如：阿玛尼 红管 405、迪奥 999）")

if st.button("查找平替", type="primary"):
    if not str(目标口红).strip():
        st.warning("请先在全库点一支，或输入口红名字")
    else:
        if 查询方式 == "从上面全库点选":
            基准 = 当前
        else:
            名字命中 = 按名字查找(目标口红)
            基准 = 名字命中[0] if 名字命中 else None

        if 基准:
            平替们 = 找平替(基准, 预算, 妆效偏好, 只看更便宜)
            st.markdown(f"### 「{基准['全名']}」的同色系平替（{基准['色系']}）")
            展示卡片(平替们)
            if not 平替们:
                st.info("这支暂时没有合适平替，可以把需求写到页面上方的建议箱。")
        else:
            st.info("全库暂时没有这支口红，请写到页面上方的建议箱，我们后面补进去。")

st.markdown(
    '<div class="hint">点开任意口红可看真人试色对比图。全库覆盖常见大牌和平价热门色。没收录的名字可以投进建议箱。屏幕有色差，下手前请对照试色。</div>',
    unsafe_allow_html=True,
)
