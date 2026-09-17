# 觅色

免费预览口红平替；扫收款码付款、客服确认后可开通会员。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run 口红平替工具.py
```

1. 收款码放在 `口红图片/收款码.png`
2. 用户付款后把截图发给你的微信
3. 你确认到账，把 `开通口令.txt` 里一个「未使用」口令发给她
4. 她在网页填口令才能解锁

`开通口令.txt` 不要上传到 GitHub。

## 上网部署（Streamlit Cloud）

1. 主文件填：`口红平替工具.py`
2. App settings → Secrets：

```toml
DEEPSEEK_API_KEY = "你的deepseek密钥"
unlock_password = """
MISE-XXXX  未使用
MISE-YYYY  未使用
"""
```
