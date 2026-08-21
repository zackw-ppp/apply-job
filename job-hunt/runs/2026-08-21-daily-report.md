# 今日汇报 — 2026-08-21（America/Los_Angeles）

LinkedIn 美国 **Product Designer** 过去 24h 全量脚本扫描（无 computerUse）。

**原始搜索：**
https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=product%20designer&geoId=103644278&f_TPR=r86400&start=0

## 扫描结果

| Metric | Count |
| --- | --- |
| Unique cards | **291** |
| Gate pass | **35** |
| Gate skip | **184** |
| Repost (jobId < **4445064391**) | **72** |

完整表（含全部跳过原因 + 原始 LinkedIn URL）：
→ [`2026-08-21-linkedin-us-apply.md`](./2026-08-21-linkedin-us-apply.md)
→ catalog：[`2026-08-21-linkedin-catalog.json`](./2026-08-21-linkedin-catalog.json)

## 优先投递

| 公司 | 职位 | 链接 | 备注 |
| --- | --- | --- | --- |
| **Vercel** | Senior Product Designer, Growth | https://www.linkedin.com/jobs/view/senior-product-designer-growth-at-vercel-4447096809 | 未见 5+ / 不赞助 knockout |
| **Menlo Security** | Product Designer | https://www.linkedin.com/jobs/view/product-designer-at-menlo-security-inc-4457046625 | 4+ years |
| **FOX Direct to Consumer** | Product Designer II | https://www.linkedin.com/jobs/view/product-designer-ii-at-fox-direct-to-consumer-4447078575 | 2+ years |
| **Sony Music Entertainment** | Senior Product Designer | https://www.linkedin.com/jobs/view/senior-product-designer-at-sony-music-entertainment-4456283232 | EEO citizenship 文案 |
| **The Mortgage Office** | Product Designer | https://www.linkedin.com/jobs/view/product-designer-at-the-mortgage-office-4447278038 | 3+ years |
| **Haystack** | Senior Product Designer | https://www.linkedin.com/jobs/view/senior-product-designer-at-haystack-4457345085 | JD 较薄 |
| **GlobalLogic** | Product Designer UX/UI | https://www.linkedin.com/jobs/view/product-designer-ux-ui-irc302942-at-globallogic-4456036790 | 偏交付商 |

## 今日明确不投（抽样，全表见 apply 报告）

| 公司 | 原因 |
| --- | --- |
| TCP Software / Cognizant | **不赞助**（gate 已加固 `not able to sponsor`） |
| Paraform / InventWood / Ceno / Gusto Manager / BNY SVP | JD **5+ / 8+** 或 Manager/SVP |
| 大量 Mechanical / Design Engineer / Staff / Google / 聚合器 | 角色或规则跳过 |
| 昨日 Figma / Nextdoor / 7-Eleven 等 | 已滚出 24h 窗口 |

## gate.py 本轮加固

- 识别 `not able to sponsor` / `unable to sponsor` / `not able to offer … sponsorship`
- 识别区间下限 `5-8 years` / `5-10 years` 为 5+ knockout
- 收紧 “preferred” 误判（不再把 Preferred Qualifications 段里的 5+ 当成 soft）
