# 流畅版试色视频：慢推镜 + 柔化转场 + 对比滑入
# 运行：python 生成试色视频.py

from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from 口红数据 import 获取口红库

根目录 = Path(__file__).parent
图片目录 = 根目录 / "口红图片" / "试色模特"
视频目录 = 根目录 / "口红视频"
视频目录.mkdir(exist_ok=True)

宽, 高 = 540, 720
源宽, 源高 = 612, 816
帧率 = 24
时长 = 6.0
奶油 = np.array([248.0, 236.0, 228.0], dtype=np.float32)


def 找字体():
    for 路径 in [
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
    ]:
        if 路径.exists():
            return str(路径)
    return None


def 平滑(t):
    t = float(np.clip(t, 0.0, 1.0))
    return t * t * t * (t * (t * 6 - 15) + 10)


def 打开阵(路径):
    图 = Image.open(路径).convert("RGB")
    图 = 图.resize((源宽, 源高), Image.Resampling.LANCZOS)
    return np.asarray(图, dtype=np.float32)


def 推镜(阵, 进度):
    """只裁切、不缩放：镜头平稳下移靠近嘴唇。"""
    h, w = 阵.shape[:2]
    最大上 = h - 高
    最大左 = w - 宽
    上 = int(最大上 * 平滑(进度))
    左 = 最大左 // 2
    return 阵[上:上 + 高, 左:左 + 宽]


def 奶油转场(甲, 乙, u):
    k = 平滑(u)
    if k < 0.5:
        p = k / 0.5
        return 甲 * (1 - p) + 奶油 * p
    p = (k - 0.5) / 0.5
    return 奶油 * (1 - p) + 乙 * p


def 滑入对比(素唇, 妆后, u):
    p = 平滑(u)
    出 = 妆后.copy()
    缝 = 18
    分界 = int((宽 // 2) * p)
    if 分界 <= 0:
        return 出
    出[:, :分界] = 素唇[:, :分界]
    if 分界 < 宽:
        右 = min(宽, 分界 + 缝)
        xs = np.linspace(0, 1, 右 - 分界, dtype=np.float32)[None, :, None]
        出[:, 分界:右] = 素唇[:, 分界:右] * (1 - xs) + 妆后[:, 分界:右] * xs
    return 出


def 做字层(口红, 字体文件):
    底 = Image.new("RGBA", (宽, 高), (0, 0, 0, 0))
    画 = ImageDraw.Draw(底)
    大字 = ImageFont.truetype(字体文件, 24) if 字体文件 else ImageFont.load_default()
    小字 = ImageFont.truetype(字体文件, 17) if 字体文件 else ImageFont.load_default()
    色卡 = tuple(int(口红["色卡"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    画.rectangle((0, 高 - 96, 宽, 高), fill=(40, 24, 24, 150))
    画.rectangle((0, 高 - 102, 宽, 高 - 96), fill=(*色卡, 255))
    画.text((18, 高 - 86), 口红["全名"], font=大字, fill=(255, 255, 255, 235))
    画.text((18, 高 - 52), f"{口红['色系']}  ·  {口红['妆效']}  ·  ¥{口红['价格']}", font=小字, fill=(243, 210, 210, 220))
    return np.asarray(底, dtype=np.float32)


def 做角标(文字, 字体文件, 强调=False):
    层 = Image.new("RGBA", (宽, 高), (0, 0, 0, 0))
    画 = ImageDraw.Draw(层)
    字 = ImageFont.truetype(字体文件, 18) if 字体文件 else ImageFont.load_default()
    填充 = (196, 46, 58, 200) if 强调 else (40, 24, 24, 170)
    画.rounded_rectangle((16, 18, 168, 56), radius=18, fill=填充)
    画.text((32, 26), 文字, font=字, fill=(255, 255, 255, 240))
    return np.asarray(层, dtype=np.float32)


def 叠字(画面, 透明层, 透明度=1.0):
    a = 透明层[:, :, 3:4] / 255.0 * 透明度
    return 画面 * (1 - a) + 透明层[:, :, :3] * a


def 角标透明度(秒, 起点, 终点):
    if 秒 < 起点 or 秒 > 终点:
        return 0.0
    淡 = 0.35
    if 秒 < 起点 + 淡:
        return 平滑((秒 - 起点) / 淡)
    if 秒 > 终点 - 淡:
        return 平滑((终点 - 秒) / 淡)
    return 1.0


def 写视频(口红, 字体, 底栏, 标1, 标2, 标3, 标4):
    色系 = 口红["色系"]
    素唇 = 打开阵(图片目录 / f"素唇_{色系}.png")
    妆后 = 打开阵(图片目录 / f"{色系}.png")
    涂抹路径 = 图片目录 / f"涂抹_{色系}.png"
    涂抹 = 打开阵(涂抹路径) if 涂抹路径.exists() else (素唇 * 0.55 + 妆后 * 0.45)

    总帧 = int(时长 * 帧率)
    输出 = 视频目录 / 口红["视频"]
    临时 = 视频目录 / f"_tmp_{口红['视频']}"
    writer = imageio.get_writer(
        str(临时),
        fps=帧率,
        format="FFMPEG",
        codec="libx264",
        pixelformat="yuv420p",
        ffmpeg_log_level="error",
        macro_block_size=1,
        output_params=["-crf", "26", "-preset", "veryfast"],
    )
    try:
        for i in range(总帧):
            秒 = i / 帧率
            进度 = i / max(总帧 - 1, 1)

            素 = 推镜(素唇, 进度)
            涂 = 推镜(涂抹, 进度)
            妆 = 推镜(妆后, 进度)

            if 秒 < 1.0:
                画面 = 素
            elif 秒 < 2.2:
                画面 = 奶油转场(素, 涂, (秒 - 1.0) / 1.2)
            elif 秒 < 2.7:
                画面 = 涂
            elif 秒 < 4.0:
                画面 = 奶油转场(涂, 妆, (秒 - 2.7) / 1.3)
            elif 秒 < 4.6:
                画面 = 妆
            else:
                画面 = 滑入对比(素, 妆, (秒 - 4.6) / 1.4)

            画面 = 叠字(画面, 底栏)
            画面 = 叠字(画面, 标1, 角标透明度(秒, 0.0, 1.2))
            画面 = 叠字(画面, 标2, 角标透明度(秒, 1.1, 2.9))
            画面 = 叠字(画面, 标3, 角标透明度(秒, 2.8, 4.8))
            画面 = 叠字(画面, 标4, 角标透明度(秒, 4.55, 6.2))
            writer.append_data(np.clip(画面, 0, 255).astype(np.uint8))
    finally:
        writer.close()
    临时.replace(输出)


def main():
    字体 = 找字体()
    _ = imageio_ffmpeg.get_ffmpeg_exe()
    库 = 获取口红库()
    print(f"共 {len(库)} 支，生成更流畅的试色视频…")
    for 序号, 口红 in enumerate(库, start=1):
        底栏 = 做字层(口红, 字体)
        标1 = 做角标("未涂口红", 字体)
        标2 = 做角标("正在上妆", 字体)
        标3 = 做角标("涂好后", 字体, 强调=True)
        标4 = 做角标("前后对比", 字体, 强调=True)
        写视频(口红, 字体, 底栏, 标1, 标2, 标3, 标4)
        print(f"[{序号}/{len(库)}] {口红['全名']}", flush=True)
    print("全部完成")


if __name__ == "__main__":
    main()
