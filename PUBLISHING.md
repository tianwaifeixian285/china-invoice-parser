# 发布说明

本项目当前已经支持：

- Git tag 触发 GitHub Release
- 构建 `sdist` 和 `wheel`
- 手动触发 PyPI 发布工作流

## 部署到其他 Hermes 机器

推荐使用仓库自带安装脚本：

```bash
git clone https://github.com/tianwaifeixian285/china-invoice-parser.git
cd china-invoice-parser
./scripts/install_hermes_skill.sh
```

开启 OCR：

```bash
./scripts/install_hermes_skill.sh --with-ocr
```

校验安装：

```bash
./scripts/verify_hermes_install.sh
```

默认安装位置：

- `~/.hermes/skills/china-invoice-parser`

## GitHub Release

标准流程：

```bash
./scripts/check.sh
./scripts/release.sh 0.1.1
git push origin main --tags
```

推送 tag 后，`.github/workflows/release.yml` 会：

- 再次执行仓库检查
- 构建发布产物
- 自动创建 GitHub Release

## PyPI 发布准备

推荐使用 PyPI Trusted Publisher，而不是长期保存 API Token。

### 建议配置

1. 在 PyPI 创建项目 `china-invoice-parser`
2. 在 PyPI 项目设置中启用 Trusted Publisher
3. 绑定 GitHub 仓库：
   - owner: `tianwaifeixian285`
   - repository: `china-invoice-parser`
   - workflow: `publish-pypi.yml`
   - environment: `pypi`
4. 在 GitHub 仓库中创建环境 `pypi`
5. 为 `pypi` 环境加审批规则

## PyPI 发布

PyPI 发布工作流当前设计为手动触发，避免在 Trusted Publisher 未配置好之前误触发失败。

触发方式：

- GitHub Actions
- 选择 `Publish PyPI`
- 填入版本号，例如 `v0.1.0`

工作流会：

- 检查 tag 是否存在
- 构建 `sdist` 和 `wheel`
- 发布到 PyPI

## 发布前检查

至少确认：

- `./scripts/check.sh` 通过
- `python -m build` 成功
- `pip install dist/*.whl` 成功
- `CHANGELOG.md` 已更新
- GitHub Release 说明已准备
