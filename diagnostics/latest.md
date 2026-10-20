# v229-local 整合版部署驗收 — 2026-10-21 02:00 台北

## 結果
已按擁有者授權部署；平台儲存版本為 **v230**，原站 v229 保留為回滾目標。Sites 回傳 succeeded；私人擁有者存取未改。沒有部署本輪未授權的固定指標目錄或隔日前日餘額回補。

## 部署前驗證
- 乾淨基線：543793fa6be1a9d4dfde79d0be4313eeb436f8e8。
- 指定補丁：`diagnostics/tiingo-integration/v229-local.patch`；SHA-256 `78cf08852783b9cf355568cdcb9d0ea417500fdb6383094808dc0a08b3b583d0`。重新套用成功，沒有追加網站程式修改。
- `npm test` 完整執行 exit 0：既有全套測試通過；新增整合 38/38 通過；連續兩次 build 可重現；`git diff --check` 通過。
- HTML SHA-256：b99f41694ceeaea4f303eb42136179708ca5e641604ef2f6a5e58e9e43b50ace。
- Worker SHA-256：fa889e3ffbb145b18b8185230c4ae799ead986fa06d09e3777f5f642d9e52fdc。
- 已推送來源：f9c5f15b371de58d0a06ef5251ce5c8a895f217e。部署封裝與上述來源一致。
- 完整 diff 仍在上述已核准 patch；本輪只部署該 patch。

## 第一次真 Tiingo 驗收
- 正式站強制更新 HTTP 200、status OK、Tiingo 主要來源。
- 應有交易日 **2026-10-19**，當時美股 10/20 尚未完成收盤與發布寬限；沒有把盤中日期當完成日。
- 22 檔通過：類股 11/11、SPY、RSP、其餘全球市場 9/9；同一日期驗證由正常化器、寬度與 RSP/SPY 共同檢查。API 可讀類股來源覆蓋12/12、全球10/10與RSP/SPY共同日期10/19，沒有將 raw histories 輸出至瀏覽器。
- Yahoo 同日 33 個相對報酬比較：within_guard；最大絕對差 **0.000011459642189848296 個百分點**，小於暫定 0.25 保護值。
- 私人 D1 額度表實際讀回：滾動一小時 **22/50**、24小時 **22/1000**、本月不同代號 **22/500**；refresh lease 已釋放。再讀四檔 Master 後仍22次，未重抓。
- **沒有將 Tiingo 原始價格或私密服務憑證寫進本公開 repo。**

## Tiingo 失敗與 Yahoo 備援
真實 Tiingo 首次成功，未發生401/429/空資料。另以這次部署的原始 orchestration 函式做本機故障注入，替換網路及儲存邊界：
- 401：1次請求後停止 fan-out，回 Yahoo，sourceRole＝備援來源。
- 429：1次請求後停止 fan-out，回 Yahoo，sourceRole＝備援來源。
- 空資料：22檔失敗後回 Yahoo，sourceRole＝備援來源。
- 三項均通過；這是**本機注入測試，不是假稱正式站真的遇到這些錯誤**。沒有更換真金鑰或清除正式快取來製造故障。

## 四檔 Master 前後核對
8299 D→D、5289 D→D、2404 D→D、5009 C→C。這些是既有自訂退避風險評級；原始10D總分仍為null，未補造分數。
四檔的 scoring、adaptiveRating、veto 完整物件逐一深度相同；40個 Gate 的 status、blocksOverall 全部相同。新面板與綜合判斷 contribution 都為0；suggestedRange都為null；appliedToRating與appliedToRiskBudget都為false。
正式 HTML 有新面板程式與掛載點；四份真實讀回資料均通過本機 DOM renderer，顯示補充觀測與「綜合觀察｜草案未啟用」。**未完成實際瀏覽器截圖驗收**；這次驗證是正式 API＋已部署 HTML＋真實資料 DOM 渲染，未宣稱手機視覺驗收。
Gate4/5/8缺項、Gate6財報警訊仍保留；沒有因資料接通自動通過Gate。沒有整站失效跡象，未回滾。

完整逐 Gate 前後：
```json
[
  {
    "symbol": "8299",
    "gradeBefore": "D",
    "gradeAfter": "D",
    "scoringExactSame": true,
    "ratingExactSame": true,
    "vetoExactSame": true,
    "gateStatusesAndBlocksSame": true,
    "gates": [
      {
        "id": 1,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 2,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 3,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 4,
        "before": "warning",
        "after": "warning",
        "blocksSame": true
      },
      {
        "id": 5,
        "before": "partial",
        "after": "partial",
        "blocksSame": true
      },
      {
        "id": 6,
        "before": "warning",
        "after": "warning",
        "blocksSame": true
      },
      {
        "id": 7,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 8,
        "before": "partial",
        "after": "partial",
        "blocksSame": true
      },
      {
        "id": 9,
        "before": "conditional",
        "after": "conditional",
        "blocksSame": true
      },
      {
        "id": 10,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      }
    ],
    "newPanelsPresent": true,
    "newPanelsContribution": 0,
    "newDecisionContribution": 0,
    "suggestedRange": null,
    "appliedToRating": false,
    "appliedToRiskBudget": false
  },
  {
    "symbol": "5289",
    "gradeBefore": "D",
    "gradeAfter": "D",
    "scoringExactSame": true,
    "ratingExactSame": true,
    "vetoExactSame": true,
    "gateStatusesAndBlocksSame": true,
    "gates": [
      {
        "id": 1,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 2,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 3,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 4,
        "before": "warning",
        "after": "warning",
        "blocksSame": true
      },
      {
        "id": 5,
        "before": "needs_user_records",
        "after": "needs_user_records",
        "blocksSame": true
      },
      {
        "id": 6,
        "before": "warning",
        "after": "warning",
        "blocksSame": true
      },
      {
        "id": 7,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 8,
        "before": "needs_user_records",
        "after": "needs_user_records",
        "blocksSame": true
      },
      {
        "id": 9,
        "before": "blocked",
        "after": "blocked",
        "blocksSame": true
      },
      {
        "id": 10,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      }
    ],
    "newPanelsPresent": true,
    "newPanelsContribution": 0,
    "newDecisionContribution": 0,
    "suggestedRange": null,
    "appliedToRating": false,
    "appliedToRiskBudget": false
  },
  {
    "symbol": "2404",
    "gradeBefore": "D",
    "gradeAfter": "D",
    "scoringExactSame": true,
    "ratingExactSame": true,
    "vetoExactSame": true,
    "gateStatusesAndBlocksSame": true,
    "gates": [
      {
        "id": 1,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 2,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 3,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 4,
        "before": "partial",
        "after": "partial",
        "blocksSame": true
      },
      {
        "id": 5,
        "before": "needs_user_records",
        "after": "needs_user_records",
        "blocksSame": true
      },
      {
        "id": 6,
        "before": "partial",
        "after": "partial",
        "blocksSame": true
      },
      {
        "id": 7,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 8,
        "before": "needs_user_records",
        "after": "needs_user_records",
        "blocksSame": true
      },
      {
        "id": 9,
        "before": "partial",
        "after": "partial",
        "blocksSame": true
      },
      {
        "id": 10,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      }
    ],
    "newPanelsPresent": true,
    "newPanelsContribution": 0,
    "newDecisionContribution": 0,
    "suggestedRange": null,
    "appliedToRating": false,
    "appliedToRiskBudget": false
  },
  {
    "symbol": "5009",
    "gradeBefore": "C",
    "gradeAfter": "C",
    "scoringExactSame": true,
    "ratingExactSame": true,
    "vetoExactSame": true,
    "gateStatusesAndBlocksSame": true,
    "gates": [
      {
        "id": 1,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 2,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 3,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 4,
        "before": "warning",
        "after": "warning",
        "blocksSame": true
      },
      {
        "id": 5,
        "before": "needs_user_records",
        "after": "needs_user_records",
        "blocksSame": true
      },
      {
        "id": 6,
        "before": "warning",
        "after": "warning",
        "blocksSame": true
      },
      {
        "id": 7,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      },
      {
        "id": 8,
        "before": "needs_user_records",
        "after": "needs_user_records",
        "blocksSame": true
      },
      {
        "id": 9,
        "before": "conditional",
        "after": "conditional",
        "blocksSame": true
      },
      {
        "id": 10,
        "before": "evaluated",
        "after": "evaluated",
        "blocksSame": true
      }
    ],
    "newPanelsPresent": true,
    "newPanelsContribution": 0,
    "newDecisionContribution": 0,
    "suggestedRange": null,
    "appliedToRating": false,
    "appliedToRiskBudget": false
  }
]
```

## 巡檢時間
既有任務改為台北06:30、22:30；信用統計只在22:30之後抓，早上保留昨晚原觀測日期與擷取時間。若晚間官方仍未公布就照實留缺。未新增另一個排程。
固定目錄缺值列與融資最終值回補：**未修改，等下一輪授權**。
來源診斷往後需列出每個來源網址、HTTP與筆數，consumer零筆原因仍待下一次實際收集紀錄，不在這次部署中假稱修復。

## 其他驗證與限制
檢查近期 Worker 紀錄未見新版本未處理崩潰；看到的401為既有私人研究紀錄API缺訪客身分，不能當成整站崩潰，也未偽造身分繞過。
舊資料缺口、策略回測、門檻校準不在本輪部署驗收成功範圍；整體研究可用性仍非全數完成。
