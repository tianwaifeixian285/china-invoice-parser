---
name: china-invoice-parser
description: 解析中国发票文件，支持 PDF、OFD、XML、图片或已提取文本；提取结构化发票字段；在可用时校验 PDF/OFD 数字签名；并输出规范化 JSON 和简短摘要。适用于 Hermes、微信、钉钉、飞书、OpenClaw、本地目录或其他自动化流程中的发票处理任务。
---

# 中国发票解析器

当用户需要读取中国电子发票、提取结构化字段、校验签名或汇总发票内容时，使用这个 skill。

## 工作流

1. 识别输入类型：PDF、OFD、图片、XML、纯文本或目录批量输入。
2. 对支持签名的原始文件先验签，再做转换或文本提取。
3. 从文件中提取源文本。
4. 将发票字段归一化到稳定的 JSON 结构。
5. 返回：
   - 规范化 JSON
   - 面向用户的简短摘要
   - 依赖缺失、不支持格式、低置信度字段等告警

## 执行方式

运行 CLI 入口：

```bash
python3 scripts/parse_invoice.py /绝对路径/发票.pdf
```

可选参数：

```bash
python3 scripts/parse_invoice.py /路径/文件.ofd --pretty
python3 scripts/parse_invoice.py /路径/文件.pdf --summary-only
```

## 输出约定

CLI 输出 JSON，顶层字段包括：

- `engine`
- `file_type`
- `invoice`
- `signature`
- `warnings`
- `raw_text`
- `summary`

## 参考文档

- 中文说明：`README.md`
