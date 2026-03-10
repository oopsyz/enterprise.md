# ENTERPRISE.md

一个拟议中的标准，用于定义多层级仓库导航与确定性路由约定，在 `AGENTS.md` 的基础上扩展到企业级、多仓库交付场景。

## 状态

**草案** - 欢迎反馈。

分类：**拟议标准**。

## 如何引用本提案

当其他项目引用该约定时，请将本仓库作为规范的权威参考。

推荐引用文本：

`Multi-Level Repository Navigation and Routing Convention (Proposed Standard, Draft)`

规范正文：

- [enterprise_repo_convention.zh-CN.md](enterprise_repo_convention.zh-CN.md)

## 问题

`AGENTS.md` 适合定义单仓库内的 agent 行为，但企业级交付通常会跨越多个仓库以及不同架构层级（企业、解决方案、领域）。团队需要具备层级感知的入口文件、确定性的跨仓库路由，以及明确的归属与治理机制。

## 本提案的内容

本提案定义了两个彼此独立、可分离采用的层次：

| 层次 | 目的 | 是否需要工具支持？ |
|---|---|---|
| **Layer A: Entrypoint Convention** | 通过 `ENTERPRISE.md`、`SOLUTION.md`、`DOMAIN.md` 实现人员/agent 导航 | 否 |
| **Layer B: Routing Catalog Specification** | 通过 YAML 目录和工作流上下文在不同层级之间进行确定性机器路由 | 仅编排/运行时需要 |

组织可以只采用 Layer A，而不采用 Layer B。

本提案围绕“渐进式披露”构建：

1. 入口文件提供简洁的导航和上下文。
2. 规范化目录承载确定性的路由数据。
3. 更详细的设计与实现上下文保留在被链接的工件中。

## 定位

`ENTERPRISE.md` 不是一个新的 AI 助手、IDE 或编码代理。

它是一个拟议中的约定层，现有工具可以实现或遵循它，以便在企业级多仓库环境中更高效地工作。

从实际角度看，该提案定义了：

1. 面向仓库级与架构级入口文件的导航标准
2. 在企业、解决方案、领域和实现上下文之间切换的确定性路由标准
3. 面向隔离会话或线程的共享工件上下文模型
4. 面向企业安全自动化的失败即关闭治理模型

这意味着二者关系如下：

1. Codex、Claude Code、Cursor、Copilot 等工具提供 AI 执行界面
2. `ENTERPRISE.md` 为这些工具提供跨多仓库交付可遵循的仓库与路由约定

简而言之：

`ENTERPRISE.md` 是多仓库协同标准，而不是编码助手本身。

## 关键规则

1. `AGENTS.md` 仍然是仓库本地行为约束的契约。背景可参考 [`AGENTS.md` convention](https://github.com/agentsmd/agents.md)。
2. Agent 必须从 `AGENTS.md` 开始，且 `AGENTS.md` 必须指示 agent 始终读取当前仓库对应层级的入口文件。
3. `ENTERPRISE.md`、`SOLUTION.md` 和 `DOMAIN.md` 是导航入口，而不是重复存放数据的文件。
4. 上游链接必须按层级显式给出：当企业层存在时，`SOLUTION.md` 和 `DOMAIN.md` 都应链接到 `ENTERPRISE.md`。
5. `DOMAIN.md` 不将 `SOLUTION.md` 作为必需的父级链接，因为解决方案与领域之间通常是多对多关系，应由路由目录或交接工件表达。例如，共享的 “identity” 领域可以同时服务于 “customer portal” 解决方案和 “internal tools” 解决方案。
6. YAML 是路由目录的规范格式；JSON 仅作为可选的、与 schema 等价的兼容性投影。
7. 对于缺失选择器、歧义选择器以及默认不可路由状态，路由必须失败即关闭。
8. 实现不得依赖仓库名启发式、关键字推断或其他推测方式完成核心路由。

## 一致性配置档位

| 档位 | 需要具备的内容 |
|---|---|
| **Core** | Layer A + 顶层存在层级的确定性引导发现机制 + 对实际存在边界的路由目录 |
| **Governed** | Core + 治理注册表、解决方案范围清单以及治理状态工件 |

可参考 [examples/](examples/) 中各档位的完整示例。

格式说明：YAML 是路由目录的规范格式。JSON 仅为可选的、与 schema 等价的兼容格式。

## 路由模型

规范目录与选择器如下：

| Catalog | Level | Selector | Resolves |
|---|---|---|---|
| `initiatives.yml` | Enterprise | `initiative_id` | 解决方案仓库 + `solution_entrypoint` |
| `domain-workstreams.yml` | Solution | `workstream_id` | `domain_id` + 工作流上下文 + 仓库目标 |
| `implementation-catalog.yml` | Domain | `work_item_id` 或 `api_id` | 实现目标/路径 |

默认可路由状态为 `active` 和 `in_progress`。

Core 和 Governed 的实现必须至少提供一种确定性的引导发现机制，用于解析当前组织中存在的最高层级：

1. 显式启动参数。
2. 环境变量。
3. 约定俗成的发现端点。

## 快速开始

1. 阅读[完整提案](enterprise_repo_convention.zh-CN.md)。
2. 判断你是只需要 Layer A，还是需要 `Core` / `Governed` 一致性档位。
3. 从 [templates/](templates/) 复制相关起始文件到你的仓库中。
4. 如果你采用的是 `Core` 或 `Governed` 档位，请定义引导发现机制（例如 `ENTERPRISE_REPO_URL` 环境变量、启动参数，或类似 `https://config.example.com/enterprise-catalog` 的固定发现端点）。
5. 将占位符替换为你组织的真实数据，并将路由数据保存在规范 YAML 目录中。
6. 参考 [examples/](examples/) 中各档位的完整示例。

## 仓库内容

```text
README.md                                          -- 英文说明
README.zh-CN.md                                    -- 中文说明
LICENSE                                            -- Apache 2.0 许可证
AGENTS.md                                          -- 本仓库的 agent 导航说明
enterprise_repo_convention.md                      -- 英文提案正文
enterprise_repo_convention.zh-CN.md                -- 中文提案正文
templates/
  README.md                                        -- 模板使用说明
  ENTERPRISE.md.template                           -- 企业层入口模板
  SOLUTION.md.template                             -- 解决方案层入口模板
  DOMAIN.md.template                               -- 领域层入口模板
  AGENTS.{ea,sa,da,dev}.md.template                -- 不同角色的 AGENTS.md 模板
  initiatives.yml.template                         -- 企业层路由目录模板
  domain-workstreams.yml.template                  -- 解决方案层路由目录模板
  implementation-catalog.yml.template              -- 领域到实现层路由目录模板
  domain-registry.yml.template                     -- 领域治理注册表模板
  solution-index.yml.template                      -- 解决方案范围清单模板
  initiative-pipeline.yml.template                 -- 组合级流水线源模板
  industry/
    domain-registry.telco.yml.template             -- 电信行业 TMF ODA 组件基线模板
examples/
  core/                                            -- 核心路由示例
  governed/                                        -- 企业治理示例
reference/
  harness-engineering.md                           -- 参考说明
  machine-access-contract.md                       -- 查询规范路由目录的可选契约
```

## 归属模型

建议的默认归属如下：

| Artifact | Owner |
|---|---|
| `AGENTS.md` | 仓库所有者 |
| `ENTERPRISE.md` | EA |
| `SOLUTION.md` | SA |
| `DOMAIN.md` | DA |
| `initiatives.yml` | EA/PMO |
| `domain-workstreams.yml` | SA |
| `implementation-catalog.yml` | DA |

如果多个角色在同一团队或同一仓库中合并承担，则必须在相应入口文件中显式声明归属。

## 贡献

本提案当前仍处于草案阶段。欢迎通过 issue 或 pull request 提供反馈。

提交 issue 时，请注明你的反馈对应哪一层（A 或 B）或哪一个一致性档位（`Core` / `Governed`）。提交 pull request 时，请尽量将变更聚焦在提案的单一章节。

## 许可证

本仓库采用 Apache 2.0 许可证。详见 [LICENSE](LICENSE)。

## 兼容性

本提案是对 `AGENTS.md` 的增量扩展，不会替代或修改现有标准。
