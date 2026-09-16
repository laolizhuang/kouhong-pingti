# 口红平替馆

免费预览口红平替；开通会员可看试色视频、涂口红教学和 AI 查询。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run 口红平替工具.py
```

## 上网部署（Streamlit Cloud）

1. 把本仓库连到 [Streamlit Cloud](https://share.streamlit.io/)
2. 主文件填：`口红平替工具.py`
3. 在 App settings → Secrets 里粘贴：

```toml
DEEPSEEK_API_KEY = "你的deepseek密钥"
member_codes = """
LIP-XXXX-XXXX  月卡  未使用
LIP-YYYY-YYYY  永久  未使用
"""
```

卡密不要写进 GitHub。本地卡密在 `会员卡密.txt`。
