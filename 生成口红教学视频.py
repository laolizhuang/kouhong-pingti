# 生成一支「教人画口红」的教学短视频
# 运行：python 生成口红教学视频.py

from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

根目录 = Path(__file__).parent
图片目录 = 根目录 / "口红图片" / "口红教学"
视频目录 = 根目录 / "口红视频"
视频目录.mkdir(exist_ok=True)

宽, 高 = 540, 720
源宽, 源高 = 612, 816
帧率 = 24
奶油 = np.array([248.0, 236.0, 228.0], dtype=np.float32)

步骤 = [
    ("01.png", "第1步  打底保湿", "先涂薄薄一层润唇膏，唇纹会更细"),
    ("02.png", "第2步  勾勒唇峰", "从唇峰两点开始，轻轻画出上唇轮廓"),
    ("03.png", "第3步  填满上唇", "沿着唇线往中间填，不要画出唇外"),
    ("04.png", "第4步  填满下唇", "从下唇中央向外推开，嘴角对整齐"),
    ("05.png", "第5步  抿匀修角", "轻轻抿一下，用指腹修齐左右嘴角"),
    ("06.png", "第6步  完成", "左右对称、唇线干净，就可以出门了"),
]


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
    h, w = 阵.shape[:2]
    最大上 = h - 高
    左 = (w - 宽) // 2
    上 = int(最大上 * 平滑(进度))
    return 阵[上:上 + 高, 左:左 + 宽]


def 奶油转场(甲, 乙, u):
    k = 平滑(u)
    if k < 0.5:
        p = k / 0.5
        return 甲 * (1 - p) + 奶油 * p
    p = (k - 0.5) / 0.5
    return 奶油 * (1 - p) + 乙 * p


def 做字层(标题, 说明, 字体文件):
    层 = Image.new("RGBA", (宽, 高), (0, 0, 0, 0))
    画 = ImageDraw.Draw(层)
    大字 = ImageFont.truetype(字体文件, 24) if 字体文件 else ImageFont.load_default()
    小字 = ImageFont.truetype(字体文件, 16) if 字体文件 else ImageFont.load_default()
    画.rectangle((0, 高 - 118, 宽, 高), fill=(40, 24, 24, 160))
    画.rectangle((0, 高 - 124, 宽, 高 - 118), fill=(196, 46, 58, 255))
    画.rounded_rectangle((16, 18, 250, 56), radius=18, fill=(196, 46, 58, 200))
    画.text((28, 26), 标题, font=大字, fill=(255, 255, 255, 240))
    画.text((18, 高 - 100), 说明, font=小字, fill=(255, 255, 255, 235))
    画.text((18, 高 - 68), "口红教学  ·  跟着涂就不会花", font=小字, fill=(243, 210, 210, 220))
    return np.asarray(层, dtype=np.float32)


def 叠字(画面, 透明层):
    a = 透明层[:, :, 3:4] / 255.0
    return 画面 * (1 - a) + 透明层[:, :, :3] * a


def main():
    字体 = 找字体()
    _ = imageio_ffmpeg.get_ffmpeg_exe()
    图们 = [打开阵(图片目录 / 文件) for 文件, _, _ in 步骤]
    字层 = [做字层(标题, 说明, 字体) for _, 标题, 说明 in 步骤]

    每步秒 = 1.45
    转场秒 = 0.7
    总秒 = 每步秒 * len(步骤) + 转场秒 * (len(步骤) - 1)
    总帧 = int(总秒 * 帧率)

    输出 = 视频目录 / "口红教学.mp4"
    临时 = 视频目录 / "_tmp_口红教学.mp4"
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

    节点 = []
    t = 0.0
    for i in range(len(步骤)):
        节点.append(("hold", i, t, t + 每步秒))
        t += 每步秒
        if i < len(步骤) - 1:
            节点.append(("fade", i, t, t + 转场秒))
            t += 转场秒

    print(f"开始生成教学视频，约 {总秒:.1f} 秒…", flush=True)
    try:
        for i in range(总帧):
            秒 = i / 帧率
            进度 = i / max(总帧 - 1, 1)
            种类, 序号, 起, 止 = 节点[-1]
            for 项 in 节点:
                if 项[2] <= 秒 <= 项[3] or (项 is 节点[-1] and 秒 >= 项[2]):
                    种类, 序号, 起, 止 = 项
                    break

            if 种类 == "hold":
                画面 = 推镜(图们[序号], 进度)
                画面 = 叠字(画面, 字层[序号])
            else:
                u = (秒 - 起) / max(止 - 起, 0.01)
                甲 = 推镜(图们[序号], 进度)
                乙 = 推镜(图们[序号 + 1], 进度)
                画面 = 奶油转场(甲, 乙, u)
                字幕 = 字层[序号] if 平滑(u) < 0.5 else 字层[序号 + 1]
                画面 = 叠字(画面, 字幕)

            writer.append_data(np.clip(画面, 0, 255).astype(np.uint8))
    finally:
        writer.close()
    临时.replace(输出)
    print(f"完成：{输出}")


if __name__ == "__main__":
    main()
