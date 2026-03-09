# 提案：多层级仓库导航与路由约定

状态：草案
受众：标准/社区贡献者、平台/工具构建者、企业架构团队
范围：跨企业层、解决方案层、领域层的多仓库人员与 agent 协作

## 1. 问题

`AGENTS.md` 很适合定义仓库本地行为，但企业级交付通常横跨多个仓库和多个架构层级。
在这种规模下，团队需要：

1. 具备层级感知能力的入口文件。
2. 确定性的跨仓库路由。
3. 明确的归属、治理和失败处理行为。

本提案通过层级入口文件（Layer A）以及面向自动化的可选路由目录（Layer B）来解决这些问题。

## 2. 拟议方案

本提案是对第 1 节问题的回答：它让仓库本地指导保持轻量、面向人类，同时在需要时仍能为自动化提供确定性的跨仓库路由能力。

### 指导原则：跨仓库的渐进式披露

本提案在每个尺度上都采用渐进式披露，而不是把所有内容堆到一个仓库和一个文件里：

1. **仓库层级**（存在 Layer B 时）：路由目录（`initiatives.yml`、`domain-workstreams.yml`、`implementation-catalog.yml`）披露下一个稳定目标，并在需要时给出要打开的精确工作流上下文。解析是确定性的，要么解析成功，要么失败即关闭（见第 5.5 节）。
2. **文件层级**（Layer A）：入口文件披露该仓库中*真正重要*的信息。它们是地图，不是百科全书。
3. **工件层级**：被链接的目录和设计文件披露*细节*，而且只有在你跟随链接时才展开。

每一层都只揭示该层真正相关的信息。当路由目录存在时，它们只是最粗粒度的披露层。

为了实现这一原则，本提案定义了两个彼此独立、可分开采用的层：

1. **Layer A: Entrypoint Convention**
   1. 目的：人员/agent 导航与上下文发现。
   2. 工具依赖：无。
2. **Layer B: Routing Catalog Specification（可选）**
   1. 目的：在不同层级之间进行确定性的机器路由（例如企业仓库 -> 解决方案仓库 -> 领域仓库）。
   2. 工具依赖：仅编排/运行时。

组织可以只采用 Layer A，而不采用 Layer B。

```mermaid
flowchart LR
    subgraph ER["企业仓库"]
        EEntry["ENTERPRISE.md"]:::entry
        ELocal["其他企业层文件
        (readmes, policies, strategy docs)"]:::artifact
        ERoute["initiatives.yml
        (选择解决方案仓库)"]:::routing

        EEntry -->|"链接到"| ELocal
        EEntry -->|"需要某个解决方案？"| ERoute
    end

    subgraph SR["解决方案仓库"]
        SEntry["SOLUTION.md"]:::entry
        SLocal["其他解决方案文件
        (architecture, ADRs, roadmaps)"]:::artifact
        SRoute["domain-workstreams.yml
        (选择领域工作流)"]:::routing

        SEntry -->|"链接到"| SLocal
        SEntry -->|"需要某个领域？"| SRoute
    end

    subgraph DR["领域仓库"]
        DEntry["DOMAIN.md"]:::entry
        DLocal["其他领域文件
        (ADRs, API specs, schemas)"]:::artifact

        DEntry -->|"链接到"| DLocal
    end

    ERoute -->|"打开仓库"| SEntry
    SRoute -->|"打开工作流上下文"| DEntry

    classDef routing fill:#e8f4f8,stroke:#4a9aba;
    classDef entry fill:#f0f8e8,stroke:#6aaa4a;
    classDef artifact fill:#fdf5e8,stroke:#c8963a;
```

## 3. Layer A：入口文件约定

### 3.1 入口文件

1. `AGENTS.md`（现有 agents.md 标准；不变）。
2. `ENTERPRISE.md`（企业层入口文件）。
3. `SOLUTION.md`（解决方案层入口文件）。
4. `DOMAIN.md`（领域层入口文件）。

### 3.2 入口文件规则

1. `AGENTS.md` 仍然是仓库本地行为契约。
2. 当某一层级在仓库中存在时，对应层级的入口文件 SHOULD 存在。
3. 入口文件 SHOULD 保持简洁，并链接到规范化的机器工件，而不是复制易变数据。这一点在目录由生成流程产生时尤其重要：入口文件应该链接该工件，而不是复制其内容。
4. 上游入口链接 MUST 是确定性的、显式标明层级的：当企业层存在时，`SOLUTION.md` MUST 包含到 `ENTERPRISE.md` 的链接；当企业层存在时，`DOMAIN.md` MUST 包含到 `ENTERPRISE.md` 的链接。`DOMAIN.md` MUST NOT 要求通过 `SOLUTION.md` 进行上游导航，因为解决方案到领域的关联是多对多关系，并且会随时间变化；这些关联应属于路由目录和交接工件，而不是 Markdown 的父子结构。
5. 当路由目录存在时，下游目标信息 MUST 维护在规范 YAML 目录（`initiatives.yml`、`domain-workstreams.yml`、`implementation-catalog.yml`）中。入口文件 MAY 包含轻量级导航链接，但 SHOULD 避免复制详尽的下游映射，以防漂移。
6. 如果不存在上游层级，Parent 部分 MUST 写明 `Not applicable`。
7. Agent MUST 从 `AGENTS.md` 开始。`AGENTS.md` MUST 指示 agent 始终读取当前仓库的层级入口文件（`ENTERPRISE.md`、`SOLUTION.md` 或 `DOMAIN.md`），以获取架构上下文和导航信息。规范的指令形式为：`Always read <LEVEL>.md`。

实现参考：

1. AGENTS 交接模板：`templates/AGENTS.ea.md.template`、`templates/AGENTS.sa.md.template`、`templates/AGENTS.da.md.template`。
2. 层级入口模板：`templates/ENTERPRISE.md.template`、`templates/SOLUTION.md.template`、`templates/DOMAIN.md.template`。
3. 端到端示例：`examples/profile-a/`、`examples/profile-b/`、`examples/profile-c/`。

### 3.3 Parent 链接格式

允许的父级链接形式：

1. 指向父级入口文件的绝对 HTTPS URL。
2. 当父级位于同一仓库时，使用仓库相对路径。
3. 稳定的仓库标识符加路径（当 URL 在运行时解析时）。
4. Parent 部分 SHOULD 按层级标注上游链接（例如 `ENTERPRISE`）。

标识符说明：

1. 稳定的仓库标识符 SHOULD 带有提供方限定且持久（例如 `github:example-org/ea-repo`）。
2. 父级引用示例：`github:example-org/ea-repo#/ENTERPRISE.md`。

### 3.4 最小入口文件示例

#### ENTERPRISE.md（最小示例）

```markdown
# ENTERPRISE

Purpose: Enterprise portfolio entrypoint.

## Read First
1. This file - enterprise context and navigation

## Parent
Not applicable

## Canonical Artifacts
- initiatives.yml
- domain-registry.yml
```

#### SOLUTION.md（最小示例）

```markdown
# SOLUTION

Purpose: Solution architecture entrypoint.

## Read First
1. This file - solution context and navigation

## Parent
- [ENTERPRISE](https://github.com/example/ea-repo/blob/main/ENTERPRISE.md)

## Canonical Artifacts
- domain-workstreams.yml
- solution-index.yml
```

#### DOMAIN.md（最小示例）

```markdown
# DOMAIN

Purpose: Domain architecture entrypoint.

## Read First
1. This file - domain context and navigation

## Parent
- [ENTERPRISE](https://github.com/example/ea-repo/blob/main/ENTERPRISE.md)

## Canonical Artifacts
- implementation-catalog.yml
```

## 4. 引导发现（路由配置档位的核心）

对于路由配置档位（Profile B/C），实现 MUST 至少提供一种确定性的引导发现机制，用于解析组织中存在的最高层级：

1. 显式启动参数。
2. 环境变量。
3. 约定俗成的发现端点。

引导目标是路由链中最高层级的仓库（三层组织是企业仓库，两层组织是解决方案仓库）。实现 MUST 说明哪一种机制是权威机制。

## 5. Layer B：路由目录规范

路径放置是有意保持实现自定义的。
本标准定义文件名和语义，而不是固定目录结构。

### 5.1 规范目录集合

| Catalog | Level | Selector | Resolves |
|---|---|---|---|
| `initiatives.yml` | Enterprise | `initiative_id` | `solution_repo_url` + `solution_entrypoint` |
| `domain-workstreams.yml` | Solution | `workstream_id` | 工作流上下文（见第 5.3 节） |
| `implementation-catalog.yml` | Domain | `work_item_id` 或 `api_id` | 实现目标/路径 |

目录解析是按边界定义的。本规范不保证选择器会跨边界自动传递；调用方必须独立拥有或获取下一个边界所需的选择器。实现 MAY 定义跨边界传递选择器的交接机制，但这些机制属于实现自定义。

格式规则：

1. YAML 是本提案中所有目录的规范格式。
2. JSON 仅允许作为与 schema 等价的兼容性投影（字段相同、语义相同）。
3. 当同一目录同时存在 YAML 和 JSON 形式时，YAML 具有权威性。
4. 支持 JSON 的消费者在 YAML 与 JSON 内容不一致时 MUST 失败即关闭。

作者说明：路由目录通常是生成工件，由摄取流水线从更丰富的源（例如 `initiative-pipeline.yml`）中过滤并生成选择器清单。正因为它们是生成的，所以必须与人工编写的入口文件（`ENTERPRISE.md`）分离。若将它们内联进入口文件，要么会使入口文件也变成生成文件（违背其作为稳定导航指南的角色），要么会产生一个人工维护的副本，并最终与流水线源发生漂移。

### 5.2 版本契约

目录头 MUST 符合该目录类型的规范 schema：

1. `initiatives.yml` MUST 包含 `version`。
2. `domain-workstreams.yml` MUST 包含 `version`。
3. `implementation-catalog.yml` MUST 包含 `spec_name` 和 `spec_version`。

版本规则：

1. `MAJOR`：破坏性变更。
2. `MINOR`：向后兼容的新增。
3. `PATCH`：向后兼容的澄清/修复。

运行时行为：

1. 消费者在遇到未知 `MAJOR` 版本时 MUST 失败即关闭。
2. 生产者在增加 `MAJOR` 版本时 MUST 提供迁移说明。

### 5.3 最小字段集

跨仓库目标字段：

1. `initiatives.yml` 的条目 MUST 同时包含 `solution_repo_url` 和 `solution_entrypoint`（例如 `SOLUTION.md`）。
2. 当 `domain-registry.yml` 条目包含 `domain_repo_url` 时，MUST 同时包含 `domain_entrypoint`（例如 `DOMAIN.md`）。
3. `domain-workstreams.yml` 条目 MUST 包含 `domain_id`、`workstream_entrypoint` 和 `workstream_git_ref`。
   当企业层存在（即存在 `initiatives.yml`）时，条目还 MUST 包含 `initiative_id`，以将工作流关联到其来源 initiative。当企业层不存在（第 12.2 节定义的两层拓扑）时，`initiative_id` MAY 省略。
   当 `initiative_id` 存在时，它可用于将工作流与 initiative 做关联，但不会创建一个规范性的路由步骤；`domain-workstreams.yml` 的规范选择器仍然是 `workstream_id`。
   `domain_id` 是稳定的目标标识，即使 `workstream_repo_url` 已足以进行直接运行时解析，它仍然是必需字段。
4. `domain-workstreams.yml` 条目 MUST 包含 `workstream_repo_url`，除非运行时能够访问一个权威的 `domain-registry.yml`，可将 `domain_id` 解析为稳定的领域仓库。
5. 在工作流上下文尚未实体化时，`workstream_entrypoint` MAY 为 `null`。对于任何可路由的工作流状态，`workstream_entrypoint` MUST 为非空。
6. `domain-workstreams.yml` 条目 MAY 包含 `workstream_path`，用于标识承载该工作流工件的仓库相对目录。
7. `implementation-catalog.yml` 条目 MAY 包含 `workstream_id` 和 `initiative_id`，以支持从实现工件向上追溯到工作流和 initiative。这些字段已标准化，但不是必需字段；若实现包含它们，MUST 与对应的 `domain-workstreams.yml` 和 `initiatives.yml` 条目保持一致。

#### initiatives.yml

```yaml
version: "1.0"
initiatives:
  - initiative_id: init-example
    solution_repo_url: https://github.com/example/solution-repo
    solution_entrypoint: SOLUTION.md
    status: active
```

#### domain-workstreams.yml

```yaml
version: "1.0"
workstreams:
  - workstream_id: ws-init-example-order
    initiative_id: init-example
    domain_id: order
    workstream_entrypoint: inputs/workstreams/ws-init-example-order/WORKSTREAM.md
    workstream_git_ref: feature/ws-init-example-order
    workstream_repo_url: https://github.com/example/order-domain-repo
    workstream_path: inputs/workstreams/ws-init-example-order/
    status: active
```

#### implementation-catalog.yml

```yaml
spec_name: multi-scale-routing
spec_version: "1.0.0"
work_items:
  - work_item_id: job-order-api-001
    api_id: ORDER_API
    repo_path: src/order
    status: active
    # 可选的上游谱系字段（见第 5.3 节规则 7）：
    # workstream_id: ws-init-example-order
    # initiative_id: init-example
```

### 5.4 状态词汇表（规范性）

允许的值：

1. `active`
2. `approved`
3. `ready`
4. `in_progress`
5. `paused`
6. `completed`
7. `archived`
8. `deprecated`

语义：

1. `active`：可路由。
2. `approved`：默认不可路由；工作已获批准但尚未开始。
3. `ready`：默认不可路由；工作已准备好开始。
4. `in_progress`：可路由；工作正在进行中。
5. `paused`：默认不可路由；可由策略决定是否恢复。
6. `completed`：只读历史状态。
7. `archived`：历史状态，通常不出现在活动选择器视图中。
8. `deprecated`：只读墓碑状态；绝不能用于写操作路由。

默认可路由状态：`active`、`in_progress`。

实现 MAY 通过显式配置将 `approved` 和/或 `ready` 也纳入可路由集合。若实现扩展了可路由集合，MUST 在配置或运行时元数据中声明生效的可路由状态集合，以便消费者无需依赖实现私有知识即可判断当前路由掩码。

### 5.5 路由策略

1. 对缺失选择器 ID 失败即关闭（`ERR_SELECTOR_MISSING`）。
2. 对歧义选择器 ID 失败即关闭（`ERR_SELECTOR_AMBIGUOUS`）。
3. 默认对不可路由状态失败即关闭（`ERR_SELECTOR_NOT_ROUTABLE`）。
4. 实现 MUST NOT 回退到仓库名启发式、关键字搜索或其他推断上下文。

无论是否实现了可选的机器访问契约（第 5.7 节），这些错误语义对所有路由行为都是规范性的。实现如何暴露这些错误（结构化错误对象、异常、日志事件）由实现自行决定；必须“失败即关闭”的行为要求不变。

### 5.6 选择器唯一性

1. 每个选择器字段 MUST 在其目录内部独立唯一。
2. 当一个目录支持多个选择器字段（例如 `implementation-catalog.yml` 中的 `work_item_id` 和 `api_id`）时，一个选择器命名空间中的值 MUST NOT 与另一个命名空间中的值冲突。
3. 实现 MUST 在存在重复选择器值时失败即关闭。

### 5.7 可选的机器访问契约

实现 MAY 在规范路由目录之上暴露机器访问接口。

本节只定义查询语义。传输方式、调用语法、认证方式、编程语言和部署模型均由实现自行定义。

契约规则：

1. 必需操作：
   1. `resolve`：根据规范选择器类型和值返回单个条目。
   2. `list`：返回某一目录中的条目，并可按精确状态进行过滤。
   3. `validate`：根据第 7 节中的最小检查项报告目录完整性。
2. 输入契约：
   1. `resolve` 输入 MUST 包含规范选择器类型和选择器值。
   2. `list` 输入 MAY 包含目录标识符和精确状态过滤条件。
   3. 实现 MUST NOT 依赖模糊搜索、关键字搜索或推断式选择器别名来完成核心解析行为。
3. 输出契约：
   1. `resolve` 响应 MUST 包含第 5.3 节中该目录类型要求的规范字段。
   2. `list` 响应 MUST 为每个返回条目保留其规范语义。
   3. 在规范字段保持存在且未被修改的前提下，实现 MAY 添加元数据或扩展字段。
4. 错误契约：
   1. 结构化错误 MUST 包含 `error_code`。
   2. 实现 MUST 至少支持 `ERR_SELECTOR_MISSING`、`ERR_SELECTOR_AMBIGUOUS` 和 `ERR_SELECTOR_NOT_ROUTABLE`。
   3. 在适用时，实现 MAY 还会发出第 11 节中的其他错误码。
5. 冲突规则：
   1. 规范 YAML 始终是权威来源。
   2. 实现 MUST NOT 返回与权威 YAML 内容在规范语义上相冲突的结果。
6. 新鲜度规则：
   1. 实现 MUST 要么返回与当前权威 YAML 修订一致的结果，要么显式声明该响应所代表的修订版本或陈旧边界。

配套指导与示例实现模式见 `reference/machine-access-contract.md`。

## 6. 兼容性与别名策略

规范键名：

1. `workstreams[]` + `workstream_id`
2. `work_items[]` + `work_item_id`

迁移策略：

1. 写入方 MUST 输出规范键名。
2. 读取方 SHOULD 强制使用规范键名，以获得确定性行为。
3. 旧别名不属于本草案基线范围。

## 7. 目录健康校验（建议纳入 CI）

建议的 CI 检查项：

1. 校验 schema 和必需字段。
2. 校验选择器唯一性（见第 5.6 节）。
3. 校验状态策略合规性。
4. 对照第 5.2 节校验目录版本兼容性。
5. 校验被引用的仓库 URL 是否可被 CI 身份访问（或通过等效的提供方 API 校验）。
6. 在运行时之前标记陈旧或不可访问的路由目标。

## 8. 归属模型

| Artifact | 推荐所有者 | 主要用途 |
|---|---|---|
| `AGENTS.md` | 仓库所有者 | 仓库本地 agent 行为契约 |
| `ENTERPRISE.md` | EA | 企业上下文入口 |
| `SOLUTION.md` | SA | 解决方案上下文入口 |
| `DOMAIN.md` | DA | 领域上下文入口 |
| `initiatives.yml` | EA/PMO | 企业 -> 解决方案路由 |
| `domain-workstreams.yml` | SA | 解决方案 -> 领域路由 |
| `implementation-catalog.yml` | DA | 领域 -> 实现路由 |
| 治理状态工件 | 治理团队 + 各层所有者 | 阶段闸门与进度 |

覆盖规则：

1. 如果多个角色在同一团队/仓库中合并承担，MUST 在相关入口文件中显式声明归属。

## 9. 一致性配置档位

### Profile A：仅入口文件

必需项：

1. `AGENTS.md`
2. 至少一个适用的层级入口文件（`ENTERPRISE.md`、`SOLUTION.md` 或 `DOMAIN.md`）

### Profile B：路由自动化

必需项：

1. Profile A
2. 针对组织中存在的最高层级的确定性引导发现机制
3. 为组织中实际存在的每个层级边界提供路由目录：
   1. 企业 -> 解决方案（当企业层和解决方案层都存在时）：`initiatives.yml`
   2. 解决方案 -> 领域（当解决方案层和领域层都存在时）：`domain-workstreams.yml`
   3. 领域 -> 实现（当存在选择器驱动的领域到实现路由边界时）：`implementation-catalog.yml`

对于两层组织（例如只有 Solution + Domain），只要使用 `domain-workstreams.yml` 支持解决方案到领域的工作流路由，就满足 Profile B。只有当范围中存在选择器驱动的领域到实现路由时，才需要 `implementation-catalog.yml`。不存在的边界不要求对应目录。

Profile B 解析规则：

1. 当运行时没有权威的 `domain-registry.yml` 可用时，`domain-workstreams.yml` MUST 对运行时解析自给自足。
2. 在这种情况下，每个工作流条目 MUST 包含 `workstream_repo_url`。
3. 当运行时可访问权威 `domain-registry.yml` 时，`workstream_repo_url` MAY 省略，此时通过 `domain_id` 经由该注册表解析。

### Profile C：受治理的企业级配置

必需项：

1. Profile B
2. 领域治理注册表（例如 `domain-registry.yml`）
   1. 当某个领域条目包含 `domain_repo_url` 时，MUST 包含 `domain_entrypoint`
3. 解决方案范围/索引清单（例如 `solution-index.yml`）
4. 治理状态工件，至少包含以下字段：
   1. `spec_name`
   2. `spec_version`
   3. `layers`（以级联层名称为键的字典，每层包含 `status`）

治理层状态值与第 5.4 节中的路由状态词汇表是分离的。允许的治理层状态值：`not_started`、`in_progress`、`proposed`、`approved`、`blocked`、`rejected`。

最小示例：

```yaml
spec_name: governance-state
spec_version: "1.0.0"
layers:
  requirements:
    status: approved
    approved_by: product-owner
    approved_at: "2026-02-28T10:00:00Z"
  solution_architecture:
    status: in_progress
  domain_architecture:
    status: not_started
```

## 10. 冲突解决与优先级

按关注点的优先级：

1. Agent 行为/安全约束：`AGENTS.md` 优先。
2. 路由与目标解析：路由目录优先。
3. 叙述性/上下文说明：层级入口文件（`ENTERPRISE.md` / `SOLUTION.md` / `DOMAIN.md`）优先。

如果两个工件在同一关注点域内发生冲突：

1. 运行时 MUST 失败即关闭。
2. 运行时 MUST 发出结构化冲突错误事件。

## 11. 可观测性与错误模型（配套指导，非规范性）

最小结构化失败记录 SHOULD 包含：

1. `timestamp`
2. `level`（enterprise / solution / domain）
3. `selector_type`
4. `selector_id`
5. `artifact_path`
6. `error_code`
7. `message`

建议错误码：

1. `ERR_SELECTOR_MISSING`
2. `ERR_SELECTOR_AMBIGUOUS`
3. `ERR_SELECTOR_NOT_ROUTABLE`
4. `ERR_TARGET_UNREACHABLE`
5. `ERR_ACCESS_DENIED`
6. `ERR_PARENT_LINK_MISSING`
7. `ERR_CONFLICT`

## 12. 部分采用模式

### 12.1 单层仓库

1. 使用 `AGENTS.md` 加一个层级入口文件。
2. 路由目录是可选的。

### 12.2 两层结构（Solution + Domain）

1. 使用 `SOLUTION.md` 和 `DOMAIN.md`。
2. 只对实际存在的边界使用路由目录。
3. `ENTERPRISE.md` 和 `initiatives.yml` 是可选的。
4. 在这种拓扑中，`DOMAIN.md` 不需要 `SOLUTION.md` 作为父级链接。解决方案到领域的关系仍然是多对多的，应从 `domain-workstreams.yml` 或等效交接工件中发现。

### 12.3 三层结构（Enterprise + Solution + Domain）

1. 在全部三个层级边界上使用完整 Layer A + Layer B，以实现逐边界的确定性路由。

## 13. 发现与遍历

自顶向下的逐边界路由序列（每一步都要求调用方持有该边界所需的选择器）：

1. `initiative_id` -> `initiatives.yml` -> 解决方案仓库 + `solution_entrypoint`
2. `workstream_id` -> `domain-workstreams.yml` -> `domain_id` + `workstream_entrypoint` + `workstream_git_ref`
3. 工作流目标的仓库解析：
   1. 若 `domain-workstreams.yml` 中存在 `workstream_repo_url`，则使用它
   2. 否则解析 `domain_id` -> 权威 `domain-registry.yml` -> `domain_repo_url`
4. `work_item_id` / `api_id` -> `implementation-catalog.yml` -> 实现目标（当存在选择器驱动的领域到实现路由边界时）

自底向上的发现：

1. 当企业层存在时，领域 agent 通过 `DOMAIN.md` 中的上游链接读取 `ENTERPRISE.md`。
2. 如果企业层不存在，`DOMAIN.md` MAY 使用 `Parent: Not applicable`；解决方案关联仍应通过 `domain-workstreams.yml` 或等效交接工件恢复，而不是通过 Markdown 父级链接。
3. 当企业层存在时，解决方案 agent 通过 `SOLUTION.md` 的父级链接读取 `ENTERPRISE.md`。
4. 当这些 ID 存在于目录条目中时，agent MAY 使用共享 ID（`initiative_id`、`workstream_id`、`domain_id`）进行部分谱系重建。核心目录最小字段集并不保证从实现工件到业务 initiative 的端到端谱系（见第 5.3 节）。

## 14. 配套指导：Agent 上下文工程（非规范性）

建议的 harness / 上下文实践：

1. 将入口文件视为地图，而不是百科全书（见第 2 节指导原则）。
2. 将详细知识保存在被链接的工件/文档中。
3. 在 CI 中加入机械化的文档新鲜度检查。

## 15. 与 agents.md 的兼容性

本提案是增量性的：

1. `AGENTS.md` 仍然是基础标准，并未被替换。
2. `ENTERPRISE.md` / `SOLUTION.md` / `DOMAIN.md` 扩展了多层级仓库的导航能力。
3. 在路由配置档位之外，路由目录是可选的。

## 16. 参考布局（示意）

```text
<enterprise-repo>/
  AGENTS.md
  ENTERPRISE.md
  initiatives.yml
  domain-registry.yml

<solution-repo>/
  AGENTS.md
  SOLUTION.md
  domain-workstreams.yml
  solution-index.yml

<domain-repo>/
  AGENTS.md
  DOMAIN.md
  implementation-catalog.yml
  governance-state.yml
```

## 17. 参考实现映射（非规范性）

实现 MAY 将目录映射到架构目录中，例如：

1. `architecture/portfolio/initiatives.yml`
2. `architecture/solution/domain-workstreams.yml`
3. `implementation-catalog.yml`（可选附带 `implementation-catalog.json` 兼容投影）

实现 MAY 使用环境变量引导机制（例如 `OPENARCHITECT_ROOT_REPO_URL`）作为解析最高层级的具体引导机制。

## 18. 下一步

作为扩展提案提交：

1. 核心扩展：多尺度入口文件约定。
2. 可选扩展：路由目录规范。
3. 配套扩展：schema 一致性档位与迁移指导。
4. 配套指导：harness / 上下文工程实践。
