# 今日汇报 — 2026-08-19（America/Los_Angeles）

LinkedIn 美国 **Product Designer** 过去 24h 全量脚本扫描（无 computerUse）。

## 扫描结果

- **385** 张 unique 卡片（guest API 分页至 start=950 空页）
- Repost 启发式 cutoff：**jobId < 4442250693** → 96 条排除
- Gate 通过：**62**（含机械/Principal 误匹配；人工精选见 apply 表）
- 相对昨日 ~900 槽位：24h 窗口滚动，大量昨日链接已掉出

## 新推荐（优先直招）

1. **Yara AI** Product Designer — https://www.linkedin.com/jobs/view/product-designer-at-yara-ai-4456156617
2. **Moritz** Founding Product Designer — https://www.linkedin.com/jobs/view/founding-product-designer-at-moritz-4455980703
3. **Tilt** Senior Product Designer — https://www.linkedin.com/jobs/view/senior-product-designer-at-tilt-4455956709
4. **Rockstar** Product Designer — https://www.linkedin.com/jobs/view/product-designer-at-rockstar-4455431590
5. **DesignMeshAI** Product Designer Remote — https://www.linkedin.com/jobs/view/product-designer-remote-at-designmeshai-4455402823
6. **Whisker** UI/UX — https://www.linkedin.com/jobs/view/ui-ux-designer-at-whisker-4454918004
7. **1-800-FLOWERS** Product Designer — https://www.linkedin.com/jobs/view/product-designer-at-1-800-flowers-com-inc-4449952147
8. **Coca-Cola** Senior Product Designer II — https://www.linkedin.com/jobs/view/senior-product-designer-ii-at-the-coca-cola-company-4455985251

Amazon 6 岗（Shopping / Alexa / IMDb / AWS）— 投前确认签证。

## 已投（历史，今日 scan 未再出现或未重投）

OpenAI People Innovation · Babylist · IMC · Wispr Mobile · IDR · Chewy · Nuvo · LodgeLink · Hexaware · J.Hilburn

## 工具

- 新增 `job-hunt/helpers/linkedin_scan.py` — guest 分页 + JD 限速抓取 + gate + repost 过滤
- `gate.py` — Principal / 机械硬件岗 / 非 UX Product Engineer

完整列表：`runs/2026-08-19-linkedin-us-apply.md`
