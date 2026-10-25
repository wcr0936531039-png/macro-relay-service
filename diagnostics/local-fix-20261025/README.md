# 2026-10-25 三項本機修補審查

狀態：LOCAL ONLY，未部署。正式站仍為 v233；沒有推送網站來源分支、沒有改排程或生產資料。
基線：488b8bc9ab0402472496a80abb1cee17aea35fae。
交接：gate-probe `handoff/CLAUDE_TO_GPT_LATEST.md` 的 2026-10-25 14:40 節（blob 2107fe99490faa12bb190e5c08f6c4699f2ae8f2）。

## 1. 官方實際交易日

`validateTaiwanStatistics()` 原本同時要求預定行事曆推算日和 FMTQIK 最後資料日等於匯入日。臨時休市時，前者為 10/23、後者為 10/22，造成拒收。

修改後以通過來源、欄位、金額與日期交叉核對的 FMTQIK 實際最後一筆決定最新日；保留預定行事曆作為 expectedSession，另存 calendarDiscrepancy、basis、tradingDates 與來源網址。仍檢查36小時擷取有效期、未來資料及20日觀測封頂，不擴大任何投資評分門檻。

- 10/23 缺資料：接受 10/22，記錄 expectedSession=10/23、calendarDiscrepancy=true。
- 10/26：使用官方行事曆中的補假列；不將它當作開盤日。10/27 才是下一個預期交易日。
- 10/22 的今日餘額仍為 provisional；final 仍須下一個實際交易日報表的前日餘額。未更動既有修訂規則。
- 這是受控本機重播，不是本輪對正式 API 的新讀回，也沒有將測試fixture宣稱為新的官方原始存證。

## 2. 保留來源時間

`retainedTaiwanCreditRows()` 不再以容器快照 checkedAt 充當資料列來源時間；必須已有 verifiedAt 或 fetchedAt。deferred 合併分支保留來源時間，沒有來源時間時留 null。本輪檢查時間另寫 checkedAt。

| 情境 | 修補前 | 修補後 |
|---|---|---|
| 有原 verifiedAt | 保留原值 | 保留原值 |
| deferred 無 verifiedAt／fetchedAt | 補為當下時間 | null |
| 只有容器 checkedAt 的信用資料 | 可被當作有來源時間 | missing |
| 過期、錯來源或未來日期 | 失效／缺項 | 維持失效／缺項 |

無法用程式推回過去已遭覆寫的真實來源時間；部署後仍須實際晚間保存與隔日上午讀回配對驗收。

## 3. run 模組與直接 API 一致

finalize 新增逐模組持久 checkpoint，每次重讀一個與畫面相同的 API。摘要存 summaryScope=final_readback、readbackAt，完成後 history 採最後摘要。此處不再次強制刷新 Tiingo 或公開其原始價格。

來源抓取失敗但直接API仍可回傳舊快取時，保存 latestReadback 同時保留 sourceAttemptFailed 與原錯誤，scope 為 final_readback_with_source_failure；不把來源失敗洗成整輪成功。板塊30次重試上限也保留，最後pending另存readbackStatus。

擴展總經與美股指數回應快取過期時，改走共用逐列有效性判斷，不再呼叫整包markSnapshotStale；原始觀測日、來源時間、發布核對有效期仍需通過。回應 refreshing 和觀測可用性分開保存，不隱藏背景更新。

| 固定輸入重播 | 基線 | 本機修補 |
|---|---|---|
| 10/22 信用，10/23臨時休市 | statistics_not_latest_session | 接受，觀測日仍10/22 |
| deferred缺來源時間 | verifiedAt=重播當下 | verifiedAt=null |
| PAYEMS月度觀測有效，15分鐘回應快取過期 | stale | ok |
| 外銷訂單來源HTTP403 | stale／HTTP403 | stale／HTTP403 |
| run初讀pending，結尾API已有有效資料 | 留初讀摘要 | final_readback摘要與history同步 |

完整逐列輸出：before-after.json；重播程式在patch中的 tests/replay-local-fix-20261025.mjs。

## 驗證與已知限制

- 信用時段／保存／接續35項通過；新增回歸8項通過；原observation-freshness通過。
- 完整 `npm test` 最終 exit 0，已執行到 source-recovery 最後一組；信用／接續35/35、來源恢復含新增回歸14/14，fail均0。legacy、advisory-integration、fixpack、C2皆通過。
- 過程中兩個失敗皆留案：finalize以舊快取蓋掉來源失敗（已修）；既有collector測試把週日當行情日（只修測試fixture選最近平日，未改生產收集器）。
- 乾淨基線重新套 `final.patch` 並build成功，Worker／HTML SHA-256與工作副本一致。`fix.patch`僅為初版checkpoint，最終審查請使用`final.patch`。
- 沒有修改Gate判斷、評分公式、權重、風險預算；恢復有效觀測可能改變模型輸入，不能預先保證正式站分數永遠相同。
- MOEA403、央行月度核對、Gate4／5／8證據不足、Gate6真實財報警訊與手機／桌面實際畫面驗收仍為既有缺口。
- 正式站部署及部署後真實資料驗收等待擁有者授權。

## 最終檔案指紋

```text
d4940c2da9bc70452a36d75481c70143b69ccc82a6fdcc2ee5a5cbb3e4503899  final.patch
6fd09b2590bb7bf1c3138b9b450769d629196aaa0096f66a32187eb8cae4734b  dist/server/index.js
080f721d52eb610eb245a5a7f6a1fa630bc42e12740828d3fc3e5207c4186d3d  dist/index.html
```
