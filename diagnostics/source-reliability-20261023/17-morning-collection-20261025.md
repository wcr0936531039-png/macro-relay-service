# 2026-10-25 上午資料收集與匯入

## 時段與工具

- 使用當輪正式站 `official-data-tools`；collector／importer／source collector 的 SHA-256 與已驗證本機副本完全一致。
- 既有行情歷史 72 個交易日，因此使用 `--sessions 1 --market-only`。
- 上午總經使用 `macro_morning.py` 包裝；輸出明確回報 `morningCreditSkipped=true`。
- 匯入前確認 payload **不存在** `statistics.json`。

## 已保存並讀回

- 官方行情：最新日期 2026-10-22，1,947／1,985 檔，覆蓋 98.09%，錯誤 0；週末沒有建立假交易日。
- 官方總經序列：8 項，錯誤 0。
- 核心 CPI：BLS／FRED 均為 2026-09、338.896，passed。
- 公司／產業來源：8/8、123 筆、錯誤 0：
  - TWSE 5、TPEx 26、半導體 10、面板 10、能源 10、消費電子 5、鋼鐵 7、航空 50。
- 官方公告：政策／利率 3、能源供給 3、通膨／就業 1，錯誤 0。
- source-only 相同位元重匯後，`official-import-status` 獨立讀回 8 個來源及相同筆數。

## 信用資料

本輪上午沒有抓取或匯入信用統計。正式站目前顯示的 2026-10-22 信用列仍是 deferred 舊值；前一份診斷已確認 refresh 會重寫其 `verifiedAt`，因此不能把畫面時間當成新的官方信用快照。
