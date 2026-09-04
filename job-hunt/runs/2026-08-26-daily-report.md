# 今日汇报 — 2026-08-26（America/Los_Angeles）

LinkedIn 美国 **Product Designer** 过去 24h 全量脚本扫描（无 computerUse）。

**原始搜索：**
https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=product%20designer&geoId=103644278&f_TPR=r86400&start=0

## 扫描结果

| Metric | Count |
| --- | --- |
| Unique cards | **95** |
| Gate pass | **14** |
| Gate skip | **58** |
| Repost (jobId < **4440078775**) | **23** |

今日库存继续偏少。完整跳过表 + 原因 + 原始 LinkedIn URL：
→ [`2026-08-26-linkedin-us-apply.md`](./2026-08-26-linkedin-us-apply.md)
→ catalog：[`2026-08-26-linkedin-catalog.json`](./2026-08-26-linkedin-catalog.json)

## 优先投递

| 公司 | 职位 | 链接 | 备注 |
| --- | --- | --- | --- |
| **Discord** | Product Designer, Growth | https://www.linkedin.com/jobs/view/product-designer-growth-at-discord-4448249558 | 3+ years |
| **Tailscale** | Product Designer (Growth) | https://www.linkedin.com/jobs/view/product-designer-growth-at-tailscale-4456947225 | 3–5+ years（下限 3） |
| **Morgan Stanley** | Associate, UX Designer – Equity Zen | https://www.linkedin.com/jobs/view/associate-ux-designer-%E2%80%93-equity-zen-at-morgan-stanley-4457643549 | 1–3 years |
| **AutoZone** | SR UX DESIGNER | https://www.linkedin.com/jobs/view/sr-ux-designer-at-autozone-4457668792 | |
| **Warp** | Design Engineer | https://www.linkedin.com/jobs/view/design-engineer-at-warp-4447570269 | 2+；偏 design-eng |
| **Neuralink** | UI Design Engineer | https://www.linkedin.com/jobs/view/ui-design-engineer-at-neuralink-4457494790 | 投前看签证/安全审查 |
| **Seven Stars** (Tavus) | Brand & Product Designer | https://www.linkedin.com/jobs/view/brand-product-designer-at-seven-stars-4459133218 | 含品牌；JD 写 Tavus |

## 次要

| 公司 | 职位 | 为何次要 |
| --- | --- | --- |
| Counterspell Games | Mobile Game UX Designer | 合同 / 游戏 |
| University of Michigan | UX Designer | 高校岗 |
| Miracle Software (W2) | Senior Product Designer | 中介 W2；3–5+ |
| Cloud and Things | UX/UI Engineer | 偏工程 |
| Technatomy | UI/UX Specialist | 需再看客户/清关 |

## 今日明确不投（抽样；全表见 apply 报告）

| 公司 | 原因 |
| --- | --- |
| Deloitte Delivery Consultant UX | **不赞助**（`without the need for employer sponsorship`） |
| GameChanger Senior PD New Ventures | **at least 5 years** |
| Replit Director of Product Design | Director / 过 senior |
| Retractable Technologies | 物理产品 Design Engineer |
| Stripe / Sydecar / Anori 等昨日优先 | 已滚出 24h |

## gate.py 本轮加固

- 捕获 `authorized to work … without the need for employer sponsorship`
- 捕获 `at least N years`（GameChanger 类）
