# 觅色

免费查询口红平替。全库没有的色号可以投进页面最下面的建议箱。介绍页有「去购买」（广告）。

介绍页「去购买」已接联盟广告。优先淘宝佣金，其次京东、拼多多（只收录核对过色号的）。都没有的可去三平台搜索，不产生佣金。

用户留言会发到 QQ 邮箱。需要先在 QQ 邮箱开启 SMTP，把授权码写进 `邮箱授权码.txt`。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run 口红平替工具.py
```

## 上网部署（Streamlit Cloud）

主文件填：`口红平替工具.py`  
Secrets 里加上：`qq_auth_code = "你的授权码"`
