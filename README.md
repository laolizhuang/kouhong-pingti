# 觅色

免费预览口红平替；扫收款码开通会员后可看试色视频、涂口红教学和 AI 查询。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run 口红平替工具.py
```

把微信或支付宝收款码图片放到 `口红图片/收款码.png`，网页里就会显示。用户扫码付款后点「我已付款，立即解锁」。

## 上网部署（Streamlit Cloud）

1. 把本仓库连到 [Streamlit Cloud](https://share.streamlit.io/)
2. 主文件填：`口红平替工具.py`
3. 在 App settings → Secrets 里粘贴：

```toml
DEEPSEEK_API_KEY = "你的deepseek密钥"
```
