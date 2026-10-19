# 板塊恢復逐項紀錄：01 基準排查

使用者要求：每處理一項立即上傳，遇阻礙優先記錄。日期：2026-10-20 台北。

狀態：進行中；尚未恢復行情，未部署網站、未合併 PR。

已完成：
- 重新讀 Claude 最新交接 blob `83b338bb23b6a94a5265ee19bbc7c522f1966eae`。
- main 採集器為 Yahoo chart 日線，12 代號；原始流程跳過 null close，但沒有保存被跳過日期，也沒有要求最後完成交易日。
- main 排程僅 UTC 23:35 週一至週五；最近 US Sector History run `38991007493` 為 10/17 01:28Z，success，但發布內容只到10/15，success 不代表最新行情可用。
- PR #6 已加最後交易日檢查與補抓，CI 通過但尚未合併；先以不修改正式程式的資料重抓與驗證路徑排查。

遇到的限制：
- GitHub fetch 以 workflow 檔名帶 query 的 runs URL 回 `INVALID_ARGUMENT`；改用 `/actions/runs` 成功，並非行情來源故障。
- 連接器有讀取／重跑失敗 job 的工具，未找到 workflow_dispatch 工具；目前未以其他帳號或存取權繞過。
- 本機 SPY 真實來源探測正在執行；完成後立即補下一份紀錄。未拿舊 close 補新日期。

下一步：讀回 SPY 原始回應，判定缺日是來源 null bar、延遲、日期轉換還是抓取失敗；所有抓取保留 URL、時間、HTTP 狀態、SHA-256。