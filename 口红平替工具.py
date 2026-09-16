# ============================================
# 觅色：口红平替查询（全库版：所有口红都能点、能搜）
# 使用前：把密钥占位符换成你的真实 DeepSeek 密钥（AI 查询才可用）
# 运行：streamlit run 口红平替工具.py
# ============================================

import os
from pathlib import Path

import requests
import streamlit as st

from 口红数据 import 获取口红库
from 会员系统 import (
    免费可看支数,
    免费平替条数,
    客服微信,
    开通会员,
    收款码路径,
    月卡价格,
    月卡说明,
    会员仍有效,
    会员文案,
)

st.set_page_config(page_title="觅色", page_icon="💄", layout="wide")

try:
    api_key = st.secrets.get("DEEPSEEK_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY", "")
except Exception:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")

图片目录 = Path(__file__).parent / "口红图片"
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
    .plan {
        background: #fff;
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 8px 22px rgba(120, 60, 60, 0.08);
        border: 1px solid rgba(196, 92, 92, 0.18);
        margin-bottom: 8px;
    }
    .plan-price { color: #c45c5c; font-size: 1.6rem; font-weight: 700; }
    .lock-tip { color: #a05a5a; font-size: 0.9rem; }
    .pay-note {
        text-align: center;
        color: #8a5a5a;
        font-size: 0.92rem;
        margin: 8px 0 14px 0;
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


def 展示卡片(列表):
    if not 列表:
        st.warning("按当前条件没有筛到。试试放宽品牌/色系/预算，或勾选 AI 再查。")
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

if "会员" not in st.session_state:
    st.session_state["会员"] = None
会员 = 会员仍有效(st.session_state.get("会员"))
st.session_state["会员"] = 会员
已开通 = 会员 is not None
st.caption("当前身份：" + 会员文案(会员))

with st.expander("开通会员，解锁全部试色视频 / 教学 / AI 平替", expanded=not 已开通):
    if 已开通:
        st.success("已是会员。" + 会员文案(会员))
    else:
        st.markdown(
            f'<div class="plan"><div>会员</div>'
            f'<div class="plan-price">¥ {月卡价格}</div>'
            f'<div class="lock-tip">{月卡说明}</div></div>',
            unsafe_allow_html=True,
        )
        收款码 = 收款码路径()
        if 收款码:
            左空, 码列, 右空 = st.columns([1, 1.2, 1])
            with 码列:
                st.image(str(收款码), use_container_width=True, caption="微信 / 支付宝收款码")
            st.markdown(
                f'<div class="pay-note">打开微信或支付宝，扫上面的码付 ¥{月卡价格}，'
                "付完回到这里点按钮即可解锁。</div>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("还没放收款码。请把微信或支付宝收款码图片保存为 `口红图片/收款码.png`。")
        if st.button("我已付款，立即解锁", type="primary"):
            st.session_state["会员"] = 开通会员()
            st.rerun()
        st.caption(
            f"免费可看 12 支口红和 1 条平替。付款遇到问题可加微信 {客服微信}。"
        )

st.markdown("### 先学怎么涂")
教1, 教2 = st.columns([1.15, 1.35])
with 教1:
    教学视频 = Path(__file__).parent / "口红视频" / "口红教学.mp4"
    if 已开通 and 教学视频.exists():
        st.video(str(教学视频), format="video/mp4", autoplay=True, muted=True, loop=True)
    elif 教学视频.exists():
        st.image(图片路径("banner.png"), use_container_width=True)
        st.warning("教学视频是会员内容。开通后可看完整 6 步示范。")
    else:
        st.info("教学视频还没生成，请先运行：python 生成口红教学视频.py")
with 教2:
    st.markdown("**6 步把口红画干净**")
    st.markdown(
        """
1. **打底保湿** — 先涂薄薄一层润唇膏  
2. **勾勒唇峰** — 从唇峰两点开始画轮廓  
3. **填满上唇** — 沿着唇线往中间填色  
4. **填满下唇** — 从下唇中央向外推开  
5. **抿匀修角** — 轻轻抿一下，修齐嘴角  
6. **完成** — 左右对称就可以出门了  
        """
    )
    st.caption("视频会循环播放，跟着做一遍就不会花、不会歪。")

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

全部命中 = len(展示列表)
if not 已开通:
    展示列表 = 展示列表[:免费可看支数]
    st.markdown(
        f'<div class="count">免费预览 {len(展示列表)} / {全部命中} 支'
        f'（全库共 {len(口红库)} 支，开通会员看全部）</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="count">当前显示 {len(展示列表)} / {len(口红库)} 支，点击下方色号即可选中</div>',
        unsafe_allow_html=True,
    )

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

c1, c2, c3 = st.columns(3)
with c1:
    预算 = st.slider("最高预算（元）", min_value=30, max_value=500, value=150, step=10)
with c2:
    妆效偏好 = st.selectbox("妆效", ["不限", "哑光/雾面", "丝绒", "润泽/水光"])
with c3:
    肤色 = st.selectbox("肤色", ["不限", "黄皮", "白皮", "自然偏深"])

只看更便宜 = st.checkbox("只看不超过预算的平替", value=True)
用AI补充 = st.checkbox("本地查完后，再用 AI 多推荐几款", value=False)

当前 = 按id查找(st.session_state["选中id"])
目标口红 = ""
if 查询方式 == "从上面全库点选":
    目标口红 = 当前["全名"]
    左, 右 = st.columns([1.1, 1.4])
    with 左:
        视频文件 = Path(__file__).parent / "口红视频" / 当前["视频"]
        if 已开通 and 视频文件.exists():
            st.video(str(视频文件), format="video/mp4", autoplay=True, muted=True, loop=True)
        else:
            st.image(图片路径(当前["图片"]), use_container_width=True)
            if not 已开通:
                st.caption("开通会员可看：未涂 → 涂抹 → 涂好 → 左右对比")
    with 右:
        st.markdown(f"#### {当前['全名']}")
        st.markdown(
            f'<div class="swatch" style="background:{当前["色卡"]}; width:160px;"></div>',
            unsafe_allow_html=True,
        )
        st.write(f"{当前['色系']} · {当前['妆效']} · ¥{当前['价格']}")
        st.caption(当前["说明"] + "（视频：未涂 → 涂抹 → 涂好 → 左右对比）")
else:
    目标口红 = st.text_input("输入口红名字（如：阿玛尼 红管 405、迪奥 999）")

系统指令 = (
    "你是美妆顾问，专门帮人找口红平替。"
    "请根据用户想找的口红、预算、妆效和肤色，推荐 3 款国内容易买到的平价平替。"
    "每款写清：品牌+名字、色号、大约价格、妆效、为什么像、适合什么肤色。"
    "只推荐真实常见的国货/平价品牌（如完美日记、INTO YOU、花西子、珂拉琪、橘朵、3CE、美宝莲、卡姿兰、ColorKey）。"
    "语气真诚，不要夸张，并提醒：屏幕色差存在，最终以试色为准。"
)

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
            if not 已开通:
                隐藏数 = max(0, len(平替们) - 免费平替条数)
                平替们 = 平替们[:免费平替条数]
                st.markdown(f"### 「{基准['全名']}」的同色系平替（{基准['色系']}）")
                展示卡片(平替们)
                if 隐藏数:
                    st.warning(f"还有 {隐藏数} 条平替已锁定。开通会员可看全部，并解锁试色视频和 AI。")
            else:
                st.markdown(f"### 「{基准['全名']}」的同色系平替（{基准['色系']}）")
                展示卡片(平替们)
            筛选后 = 平替们
        else:
            st.info("全库暂时没有完全对上这支名字，下面用 AI 帮你找平替。")
            筛选后 = []

        需要AI = 已开通 and ((not 筛选后) or 用AI补充)
        if (not 筛选后 or 用AI补充) and not 已开通:
            st.info("AI 平替是会员功能。开通后可对全库没有的色号继续查询。")
        elif 需要AI:
            if not api_key:
                st.error("还没设置 DeepSeek 密钥。请在终端先运行：$env:DEEPSEEK_API_KEY='你的密钥'")
            else:
                with st.spinner("正在找平替..."):
                    用户需求 = (
                        f"目标口红：{目标口红}；预算最高：{预算}元；"
                        f"妆效偏好：{妆效偏好}；肤色：{肤色}"
                    )
                    请求头 = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                    数据 = {
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": 系统指令},
                            {"role": "user", "content": 用户需求},
                        ],
                    }
                    try:
                        响应 = requests.post(
                            "https://api.deepseek.com/chat/completions",
                            json=数据, headers=请求头, timeout=60
                        )
                        结果 = 响应.json()
                        if 响应.status_code == 200:
                            st.subheader("AI 平替推荐")
                            st.write(结果["choices"][0]["message"]["content"])
                        else:
                            st.error(f"出错了：{结果}")
                    except Exception as e:
                        st.error(f"请求出错：{e}")

st.markdown(
    '<div class="hint">点开任意口红可看真人试色短视频。全库覆盖常见大牌和平价热门色。没收录的名字可以自己输入，用 AI 补查。屏幕有色差，下手前请对照试色。</div>',
    unsafe_allow_html=True,
)
