# 觅色

免费查询口红平替。介绍页「去购买」是联盟广告：核对过色号才收录，优先淘宝，其次京东、拼多多、唯品会。

线上：https://laolizhuang.github.io/kouhong-pingti/

改完口红数据后，在本机运行 `python 生成网页数据.py`，再把 `kouhong.json`、`p/`、`sitemap.xml` 一起提交。搜索引擎用地图：https://laolizhuang.github.io/kouhong-pingti/sitemap.xml

本地预览：

```bash
python 生成网页数据.py
python -m http.server 8080
```

浏览器打开 http://127.0.0.1:8080/

建议箱会打开访客的邮箱，发到站长 QQ 邮箱。
