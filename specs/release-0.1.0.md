# 0.1.0 发布说明

`0.1.0` 是 `china-invoice-parser` 的首个可用版本。

## 发布目标

- 形成稳定的 CLI 入口
- 固定结果 JSON schema v1
- 提供最小但真实可跑的 PDF/OFD 样本
- 建立首版测试门禁

## 功能清单

- PDF 文本提取
- OFD 文本提取
- PDF 验签
- OFD 签名结构校验
- 发票字段提取
- 发票明细行提取
- 样本与回归测试
- 发布脚本

## 发布门禁

发布前必须确认：

- `./scripts/check.sh` 通过
- `pytest -q` 通过
- `tests/fixtures/build_samples.py` 可重复生成样本
- 输出符合 `specs/result-schema-v1.json`
- 版本号在以下文件保持一致
  - `pyproject.toml`
  - `src/china_invoice_parser/__init__.py`

## 分支与标签

- 功能开发：`feat/*`
- 发布分支：直接从 `main` 发版
- 标签格式：`v0.1.0`

## 建议发布动作

```bash
git checkout main
git merge --ff-only feat/python-parser-core
./scripts/check.sh
./scripts/release.sh 0.1.0
git push origin main --tags
```
