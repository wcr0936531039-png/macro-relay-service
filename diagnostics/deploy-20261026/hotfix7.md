# 2026-10-29 v245／第 2 項讀回
- 正式站 v245 已部署；v244 保留回滾。dist/index.html SHA-256：7a5fabb193d7c85b95079a98bc3f0b99f1fde252233937bd0bdb9d65a60cbd60。
- v245 patch SHA-256：4098543868c90113ca38feb75b3b18cb82e09272737e298735722faa30a7131d；build 成功；TZ=UTC npm test：53/53 pass。
- 8299 桌面個股區順序符合規格；未見「畫面呈現未完成」。
- 去重讀回未通過：收盤、均線、估值情境及 ROIC／CFO／FCF 仍重複出現在摘要／Gate；五檔對 v242 比較未完成（目前僅 8299 有行情，另四檔卡片尚未取得）。
- 手機版未驗證：目前瀏覽器介面不能設定 viewport，未以桌面畫面代替。
- v234 ① PASS：/api/macro-market 七個信用欄位均為最新交易日 2026-10-28。
- ② PARTIAL/FAIL：TWSE 10/28 報表「前日融資金額」為 623,386,833 仟元，與交接預期 623,386,860 相差 27 仟元；網站 10/28 值減日增量與官方數字相符，但 API 無獨立 10/27 final 歷史列。來源：https://www.twse.com.tw/exchangeReport/MI_MARGN?date=&response=html
- ③ PASS：七欄 verifiedAt 保留 2026-10-28T14:43:41.618Z；晨間 checkedAt 更新，captureDeferred=true。
- ④ PARTIAL：history 有 5/5 Gate audit、marketAndPreciousMetals=ok；直接讀回七欄為 snapshot/deferred，摘要無逐欄驗證，不能宣稱完全一致。
- 第 3 項待 v245 部署後首個 2026-10-29 22:30 巡檢完成，再補五檔摘要、模組讀回及貴金屬原文。
- 第 3 項已加入既有每日巡檢的一次性指示：首個 v245 部署後晚間巡檢完成後追加；排程時刻與啟用狀態未更動。


## 第 3 項：2026-10-29 22:30 晚間巡檢（一次性，已完成）
- run `f2bf6761-31cb-4640-b125-de52b46c9172`：POST 202；同 run status 200 推進至 23:01:18 completedAt；history 200 匹配，狀態 partial，Gate audit 5/5。
- 五檔 8299／5289／2404／5009／2330 均 `status=ok`、`refreshedThisRun=true`、`summaryScope=final_readback`；run 內最終直接讀回完成。8299/5289/2404/2330 audit=valuation_divergence，5009=degraded。
- 差異：五檔 `stepStatus` 在完成快照仍為 `pending`，與 `status=ok` 不一致；照實保留，不宣稱完全一致。
- expandedMacro=ok 12/12、marketAndPreciousMetals=ok 36/36、usIndices=ok 3/3；三者 `refreshState`、`finalizeWaits` 在 final_readback 均未提供（null），沒有造值。
- 黃金現貨參考價（XAU/USD）：4032 美元/金衡盎司；2026-10-29；ok；2/3 來源可用，核對通過（價差 0.1119%、時間差 0.44 分鐘）
- 白銀現貨參考價（XAG/USD）：52.740002 美元/金衡盎司；2026-10-29；ok；2/3 來源可用，核對通過（價差 0.263%、時間差 0.46 分鐘）
- 黃金／白銀比（XAU/XAG）：76.4505090462454 倍；2026-10-29；ok；金價 2/3 來源可用、銀價 2/3 來源可用，核對通過；歷史 23 點
- 本一次性追加已完成；後續巡檢不再重複執行本段。
