# DEMO-PACK · 跨介质智联网演示包（2026-11-13）

> 给发帖用：一张架构图 + 一条真实跨介质链路 + 可复现步骤。

## 一、架构图（已完成）
- `assets/architecture.svg` — NexusCore 跨物理介质智联网架构
  四个介质（Android 传感器 / Linux 常驻脑+免疫 / Windows GPU / 人类数据盘）
  四大能力（A11y 语义流 / 双生免疫 / 快慢脑 / 文件货币化）+ 图论寻址 + 统一根 FUSE
  底部三判据：角色可迁移 · 接口统一 · 故障可接管

## 二、跨介质链路（实验状态）
```
红米(Android) 传感器 ──a11y 文本树 :3299/树──▶ 戴尔(Linux) 快脑 :9300
                                                   │ 读取→增量→过滤（RAM）
                                                   ▼
红米(Android) 嘴 ◀── TTS :3299/说 ◀── 戴尔脑 :9300/答（跨介质回传）
```
**已验证**：
- 快脑@linux.py 在戴尔前台运行成功（打印 "快脑起于 :9300 · 纯内存"）
- 红米 a11y 语义流 :3299/树 输出真实节点（240 节点/137 有效，文本样例见 PRIVACY 前的实测）
- 红米 TTS :3299/说 与录音 :3299/录 均实测可用
**诚实缺口**（正在修）：
- 戴尔侧后台常驻被 SSH 会话回收（cron 托管已配置但尚未稳定拉起）→ 需要 systemd 单元或 cron 绝对路径 + 日志确认
- 全链路"传感器→戴尔脑→红米嘴"尚未在同一分钟内跑通（前台跑通、后台未持久）

## 三、复现步骤
```bash
# 1) 红米侧传感器（Android app 内，需开启无障碍）
curl http://<phone>:3299/树          # 语义节点流（授权级别内）
curl http://<phone>:3299/说?text=你好  # TTS
# 2) Linux 侧快脑（角色可迁移）
/usr/bin/python3 快脑@linux.py        # 监听 :9300，读 <phone>:3299/树
curl http://<linux>:9300/ping
curl http://<linux>:9300/语义全部     # 开启跨介质语义采集
curl http://<linux>:9300/语义         # 看戴尔脑读到的红米传感器数据
curl http://<linux>:9300/答?文本=...  # 戴尔脑用红米的嘴说话
```

## 四、发帖素材（来自真实代码与实测）
1. 架构图 assets/architecture.svg
2. 三份实测报告：REPORT-AREA（算力当量）/ REPORT-CURRENCY（货币结算+假PNG）/ REPORT-IMMUNITY（外部免疫除颤）
3. 语义流实测：前台 app 240 节点 / 137 语义节点（文本样例）
4. 双脑实测：34 条摄入 → 过滤保留 4 条（88% 丢弃），落盘只 4 行
5. 管理包：PHILOSOPHY 宣言 + PRIVACY 感知同意 + SECURITY 威胁模型
