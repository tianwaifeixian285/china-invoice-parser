# 贡献指南

感谢你为 `china-invoice-parser` 做贡献。

## 开发原则

- `main` 始终保持可发布状态
- 日常开发使用 `feat/*`、`fix/*` 等功能分支
- 合并前必须通过 `./scripts/check.sh`
- 只提交脱敏样本，不接受真实发票、真实税号、真实证书

## 开发环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[pdf,sign,dev]'
pre-commit install
```

## 本地检查

```bash
./scripts/check.sh
```

当前检查内容包括：

- `ruff` 静态检查
- `black --check` 格式检查
- 结果 schema 格式有效
- 脱敏样本可重复生成
- 全量测试通过
- 构建产物可成功生成并安装

## 自动格式化

```bash
./scripts/format.sh
```

## 构建产物

```bash
./scripts/build_dist.sh
```

## 提交建议

- `feat: ...` 新功能
- `fix: ...` 缺陷修复
- `test: ...` 测试或契约补充
- `build: ...` 构建、脚本、依赖或仓库基础设施
- `docs: ...` 文档变更

## Pull Request 要求

- 说明变更目的和影响范围
- 如涉及解析逻辑，请补测试
- 如涉及 schema 变更，请更新 `specs/`
- 如涉及样本，请确保样本已脱敏并说明来源类型

## 版本与发布

- `0.1.x`：兼容性修复和小增强
- `0.2.x`：新增能力但尽量不破坏 `result-schema-v1`
- 发布前执行：

```bash
./scripts/check.sh
./scripts/release.sh <version>
```
