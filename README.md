# 觅色

免费查询口红平替，可看试色对比图、涂口红教学和 AI 查询。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run 口红平替工具.py
```

## 上网部署（Streamlit Cloud）

1. 主文件填：`口红平替工具.py`
2. 要用 AI 查询时，在 App settings → Secrets 里粘贴：

```toml
DEEPSEEK_API_KEY = "你的deepseek密钥"
```
