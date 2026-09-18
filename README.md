# 觅色

免费查询口红平替。介绍页「去购买」是联盟广告：核对过色号才收录，优先淘宝，其次京东、拼多多、唯品会。

## 网页（推荐，打开更快）

线上：https://laolizhuang.github.io/kouhong-pingti/

改完口红数据后，在本机运行 `python 生成网页数据.py`，再把 `kouhong.json` 一起提交。

本地预览：

```bash
python 生成网页数据.py
python -m http.server 8080
```

浏览器打开 http://127.0.0.1:8080/

建议箱会打开访客的邮箱，发到站长 QQ 邮箱。

## Streamlit 版（旧）

```bash
pip install -r requirements.txt
streamlit run 口红平替工具.py
```
