# DemoTenant Switchboard

DemoTenant Switchboard 使用 YAML 场景配方生成可复位的 SaaS 演示租户、角色、业务数据和 Playwright 巡演脚本。目标用户是售前、解决方案工程师、DevRel、培训团队和 SaaS 开发者。

当前状态：`v0.1.0`。

## 快速开始

```bash
python -m pip install -e ".[dev]"
demotenant-switchboard generate examples/ecommerce.yaml --output demo-output/ecommerce
demotenant-switchboard validate --output demo-output/ecommerce
demotenant-switchboard switch mina-ops --output demo-output/ecommerce
```

生成结果包含 `dataset.json`、`records.csv`、`personas.csv`、`tenant.sqlite`、`demo.html`、`playwright_tour.py`、`TOUR_STEPS.md` 和 `manifest.json`。

## 核心能力

- 用 YAML 定义 tenant、persona、数据量、时间线和演示故事。
- 生成确定性的 SQLite、JSON 和 CSV 数据集。
- 提供角色切换、场景 reset、数据校验和 checksum 命令。
- 生成 Playwright 巡演脚本和演示步骤文档。
- 内置电商、项目管理、客服工单三类场景。

## 验证命令

```bash
python scripts/verify.py
python scripts/demo.py
python scripts/package_release.py
python scripts/release_check.py
```

如果系统支持 `make`：

```bash
make verify
make demo
make package
make release-check
```

## 隐私边界

项目离线运行，内置示例均为固定 seed 生成的合成数据。不要把真实客户数据、密钥、Cookie、Token 或生产数据库导出写入 recipe。

## 差异化

公开仓库抽样检索未发现同名且高度同构的活跃项目。相邻项目多为单产品 demo data generator 或通用 Playwright 示例，本项目把 YAML 场景 DSL、可复位 checksum、persona session、SQLite/JSON/CSV 输出和 Playwright 巡演串在一起。
