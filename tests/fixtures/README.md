# 脱敏样本说明

本目录存放测试和开发用的脱敏样本。

原则：

- 不包含真实企业证照、真实税号、真实金额或真实证书
- 样本结构尽量贴近中国电子发票常见版式
- PDF 样本用于文本提取和 PDF 签名测试
- OFD 样本用于结构化文本提取和 OFD 签名结构校验

如果需要重新生成样本，可执行：

```bash
source .venv/bin/activate
python tests/fixtures/build_samples.py
```
