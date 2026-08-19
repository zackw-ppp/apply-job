# Run — 2026-08-19 LinkedIn US product designer (past 24h)

Search:

https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=product%20designer&geoId=103644278&f_TPR=r86400&start=0

Script: `job-hunt/helpers/linkedin_scan.py` · Full gated JSON: `/tmp/li-2026-08-19-gated.json`

## Inventory

| Metric | Count |
| --- | --- |
| Unique cards (paginate to empty @ start=950) | **385** |
| JD fetched + gated | 385 |
| Repost heuristic (jobId < P25 **4442250693**) | 96 |
| Gate pass (before role curation) | 62 |
| Already applied / logged | 0 in fresh pass |

**Note:** 24h window rolled since yesterday — Tatari、Paramount+、Klaviyo、Fox、CurbWaste、Wayfair、Narmi、ServiceLink 等昨日链接多数已不在今日 24h 结果里。

## 推荐投递（新公司 / 今日 fresh，已去 repost + Principal + 机械岗）

### 优先 — 直招 / 产品岗明确

| 公司 | 职位 | Job ID | 链接 |
| --- | --- | --- | --- |
| **Yara AI** | Product Designer | 4456156617 | https://www.linkedin.com/jobs/view/product-designer-at-yara-ai-4456156617 |
| **Moritz** | Founding Product Designer | 4455980703 | https://www.linkedin.com/jobs/view/founding-product-designer-at-moritz-4455980703 |
| **Tilt** | Senior Product Designer | 4455956709 | https://www.linkedin.com/jobs/view/senior-product-designer-at-tilt-4455956709 |
| **Rockstar** | Product Designer | 4455431590 | https://www.linkedin.com/jobs/view/product-designer-at-rockstar-4455431590 |
| **DesignMeshAI** | Product Designer \| Remote | 4455402823 | https://www.linkedin.com/jobs/view/product-designer-remote-at-designmeshai-4455402823 |
| **Whisker** | UI/UX Designer | 4454918004 | https://www.linkedin.com/jobs/view/ui-ux-designer-at-whisker-4454918004 |
| **1-800-FLOWERS.COM** | Product Designer | 4449952147 | https://www.linkedin.com/jobs/view/product-designer-at-1-800-flowers-com-inc-4449952147 |
| **The Coca-Cola Company** | Senior Product Designer II | 4455985251 | https://www.linkedin.com/jobs/view/senior-product-designer-ii-at-the-coca-cola-company-4455985251 |
| **Patterson Companies** | Senior UX Designer | 4456106371 | https://www.linkedin.com/jobs/view/senior-ux-designer-at-patterson-companies-inc-4456106371 |
| **VeriiPro** | UI/UX Designer – AI-Powered Applications | 4456152418 | https://www.linkedin.com/jobs/view/ui-ux-designer-%E2%80%93-ai-powered-applications-at-veriipro-4456152418 |

### Amazon 簇 — 投前确认签证政策

| 职位 | Job ID | 链接 |
| --- | --- | --- |
| UX Designer, Shopping Design | 4455904216 | https://www.linkedin.com/jobs/view/ux-designer-shopping-design-at-amazon-4455904216 |
| UX Designer, Amazon Alexa for Shopping | 4455909379 | https://www.linkedin.com/jobs/view/ux-designer-amazon-alexa-for-shopping-at-amazon-4455909379 |
| UX Designer, Design Systems, PEX | 4455795912 | https://www.linkedin.com/jobs/view/ux-designer-design-systems-people-engagement-experience-pex-at-amazon-4455795912 |
| UX Designer, Alexa Enterprise | 4455911678 | https://www.linkedin.com/jobs/view/ux-designer-alexa-enterprise-and-emerging-design-at-amazon-4455911678 |
| UX Designer, IMDb | 4455918374 | https://www.linkedin.com/jobs/view/ux-designer-imdb-at-imdb-com-4455918374 |
| UX Designer, AI Services (AWS) | 4455921125 | https://www.linkedin.com/jobs/view/ux-designer-ai-services-at-amazon-web-services-aws-4455921125 |

### 猎头 / 合同 — 次要

ENFOS UX Designer · Dahl Consulting UX · TEKsystems UX · Insight Global UX · Experis UX · Entegee UX · TCS Figma UX — 见 gated JSON。

## 今日 gate 跳过（抽样）

| 公司 | 原因 |
| --- | --- |
| Reddit | Principal title |
| Walmart | Principal title |
| 大量 Mechanical/Hardware/PCB Design Engineer | 非数字产品 UX |
| Staff 标题（LinkedIn、Intuit、NPR 等） | Staff |
| Google 各岗 | Zack 规则 |
| Underdog / Sundayy / Ladders / Jobright | 聚合器 |
| State Farm / Epic / Deloitte 等 | 不赞助 |
| Wispr / Biorce / Crossing Hurdles | repost 或已投 |

## 仍待 Zack 手动

Allegis iCIMS · Target Workday · Radar Ashby · TeamViewer · Aaru（若 LinkedIn 未显示已投）

## gate.py 小改（本 run）

- 跳过 **Principal** 标题
- 扩展 **机械/硬件/PCB** 等非 UX 岗
- `Product Engineer`（非 design engineer）跳过
