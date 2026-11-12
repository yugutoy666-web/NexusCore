# NexusCore

**基于文件系统图论与算力当量的去中心化智能体架构**
*A graph-theoretic, filesystem-native, compute-equivalent-metered agent architecture.*

> 状态：早期可运行原型（Early prototype, running daily on real hardware）
> 许可：MIT · 语言：Python / Shell · 依赖：零（核心模块仅用标准库；SVD 可选 numpy）

---

## MANIFESTO

> **不要尝试训练一个 100 亿参数的超级大脑，去组装 3 个不同物理介质的计算节点。**
> **大模型是廉价的脑子，而跨设备组装、因果图论和异层免疫，才是智能体真正的身体。**

**This is not a chatbot. This is a cross-medium agent OS.**
We are not building a bigger model — we are building a body that any model can wear.

## 为什么做这个

大多数智能体框架把「记忆、工具、身体」外包给向量库和云服务。我们反过来：

- **文件系统就是身体**：状态写在文件名上，`ls` 是查询接口，`mv` 是状态转换。
- **世界就是记忆**：内容寻址 + 锚点/接手协议，进程重启后身份不丢。
- **模型只是可替换的脑**：路由层把无需模型的问题（算术/事实/检索/状态）用确定性算子解掉，零 Token。

这套系统在一个真实环境里跑：手机（世界根）+ Linux 常开主机（镜像/调度）+ Windows GPU 机（闲置算力）+ 一块人类数据盘。
100k+ 实体、跨设备统一文件系统、自愈免疫链，全部是实测数字，不是 PPT。

---

## 四大核心卖点

### 1. 零 Token 本地寻址（WordNet Router）

把世界里所有**文件/目录名切成词元**，建词元共现网络（PPMI + SVD → 64 维嵌入），
可以用一句话直接定位文件，不调模型、不花 Token：

```
query: "五公理 体检"
→ hit: 0.引擎/律/体检@五公理.py   (exact file)
query: "回源 镜像 人的盘"
→ top candidate: 0.引擎/决策/_∅_回源   (RRF fusion, multi-token)
```

实测规模：112,231 条名序列 → 15,188 个有效词元 → 2,540 词 × 64 维嵌入（1.2MB）。
**词元=地址**：生成的每个 token 都能落成真实路径，路径类幻觉在结构上不可能。

### 2. 算力当量防炸引擎（Compute-Equivalent Area Gate）

不用字节数，而用「算力当量」给文件定价：

```
Area = 编码协议系数 × 容量        (字节当量；系数：文本1 / 代码5 / 图片20 / 视频100 / 模型200)
```

实测：108,386 文件 / 10,252 目录 / 物理 7.28 GB → **面积 314.52 GB当量（43.22×）**。
读取前先算面积，超过阈值（默认 1000 KB当量）**强制流式读取**：

```
world.tar.gz  面积 27,565,997 KB当量 → streaming, 539 blocks, sha256 verified
```

诚实边界（重要）：面积 = *算力当量/生产质量*，**不是**信息熵。
真实信息密度用压缩率实测（媒体≈0.95–1.0 / 文本 0.5–0.85 / 日志 0.125），双指标并列。
面积只用于：读取门、备份/迁移预算、可视化排序。**不可**用于判断"重要性"。

### 3. 文件货币化流转（Crypto-Barter Gateway）

应用 = 黑盒宏节点，只登记 `inputs`（吃什么格式）与 `outputs`（拉什么格式），不透视内部依赖。
应用之间不直接对话，只交换**文件货币**；网关负责：拦截 → 打面值卡 → 入库 → 记账 → 防篡改验证。

```
$ nexuscore-gateway settle downloader https://example.com
[gateway] input currency: URL
[gateway] black-box app: downloader (curl) working…
[gateway] intercepted: 示例站@…html  577 B
[gateway] face value: 1,731 byte-equivalent (coeff 3.0) · entropy 0.676
[gateway] stored: <world>/currencies/ · ledger: currencies.jsonl
```

实测三笔结算，其中一笔当场抓出「假 PNG」：URL 声称 PNG、实际返回 HTML 15,770B
→ 网关按 URL 扩展名定价失真 → v0.2 已规划**魔数嗅探**按内容定币种。

### 4. 外部双生免疫（Dual External Immunity）

「监控与被监控同层 = 没有监控」：手机侧的免疫脚本会跟细胞一起被系统清洗，
所以免疫系统必须跑在**另一个常开节点**上：

```
常开主机 (Linux, cron every 60s)
  ├─ wireless adb → 手机: 读心跳文件(120s 阈值) + /proc/net/tcp 端口(3280/3296/8767)
  ├─ 缺失即除颤: adb shell 执行 rescue.sh (重启核心进程 + 复位服务)
  ├─ 癌变扫描: 只杀"常驻细胞特征"进程；系统/用户 app/自身帮手禁止误杀
  ├─ ssh → Windows GPU 机: 受限壳拒绝 tasklist → 走 python 内部枚举
  └─ 每杀必记: immunity ledger (谁杀/为什么/后果)
```

实测：心跳探针 23s ✓ / 无癌变 ✓ / ROG 在线 ✓；链路四 bug（ps 截断、mksh /dev/tcp 误测、
免疫误杀自身帮手、心跳变量名错）全部在真实演练中暴露并修复——**免疫系统是撞出来的**。

---

## 架构总览

```
L0 Ontology        Node/Label · Edge/Path · Entity/Subgraph · App/Collection · Agent/Process
L1 Positions       多台异构设备（手机 / Linux 主机 / Windows GPU / 人类数据盘），身份=硬件指纹
L2 World           文件系统即记忆；状态在文件名上；内容寻址 + 锚点分层
L3 Perception      器官 app：耳/口/眼/手；WebDAV/HTTP 本地通道；截图/朗读/通知
L4 Mind            白盒路由（零 Token 算子）→ 免费模型池 → 付费兜底；一行 JSON 工具协议
L5 Entities        App_Model 黑盒宏节点：inputs/outputs/env/runtime_metrics/status + 探针
L6 Metering        算力当量面积 + 熵密度；读取门；货币面值卡
L7 Transport       文件货币网关：拦截/定价/入库/账本/防篡改
L8 Immunity        外部双生免疫：心跳+端口双判据、除颤、癌变清理、免疫账本
L9 Federation      跨设备统一文件系统（rclone combine → FUSE），一个 POSIX 根访问所有设备
```

详见 [ARCHITECTURE.md](ARCHITECTURE.md)。

---

## 快速开始（单机最小闭环）

```bash
git clone <repo> NexusCore && cd NexusCore

# 1) 给世界建词元网络（零依赖；SVD 可选 numpy 加速）
python3 src/wordnet.py build --root /path/to/world --out ./index
python3 src/wordnet.py query --index ./index --q "五公理 体检"

# 2) 算力当量体检 + 防炸读取门
python3 src/area.py report --root /path/to/world
python3 src/area.py read --file big.bin --limit-kb 1000

# 3) 应用黑盒模型 + 调度匹配
python3 src/app_model.py gen --spec apps.yaml
python3 src/app_model.py match --need "read a huge file without blowing memory"

# 4) 货币网关（示例：任意命令行应用做黑盒）
python3 src/gateway.py settle --app downloader --url https://example.com --store ./currencies

# 5) 外部免疫（需一台常开主机 + 可 adb/ssh 达成的对端；无对端时只读自检）
python3 src/immune.py tick --config immune.json
```

> 安全提醒：免疫与网关会执行命令/kill 进程。请先读 `docs/SECURITY.md`，按白名单配置，切勿直接用于生产。

---

## 证据（真实运行报告）

- [docs/REPORT-AREA.md](docs/REPORT-AREA.md) — 算力当量体检：108,386 文件 / 7.28GB / 314.52GB当量 / 流式 539 块校验
- [docs/REPORT-CURRENCY.md](docs/REPORT-CURRENCY.md) — 货币结算三笔 + 假 PNG 拦截实录
- [docs/REPORT-IMMUNITY.md](docs/REPORT-IMMUNITY.md) — 外部免疫链路实测 + 四个真实 bug 的修复记录
- [ARCHITECTURE.md](ARCHITECTURE.md) — 分层架构（L0–L9）
- [docs/PHILOSOPHY.md](docs/PHILOSOPHY.md) — 组装大于单体 · 最终架构图 · 智联网操作系统判据
- [docs/PRIVACY.md](docs/PRIVACY.md) — **感知同意（产品级隐私机制）**：默认关闭 · 三级授权 · 指示器 · 数据不落盘

---

## 与现有方案的区别

| 维度 | 常见向量库/框架 | NexusCore |
|---|---|---|
| 记忆 | 向量嵌入 + 云数据库 | 文件系统 + 名称寻址 + 锚点分层 |
| 工具 | JSON schema 工具调用 | 黑盒 App 模型（输入/输出规则） |
| 计费 | token 账单 | 算力当量面值（本地零 Token 算子先行） |
| 可靠性 | 单进程自愈 | 跨设备外部双生免疫（异层监控） |
| 多设备 | 主从复制 | 统一 POSIX 根（FUSE 联邦） |

---

## Roadmap

- [x] 词元网络寻址（PPMI + SVD）
- [x] 算力当量读取门 + 熵密度双指标
- [x] 文件货币网关（面值卡/账本/验真）
- [x] 外部双生免疫（心跳+端口/除颤/癌变清理）
- [ ] 魔数嗅探（按内容定币种）
- [ ] App_Model 自动生成（从运行痕迹反推规则）
- [ ] 微权重本地模型（词元级 tiny transformer，命名/分类/路由）
- [ ] SMB/NFS 导出统一根给移动端

## License

MIT — 见 [LICENSE](LICENSE)。核心模块不含任何第三方代码；SVD 可选依赖 numpy。
