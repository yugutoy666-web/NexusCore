# REPORT · Dual External Immunity（外部双生免疫实测）

> 「监控与被监控同层 = 没有监控」
> 手机侧的免疫脚本会跟细胞一起被系统清洗 → 免疫必须跑在另一台常开节点。
> 工具：`src/immune.py` + `rescue.sh`（本仓库）· 数据脱敏（主机名/IP 以占位符表示）

## 一、拓扑

```
常开主机 Host-A (Linux, systemd/cron)
  ├─ 无线 adb ──▶ Phone（World Root 所在）
  │    双判据：心跳文件新鲜度(>120s 除颤) + /proc/net/tcp 端口(3 个关键端口)
  │    除颤：adb shell 执行 rescue.sh（重启核心进程 + 幂等复位）
  │    癌变扫描：只杀"常驻细胞特征"进程；系统/用户 app/自身帮手禁杀
  ├─ ssh ──▶ Host-B (Windows GPU)
  │    受限 shell 拒绝 tasklist → 改由 Windows 侧 python 内部枚举（JSON 回传）
  └─ 每杀必记：immunity ledger (时间/对象/理由/后果)
```

## 二、实测结果

| 检查项 | 结果 |
|---|---|
| 心跳探针（心跳文件） | ✅ 23s（阈值 120s） |
| 癌变扫描 | ✅ 无癌变细胞（956 进程全扫） |
| 对端在线（Host-B） | ✅ 在线，可疑进程 0 |
| 端口判据 | ✅ 三个关键端口按 /proc/net/tcp 判定 |

## 三、真实演练暴露的四个 bug（这是免疫系统的价值证明）

1. **进程名截断**：`ps -o cmd` 只给 15 字符短名，看不出是不是循环脚本 → 改 `args` 全参数。
2. **错误的端口测法**：Android 的 mksh 不支持 `/dev/tcp`，用它测端口恒"关" → 改读 `/proc/net/tcp` 或用 socket。
3. **免疫误杀自身帮手**：扫描到命令行含「免疫」的辅助进程（自身包装器）→ 判为癌变 kill → 加禁杀标记（免疫/包装器/一次性脚本）。
4. **心跳文件不落盘**：写入用了未定义变量，异常被吞 → 变量修正后 `心跳.txt` 正常出现。

## 四、防误杀红线（写进规范）

```
宿主器官禁杀：system_server / systemui / 用户 app（com.tencent/com.deepseek/com.android/...）
自身帮手禁杀：含 免疫 / 包装器 / --once / sh -c 的进程
只杀常驻细胞：核/守护/服务进程的特征命令行 + 僵尸繁殖(>3) / RSS>800MB / CPU 持续>30%
每杀必账：谁杀 · 为什么 · 后果（防误杀无据）
```
