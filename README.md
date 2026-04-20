# China Invoice Parser

[![CI](https://github.com/tianwaifeixian285/china-invoice-parser/actions/workflows/ci.yml/badge.svg)](https://github.com/tianwaifeixian285/china-invoice-parser/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/tag/tianwaifeixian285/china-invoice-parser?label=release)](https://github.com/tianwaifeixian285/china-invoice-parser/releases)
[![License](https://img.shields.io/github/license/tianwaifeixian285/china-invoice-parser)](https://github.com/tianwaifeixian285/china-invoice-parser/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/china-invoice-parser)](https://pypi.org/project/china-invoice-parser/)

China Invoice Parser 是一个以 Python 为主栈的技能项目，用于解析中国发票文件，支持从 PDF 和 OFD 中提取字段，并在具备条件时验证数字签名。

## 当前状态

当前仓库已经包含第一版开发骨架：

- Python CLI 入口
- 结构化 JSON 输出协议
- `specs/` 规格目录
- PDF 文本提取兜底实现
- OFD 文本提取兜底实现
- 基于 `pyHanko` 的 PDF 验签实现
- OFD 签名结构校验
- 脱敏 PDF/OFD 样本与自动化测试
- 中文文档

## 设计目标

- 作为可复用 skill，适配 Hermes、微信、钉钉、飞书、OpenClaw 以及其他自动化流程
- 以 Python 作为主运行时
- 使用“可选依赖增强”而不是强制安装重型环境
- 输出确定性的 JSON，而不是仅靠模型猜测字段

## 目录结构

```text
china-invoice-parser/
├── SKILL.md
├── README.md
├── pyproject.toml
├── scripts/
│   └── parse_invoice.py
└── src/
    └── china_invoice_parser/
        ├── cli.py
        ├── parser.py
        ├── models.py
        ├── fields.py
        ├── pdf_extract.py
        ├── pdf_verify.py
        ├── ofd_extract.py
        ├── ofd_verify.py
        └── format_result.py
```

## 快速开始

```bash
cd /Users/mac/2026/研究/china-invoice-parser
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[pdf,sign,dev]'
python3 scripts/parse_invoice.py /绝对路径/发票.pdf --pretty
```

启用 OCR 能力：

```bash
pip install -e '.[pdf,sign,ocr,dev]'
brew install tesseract
```

## 规格目录

`0.1.0` 起，项目采用更明确的 SDD + TDD 结构：

- [specs/README.md](/Users/mac/2026/研究/china-invoice-parser/specs/README.md)：版本范围、模块边界、验收标准
- [specs/result-schema-v1.json](/Users/mac/2026/研究/china-invoice-parser/specs/result-schema-v1.json)：结果 JSON schema
- [specs/release-0.1.0.md](/Users/mac/2026/研究/china-invoice-parser/specs/release-0.1.0.md)：`0.1.0` 发布约束与清单

## 当前能力

- `PDF`：若安装 `pypdf`，优先读取 PDF 文本；未安装则返回告警
- `PDF OCR`：若文本提取质量差，且已安装 OCR 依赖与 `tesseract`，自动尝试 OCR 兜底
- `OFD`：尽量从 OFD 容器中的 XML/文本描述内容中抽取文本；失败时返回告警
- `图片发票`：安装 OCR 依赖后可直接识别 `png/jpg/jpeg/webp/tiff/bmp`
- `PDF 验签`：使用 `pyHanko` 做签名检测和校验；在信任链不足时保守返回 `unknown`
- `OFD 验签`：已做签名清单、引用文件和基础元数据校验；后续继续增强密码学验签
- `字段提取`：支持票种、代码、号码、日期、购销双方、税号、金额、税额、价税合计
- `明细提取`：支持常见的管道分隔和宽空格分隔行项目

## 样本与测试

脱敏样本位于：

- `tests/fixtures/pdf/sanitized_vat_invoice.pdf`
- `tests/fixtures/ofd/sanitized_vat_invoice.ofd`

重新生成样本：

```bash
source .venv/bin/activate
python tests/fixtures/build_samples.py
```

运行测试：

```bash
source .venv/bin/activate
pytest -q
```

检查规格与测试：

```bash
./scripts/check.sh
```

自动格式化：

```bash
./scripts/format.sh
```

构建发布产物：

```bash
./scripts/build_dist.sh
```

安装到其他 Hermes 机器：

```bash
git clone https://github.com/tianwaifeixian285/china-invoice-parser.git
cd china-invoice-parser
./scripts/install_hermes_skill.sh
```

启用 OCR 的 Hermes 安装：

```bash
./scripts/install_hermes_skill.sh --with-ocr
```

安装后校验：

```bash
./scripts/verify_hermes_install.sh
```

## 分支策略

- `main`：始终保持可发布状态
- `feat/*`：功能开发分支
- 合并前必须通过样本生成和测试

当前建议：功能开发统一走 `feat/*` 分支，确认稳定后再合并到 `main`

## 发版策略

- 使用语义化版本，但在 `1.0.0` 前保持 `0.x.y`
- `0.1.0`：首个可用版本，覆盖 PDF/OFD 基础解析、字段提取、PDF 验签、OFD 签名结构校验
- `0.1.x`：仅修复缺陷或小幅增强规则
- `0.2.x`：增加新票种、OCR、批量模式、更多验签能力
- `1.0.0`：输入输出协议、字段 schema 和 CLI 基本稳定

建议发版动作：

```bash
./scripts/check.sh
./scripts/release.sh 0.1.0
```

建议发布顺序：

1. 在 `feat/*` 分支完成功能与测试
2. 合并到 `main`
3. 在 `main` 上执行 `./scripts/release.sh 0.1.0`
4. 推送 `main` 和 tag

发布细节参见：[PUBLISHING.md](/Users/mac/2026/研究/china-invoice-parser/PUBLISHING.md)

## 部署到 Hermes

推荐在其他 Hermes 机器上按以下方式安装：

```bash
git clone https://github.com/tianwaifeixian285/china-invoice-parser.git
cd china-invoice-parser
./scripts/install_hermes_skill.sh
```

脚本会：

- 克隆或更新仓库到 `~/.hermes/skills/china-invoice-parser`
- 创建独立虚拟环境
- 安装 `pdf + sign` 依赖
- 可选安装 OCR 依赖

如果目标机器要启用 OCR，还需要安装系统级 `tesseract`。

## 下一步计划

1. 按票种和地区继续补强字段模板
2. 增强 OFD 密码学验签逻辑
3. 增强 OCR 对 OFD 转图和复杂版式的支持
4. 增加目录批量模式
5. 增加更多脱敏样本和回归测试
