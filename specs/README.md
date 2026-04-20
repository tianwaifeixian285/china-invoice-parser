# 规格说明

本目录用于存放 `china-invoice-parser` 的规格文件。

从 `0.1.0` 开始，项目采用更明确的 SDD + TDD 结构：

- 规格先行：先冻结范围、输入输出协议、状态枚举、版本边界
- 测试守门：每个发布版本至少有样本、schema 验证和核心行为测试

## 0.1.0 范围

`0.1.0` 是首个可用版本，目标是：

- 支持 `PDF` 发票解析
- 支持 `OFD` 发票解析
- 支持基础字段提取
- 支持基础明细行提取
- 支持 PDF 签名检测与保守验签
- 支持 OFD 签名结构校验
- 输出稳定 JSON

`0.1.0` 明确不承诺：

- OFD 密码学完整验签
- 图片 OCR
- 批量目录模式
- 所有地区、所有票种、所有版式的全覆盖

`main` 分支在 `0.1.0` 之后已开始加入 OCR 能力，但尚未形成新的正式版本承诺。

## 模块边界

- `scripts/parse_invoice.py`
  统一 CLI 入口
- `src/china_invoice_parser/parser.py`
  文件类型识别与解析总流程
- `src/china_invoice_parser/pdf_extract.py`
  PDF 文本提取
- `src/china_invoice_parser/pdf_verify.py`
  PDF 签名检测与验签
- `src/china_invoice_parser/ofd_extract.py`
  OFD 容器文本提取
- `src/china_invoice_parser/ofd_verify.py`
  OFD 签名结构校验
- `src/china_invoice_parser/fields.py`
  字段和明细行提取
- `specs/result-schema-v1.json`
  结果 JSON 协议

## 验收标准

`0.1.0` 发布前必须满足：

1. `tests/fixtures/` 下至少存在一个脱敏 PDF 和一个脱敏 OFD 样本
2. `pytest -q` 全部通过
3. `scripts/check.sh` 通过
4. `parse_invoice.py` 对样本输出满足 `result-schema-v1.json`
5. `pyproject.toml` 与 `src/china_invoice_parser/__init__.py` 的版本一致
