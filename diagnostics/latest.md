## 最新授權執行進度（2026-10-20 05:32）

**PR #6已合併**，merge commit `835168c34472333f54eb59956ac0576c067cab54`。合併後真實US Sector History run39328238333已success，完成新交易日檢查與發布。A1精確reason回歸已補並通過目標測試，正在跑完整npm test；**網站尚未部署**。

[逐項授權紀錄](https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/diagnostics/authorized-v228/latest.md)。本次只有A1、A2、群聯面板標示與PR #6；未擴充其他項目。下方「PR未合併／待授權」是本次授權前的歷史。

---

## 板塊恢復已完成（2026-10-20 台北，逐項紀錄已上傳）

**正式Site已驗收：美股板塊OK、11/11有效、來源12/12，資料池最新10/19。** 8299、2404、5289、5009四檔Master板塊子模組均讀回成功。各代號66筆，既有重疊價格0改動；資料提交 `0000cea5f7eb3c695696b64597b263137a013cba`。

請Claude先讀 [本輪逐項恢復紀錄與原始證據](https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/diagnostics/sector-recovery/latest.md)。每完成一項已即時存steps，01至07可逐筆追蹤；遇到的工具限制也有紀錄。

正式網站仍v228、PR #6未合併，A2/A3長期程式修補仍待原先要求的擁有者授權。整體模型仍degraded，其他缺項和警訊保留。下方先前「行情仍停10/15／未恢復」是修復前歷史，以本節及恢復索引為準。

---

# GPT → Claude：v228 完整續作交接（2026-10-20 台北）

先讀本節，再看完整 diff。已讀你的固定檔最新 03:50 一節及其中 04:59 檢查紀錄，blob `83b338bb23b6a94a5265ee19bbc7c522f1966eae`。接受新的處理順序：P1 缺資料 → P2 四層真實資料稽核 → P3 固定規則的綜合判斷；Gate 5B 維持現狀、不擴充，R2～R5、B1～B8 延後。本檔保存先前已做的本機工作與剩餘問題，沒有因此部署或合併。

## 先更正交接落差

- GPT 已經找到可讀的 v228 本機原始碼，也已取得完整 `/api/macro-market` 36 列，無需再請擁有者轉存。原始碼基準 commit `0dd0df41a3aed304a8b11bf7658c855b978ea337`。此 GitHub repo 仍只是交接與中繼，不是正式網站原始碼倉庫；完整網站變更在本檔 diff，可供你審查。
- A1 已補完全部列比較；A2 八項測試由 GPT 自己執行，並已套進本機 Site；A3 已核對 MANIFEST、開分支與 PR。
- **PR #6 的中繼本身 CI 現已通過**，不是沿用 Claude 的測試。`US Sector Module Tests` 與 `US Sector Live Smoke` 都是 success，且核對 head `2c098f9263eb4838487c212e123f6dda9256c5a1`。PR 仍 open、`merged:false`；沒有合併。
- 正式網站沒有在這輪部署。**本機通過不代表美股板塊已恢復**：本次直接重讀中繼 main，SPY 與 11 板塊仍全部停在 2026-10-15，`generated_at=2026-10-17T01:28:36.371009+00:00`，資料 blob `f12ca5bdaeab02e9bbcb2c50052ad4116d16902e`。必須拿到真實缺日行情；禁止改 generated_at、複製前一日收盤來製造恢復。

## 請 Claude 接續的問題，按新優先序

| 優先 | 問題／剩餘工作 | 已有結果 | 下一步及限制 |
|---|---|---|---|
| P1 | 美股板塊真實行情缺日 | A2 本機與 A3 PR 驗收完成；main 仍全是 10/15 | 追查下一輪 Yahoo 原始回應、刪除未收盤 bar 是否誤刪與發布流程；真正補到 10/16、10/19 才重新評估。PR 合併和 Site 部署都等擁有者授權 |
| P1 | 日圓時效／舊 reason | A1 全 36 列重播完成，只有 HV20/60 status 改變 | 請審閱 below diff 與全列比較；正式站未部署，不宣稱已修復 |
| P1 | ECB 匯率借用 DEXJPUS 代號 | 中繼 DEXJPUS provider 實為 ECB 交叉換算；A1 只處理時效，不修來源口徑 | 後續以獨立 ECB 代號與衍生 lineage 修正，不將其假稱 FRED H.10；這輪未混入 A1 |
| P1 | Gate 4 各缺項 | 已讀實際 8299 checks，見下表；年報只加獨立證據 | PSR 五年／大戶歷史／CB 現行條款分開接；原始規則缺失不能自行發明分級；CFO、訴訟警訊保留 |
| P1 | Gate 5、8 缺樣本 | 5A/5B 仍 0/8；直接同業 0/3 | 群聯季度數字指引標結構性；共識取樣與口徑保持嚴格，這輪不擴 Gate 5B。Yahoo 人數不能借給 FactSet |
| P1 | EIA、官方公告與其他採集失敗 | 既有歷史報告不是本次新採集結果 | 依原始回應／日期／發布日核對，無法取得就保留缺項，不能用 passed 旗標代替原文 |
| P2 | 任何股票都能用的官方估值主幹 | 8299 實際 Gate 8 已有自身歷史 P/E fallback，1216 筆；不能據此聲稱所有代號都已驗收 | 稽核所有代號 PE/PB/殖利率歷史、月營收、財報、線型與大盤；確認缺值、負 EPS、新上市與循環股分支，不用預設價格或共識 |
| P3 | 最上層綜合判斷 | 目前 API 有 report/headline、qualifiedOutput、adaptiveRating，不代表你新規格已完成 | 對照固定規則，設計一句結論＋信心＋理由＋改變條件＋缺資料；原始資料可展開，美股板塊只作背景，AI 不決定結論 |

請勿將網站尚未部署的修補描述為 production 修復。若要繼續研究原始來源，可直接讀本檔與 artifacts；不用擁有者反覆轉貼。本輪未建立新的排程。

## 交接通道與檔案

- 固定讀取：[diagnostics/latest.md](https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/diagnostics/latest.md)。Claude 回覆仍寫 gate-probe 的 `handoff/CLAUDE_TO_GPT_LATEST.md`。
- [PR #6](https://github.com/wcr0936531039-png/macro-relay-service/pull/6)。[中繼 Module CI](https://github.com/wcr0936531039-png/macro-relay-service/actions/runs/39281730728)。[Live Smoke CI](https://github.com/wcr0936531039-png/macro-relay-service/actions/runs/39281730598)。
- `diagnostics/artifacts/v228-20261019-macro-market.json`：完整 36 列的唯讀快照，不是現在即時值。
- `diagnostics/artifacts/v228-20261019-row-comparison.json`：同一份資料、同一時鐘、全部列前後比較。
- `diagnostics/artifacts/v228-20261019-site.diff`：網站完整本機 diff，含新增檔案和 build 產物，可重建審閱。
- `diagnostics/artifacts/v228-20261019-site-test.log`：完整 Site npm test 輸出；其中 403/503 為既有故障注入測試，不代表本次正式站採集失敗。
- 本檔及 artifacts 已做 token 模式檢查，不含服務憑證、Cookie 或授權標頭；不公開完整個股使用者研究回應，只列必要公開市場結果與程式。

## A1：同一份完整 36 列修補前後比較

原始讀回擷取完成 `2026-10-19T15:51:49.247923+00:00`；payload checkedAt `2026-10-19T15:49:08.620Z`。固定評估時間 `2026-10-19T15:51:49.247Z`；基準 HEAD bundle 與修補後 bundle 各執行 `refreshingMacroSnapshot(structuredClone(payload),false)`，沒有附加或補造來源驗證 metadata，沒有在比較中連網更新。

原始 JSON SHA-256：`3905328861fb4b648d0b0c8dd4bb930b8a1bb1198e4e51a30c39c2bda1e65a96`。36/36 值與觀測日不變，順序不變。`<absent>` 與 null 分開表示；多列只是明確補出 `is_stale:false`，不是新資料。

只有 JPY_HV20、JPY_HV60 的 status 是 `stale → ok`；沿用各自 5.804832905239327、9.756886685658461，觀測日仍 10/9。這兩列重新進入有效輸入集合，是需要審閱的行為改變。另七列 DCOILWTICO、DCOILBRENTEU、DHHNGSP、DEXJPUS、US3M、US10Y、US30Y 保持原 status，只清除精確的矛盾舊 reason；其他來源警告不清除。母序列失效、缺母列或日期不同時，衍生值仍 null/missing，不放行。

| # | 指標／觀測日 | before status | after status | before is_stale | after is_stale | before reason | after reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | XAU / 2026-10-19 | "ok" | "ok" | "<absent>" | false | null | null |
| 2 | XAG / 2026-10-19 | "ok" | "ok" | "<absent>" | false | null | null |
| 3 | XAU_XAG / 2026-10-19 | "ok" | "ok" | "<absent>" | false | "金價與銀價即時比值有效；日歷史樣本 13/21，收集至少 21 個日觀測且資料缺口不超過 5 日後才判讀 20 日趨勢。" | "金價與銀價即時比值有效；日歷史樣本 13/21，收集至少 21 個日觀測且資料缺口不超過 5 日後才判讀 20 日趨勢。" |
| 4 | NYFED_REPO / 2026-10-15 | "ok" | "ok" | false | false | null | null |
| 5 | TWSE_TAIEX / 2026-10-19 | "ok" | "ok" | "<absent>" | false | "<absent>" | "<absent>" |
| 6 | TWSE_ELECTRONIC / 2026-10-19 | "ok" | "ok" | "<absent>" | false | "<absent>" | "<absent>" |
| 7 | TWSE_SEMICONDUCTOR / 2026-10-19 | "ok" | "ok" | "<absent>" | false | "<absent>" | "<absent>" |
| 8 | TWSE_FINANCIAL / 2026-10-19 | "ok" | "ok" | "<absent>" | false | "<absent>" | "<absent>" |
| 9 | TWSE_SHIPPING / 2026-10-19 | "ok" | "ok" | "<absent>" | false | "<absent>" | "<absent>" |
| 10 | TWSE_STEEL / 2026-10-19 | "ok" | "ok" | "<absent>" | false | "<absent>" | "<absent>" |
| 11 | TWSE_TOTAL_TRADE_VALUE / 2026-10-19 | "ok" | "ok" | false | false | null | null |
| 12 | TWSE_MARGIN_BALANCE_NTD / 2026-10-19 | "ok" | "ok" | "<absent>" | false | null | null |
| 13 | TWSE_MARGIN_CHANGE_NTD / 2026-10-19 | "ok" | "ok" | "<absent>" | false | null | null |
| 14 | TWSE_MARGIN_BALANCE_UNITS / 2026-10-19 | "ok" | "ok" | "<absent>" | false | null | null |
| 15 | TWSE_SHORT_BALANCE / 2026-10-19 | "ok" | "ok" | "<absent>" | false | null | null |
| 16 | TWSE_SHORT_CHANGE / 2026-10-19 | "ok" | "ok" | "<absent>" | false | null | null |
| 17 | TWSE_MARGIN_MARKET_CAP_RATIO / 2026-10-19 | "ok" | "ok" | "<absent>" | false | null | null |
| 18 | TWSE_CREDIT_TRADE_VALUE / 2026-10-19 | "ok" | "ok" | "<absent>" | false | null | null |
| 19 | TWSE_BREADTH / 2026-10-19 | "ok" | "ok" | false | false | null | null |
| 20 | TPEX_BREADTH / 2026-10-19 | "ok" | "ok" | false | false | null | null |
| 21 | TWSE_DAYTRADE / 2026-10-19 | "ok" | "ok" | false | false | null | null |
| 22 | NYFED_SRP / 2026-10-19 | "ok" | "ok" | false | false | null | null |
| 23 | ICE_DXY / 2026-10-19 | "ok" | "ok" | false | false | null | null |
| 24 | DTWEXBGS / 2026-10-09 | "ok" | "ok" | false | false | null | null |
| 25 | DCOILWTICO / 2026-10-14 | "ok" | "ok" | false | false | "資料較舊，暫不納入判讀" | null |
| 26 | DCOILBRENTEU / 2026-10-14 | "ok" | "ok" | false | false | "資料較舊，暫不納入判讀" | null |
| 27 | DHHNGSP / 2026-10-14 | "ok" | "ok" | false | false | "資料較舊，暫不納入判讀" | null |
| 28 | DEXJPUS / 2026-10-09 | "ok" | "ok" | false | false | "資料較舊，暫不納入判讀" | null |
| 29 | US3M / 2026-10-15 | "ok" | "ok" | false | false | "資料較舊，暫不納入判讀" | null |
| 30 | US10Y / 2026-10-15 | "ok" | "ok" | false | false | "資料較舊，暫不納入判讀" | null |
| 31 | US30Y / 2026-10-15 | "ok" | "ok" | false | false | "資料較舊，暫不納入判讀" | null |
| 32 | VIXCLS / 2026-10-15 | "ok" | "ok" | false | false | null | null |
| 33 | WCESTUS1 / 2026-10-09 | "snapshot" | "snapshot" | false | false | "EIA／FRED 即時來源暫不可用；使用已標明日期的 EIA 官方週資料快照。" | "EIA／FRED 即時來源暫不可用；使用已標明日期的 EIA 官方週資料快照。" |
| 34 | US10Y3M / 2026-10-16 | "ok" | "ok" | "<absent>" | false | null | null |
| 35 | JPY_HV20 / 2026-10-09 | "stale" | "ok" | true | false | "官方觀測或最近來源核對已過有效期；等待更新。" | null |
| 36 | JPY_HV60 / 2026-10-09 | "stale" | "ok" | true | false | "官方觀測或最近來源核對已過有效期；等待更新。" | null |

A1 補件另含：衍生列按原 map 順序回填、找不到母列明標 `source_missing`；`importedOfficialSeries()` 合併時明確 `reason:null`。只刪精確 age-only 舊文案，不清其他失敗。

### 搜尋兩段指定文字後定位的合併函式（修補後原文）

`worker/data-import.js#importedOfficialSeries()` 寫入「經外部抓取並保存」「官方頁面同值核對」。它先 summarize 再 spread row，原本覆寫 ok 卻保留 stale reason；下方包含這次 reason:null 修正。這段既有驗證文案不能單獨充當原始來源口徑證據，ECB lineage 仍列待處理。

```js
async function importedOfficialSeries(id, env) {
  if (!OFFICIAL_IMPORT_SERIES.has(id)) return null;
  const saved = await readRuntimeCache(env, `official-series:v1:${id}`), input = saved?.payload;
  if (!input || !saved.fresh || Date.now()-Date.parse(input.fetchedAt)>36*3600000) return null;
  const history=cleanHistory(input.history || []);
  if (history.length < (id==='DEXJPUS'?65:3)) return null;
  const row=summarize(id,history);
  if(['US3M','US10Y','US30Y'].includes(id))row.name={US3M:'13 週期美國國庫券折現殖利率（DTB3）',US10Y:'10 年期美債官方殖利率（DGS10）',US30Y:'30 年期美債官方殖利率（DGS30）'}[id];
  const releaseVerification=input.releaseVerification;
  if (row.status!=='ok'&&!releaseObservationCurrent(id,{...row,releaseVerification})) return null;
  return {...row,status:'ok',reason:null,provider:'FRED／原始官方提供者｜經外部抓取並保存',source:input.source,fetchedAt:input.fetchedAt,releaseVerification,snapshot:true,is_stale:false,historyObservations:history.length,historyFetchState:'fetched',sourceValidation:{state:'passed',method:'官方 CSV 原始觀測；日期、正值、排序及筆數已校驗'},detail:`官方來源觀測 ${row.date}；擷取 ${input.fetchedAt}。${releaseVerification?`官方頁面同值核對；下一次發布 ${releaseVerification.nextReleaseDate}。`:''}${id==='DEXJPUS'?'FRED H.10 日參考匯率，非盤中價格；保留完整歷史供 20／60 日波動率。':id==='IORB'?'聯準會準備金餘額利率；保留同日配對所需歷史。':['US3M','US10Y','US30Y'].includes(id)?'官方利率序列；DTB3 為折現殖利率，DGS10／DGS30 為固定到期投資收益率。':'官方現貨系列，與近月期貨分開。'}`};
}
```

## A2：站內美股板塊模組

- 已用連接器取得三個原始檔，GPT 自己執行 `node --test us_sector_session.test.mjs`，8/8 通過。Fixture 未改值；原始 fixture、Site fixture、中繼真實資料 SHA-256 均為 `f830f59fb059ed4b3479d8f2bc79344558336dccfdae1a0b05c6f6b66a2c1071`。
- 已以 `US_SECTOR_SESSION` 閉包嵌入 build，`normalizeUSSectorSnapshot` 取代 36 小時年齡規則；支援 NYSE 2026–2027 休市、提前收盤、15 分結算、8 小時上游發布容忍。超出日曆範圍失敗，不當作交易日。
- 不改原本資料筆數、gaps、來源與 11 板塊評分；新錯誤區分格式、來源、擷取時間、未完成交易日等。較舊而缺最新 session 的回應不覆蓋已保存的新快照，並保留 fetchError。
- 真實資料重播仍 UNKNOWN，見下面。附測試中「複製 close 補一日」只用於測試控制變因，從未寫回正式行情或聲稱取得真價格。

```json
{
  "evaluationAt": "2026-10-19T15:51:49.247Z",
  "input": "unmodified relay main 46b58640c7b3f839c0c4d55e77ddddacfaacbb64 data/us_sector_history.json",
  "before": {
    "status": "UNKNOWN",
    "errorCode": "SCHEMA_SOURCE_OR_CAPTURE",
    "coverage": {
      "valid": 0,
      "total": 11
    }
  },
  "after": {
    "status": "UNKNOWN",
    "errorCode": "LATEST_SESSION_MISSING",
    "coverage": {
      "valid": 0,
      "total": 11
    },
    "sessionFreshness": {
      "ok": false,
      "code": "LATEST_SESSION_MISSING",
      "observed": "2026-10-15",
      "expected": "2026-10-16",
      "captured_at": "2026-10-17T01:28:36.371009+00:00"
    }
  },
  "productionDeployed": false
}
```

## A3：原檔雜湊、PR 與中繼 CI

使用 `handoff/relay_patches/files/` 完整檔案，不使用舊基準 patch。基準 `46b58640c7b3f839c0c4d55e77ddddacfaacbb64` 五個既有檔 SHA-256 全 MATCH，六個套用後檔也全 MATCH；`.github/workflows` 寫入成功，未略過補抓排程。分支 `fix/us-sector-expected-session-20261019`，PR #6，head `2c098f9263eb4838487c212e123f6dda9256c5a1`。

| 中繼路徑 | 基準 SHA-256 | 修補 SHA-256 |
| --- | --- | --- |
| .github/workflows/us-sector-history.yml | 17503bff051302237b5cb87237fe2ee5de5aa5b9923cbc054bc4f387f672e576 | 407fffa93ae833499ed79d9d23c0ea52af0bfd3ded15d594e35e4e7950b63d35 |
| scripts/check_us_sector_snapshot.py | d5ef8face544b74488c9dfba0efd69e5412840b1163ae510571fa062aed2cf19 | 780bd0b9c83c26a023b81d8445fd5eb0d3f5a4a5c26609f87b6190f051ec495c |
| scripts/test_us_sector_feed.py | dc2f97b5c0b72afa717d7f0fd91d6c2d3e2c9a9ee65c52df8c4affe42471f7ee | 23416bf2e59e7fbb067c0747ed444a8565f2c76c1fa38c399ddae175c7bd3ac2 |
| scripts/test_us_sector_snapshot.py | 315dc85e56600317e1f086280d0bc35762de28fdffe054d9249d85470c5a77d1 | ca735f7bc149f8d779ea4c727d70c47270eb5212dbe42276574c118dbd173a82 |
| scripts/us_sector_feed.py | 2edc54c159bdf9b51fc9045b82d8178b6bacc1511125d288bc0f8a5880ef6aa0 | f7e4ea5af565d81697286f6f978b5fe890837de4b8912adf488ee148dc01e307 |
| scripts/us_market_calendar.py | (new file) | 12913d6a4ed390cdafc6c79b0dcd4ff37f5330ef7e6af7728ed812b9f0fa000a |

| 執行者／環境 | 驗收內容 | 結果 |
| --- | --- | --- |
| GPT 本機 | 6 個 Node 模組檔＋published pipeline＋Python 20 項 | 全通過，完整輸出下方 |
| GitHub 中繼 PR #6 | US Sector Module Tests / run 39281730728 | completed / success；核對三個正式 run 步驟均 success |
| GitHub 中繼 PR #6 | US Sector Live Smoke / run 39281730598 | completed / success |
| 正式發布 | PR merge / Site deploy | 未執行，等待擁有者授權 |

PR 修補會擋「缺預期 session 卻標 ok」，保存 dropped bar 日期、加補抓排程、避免只有 generated_at 改變就提交。**尚未完成**每次 Yahoo 原始 HTTP 回應 SHA-256 與 dropped reason 的更完整審計；本輪不把這些列成已做。程式擋住壞資料不等於上游已補到新行情。

## 群聯面板：已做的本機修正、未解除的風險

- Gate 2 以各欄位真正共同的最新交易日比較，保留 latestAvailable 與逐筆來源。只保留最多100筆真正觀測；衝突值剔除、缺歷史留缺、未來值不收，不用帶值回填。本次實際擷取9欄已全為10/19且 Gate2 evaluated，這是來源後續更新，不能歸功於尚未部署的程式。
- Gate 5 的季度數字指引無有效樣本時，按本次已審閱官方範圍標「公司不提供季度財測（結構性）」；保留原始年度指引、候選池筆數、5A/5B=0/8、ready=false 和既有權重／上限。新合法數字指引仍可覆蓋此描述，不宣稱公司永遠不提供。
- Gate 4 加年報原文事實與頁碼、查核來源，不製造護城河分數或產能利用率。2024/25無單一客戶≥10%；台灣鎧俠28.33%是**進貨**集中，不是銷貨集中；全部委外不等於低地緣風險，產地、替代產能仍未知。公司個體年報表不直接解釋近12季合併現金流。
- Gate 8 Yahoo FY2027 12 位與平均EPS281.54、FY2026 10位與平均412.34 独立記為來源證據，`productionEligible:false`、口徑未註明。不將 Yahoo 人數借給 FactSet 2027中位362.55；故有效共識仍未補滿，直接同業仍0/3，沒有自動通過 Gate8。
- Gate 6 已核驗的真實警訊保留：CFO／淨利−0.17倍、FCF−141.57億元；三筆治理／訴訟風險、四條未知 Veto、原分數與風險限制不解除。

### 讀回的 Gate 4／5／8 非完成檢查（原資料，非修補後假裝補齊）

| Gate | 項目 | 狀態 | 資料數 | 缺口／原因 |
| --- | --- | --- | --- | --- |
| 4 | 10D 已接入必要資料 | missing | 3/10 | 逐項資料覆蓋；資料齊備不等於評分或 Veto 通過 |
| 4 | S3 同業護城河 | missing | 1/2 | 已核驗直接同業映射 1 檔；具原文來源的比較證據 0 筆。資料覆蓋不給護城河分數。 |
| 4 | S4 PSR 估值合理性 | missing | 0/2 | 當期 PSR 缺值；同口徑五年歷史 0/5 年。年度快照不當作完整五年最高值，Veto 高點另核驗。 |
| 4 | S5 PEG 動態估值 | missing | 1/2 | 本年共識 Forward P/E 4.42；次年共識 EPS 成長 待核。不外推3–5年 CAGR或設定分級。 |
| 4 | S6 法說指引動能 | missing | 0/1 | 已核對同口徑指引回測 0/8 期；定性展望不補成數值財測 |
| 4 | S7 產能與地緣風險 | missing | 0/3 | 產地／產能、替代方案與客戶曝險分別核對；客戶證據 0 筆。保留既有 >80% 複合否決，不新增利用率門檻。 |
| 4 | S8 CB／股本稀釋壓力 | missing | 0/5 | 登錄餘額：待核；目前轉換價：待核；同日股本：待核；同日匯率：待核；存量與賣回／期後事件：待核。已保存 3/3 檔餘額、0/3 檔目前轉換價；缺項不當作無 CB。 |
| 4 | S10 籌碼大戶防禦力 | missing | 1/2 | 已連結五日法人淨買賣；大戶持股分布與延續性仍待核 |
| 4 | Veto｜PSR 超過五年高點 20% | missing | 0/1 | 同口徑當期 PSR > 五年高點 ×1.2；P/E 不代替 PSR。 |
| 4 | Veto｜CB 三條件同時成立 | missing | 0/1 | CB／股本 >15%、價格低於轉換價至少20%、六個月內賣回，須三條件同時成立。 已接入 2026-10-15 TPEx 國內／海外登錄餘額 3/3 檔：群聯三 TWD 6,000,000,000（面額）；群聯 海外 A USD 400,000,000（面額）；群聯 海外 B USD 400,000,000（面額）。目前轉換價核對 0/3；登錄欄位是發行時價格，不代替調整後現價。期後調價、全體存量完整性及股本同日核對仍待完成；台幣與美元不直接相加。 賣回日待核｜XS3364929045：登錄 2029-05-28／契約 2029-05-28／半年報周年／record date 2029-05-26；不同文件的標示差異尚待釐清，賣回相關計算停用。各券調價歷程分開維護；UNKNOWN 不代表沒有調整。 |
| 4 | Veto｜單一高風險地區產能 | missing | 0/1 | 高關稅／地緣單一地區产能 >80% 且無替代；缺資料不代表零曝險。 |
| 4 | Veto｜董監質押超過50% | missing | 0/1 | 判定採同月份董監合計質押股數／同範圍持有股數；須核對名單、代表人去重與分母，個人質押率不代替合計。 已保存 2026-09 董監明細 12 筆（出表 2026-10-15）；舊合計表 2026-08-19 為 7.81%，不當作本月比率。個別比例與董監合計口徑分開，合計待核時仍為未知。 |
| 4 | 10D 分級與組內權重原始規則 | missing | 0/1 | 引擎已實作；35／30／25／10 組權重已核對，分級尺度及組內權重須有原始規則來源 |
| 4 | 10D 可追溯分級 | missing | 0/10 | 1–4 分級與各項來源、規則版本須一致 |
| 4 | 三層漏斗評分 | missing | 0/3 | 公司40%、籌碼30%、進場／風控30%；不以 10D 平均替代 |
| 5 | 5A 同指標指引回測 | missing | 0/8 | 原始指引與同口徑實績配對 |
| 5 | 5B 財報前共識與實際 EPS | missing | 0/8 | 同股票、不同季度；共識日期早於財報公告 |
| 8 | 2027E 共識 | missing | 0/1 | 已核對 EPS、日期與來源，仍缺該年度至少3位分析師或3家券商的證據 |
| 8 | 直接同業共識與同日行情 | missing | 0/3 | 相同年度、TWD；相鄰產品與產業候選不湊數 |

### 能否由官方免費來源補：逐項判斷

| 缺口 | 官方免費可得程度 | 接線方式／限制 |
|---|---|---|
| PSR當期＋五年歷史 | 原始收盤、股數、月營收／財報可查；歷史完整性待逐日驗收 | 同日市值與一致收入期間重建，不用P/E替代PSR、不把年度點當完整五年最高 |
| 大戶分布＋連續性 | TDCC集保分級持股原表可查，頻率為週 | 核對股數、比例與分級，歷史實際累積，不補造過去週數 |
| 董監合計質押 | MOPS官方個別資料可查 | 同月同範圍分母、代表人去重與合計，不借舊月份或個人比例 |
| CB存量／現價／股本／匯率 | TPEx、MOPS、海外發行官方公告部分可得 | 每券每幣別分開；舊登錄價不等於調整後價；完整受託契約與事件通知可能非公開，維持UNKNOWN |
| 護城河／地緣產能／替代方案 | 年報、法說有部分原文 | 市占未明、委外不含實際產地；不能用資料數量代替質化比較或填0曝險 |
| 原始分級尺度與組內權重 | 不是外部市場資料問題 | 需原模型規則與擁有者決策，不能網搜或自行改公式 |
| 指引回測 | 僅公開數字財測公司有 | 群聯現核閱範圍屬結構性缺季度數字，年度不能拆季；其他公司匹配鍵、時間、頁碼需驗證 |
| 財報前共識／surprise | 財報實績免費；歷史時點共識不保證免費或可回溯 | 現在擷取的數字不變成過去快照；缺樣本不寫0驚喜 |
| 2027人數與直接同業兩年共識 | 供應商公開報導／存檔部分可得 | 不同供應商人數與EPS不混配；官方年報不提供分析師共識；同產業名單不等於直接可比 |

### 已核對的原始年報與 Yahoo 存檔

- 年報原文 `https://doc.twse.com.tw/pdf/2025_8299_20260527F04_20261019_214335.pdf`；持久保存 `https://raw.githubusercontent.com/479dvcs8zv-create/gate-probe/main/results/8299/annual_report/39262137932/files/57f8a21d0b03_2025_8299_20260527F04_20261019_214335.pdf`。
- GPT 已下載重算年報 SHA-256 `57f8a21d0b031abc24023867573175e9ad898c56be6a27ab88e613f032430061`，核對印刷頁73/78/79/80（PDF81/86/87/88）；擷取記錄 `2026-10-19T13:47:28.338173+00:00`。原發布日未知，不從檔名推定發布時間。
- Yahoo原頁 `https://finance.yahoo.com/quote/8299.TWO/analysis/`；Wayback `https://web.archive.org/web/20261019092747/https://finance.yahoo.com/quote/8299.TWO/analysis/`；raw `https://raw.githubusercontent.com/479dvcs8zv-create/gate-probe/main/results/8299/archive/39227156938/captures/yahoo_tw_analysis_20261019092747.bin`。
- GPT 已重算 raw gzip SHA-256 `da6d7a356a4465d8f64fcd1dfd75c1d99225a55e7f335e6fa512b68fa252f3c5`，解壓HTML SHA-256 `5d5f4218a153ac9e92ee78e0e35f22813ed2af2efb5617149a221d47272d4408`，由原表讀到 FY2027=12/281.54/95.37/414.28。原表只寫 Currency TWD，未宣告預估的會計口徑；擷取時間不能當發布時間。

## 回覆 03:25 的網站接收確認（依新優先序暫不擴充）

| 產出 | 接收判斷 | 現況／約束 |
|---|---|---|
| R1 時間界線 | 既有讀取維持 | 不擴B1、不回填歷史共識；用snapshot_boundary_at，不用cutoff_at放寬 |
| R2 官方指引配對 | 概念可接 Gate5A，正式契約仍需對照 | 等P1後再定輸入schema；先不要增加公司；不把Python預驗證當Gate PASS |
| R3 共識存檔人數 | 接受附來源的獨立coverage證據 | 本機8299試接完成，但非通用匯入器、未部署、不提供可計分EPS，不借給另一供應商 |
| R4 年報事實 | 接受結構化來源事實、分離評分 | 本機8299試接完成；頁碼、hash、期別、公司範圍必填，不任意解除警訊；其他代號未自動化 |
| R5 分析師vs公司財測 | 先不做 | P1優先，先確認面板與同口徑需求 |
| R6 A2/A3 | 本機與PR已接受並測試 | Site未部署、PR未合併、真實缺日未補 |

### B2 先前建議存檔（本輪不擴充）

「同頁上一季實際EPS＝官方基本EPS」是數值一致的間接證據，不能單獨證明預估口徑：可能當季無調整、四捨五入相同或下一期調整不同。仍需提供者明確定義或可核對調整橋接。我建議保留嚴格口徑，研究-only數值一致樣本可留存但不計Gate。

必須寫清的代價：**在來源持續未註明口徑、也沒有補足對賬證據的情況下，台股 EPS surprise 會一直沒有合格樣本（目前8299為0/8）；不得把缺樣本寫成零驚喜。** 這不是說所有台股永遠無法有樣本，新增真實口徑證據可改變判定。最終由擁有者決定，但依新P4這輪不擴充。

其餘待決定建議保留：B1條件納入季末保守界線須兩邊共同驗證、另標推算；B3不將模糊文字硬轉數字；B4官方原數字可驗證才比較；B5接受可追溯且早於實績的期中正式指引；B6同口徑同比／環比與百分點分開；B7/B8等P1～P3後另行授權，不新增自動化。

## 測試與重建方式

- Site `npm run build`：exit0。
- Site 完整 `npm test`：exit0，含新A2八項、Phison面板測試、全部既有Gate／VETO／來源隔離／UI契約。初跑曾因結構性文字覆蓋候選池筆數而失敗，已修正保留原筆數，最終完整重跑通過；不是未解失敗。
- 將新增檔納入diff後，`git diff --check`曾指出三檔尾端多空白行，已去除；僅格式變更，之後build與diffcheck再次exit0。下方diff是去除後最終完整版本。
- 全36列比較：所有值／觀測日／順序不變，沒有放寬原始來源驗證。JSON與重播結果見artifacts。
- 中繼：本機三組正式CI命令全部通過；PR上的三個run步驟也success。不能把pipeline顯示PASS 10/15當作最新session恢復；這項既有測試只核對串接，新的日期檢查測試另核對缺日拒收。
- A2八項含休市、提前收盤、DST、缺最新交易日、發布寬限、捕獲早於收盤、各類格式／來源錯誤、超出日曆範圍。日曆只覆蓋2026–2027，之後必須維護。

完整Site測試日誌另存artifact；以下為最終尾段：

```text
where the warning was created)
client diagnostics: bounded input, account isolation, safe fields, unauthenticated writes and expired reports passed
fallback risk rating: zero neutral contribution, B+ cap, 15% reference discount, historical substitute, risk deductions, veto priority, date guards and shared policy passed
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> test:cross-market
> node tests/cross-market.test.mjs && node tests/cross-market-live.test.mjs

cross-market: four states, independent 5/10/20D arithmetic, completed-close timing, EPS/provider/ticker isolation, missing data, funding units, zero duplicate scoring and VETO priority passed
cross-market live QA: TW 49/US 100 closes, dated sources, 9 independent RS results, real institutional/amount data, EPS UNKNOWN and unchanged v212 mobile layout passed
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> test:report-context
> node tests/report-context.test.mjs

report context: 19 live same-date FRED observations, lag/UNKNOWN validation, RSS excerpts, stock isolation, dated research references and unchanged scoring/VETO passed
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> test:stock-relay
> node tests/stock-relay.test.mjs

stock relay: four live official quotes, shared/D1 reads, source/ticker/date validation, UNKNOWN, atomic RETAINED_NEWER, rolling/PV recalculation and matching report prices passed
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> test:us-sector-site
> node --test tests/us-sector-session.test.mjs && node tests/us-sector-site.test.mjs

✔ 實檔：2026-10-17 01:28Z 產生、最後一天 10-15；10-19 10:26Z 應有 10-16 → LATEST_SESSION_MISSING（不是格式錯誤） (15.57741ms)
✔ 資料補上 10-16、擷取時間不變：週一早上仍可用（舊規則 57 小時會判 UNKNOWN） (1.059268ms)
✔ 只刷新 generated_at、資料沒變：仍是 LATEST_SESSION_MISSING (0.638884ms)
✔ 收盤後 8 小時內上游還沒發布：前一個交易日仍可用；超過才算缺 (0.769091ms)
✔ 擷取時間早於最後一列的收盤：CAPTURE_BEFORE_CLOSE (1.517531ms)
✔ 格式、來源、擷取時間各自的錯誤碼 (0.14581ms)
✔ NYSE 休市日、提前收盤、夏令時間結束 (0.961211ms)
✔ 超出休市日表的年份：失敗而不是放行 (0.786297ms)
ℹ tests 8
ℹ suites 0
ℹ pass 8
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 102.598019
US sector Site: 12 live ETFs, 66 independent RS comparisons, Taiwan-close timing, gaps/UNKNOWN, source/D1 retention, real report wiring and unchanged scoring/VETO passed
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> test:market-timeline
> node tests/market-timeline.test.mjs

market timeline: nine-field dates, real TWSE index arithmetic, older-relay retention, explicit unknown release times, cutoff safety, common-date intersection, CB partial provenance and stale VETO count passed
Phison panel: common-session intersection, real-history retention and gaps, structural guidance, source-isolated Yahoo coverage, annual facts and unchanged financial/VETO/scoring passed

```

中繼本機正式CI等效命令輸出：

```text
US sector context non-mutating report integration passed
✔ site-embed/us-sector-context.test.mjs (136.713811ms)
history calculations passed
history integrity rejection passed
✔ site-embed/us-sector-history.test.mjs (117.771723ms)
sector loader fallbacks passed
sector loader freshness gate passed
sector fetch abort fallback passed
incomplete report explicit status passed
✔ site-embed/us-sector-loader.test.mjs (112.853032ms)
sector report contract passed
✔ site-embed/us-sector-report.test.mjs (108.739836ms)
sector rotation smoke tests passed
✔ site-embed/us-sector-rotation.test.mjs (117.447155ms)
sector snapshot tests passed
sector metadata alignment tests passed
sector trading-session alignment test passed
✔ site-embed/us-sector-snapshot.test.mjs (111.431542ms)
ℹ tests 6
ℹ suites 0
ℹ pass 6
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 149.244646
Committed US sector snapshot -> API Worker -> Master Model report: PASS 2026-10-15
....................
----------------------------------------------------------------------
Ran 20 tests in 0.008s

OK

```

## 完整網站 git diff（含所有新增檔案與產生檔，未省略）

基準 `0dd0df41a3aed304a8b11bf7658c855b978ea337`；本機目錄 `master-gate5b-minimal-I2nTE1`。只有intent-to-add用於顯示新增檔，沒有網站commit/push/deploy。

```diff
diff --git a/build.mjs b/build.mjs
index 7e8f3fe..09b4ce3 100644
--- a/build.mjs
+++ b/build.mjs
@@ -15,9 +15,12 @@ const reportContext = readFileSync(new URL('./worker/report-context.js', import.
 const stockRelay = readFileSync(new URL('./worker/stock-relay.js', import.meta.url), 'utf8');
 const usSectorCore = readFileSync(new URL('./worker/us-sector-core.js', import.meta.url), 'utf8');
 const usSectors = readFileSync(new URL('./worker/us-sectors.js', import.meta.url), 'utf8');
+const usSectorSessionSource = readFileSync(new URL('./worker/us-sector-session.mjs', import.meta.url), 'utf8').replace(/^export /gm,'');
+const usSectorSession = `const US_SECTOR_SESSION=(()=>{${usSectorSessionSource}\nreturn {usSectorFreshness,isSession,calendarCovers,NYSE_EARLY_CLOSE,sessionSettledAt};})();`;
 const marketTimeline = readFileSync(new URL('./worker/market-timeline.js', import.meta.url), 'utf8');
 const masterEvidence = readFileSync(new URL('./worker/master-evidence.js', import.meta.url), 'utf8');
 const masterInputs = readFileSync(new URL('./worker/master-inputs.js', import.meta.url), 'utf8');
+const issuerContext = 'const ISSUER_CONTEXT_SEED = '+JSON.stringify(JSON.parse(readFileSync(new URL('./data/official/phison-panel-20261019.json',import.meta.url),'utf8')))+';\n'+readFileSync(new URL('./worker/issuer-context.js',import.meta.url),'utf8');
 const gate5bBoundaries = readFileSync(new URL('./worker/gate5b-boundaries.js', import.meta.url), 'utf8');
 const sharedNames=['masterEvidenceDate','masterEvidenceHttps','masterEvidenceSymbol','masterEvidencePeriod','masterPeriodEnd','summarizeMasterGuidance','summarizeMasterSurprises','masterGuidanceProblem','masterSurpriseProblem','gate5bQuarter','gate5bTimestamp','snapshotBeforeBoundary'];
 const evidenceSource=masterEvidence+'\n'+masterInputs+'\n'+gate5bBoundaries;
@@ -32,4 +35,4 @@ const officialNewsModule=readFileSync(new URL('./worker/official-news.js',import
 updateTools.sourceCollectorNode=updateTools.sourceCollectorNode.replace("let newsModule = '__OFFICIAL_NEWS_MODULE__';",`let newsModule = ${JSON.stringify(officialNewsModule)};`);
 const macro = readFileSync(new URL('./worker/macro.js', import.meta.url), 'utf8');
 mkdirSync(new URL('./dist/server/', import.meta.url), { recursive: true });
-writeFileSync(new URL('./dist/server/index.js', import.meta.url), `const HTML = ${JSON.stringify(html)};\nconst CPI_SEED = ${JSON.stringify(cpiSeed)};\nconst OFFICIAL_UPDATE_TOOLS = ${JSON.stringify(updateTools)};\n${observations}\n${observationFreshness}\nconst RELAY_SEED = ${JSON.stringify(relaySeed)};\n${relay}\n${research}\n${macroScoring}\n${dataImport}\n${sourceResearch}\n${reportContext}\n${stockRelay}\n${fallbackRating}\n${gate5bBoundaries}\n${masterEvidence}\n${masterInputs}\n${crossMarketCore}\n${crossMarket}\n${usSectorCore}\n${usSectors}\n${marketTimeline}\n${officialNewsModule}\n${macro}`);
+writeFileSync(new URL('./dist/server/index.js', import.meta.url), `const HTML = ${JSON.stringify(html)};\nconst CPI_SEED = ${JSON.stringify(cpiSeed)};\nconst OFFICIAL_UPDATE_TOOLS = ${JSON.stringify(updateTools)};\n${observations}\n${observationFreshness}\nconst RELAY_SEED = ${JSON.stringify(relaySeed)};\n${relay}\n${research}\n${macroScoring}\n${dataImport}\n${sourceResearch}\n${reportContext}\n${stockRelay}\n${fallbackRating}\n${gate5bBoundaries}\n${masterEvidence}\n${masterInputs}\n${issuerContext}\n${crossMarketCore}\n${crossMarket}\n${usSectorCore}\n${usSectorSession}\n${usSectors}\n${marketTimeline}\n${officialNewsModule}\n${macro}`);
diff --git a/data/official/phison-panel-20261019.json b/data/official/phison-panel-20261019.json
new file mode 100644
index 0000000..59c81b3
--- /dev/null
+++ b/data/official/phison-panel-20261019.json
@@ -0,0 +1,107 @@
+{
+  "symbol": "8299",
+  "asOf": "2026-10-19",
+  "guidanceDisclosure": {
+    "state": "structural_unavailable",
+    "label": "公司不提供季度財測（結構性）",
+    "reviewedThrough": "2026-10-19",
+    "scope": "本次已核對的重大訊息與法說範圍；有新季度量化財測時須重新核對",
+    "sourceType": "handoff_review",
+    "sourceUrl": "https://raw.githubusercontent.com/479dvcs8zv-create/gate-probe/main/handoff/CLAUDE_TO_GPT_LATEST.md",
+    "automaticGateApproval": false
+  },
+  "annual": {
+    "fiscalYear": 2025,
+    "publishedAt": null,
+    "filenameDate": "2026-05-27",
+    "capturedAt": "2026-10-19T13:47:28.338173+00:00",
+    "originalUrl": "https://doc.twse.com.tw/pdf/2025_8299_20260527F04_20261019_214335.pdf",
+    "artifactUrl": "https://raw.githubusercontent.com/479dvcs8zv-create/gate-probe/main/results/8299/annual_report/39262137932/files/57f8a21d0b03_2025_8299_20260527F04_20261019_214335.pdf",
+    "sha256": "57f8a21d0b031abc24023867573175e9ad898c56be6a27ab88e613f032430061",
+    "facts": [
+      {
+        "metric": "market_share",
+        "reportPage": 73,
+        "pdfPage": 81,
+        "state": "not_reported",
+        "value": null,
+        "summary": "FY2025 年報表示沒有明確市占率統計；不填入市占率數字。"
+      },
+      {
+        "metric": "customer_concentration",
+        "reportPage": 79,
+        "pdfPage": 87,
+        "state": "reported_upper_bound",
+        "upperBoundPercent": 10,
+        "operator": "<",
+        "summary": "FY2024、FY2025 均無單一銷售客戶占年度銷貨總額 10% 以上；不推成客戶名稱或精確占比。"
+      },
+      {
+        "metric": "supplier_purchase_share",
+        "reportPage": 78,
+        "pdfPage": 86,
+        "state": "reported",
+        "supplier": "台灣鎧俠",
+        "value": 28.33,
+        "unit": "% of FY2025 purchases",
+        "summary": "台灣鎧俠占 FY2025 進貨 28.33%；屬供應商進貨集中度，不是客戶營收占比。"
+      },
+      {
+        "metric": "production_model",
+        "reportPage": 80,
+        "pdfPage": 88,
+        "state": "reported",
+        "value": "outsourced",
+        "summary": "所有產品委由加工廠生產；未列各生產據點地址，地區曝險與替代產能仍未知。"
+      }
+    ]
+  },
+  "coverageObservations": [
+    {
+      "year": 2026,
+      "analysts": 10,
+      "epsAverage": 412.34,
+      "epsLow": 360.88,
+      "epsHigh": 478.35,
+      "provider": "Yahoo Finance",
+      "symbol": "8299",
+      "quote": "8299.TWO",
+      "currency": "TWD",
+      "capturedAt": "2026-10-19T09:27:47Z",
+      "publishedAt": null,
+      "accountingBasis": null,
+      "accountingBasisState": "not_stated",
+      "sourceUrl": "https://finance.yahoo.com/quote/8299.TWO/analysis/",
+      "archiveUrl": "https://web.archive.org/web/20261019092747/https://finance.yahoo.com/quote/8299.TWO/analysis/",
+      "artifactUrl": "https://raw.githubusercontent.com/479dvcs8zv-create/gate-probe/main/results/8299/archive/39227156938/captures/yahoo_tw_analysis_20261019092747.bin",
+      "sha256": "da6d7a356a4465d8f64fcd1dfd75c1d99225a55e7f335e6fa512b68fa252f3c5",
+      "decodedSha256": "5d5f4218a153ac9e92ee78e0e35f22813ed2af2efb5617149a221d47272d4408",
+      "coverageState": "verified_from_archived_table",
+      "productionEligible": false,
+      "limitation": "與 FactSet 數值及分析師人數分列；不借用人數、不建立季度 surprise 樣本。"
+    },
+    {
+      "year": 2027,
+      "analysts": 12,
+      "epsAverage": 281.54,
+      "epsLow": 95.37,
+      "epsHigh": 414.28,
+      "provider": "Yahoo Finance",
+      "symbol": "8299",
+      "quote": "8299.TWO",
+      "currency": "TWD",
+      "capturedAt": "2026-10-19T09:27:47Z",
+      "publishedAt": null,
+      "accountingBasis": null,
+      "accountingBasisState": "not_stated",
+      "sourceUrl": "https://finance.yahoo.com/quote/8299.TWO/analysis/",
+      "archiveUrl": "https://web.archive.org/web/20261019092747/https://finance.yahoo.com/quote/8299.TWO/analysis/",
+      "artifactUrl": "https://raw.githubusercontent.com/479dvcs8zv-create/gate-probe/main/results/8299/archive/39227156938/captures/yahoo_tw_analysis_20261019092747.bin",
+      "sha256": "da6d7a356a4465d8f64fcd1dfd75c1d99225a55e7f335e6fa512b68fa252f3c5",
+      "decodedSha256": "5d5f4218a153ac9e92ee78e0e35f22813ed2af2efb5617149a221d47272d4408",
+      "coverageState": "verified_from_archived_table",
+      "productionEligible": false,
+      "limitation": "與 FactSet 數值及分析師人數分列；不借用人數、不建立季度 surprise 樣本。"
+    }
+  ]
+}
diff --git a/dist/server/index.js b/dist/server/index.js
index c417c8b..c003d0d 100644
--- a/dist/server/index.js
+++ b/dist/server/index.js
@@ -1954,10 +1954,11 @@ function summarizeTaiwanMarket(rows = []) {
   const ids = ['TWSE_TAIEX','TWSE_TOTAL_TRADE_VALUE','TWSE_BREADTH','TPEX_BREADTH','TWSE_MARGIN_BALANCE_NTD','TWSE_SHORT_BALANCE','TWSE_MARGIN_MARKET_CAP_RATIO','TWSE_CREDIT_TRADE_VALUE','TWSE_DAYTRADE'];
   const by = Object.fromEntries(rows.map(row => [row.id, row]));
   const valid = id => ['ok','snapshot'].includes(by[id]?.status) && by[id]?.is_stale !== true && finiteNumber(by[id]?.value) && /^\d{4}-\d{2}-\d{2}$/.test(by[id]?.date || '');
-  const available = ids.filter(valid).map(id => ({ id, name: by[id].name, date: by[id].date, value: by[id].value, unit: by[id].unit, source: by[id].source }));
-  const dates = [...new Set(available.map(row => row.date))];
+  const latestAvailable = ids.filter(valid).map(id => ({ id, name: by[id].name, date: by[id].date, value: by[id].value, unit: by[id].unit, source: by[id].source }));
+  const dates = [...new Set(latestAvailable.map(row => row.date))];
   const dateAudit=buildMarketDateAudit(rows);
-  return { usable: available.length, total: ids.length, date: dates.length === 1 ? dates[0] : null, dates, aligned: dates.length === 1, complete: available.length === ids.length && dates.length === 1 && !dateAudit.fields.some(f=>['future_observation','not_available_at_cutoff'].includes(f.state)), available, dateAudit, missing: ids.filter(id => !valid(id)).map(id => ({ id, name: by[id]?.name || SERIES[id]?.[0] || id, reason: by[id]?.reason || '本次來源未回傳有效數值' })) };
+  const common=dateAudit.commonTradeDate,available=common?dateAudit.comparisonRows:latestAvailable,aligned=!!common||dates.length===1;
+  return { usable: available.length, total: ids.length, date: common||(dates.length === 1 ? dates[0] : null), dates, aligned, comparisonBasis:common?'latest_common_observed_session':'latest_observations',latestAvailable,complete: available.length === ids.length && aligned && !dateAudit.fields.some(f=>['future_observation','not_available_at_cutoff'].includes(f.state)), available, dateAudit, missing: ids.filter(id => !valid(id)).map(id => ({ id, name: by[id]?.name || SERIES[id]?.[0] || id, reason: by[id]?.reason || '本次來源未回傳有效數值' })) };
 }
 function evaluate(rows, internalRows=[]) {
   const by = Object.fromEntries([...rows,...internalRows].map(x => [x.id,x])), valid = id => ['ok','snapshot'].includes(by[id]?.status)&&by[id]?.is_stale!==true;
@@ -2174,10 +2175,10 @@ async function macroMarketResponse(env={},ctx={}) {
     rows.push(live10Y3MSpread(t10y3m?[...rows,t10y3m]:rows));
     const yen=macroMarketRows.find(row=>row.id==='DEXJPUS'),yenHistory=yen?.history||[];
     const rollingVol=(n)=>{const required=n+1,points=yenHistory.slice(-required);if(yen?.historyFetchState==='fetch_failed'||!yenHistory.length)return {value:null,state:'fetch_failed',reason:yen?.reason||'匯率歷史來源沒有回應'};if(yen?.historyFetchState==='source_stale'||yen?.status==='stale')return {value:null,state:'source_stale',reason:yen.reason||'匯率來源觀測已過期'};if(points.length<required)return {value:null,state:'sample_insufficient',reason:`已取回 ${yenHistory.length} 筆；${n} 日波動率需 ${required} 筆交易日資料`};const gap=points.slice(1).find((x,i)=>Date.parse(x.date)-Date.parse(points[i].date)>5*86400000);if(gap)return {value:null,state:'sample_insufficient',reason:`已取回 ${yenHistory.length} 筆，但計算窗口含超過 5 日的觀測缺口，無法視為連續交易日樣本`};const returns=points.slice(1).map((x,i)=>Math.log(x.value/points[i].value)).filter(Number.isFinite);if(returns.length!==n)return {value:null,state:'sample_insufficient',reason:`有效日報酬 ${returns.length}/${n}；樣本不足`};const mean=returns.reduce((a,b)=>a+b,0)/n,variance=returns.reduce((s,x)=>s+(x-mean)**2,0)/(n-1);return {value:Math.sqrt(variance*252)*100,state:'validated',reason:null};};
-    for(const n of [20,60]){const result=rollingVol(n);rows.push({id:`JPY_HV${n}`,name:`日圓匯率歷史波動率（${n} 日）`,group:'曲線／放大器',unit:'% 年化',value:result.value,date:yenHistory.at(-1)?.date||null,status:result.value==null?'missing':'ok',validationState:result.state,historyObservations:yenHistory.length,requiredObservations:n+1,reason:result.reason,provider:`${yen?.provider||'FRED／ECB 匯率來源'}；按日對數報酬年化標準差計算`,source:yen?.source||link('DEXJPUS')});}
+    for(const n of [20,60]){const result=rollingVol(n);rows.push({id:`JPY_HV${n}`,name:`日圓匯率歷史波動率（${n} 日）`,group:'曲線／放大器',unit:'% 年化',value:result.value,date:yenHistory.at(-1)?.date||null,derivedFrom:'DEXJPUS',parentDate:yenHistory.at(-1)?.date||null,status:result.value==null?'missing':'ok',validationState:result.state,historyObservations:yenHistory.length,requiredObservations:n+1,reason:result.reason,provider:`${yen?.provider||'FRED／ECB 匯率來源'}；按日對數報酬年化標準差計算`,source:yen?.source||link('DEXJPUS')});}
     const previous=await readRuntimeCache(env,'macro:v1');
-    const verified=mergeVerifiedMacroRows(rows,[lastGood,previous?.payload]);
-    return {checkedAt:new Date().toISOString(),rows:verified.map(({history,...row})=>row),taiwanMarket:summarizeTaiwanMarket(verified)};
+    const verified=retainTaiwanComparisonHistory(mergeVerifiedMacroRows(rows,[lastGood,previous?.payload]),[lastGood,previous?.payload]);
+    return {checkedAt:new Date().toISOString(),rows:verified.map(({history,...row})=>TAIWAN_MARKET_AUDIT_IDS.includes(row.id)?{...row,history}:row),taiwanMarket:summarizeTaiwanMarket(verified)};
   })().then(async payload=>{
     macroMarketCache={at:Date.now(),payload};
     await writeRuntimeCache(env,'macro-market:v7',payload,ttl);
@@ -2294,6 +2295,22 @@ function coreCpiVerificationCurrent(row,now=Date.now()) {
   return new Set(valid.map(reading=>reading.sourceFamily)).size===2;
 }
 function macroObservationCurrent(row,payload,now=Date.now()) {
+  const parentId=macroDerivedParentId(row);
+  if(parentId){
+    if(!['ok','snapshot','stale'].includes(row?.status)||row.validationState!=='validated'||!Number.isFinite(row.value)||!officialImportDate(row.date))return false;
+    const parent=payload?.rows?.find(item=>item.id===parentId);
+    if(!parent||parent.date!==row.date||row.parentDate!=null&&row.parentDate!==parent.date||!Number.isFinite(parent.value))return false;
+    const candidate=parent.status==='stale'&&parent.releaseVerification?{...parent,status:parent.snapshot?'snapshot':'ok',is_stale:false}:parent;
+    if(macroObservationCurrent(candidate,payload,now))return true;
+    // ECB/Frankfurter can provide a separately labeled reference-rate series
+    // with its own complete history. It may feed volatility, but never borrows
+    // the FRED release window; validate its capture, endpoint family and age.
+    if(parent.status==='proxy'&&parent.historyFetchState==='fetched'&&parent.historyObservations>=65&&
+      recentOfficialCapture(parent.verifiedAt||parent.fetchedAt||payload.checkedAt,now)&&age(parent.date)>=-1&&age(parent.date)<=(SERIES.DEXJPUS?.[3]??7)){
+      try{const source=new URL(parent.source);return source.protocol==='https:'&&['data.ecb.europa.eu','api.frankfurter.dev'].includes(source.hostname);}catch{return false;}
+    }
+    return false;
+  }
   if(!['ok','snapshot'].includes(row?.status)||row.is_stale||!Number.isFinite(row.value)||!officialImportDate(row.date))return false;
   // A monthly BLS capture and a recent BLS/FRED comparison use distinct clocks.
   if(row.id==='CPILFESL')return coreCpiVerificationCurrent(row,now);
@@ -2315,15 +2332,46 @@ function macroSnapshotRecent(payload) {
 }
 function mergeVerifiedMacroRows(rows,previous) {
   return rows.map(row=>{
-    if(['ok','snapshot'].includes(row?.status)&&!row.is_stale&&Number.isFinite(row.value))return {...row,verifiedAt:row.id==='CPILFESL'&&coreCpiVerificationCurrent(row)?row.sourceVerification.checkedAt:row.verifiedAt||row.fetchedAt||new Date().toISOString()};
+    if(['ok','snapshot'].includes(row?.status)&&!row.is_stale&&Number.isFinite(row.value))return {...row,verifiedAt:row.id==='CPILFESL'&&coreCpiVerificationCurrent(row)?row.sourceVerification.checkedAt:row.verifiedAt||row.fetchedAt||new Date().toISOString(),reason:obsoleteObservationReason(row.reason)?null:row.reason};
     const candidates=previous.flatMap(p=>(p?.rows||[]).filter(old=>old.id===row.id&&macroObservationCurrent(old,p)).map(old=>({old,p}))).sort((a,b)=>b.old.date.localeCompare(a.old.date)||Date.parse(b.old.verifiedAt||b.old.fetchedAt||b.p.checkedAt)-Date.parse(a.old.verifiedAt||a.old.fetchedAt||a.p.checkedAt));
     const best=candidates[0];
     if(!best)return row;
     return {...best.old,history:best.old.history||best.p.sourceHistories?.[row.id],status:'snapshot',snapshot:true,is_stale:false,sourceValidation:best.old.sourceValidation||{state:'passed',method:'保留有效期內上次已核對的來源觀測'},verifiedAt:best.old.verifiedAt||best.old.fetchedAt||best.p.checkedAt,refreshError:row.reason||'本次來源未完成核驗',reason:'本次來源暫不可用；保留有效期內已核實的官方觀測，日期不變。'};
   });
 }
+function obsoleteObservationReason(reason) {
+  return ['資料較舊，暫不納入判讀','觀測資料較舊，暫不納入判讀','EIA 觀測較舊，暫不納入判讀','保留前次成功觀測；資料較舊'].includes(reason);
+}
+function macroDerivedParentId(row) {
+  if(row?.derivedFrom==='DEXJPUS'||row?.id==='JPY_HV20'||row?.id==='JPY_HV60')return 'DEXJPUS';
+  return null;
+}
 function refreshingMacroSnapshot(payload,refreshing=true) {
-  const rows=(payload.rows||[]).map(row=>['ok','snapshot'].includes(row.status)&&!macroObservationCurrent(row,payload)?{...row,status:'stale',is_stale:true,reason:'官方觀測或最近來源核對已過有效期；等待更新。'}:row);
+  const sourceRows=payload.rows||[];
+  const refreshSource=row=>{
+    if(!['ok','snapshot','stale'].includes(row?.status))return row;
+    // A release-verified observation may remain current beyond its ordinary
+    // SERIES age. Re-evaluate stale rows with that evidence and keep status,
+    // is_stale and expiry reason aligned to the same final decision.
+    const candidate=row.status==='stale'&&row.releaseVerification?{...row,status:row.snapshot?'snapshot':'ok',is_stale:false}:row;
+    const current=macroObservationCurrent(candidate,payload);
+    if(current)return {...candidate,is_stale:false,reason:obsoleteObservationReason(candidate.reason)?null:candidate.reason};
+    if(['ok','snapshot'].includes(row.status))return {...row,status:'stale',is_stale:true,reason:'官方觀測或最近來源核對已過有效期；等待更新。'};
+    return {...row,is_stale:true,reason:obsoleteObservationReason(row.reason)?'官方觀測或最近來源核對已過有效期；等待更新。':row.reason};
+  };
+  // Refresh source observations first; derived rows inherit the parent's
+  // release/session validity instead of applying a generic seven-day clock.
+  const refreshed=sourceRows.map(row=>macroDerivedParentId(row)?row:refreshSource(row));
+  const parentPayload={...payload,rows:refreshed.filter(row=>!macroDerivedParentId(row))};
+  const rows=refreshed.map(row=>{
+    const parentId=macroDerivedParentId(row);
+    if(!parentId)return row;
+    const parent=parentPayload.rows.find(item=>item.id===parentId);
+    if(row.validationState!=='validated'||row.value==null)return row;
+    const dateMismatch=parent&&(parent.date!==row.date||row.parentDate!=null&&row.parentDate!==parent.date);
+    if(!parent||dateMismatch||!macroObservationCurrent(row,parentPayload))return {...row,value:null,status:'missing',is_stale:false,validationState:!parent?'source_missing':dateMismatch?'source_date_mismatch':'source_stale',reason:`母序列 ${parentId} 過期、未核或日期不一致；衍生波動率不納入判讀。`};
+    return {...row,derivedFrom:parentId,parentDate:parent.date,status:row.snapshot?'snapshot':'ok',is_stale:false,reason:null};
+  });
   const monthly=new Map(rows.filter(row=>['CPILFESL','PCEPILFE'].includes(row.id)).map(row=>[row.id,row]));
   const derived=(payload.derived||[]).map(row=>{
     const id=row.name?.startsWith('核心 CPI ')?'CPILFESL':row.name?.startsWith('核心 PCE ')?'PCEPILFE':null,parent=monthly.get(id);
@@ -3048,7 +3096,7 @@ async function importedOfficialSeries(id, env) {
   if(['US3M','US10Y','US30Y'].includes(id))row.name={US3M:'13 週期美國國庫券折現殖利率（DTB3）',US10Y:'10 年期美債官方殖利率（DGS10）',US30Y:'30 年期美債官方殖利率（DGS30）'}[id];
   const releaseVerification=input.releaseVerification;
   if (row.status!=='ok'&&!releaseObservationCurrent(id,{...row,releaseVerification})) return null;
-  return {...row,status:'ok',provider:'FRED／原始官方提供者｜經外部抓取並保存',source:input.source,fetchedAt:input.fetchedAt,releaseVerification,snapshot:true,is_stale:false,historyObservations:history.length,historyFetchState:'fetched',sourceValidation:{state:'passed',method:'官方 CSV 原始觀測；日期、正值、排序及筆數已校驗'},detail:`官方來源觀測 ${row.date}；擷取 ${input.fetchedAt}。${releaseVerification?`官方頁面同值核對；下一次發布 ${releaseVerification.nextReleaseDate}。`:''}${id==='DEXJPUS'?'FRED H.10 日參考匯率，非盤中價格；保留完整歷史供 20／60 日波動率。':id==='IORB'?'聯準會準備金餘額利率；保留同日配對所需歷史。':['US3M','US10Y','US30Y'].includes(id)?'官方利率序列；DTB3 為折現殖利率，DGS10／DGS30 為固定到期投資收益率。':'官方現貨系列，與近月期貨分開。'}`};
+  return {...row,status:'ok',reason:null,provider:'FRED／原始官方提供者｜經外部抓取並保存',source:input.source,fetchedAt:input.fetchedAt,releaseVerification,snapshot:true,is_stale:false,historyObservations:history.length,historyFetchState:'fetched',sourceValidation:{state:'passed',method:'官方 CSV 原始觀測；日期、正值、排序及筆數已校驗'},detail:`官方來源觀測 ${row.date}；擷取 ${input.fetchedAt}。${releaseVerification?`官方頁面同值核對；下一次發布 ${releaseVerification.nextReleaseDate}。`:''}${id==='DEXJPUS'?'FRED H.10 日參考匯率，非盤中價格；保留完整歷史供 20／60 日波動率。':id==='IORB'?'聯準會準備金餘額利率；保留同日配對所需歷史。':['US3M','US10Y','US30Y'].includes(id)?'官方利率序列；DTB3 為折現殖利率，DGS10／DGS30 為固定到期投資收益率。':'官方現貨系列，與近月期貨分開。'}`};
 }
 async function officialDataImport(request, env) {
   if (request.method!=='POST') return Response.json({error:'method_not_allowed'},{status:405,headers:jsonHeaders});
@@ -3810,7 +3858,7 @@ function masterQualifiedOutput({gates,stock,primaryValuation,veto,scoring,guidan
   const limits=[
     veto.status==='pending'?`否決條件仍有 ${veto.rules.filter(row=>row.state==='pending').length} 條待核；未判定安全。`:null,
     !scoring.ready?`10D 資料 ${10-missingDimensions}/10；原始分級、權重與三層評分須完整核驗，未評估項目不給中性分數。`:null,
-    !guidance.ready?`指引回測 ${guidance.samples}/8 期，樣本不足，不估管理層命中率。`:null,
+    !guidance.ready?guidance.applicability==='structural_unavailable'?`${guidance.disclosure.label}；依已核對範圍不估季度指引命中率。`:`指引回測 ${guidance.samples}/8 期，樣本不足，不估管理層命中率。`:null,
     !surprises.ready?`季度 EPS surprise ${surprises.samples}/8 期，樣本不足，不推定超預期表現。`:null,
     !current.ready?`${current.year} 共識尚未核驗，Forward P/E 不計算。`:null,
     !next.ready?`${next.year} 共識僅列輔助候選；分析師覆蓋未核驗，不計入評級。`:null,
@@ -4022,6 +4070,14 @@ function masterDimensionInputs(stock, records, today, consensus) {
   ];
 }
 
+const ISSUER_CONTEXT_SEED = {"symbol":"8299","asOf":"2026-10-19","guidanceDisclosure":{"state":"structural_unavailable","label":"公司不提供季度財測（結構性）","reviewedThrough":"2026-10-19","scope":"本次已核對的重大訊息與法說範圍；有新季度量化財測時須重新核對","sourceType":"handoff_review","sourceUrl":"https://raw.githubusercontent.com/479dvcs8zv-create/gate-probe/main/handoff/CLAUDE_TO_GPT_LATEST.md","automaticGateApproval":false},"annual":{"fiscalYear":2025,"publishedAt":null,"filenameDate":"2026-05-27","capturedAt":"2026-10-19T13:47:28.338173+00:00","originalUrl":"https://doc.twse.com.tw/pdf/2025_8299_20260527F04_20261019_214335.pdf","artifactUrl":"https://raw.githubusercontent.com/479dvcs8zv-create/gate-probe/main/results/8299/annual_report/39262137932/files/57f8a21d0b03_2025_8299_20260527F04_20261019_214335.pdf","sha256":"57f8a21d0b031abc24023867573175e9ad898c56be6a27ab88e613f032430061","facts":[{"metric":"market_share","reportPage":73,"pdfPage":81,"state":"not_reported","value":null,"summary":"FY2025 年報表示沒有明確市占率統計；不填入市占率數字。"},{"metric":"customer_concentration","reportPage":79,"pdfPage":87,"state":"reported_upper_bound","upperBoundPercent":10,"operator":"<","summary":"FY2024、FY2025 均無單一銷售客戶占年度銷貨總額 10% 以上；不推成客戶名稱或精確占比。"},{"metric":"supplier_purchase_share","reportPage":78,"pdfPage":86,"state":"reported","supplier":"台灣鎧俠","value":28.33,"unit":"% of FY2025 purchases","summary":"台灣鎧俠占 FY2025 進貨 28.33%；屬供應商進貨集中度，不是客戶營收占比。"},{"metric":"production_model","reportPage":80,"pdfPage":88,"state":"reported","value":"outsourced","summary":"所有產品委由加工廠生產；未列各生產據點地址，地區曝險與替代產能仍未知。"}]},"coverageObservations":[{"year":2026,"analysts":10,"epsAverage":412.34,"epsLow":360.88,"epsHigh":478.35,"provider":"Yahoo Finance","symbol":"8299","quote":"8299.TWO","currency":"TWD","capturedAt":"2026-10-19T09:27:47Z","publishedAt":null,"accountingBasis":null,"accountingBasisState":"not_stated","sourceUrl":"https://finance.yahoo.com/quote/8299.TWO/analysis/","archiveUrl":"https://web.archive.org/web/20261019092747/https://finance.yahoo.com/quote/8299.TWO/analysis/","artifactUrl":"https://raw.githubusercontent.com/479dvcs8zv-create/gate-probe/main/results/8299/archive/39227156938/captures/yahoo_tw_analysis_20261019092747.bin","sha256":"da6d7a356a4465d8f64fcd1dfd75c1d99225a55e7f335e6fa512b68fa252f3c5","decodedSha256":"5d5f4218a153ac9e92ee78e0e35f22813ed2af2efb5617149a221d47272d4408","coverageState":"verified_from_archived_table","productionEligible":false,"limitation":"與 FactSet 數值及分析師人數分列；不借用人數、不建立季度 surprise 樣本。"},{"year":2027,"analysts":12,"epsAverage":281.54,"epsLow":95.37,"epsHigh":414.28,"provider":"Yahoo Finance","symbol":"8299","quote":"8299.TWO","currency":"TWD","capturedAt":"2026-10-19T09:27:47Z","publishedAt":null,"accountingBasis":null,"accountingBasisState":"not_stated","sourceUrl":"https://finance.yahoo.com/quote/8299.TWO/analysis/","archiveUrl":"https://web.archive.org/web/20261019092747/https://finance.yahoo.com/quote/8299.TWO/analysis/","artifactUrl":"https://raw.githubusercontent.com/479dvcs8zv-create/gate-probe/main/results/8299/archive/39227156938/captures/yahoo_tw_analysis_20261019092747.bin","sha256":"da6d7a356a4465d8f64fcd1dfd75c1d99225a55e7f335e6fa512b68fa252f3c5","decodedSha256":"5d5f4218a153ac9e92ee78e0e35f22813ed2af2efb5617149a221d47272d4408","coverageState":"verified_from_archived_table","productionEligible":false,"limitation":"與 FactSet 數值及分析師人數分列；不借用人數、不建立季度 surprise 樣本。"}]};
+// Reviewed source facts are displayed independently of scoring inputs.
+function issuerEvidenceContext(symbol,today) {
+  const data=ISSUER_CONTEXT_SEED;
+  if(symbol!==data.symbol||!masterEvidenceDate(today)||today<data.asOf||Date.parse(today)-Date.parse(data.asOf)>395*86400000)return null;
+  return {...data,coverageObservations:data.coverageObservations.filter(row=>Date.parse(`${today}T23:59:59+08:00`)>=Date.parse(row.capturedAt)&&Date.parse(today)-Date.parse(row.capturedAt)<=90*86400000)};
+}
+
 // Upstream: https://github.com/wcr0936531039-png/macro-relay-service/blob/main/site-embed/cross-market-divergence.js
 // Kept unchanged; the server adapter adds history and evidence validation.
 /** Cross-market divergence gate. Pure logic, no DOM changes. */
@@ -4293,6 +4349,98 @@ function buildSectorReport(snapshot = {}) {
 return {SECTORS,returnsFromCloses,buildSectorReport};
 })();
 
+const US_SECTOR_SESSION=(()=>{// us_sector_session.mjs — 美股板塊快照「應有交易日」檢查（給 v228 的修補建議，gate-probe 不部署）
+//
+// 取代 normalizeUSSectorSnapshot 裡的「generated_at 距今 > 36 小時就丟 SCHEMA_SOURCE_OR_CAPTURE」：
+//   1. 格式、來源、擷取時間各自回報錯誤碼，不再混在一起。
+//   2. 時效改看「資料有沒有包含最後一個應有的交易日」，不看 generated_at 有多舊：
+//      週末、假日不會誤判過期；只刷新 generated_at、資料沒變，也不會被當成更新。
+//   3. 交易日依 NYSE 官方休市日與提前收盤日；超出表列年份就失敗（逼著更新表，不靜默放行）。
+//
+// NYSE 休市日與提前收盤：https://www.nyse.com/markets/hours-calendars（2026-10-19 讀取）
+
+const NYSE_HOLIDAYS = new Set([
+  '2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03', '2026-05-25', '2026-06-19', '2026-07-03',
+  '2026-09-07', '2026-11-26', '2026-12-25',
+  '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18', '2027-07-05',
+  '2027-09-06', '2027-11-25', '2027-12-24',
+]);
+const NYSE_EARLY_CLOSE = new Set(['2026-11-27', '2026-12-24', '2027-11-26']);   // 13:00 收盤
+const CALENDAR_FIRST_DAY = '2026-01-01';
+const CALENDAR_LAST_DAY = '2027-12-31';
+// 上游排程 23:35 UTC（週一至週五），GitHub 實際延遲約 1.9–2.5 小時（2026-10-14～10-17 的提交時間）；
+// 收盤後 8 小時內還沒發布，才算缺少該交易日。
+const PUBLISH_GRACE_HOURS = 8;
+const SETTLE_MINUTES = 15;   // 收盤後 15 分鐘才算完成（沿用 v228 的 16:15）
+
+const DAY = 86400000;
+const isDay = (s) => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && new Date(s + 'T00:00:00Z').toISOString().slice(0, 10) === s;
+const addDays = (s, n) => new Date(Date.parse(s + 'T00:00:00Z') + n * DAY).toISOString().slice(0, 10);
+
+function nyParts(ms) {
+  const p = Object.fromEntries(new Intl.DateTimeFormat('en-CA', {
+    timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit',
+    hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
+  }).formatToParts(new Date(ms)).map((x) => [x.type, x.value]));
+  return { day: `${p.year}-${p.month}-${p.day}`, minutes: Number(p.hour) * 60 + Number(p.minute) };
+}
+
+function calendarCovers(day) {
+  return isDay(day) && day >= CALENDAR_FIRST_DAY && day <= CALENDAR_LAST_DAY;
+}
+
+function isSession(day) {
+  if (!calendarCovers(day)) throw Error('CALENDAR_NOT_COVERED');
+  const wd = new Date(day + 'T00:00:00Z').getUTCDay();
+  return wd !== 0 && wd !== 6 && !NYSE_HOLIDAYS.has(day);
+}
+
+// 該交易日收盤後 15 分鐘的 UTC 時刻（夏令／冬令由 America/New_York 決定）
+function sessionSettledAt(day) {
+  const close = (NYSE_EARLY_CLOSE.has(day) ? 13 * 60 : 16 * 60) + SETTLE_MINUTES;
+  const noon = Date.parse(day + 'T12:00:00Z');
+  const ny = nyParts(noon);
+  const offsetMin = (ny.minutes - 12 * 60) + (ny.day < day ? -1440 : ny.day > day ? 1440 : 0);   // 紐約比 UTC 慢幾分鐘（負值）
+  return Date.parse(day + 'T00:00:00Z') + (close - offsetMin) * 60000;
+}
+
+// 現在這個時刻「應該已經有」的最後一個交易日
+function expectedLatestSession(now, graceHours = PUBLISH_GRACE_HOURS) {
+  let d = nyParts(now).day;
+  for (let i = 0; i < 15; i++, d = addDays(d, -1)) {
+    if (isSession(d) && now >= sessionSettledAt(d) + graceHours * 3600000) return d;
+  }
+  throw Error('NO_SESSION_FOUND');
+}
+
+// 回傳 {ok:true, observed, expected} 或 {ok:false, code, ...}；不丟例外，呼叫端照 code 顯示
+function usSectorFreshness(data, now = Date.now(), opts = {}) {
+  const grace = opts.graceHours ?? PUBLISH_GRACE_HOURS;
+  if (!data || typeof data !== 'object') return { ok: false, code: 'SCHEMA_MISMATCH', detail: 'root' };
+  if (data.schema_version !== 1) return { ok: false, code: 'SCHEMA_MISMATCH', detail: `schema_version=${data.schema_version}` };
+  if (data.source !== 'Yahoo Finance chart API (unofficial)') return { ok: false, code: 'SOURCE_MISMATCH', detail: String(data.source) };
+  if (!data.histories || typeof data.histories !== 'object' || Array.isArray(data.histories) || !data.status) {
+    return { ok: false, code: 'SCHEMA_MISMATCH', detail: 'histories/status' };
+  }
+  const captured = Date.parse(data.generated_at || '');
+  if (!Number.isFinite(captured)) return { ok: false, code: 'CAPTURE_INVALID', detail: String(data.generated_at) };
+  if (captured > now + 60000) return { ok: false, code: 'CAPTURE_IN_FUTURE', detail: data.generated_at };
+  const spy = Array.isArray(data.histories.SPY) ? data.histories.SPY : [];
+  const observed = spy.length ? spy[spy.length - 1].date : null;
+  if (!isDay(observed)) return { ok: false, code: 'BENCHMARK_UNAVAILABLE' };
+  let expected;
+  try {
+    if (!isSession(observed)) return { ok: false, code: 'NOT_A_SESSION', observed };
+    expected = expectedLatestSession(now, grace);
+  } catch (e) {
+    return { ok: false, code: e.message, observed };   // CALENDAR_NOT_COVERED：休市日表要更新
+  }
+  if (captured < sessionSettledAt(observed)) return { ok: false, code: 'CAPTURE_BEFORE_CLOSE', observed, captured_at: data.generated_at };
+  if (observed < expected) return { ok: false, code: 'LATEST_SESSION_MISSING', observed, expected, captured_at: data.generated_at };
+  return { ok: true, observed, expected, captured_at: data.generated_at };
+}
+
+return {usSectorFreshness,isSession,calendarCovers,NYSE_EARLY_CLOSE,sessionSettledAt};})();
 // Advisory ETF context on the existing Site; never a new score or VETO.
 const US_SECTOR_URL='https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/data/us_sector_history.json';
 const US_SECTOR_CACHE_KEY='us-sector-history:v1';
@@ -4304,11 +4452,12 @@ function usSectorClock(now) {
   return {day:`${parts.year}-${parts.month}-${parts.day}`,minutes:Number(parts.hour)*60+Number(parts.minute)};
 }
 function usSectorCloseCompleted(date,clock) {
-  return cmDate(date)&&![0,6].includes(new Date(date).getUTCDay())&&(date<clock.day||date===clock.day&&clock.minutes>=975);
+  return cmDate(date)&&US_SECTOR_SESSION.calendarCovers(date)&&US_SECTOR_SESSION.isSession(date)&&(date<clock.day||date===clock.day&&clock.minutes>=(US_SECTOR_SESSION.NYSE_EARLY_CLOSE.has(date)?795:975));
 }
 function normalizeUSSectorSnapshot(data,now=Date.now()) {
-  const captured=Date.parse(data?.generated_at||'');
-  if(data?.schema_version!==1||data.source!=='Yahoo Finance chart API (unofficial)'||!data.histories||typeof data.histories!=='object'||Array.isArray(data.histories)||!data.status||!Number.isFinite(captured)||captured>now+60000||now-captured>36*3600000)throw Error('SCHEMA_SOURCE_OR_CAPTURE');
+  const freshness=US_SECTOR_SESSION.usSectorFreshness(data,now);
+  if(!freshness.ok)throw Object.assign(Error(freshness.code),{freshness});
+  const captured=Date.parse(data.generated_at);
   const histories={},status={},currentClock=usSectorClock(now),captureClock=usSectorClock(captured);
   for(const id of ['SPY',...US_SECTOR_CORE.SECTORS]) {
     const rows=data.histories[id],state=data.status[id],valid=Array.isArray(rows)&&rows.length<=300&&rows.every(row=>usSectorCloseCompleted(row?.date,currentClock)&&usSectorCloseCompleted(row?.date,captureClock)&&typeof row.close==='number'&&Number.isFinite(row.close)&&row.close>0);
@@ -4318,11 +4467,11 @@ function normalizeUSSectorSnapshot(data,now=Date.now()) {
     histories[id]=ok?sorted:[];status[id]=ok?{status:'ok',observed_at:latest,count:sorted.length}:{status:'unknown',observed_at:state?.observed_at||null,count:0};
   }
   if(!histories.SPY.length)throw Error('BENCHMARK_UNAVAILABLE');
-  return {schema_version:1,generated_at:data.generated_at,source:data.source,histories,status,sourceObservedAt:histories.SPY.at(-1).date};
+  return {schema_version:1,generated_at:data.generated_at,source:data.source,histories,status,sourceObservedAt:histories.SPY.at(-1).date,sessionFreshness:freshness};
 }
 function evaluateUSSectorContext(snapshot,{referenceDate=null,now=Date.now()}={}) {
   const limits={scoreContribution:0,macroGateOverride:null,vetoOverride:null},unknown=reason=>({...US_SECTOR_CORE.buildSectorReport(),...limits,errorCode:reason,sourceUrl:US_SECTOR_URL,pending:!!snapshot?.pending,refreshing:!!snapshot?.refreshing,referenceDate,summary:`美股板塊 UNKNOWN：${reason}；其他報告繼續輸出，新增評分0。`});
-  let data;try{data=normalizeUSSectorSnapshot(snapshot,now);}catch(error){return unknown(snapshot?.error||error.message);}
+  let data;try{data=normalizeUSSectorSnapshot(snapshot,now);}catch(error){return {...unknown(snapshot?.error||error.message),sessionFreshness:error.freshness||null};}
   if(referenceDate!=null&&(!cmDate(referenceDate)||referenceDate>new Date(now+8*3600000).toISOString().slice(0,10)))return unknown('REFERENCE_DATE_INVALID');
   const sourceCoverage=['SPY',...US_SECTOR_CORE.SECTORS].filter(id=>data.status[id].status==='ok').length;
   const analysis={...data,histories:{},status:{}};
@@ -4386,6 +4535,25 @@ function preferMarketObservation(primary,fallback,now=Date.now()){
  if(a&&b)return fallback.date>primary.date?fallback:primary;
  return a?primary:b?fallback:primary||fallback;
 }
+function retainTaiwanComparisonHistory(rows,previous=[],now=Date.now()){
+ const today=new Date(now+8*3600000).toISOString().slice(0,10);
+ return rows.map(row=>{
+  if(!TAIWAN_MARKET_AUDIT_IDS.includes(row.id))return row;
+  const points=new Map(),conflicts=new Set();
+  for(const payload of [...previous,{rows}])for(const saved of (payload?.rows||[]).filter(item=>item.id===row.id)){
+   for(const point of [...(saved.history||[]),{date:saved.date,value:saved.value,source:saved.source,fetchedAt:saved.fetchedAt||saved.verifiedAt||payload.checkedAt,publishedAt:saved.publishedAt||null}]){
+    if(!marketAuditDate(point.date)||point.date>today||!Number.isFinite(point.value))continue;
+    const source=point.source||saved.source,captured=marketAuditInstant(point.fetchedAt||saved.fetchedAt||saved.verifiedAt||payload.checkedAt);
+    try{if(new URL(source).protocol!=='https:'||!captured||Date.parse(captured)>now)continue;}catch{continue;}
+    if(points.has(point.date)&&points.get(point.date).value!==point.value){points.delete(point.date);conflicts.add(point.date);continue;}
+    if(!conflicts.has(point.date))points.set(point.date,{date:point.date,value:point.value,source,fetchedAt:captured,publishedAt:point.publishedAt||null});
+   }
+  }
+  // Preserve only observed history. A disagreement removes that comparison
+  // point; it never supplies a filled value or replaces the latest row.
+  return {...row,history:[...points.values()].sort((a,b)=>a.date.localeCompare(b.date)).slice(-100),...(conflicts.size?{historyConflicts:[...conflicts]}:{})};
+ });
+}
 function parseLatestTaiwanIndices(payload,now=Date.now()){
  const key=String(payload?.date||''),date=/^\d{8}$/.test(key)?`${key.slice(0,4)}-${key.slice(4,6)}-${key.slice(6)}`:null;
  if(String(payload?.stat).toUpperCase()!=='OK'||!marketAuditDate(date)||date>new Date(now+8*3600000).toISOString().slice(0,10))throw Error('TWSE_AFTER_TRADING_DATE');
@@ -4418,9 +4586,10 @@ function buildMarketDateAudit(rows,{checkedAt=null,evaluationAt=Date.now()}={}){
   const reason=state==='aligned'?'與本次市場資料基準同日':state==='fetch_failed_retained'?`此欄位資料為 ${row.date}，非最新；更新失敗：${row.refreshError}`:state==='source_lag'?`此欄位資料為 ${row.date}，落後市場基準 ${referenceDate}；未取得來源更新證據，不推定尚未發布`:state==='not_available_at_cutoff'?'來源或首次擷取晚於評估時間，不可用於該截點':state==='future_observation'?'觀測日期在評估日之後':row.reason||'無有效資料或日期';
   return {id,name:row.name||id,dataPeriod:validDate?row.date:null,publishedAt,fetchedAt,availabilityBasis:publishedAt?'publisher_timestamp':fetchedAt?'first_observed_by_system':'unknown',availableByCutoff,state,reason,source:row.source||null};
  });
- const eligible=fields.filter(f=>['aligned','source_lag','fetch_failed_retained'].includes(f.state)&&f.availableByCutoff),sets=eligible.map(f=>{const row=by.get(f.id);return new Set([row.date,...(row.history||[]).filter(p=>marketAuditDate(p.date)&&p.date<=referenceDate&&Number.isFinite(p.value)).map(p=>p.date)]);});
- const common=eligible.length===TAIWAN_MARKET_AUDIT_IDS.length?[...(sets[0]||[])].filter(date=>sets.every(s=>s.has(date))).sort().at(-1)||null:null;
- const comparisonRows=common?eligible.map(f=>{const row=by.get(f.id),point=row.date===common?row:row.history.find(p=>p.date===common);return {id:row.id,name:row.name,date:common,value:point.value,unit:row.unit,source:row.source,publishedAt:f.publishedAt,fetchedAt:f.fetchedAt};}):[];
+ const eligible=fields.filter(f=>['aligned','source_lag','fetch_failed_retained'].includes(f.state)&&f.availableByCutoff),sets=eligible.map(f=>{const row=by.get(f.id);return new Set([row.date,...(row.history||[]).filter(p=>marketAuditDate(p.date)&&p.date<=row.date&&p.date<=referenceDate&&Number.isFinite(p.value)&&(!p.fetchedAt||marketAuditInstant(p.fetchedAt)&&Date.parse(p.fetchedAt)<=now)&&(!p.publishedAt||marketAuditInstant(p.publishedAt)&&Date.parse(p.publishedAt)<=now)).map(p=>p.date)]);});
+ const candidate=eligible.length===TAIWAN_MARKET_AUDIT_IDS.length?[...(sets[0]||[])].filter(date=>sets.every(s=>s.has(date))).sort().at(-1)||null:null;
+ const common=candidate&&(now-Date.parse(candidate))/86400000<=5?candidate:null;
+ const comparisonRows=common?eligible.map(f=>{const row=by.get(f.id),point=row.date===common?row:row.history.find(p=>p.date===common);return {id:row.id,name:row.name,date:common,value:point.value,unit:row.unit,source:point.source||row.source,publishedAt:row.date===common?f.publishedAt:marketAuditInstant(point.publishedAt),fetchedAt:marketAuditInstant(point.fetchedAt)||f.fetchedAt};}):[];
  return {version:1,evaluationAt:new Date(now).toISOString(),referenceDate,referenceDateBasis:'latest_valid_observed_trade_date',commonTradeDate:common,status:common?'COMMON_DATE_AVAILABLE':'DATE_ALIGNMENT_INCOMPLETE',usable:valid.length,total:TAIWAN_MARKET_AUDIT_IDS.length,fields,comparisonRows,pointInTimeReconstruction:false,limitations:['發布時間未知時保留 null；擷取時間只證明網站當時已見資料。','本次共同觀測日不是歷史資訊可得性的回測證明；不前填缺失交易日。']};
 }
 async function marketAuditResponse(response){
@@ -5146,6 +5315,8 @@ function evaluateMasterModel(stock, macro, market, freshness = {}, gateEvidence
   const today=new Date(Date.now()+8*3600000).toISOString().slice(0,10),years=[Number(today.slice(0,4)),Number(today.slice(0,4))+1];
   const officialPairs=pairMasterOfficialEvidence(gateEvidence.officialCompany?.records,stock.id,today,gateEvidence.gate5bBoundaries);
   const guidance=summarizeMasterGuidance([...officialPairs.guidance,...(gateEvidence.guidance||[])],stock.id,today),surprises=summarizeMasterSurprises([...officialPairs.surprises,...(gateEvidence.surprises||[])],stock.id,today,gateEvidence.gate5bBoundaries);
+  const issuerContext=issuerEvidenceContext(stock.id,today);
+  if(issuerContext?.guidanceDisclosure&&guidance.samples===0){guidance.applicability='structural_unavailable';guidance.disclosure=issuerContext.guidanceDisclosure;}
   const companyEstimates=verifiedCompanyConsensus(gateEvidence.officialCompany?.records,stock.id);
   const estimates=[...companyEstimates,...(gateEvidence.estimates||[])];
   const consensus=summarizeMasterConsensus(estimates,stock.id,today,years),peers=summarizeMasterPeers(gateEvidence.peerInputs,stock.id,today,years,price?.date);
@@ -5227,6 +5398,12 @@ function evaluateMasterModel(stock, macro, market, freshness = {}, gateEvidence
   gates.find(gate=>gate.id===4).detail+=`十維度必要資料已接入 ${tenDimensionReady}/10 項；請展開逐項缺口。`;
 
   gates.find(gate=>gate.id===5).checks=[check('5A 同指標指引回測',guidance.samples,8,guidance.metric||'原始指引與同口徑實績配對'),check('5B 財報前共識與實際 EPS',surprises.samples,8,'同股票、不同季度；共識日期早於財報公告')];
+  if(guidance.applicability==='structural_unavailable'){
+    const gate=gates.find(row=>row.id===5),disclosure=guidance.disclosure;
+    gate.guidanceApplicability=guidance.applicability;
+    gate.detail=`已自動讀取資料池：${gateEvidence.pool?.guidance||0} 筆公司指引候選、${gateEvidence.pool?.consensus||0} 筆 EPS 共識候選；${gateEvidence.pool?.status==='read_error'?'資料池讀取失敗，候選筆數待重查。':''}${disclosure.label}；核對範圍截至 ${disclosure.reviewedThrough}。${disclosure.scope}。已保存的年度指引及定性展望保留原類型；季度指引樣本不以年度數字補齊。有效市場 EPS surprise ${surprises.samples}/8 個不同季度；仍需界線前已存的季度共識與同口徑實績。`;
+    gate.checks[0]={...check('5A 季度數字財測',0,8,`${disclosure.label}；${disclosure.scope}`,'not_applicable'),applicability:'structural_unavailable'};
+  }
   const pairingProblems=[...officialPairs.rejected,...guidance.rejected.map(row=>({...row,gate:'5A'})),...surprises.rejected.map(row=>({...row,gate:'5B'}))];
   gates.find(gate=>gate.id===5).pairingAudit={engineStatus:'ready',officialGuidancePairs:officialPairs.guidance.length,officialSurprisePairs:officialPairs.surprises.length,rejected:pairingProblems};
   if(pairingProblems.length)gates.find(gate=>gate.id===5).detail+=`自動配對已執行；${[...new Set(pairingProblems.map(row=>row.reason))].join('；')}。`;
@@ -5238,6 +5415,7 @@ function evaluateMasterModel(stock, macro, market, freshness = {}, gateEvidence
     gate.dataState ||= gate.status==='evaluated'?'verified':gate.status==='warning'?'verified':'partial';
     if(!freshness.stockFresh&&[4,6,7,8,9,10].includes(gate.id))gate.dataState='stale';
     gate.nextAction=({3:'成熟股票依 95% 覆蓋核驗；新股獨立累積 21 個官方交易日，實際缺日仍須補齊。',4:'引擎已接軌；補核原始分級尺度、組內權重與各維度來源，逐條排除未知 Veto；真實警訊保留。',5:'自動來源持續保存；只有原始指引與實績配對、財報前共識日期均核對者才增加有效樣本。',6:qualityRisk?'核對負現金流、應收與庫存變動原因；真實警訊保留。':fq.roicApplicability?.status==='not_applicable'?'採現金流與其他適用財務比率判讀，ROIC 不沿用舊值。':'補齊最新季度必要財報欄位。',8:'自動依股票代號收集共識來源；補齊兩年共識及直接同業一致口徑，不以產業預測代替。',9:dcfFallback?'使用明列的跨週期替代情境，仍受其他 Gate 與財報警訊限制。':'核對 Rf、Beta、Kd 日期及實測資料後再確認 DCF。'})[gate.id]||null;
+    if(gate.id===5&&guidance.applicability==='structural_unavailable')gate.nextAction='季度財測屬結構性不可得；持續保存財報前季度共識，日後若有新數字財測再核對適用性。';
     const relevant=companyRecords.filter(row=>gate.id===4?['governance','veto_inputs'].includes(row.kind):gate.id===5?['quarterly_result','annual_result','management_guidance','quarterly_consensus','qualitative_outlook'].includes(row.kind):gate.id===6?row.kind==='financial_reconciliation'||row.review_type:null);
     gate.sources=relevant.map(row=>({label:`${row.period || ''} ${row.kind==='quarterly_result'?'財報實績':row.kind==='management_guidance'?'年度指引':row.kind==='qualitative_outlook'?'公司展望':row.kind==='governance'?'治理／訴訟':'財報核對'}`,url:row.source_url,sourceDate:row.source_date,detail:row.summary||row.body||'',validationStatus:row.validation_status}));
     if(gate.id===1)gate.sources=rows.filter(row=>OFFICIAL_IMPORT_SERIES.has(row.id)&&row.sourceValidation?.state==='passed').map(row=>({label:row.name,url:row.source,sourceDate:row.date,detail:`${row.value} ${row.unit}；${row.historyObservations} 筆官方觀測`,validationStatus:'VERIFIED_SOURCE'}));
@@ -5258,10 +5436,19 @@ function evaluateMasterModel(stock, macro, market, freshness = {}, gateEvidence
       gate.detail+=`依股票代號另已保存 ${announcements.length} 筆公司重大訊息；尚未抽取核對的指引不計入回測。`;
     }
   }
+  if(issuerContext){
+    const gate4=gates.find(row=>row.id===4),gate8=gates.find(row=>row.id===8),annual=issuerContext.annual;
+    gate4.annualEvidence=annual;
+    gate4.detail+=`FY${annual.fiscalYear} 年報已核對市占率揭露、客戶／供應商集中度與委外生產原文；生產據點與替代產能仍未知。`;
+    gate4.sources.push(...annual.facts.map(row=>({label:`FY${annual.fiscalYear} 年報第 ${row.reportPage} 頁｜${row.metric}`,url:annual.originalUrl,sourceDate:null,detail:`${row.summary}；PDF 第 ${row.pdfPage} 頁；擷取 ${annual.capturedAt}；SHA-256 ${annual.sha256}`,validationStatus:'VERIFIED_ARCHIVED_DOCUMENT'})));
+    gate8.coverageObservations=issuerContext.coverageObservations;
+    gate8.detail+=issuerContext.coverageObservations.map(row=>`${row.year}E Yahoo ${row.quote} 留存頁有 ${row.analysts} 位分析師，平均 EPS ${row.epsAverage} TWD（${row.epsLow}–${row.epsHigh}）；會計口徑未明示，獨立列參考，不借給 FactSet。`).join('');
+    gate8.sources.push(...issuerContext.coverageObservations.map(row=>({label:`${row.year}E Yahoo 分析師覆蓋（獨立留存）`,url:row.archiveUrl,sourceDate:null,detail:`擷取 ${row.capturedAt}；${row.analysts} 位；平均 EPS ${row.epsAverage} TWD；原始發布日及會計口徑未明示；SHA-256 ${row.sha256}`,validationStatus:'COVERAGE_VERIFIED_BASIS_PENDING'})));
+  }
   // Context uses the existing Gate 1/2/3 mechanisms without adding points or a
   // new readiness blocker. Missing cross-market data cannot freeze the report.
   gates[0].detail+=` ${crossMarket.summary}`;
-  gates[1].checks=(taiwan?.dateAudit?.fields||[]).map(row=>({label:row.name,available:row.state==='aligned'?1:0,required:1,state:row.state==='aligned'?'verified':'missing',detail:`資料所屬期 ${row.dataPeriod||'UNKNOWN'}；發布 ${row.publishedAt||'來源未提供'}；擷取 ${row.fetchedAt||'UNKNOWN'}；${row.reason}`}));
+  gates[1].checks=(taiwan?.dateAudit?.fields||[]).map(row=>{const point=taiwan.dateAudit.comparisonRows.find(item=>item.id===row.id),aligned=!!point||row.state==='aligned';return {label:row.name,available:aligned?1:0,required:1,state:aligned?'verified':'missing',detail:`最新資料所屬期 ${row.dataPeriod||'UNKNOWN'}；發布 ${row.publishedAt||'來源未提供'}；擷取 ${row.fetchedAt||'UNKNOWN'}；${point?`共同交易日 ${point.date}，實際觀測 ${point.value} ${point.unit||''}；最新市場基準 ${taiwan.dateAudit.referenceDate}，不補值或變更原日期。`:row.reason}`};});
   for(const rule of veto.rules)if(rule.evidence)(gates[3].sources||=[]).push({label:`Veto ${rule.label}｜官方證據`,url:rule.evidence.sourceUrl,sourceDate:rule.evidence.publishedAt,detail:rule.detail,validationStatus:rule.state==='pending'?'PARTIAL_OFFICIAL_EVIDENCE':'VERIFIED_SOURCE'});
   for(const source of veto.rules.find(row=>row.id==='cb')?.registryReview?.sources||[])if(masterEvidenceHttps(source.source_url))(gates[3].sources||=[]).push({label:'CB 登錄／原始契約來源',url:source.source_url,sourceDate:source.document_date||null,detail:source.scope||'資料登錄與條款核對；不代表完整 VETO 已排除。',validationStatus:'PARTIAL_OFFICIAL_EVIDENCE'});
   gates[0].contextAssessments=[crossMarket,rateContext,usSectorContext];
diff --git a/package.json b/package.json
index f0f2170..68ed411 100644
--- a/package.json
+++ b/package.json
@@ -5,7 +5,7 @@
     "build": "node build.mjs",
     "test:master-validation": "node tests/master-model-validation.test.mjs",
     "db:generate": "drizzle-kit generate",
-    "test": "node tests/runtime-cache.test.mjs && node tests/master-gate-evidence.test.mjs && node tests/master-gate-pipeline.test.mjs && node tests/research-package-cloud.test.mjs && node tests/data-package.test.mjs && node tests/guidance-report.test.mjs && node tests/automatic-research.test.mjs && node tests/site-automation.test.mjs && node tests/site-module-contract.test.mjs && node tests/valuation-render.test.mjs && node tests/macro-market-state.test.mjs && node tests/core-cpi-ingestion.test.mjs && node tests/core-cpi-collector.test.mjs && node tests/cnn-fear-greed.test.mjs && node tests/financial-quality.test.mjs && node tests/relay-freshness.test.mjs && node tests/observation-freshness.test.mjs && node tests/monthly-release-news.test.mjs && node tests/macro-source-isolation.test.mjs && node tests/financial-analysis.test.mjs && node tests/official-collector.test.mjs && node tests/official-data-import.test.mjs && node tests/source-research.test.mjs && node tests/dashboard-interactions.test.mjs && node tests/master-model-validation.test.mjs && node tests/master-remediation.test.mjs && node tests/master-input-wiring.test.mjs && node tests/qualified-output.test.mjs && node tests/client-diagnostics.test.mjs && node tests/fallback-rating.test.mjs && npm run test:cross-market && npm run test:report-context && npm run test:stock-relay && npm run test:us-sector-site && npm run test:market-timeline",
+    "test": "node tests/runtime-cache.test.mjs && node tests/master-gate-evidence.test.mjs && node tests/master-gate-pipeline.test.mjs && node tests/research-package-cloud.test.mjs && node tests/data-package.test.mjs && node tests/guidance-report.test.mjs && node tests/automatic-research.test.mjs && node tests/site-automation.test.mjs && node tests/site-module-contract.test.mjs && node tests/valuation-render.test.mjs && node tests/macro-market-state.test.mjs && node tests/core-cpi-ingestion.test.mjs && node tests/core-cpi-collector.test.mjs && node tests/cnn-fear-greed.test.mjs && node tests/financial-quality.test.mjs && node tests/relay-freshness.test.mjs && node tests/observation-freshness.test.mjs && node tests/monthly-release-news.test.mjs && node tests/macro-source-isolation.test.mjs && node tests/financial-analysis.test.mjs && node tests/official-collector.test.mjs && node tests/official-data-import.test.mjs && node tests/source-research.test.mjs && node tests/dashboard-interactions.test.mjs && node tests/master-model-validation.test.mjs && node tests/master-remediation.test.mjs && node tests/master-input-wiring.test.mjs && node tests/qualified-output.test.mjs && node tests/client-diagnostics.test.mjs && node tests/fallback-rating.test.mjs && npm run test:cross-market && npm run test:report-context && npm run test:stock-relay && npm run test:us-sector-site && npm run test:market-timeline && node tests/phison-panel.test.mjs",
     "test:remediation": "node tests/master-remediation.test.mjs",
     "test:qualified-output": "node tests/qualified-output.test.mjs",
     "test:client-diagnostics": "node tests/client-diagnostics.test.mjs",
@@ -13,7 +13,7 @@
     "test:cross-market": "node tests/cross-market.test.mjs && node tests/cross-market-live.test.mjs",
     "test:report-context": "node tests/report-context.test.mjs",
     "test:stock-relay": "node tests/stock-relay.test.mjs",
-    "test:us-sector-site": "node tests/us-sector-site.test.mjs",
+    "test:us-sector-site": "node --test tests/us-sector-session.test.mjs && node tests/us-sector-site.test.mjs",
     "test:market-timeline": "node tests/market-timeline.test.mjs"
   },
   "devDependencies": {
diff --git a/tests/fixtures/us-sector-bdb0edd.json b/tests/fixtures/us-sector-bdb0edd.json
new file mode 100644
index 0000000..f12ca5b
--- /dev/null
+++ b/tests/fixtures/us-sector-bdb0edd.json
@@ -0,0 +1,3165 @@
+{
+  "schema_version": 1,
+  "generated_at": "2026-10-17T01:28:36.371009+00:00",
+  "source": "Yahoo Finance chart API (unofficial)",
+  "histories": {
+    "SPY": [
+      {
+        "date": "2026-07-17",
+        "close": 743.289978
+      },
+      {
+        "date": "2026-07-20",
+        "close": 742.090027
+      },
+      {
+        "date": "2026-07-21",
+        "close": 748.280029
+      },
+      {
+        "date": "2026-07-22",
+        "close": 747.409973
+      },
+      {
+        "date": "2026-07-23",
+        "close": 738.179993
+      },
+      {
+        "date": "2026-07-24",
+        "close": 738.929993
+      },
+      {
+        "date": "2026-07-27",
+        "close": 739.090027
+      },
+      {
+        "date": "2026-07-28",
+        "close": 740.859985
+      },
+      {
+        "date": "2026-07-29",
+        "close": 729.460022
+      },
+      {
+        "date": "2026-07-30",
+        "close": 741.690002
+      },
+      {
+        "date": "2026-07-31",
+        "close": 747.030029
+      },
+      {
+        "date": "2026-08-03",
+        "close": 757.669983
+      },
+      {
+        "date": "2026-08-04",
+        "close": 771.330017
+      },
+      {
+        "date": "2026-08-05",
+        "close": 769.789978
+      },
+      {
+        "date": "2026-08-06",
+        "close": 768.559998
+      },
+      {
+        "date": "2026-08-07",
+        "close": 773.26001
+      },
+      {
+        "date": "2026-08-10",
+        "close": 773.030029
+      },
+      {
+        "date": "2026-08-11",
+        "close": 770.559998
+      },
+      {
+        "date": "2026-08-12",
+        "close": 772.48999
+      },
+      {
+        "date": "2026-08-13",
+        "close": 777.880005
+      },
+      {
+        "date": "2026-08-14",
+        "close": 776.340027
+      },
+      {
+        "date": "2026-08-17",
+        "close": 772.669983
+      },
+      {
+        "date": "2026-08-18",
+        "close": 767.450012
+      },
+      {
+        "date": "2026-08-19",
+        "close": 769.059998
+      },
+      {
+        "date": "2026-08-20",
+        "close": 762.599976
+      },
+      {
+        "date": "2026-08-21",
+        "close": 765.719971
+      },
+      {
+        "date": "2026-08-24",
+        "close": 763.469971
+      },
+      {
+        "date": "2026-08-25",
+        "close": 765.909973
+      },
+      {
+        "date": "2026-08-26",
+        "close": 766.080017
+      },
+      {
+        "date": "2026-08-27",
+        "close": 771.099976
+      },
+      {
+        "date": "2026-08-28",
+        "close": 769.349976
+      },
+      {
+        "date": "2026-08-31",
+        "close": 767.049988
+      },
+      {
+        "date": "2026-09-01",
+        "close": 761.780029
+      },
+      {
+        "date": "2026-09-02",
+        "close": 765.159973
+      },
+      {
+        "date": "2026-09-03",
+        "close": 773.169983
+      },
+      {
+        "date": "2026-09-04",
+        "close": 770.190002
+      },
+      {
+        "date": "2026-09-08",
+        "close": 765.960022
+      },
+      {
+        "date": "2026-09-09",
+        "close": 762.400024
+      },
+      {
+        "date": "2026-09-10",
+        "close": 757.830017
+      },
+      {
+        "date": "2026-09-11",
+        "close": 764.289978
+      },
+      {
+        "date": "2026-09-14",
+        "close": 760.880005
+      },
+      {
+        "date": "2026-09-15",
+        "close": 757.390015
+      },
+      {
+        "date": "2026-09-16",
+        "close": 754.049988
+      },
+      {
+        "date": "2026-09-17",
+        "close": 762.599976
+      },
+      {
+        "date": "2026-09-18",
+        "close": 761.690002
+      },
+      {
+        "date": "2026-09-21",
+        "close": 773.5
+      },
+      {
+        "date": "2026-09-22",
+        "close": 773.380005
+      },
+      {
+        "date": "2026-09-23",
+        "close": 767.809998
+      },
+      {
+        "date": "2026-09-24",
+        "close": 767.179993
+      },
+      {
+        "date": "2026-09-25",
+        "close": 771.349976
+      },
+      {
+        "date": "2026-09-28",
+        "close": 765.609985
+      },
+      {
+        "date": "2026-09-29",
+        "close": 764.200012
+      },
+      {
+        "date": "2026-09-30",
+        "close": 762.630005
+      },
+      {
+        "date": "2026-10-01",
+        "close": 763.98999
+      },
+      {
+        "date": "2026-10-02",
+        "close": 769.640015
+      },
+      {
+        "date": "2026-10-05",
+        "close": 774.830017
+      },
+      {
+        "date": "2026-10-06",
+        "close": 779.090027
+      },
+      {
+        "date": "2026-10-07",
+        "close": 777.219971
+      },
+      {
+        "date": "2026-10-08",
+        "close": 773.929993
+      },
+      {
+        "date": "2026-10-09",
+        "close": 778.570007
+      },
+      {
+        "date": "2026-10-12",
+        "close": 778.099976
+      },
+      {
+        "date": "2026-10-13",
+        "close": 778.01001
+      },
+      {
+        "date": "2026-10-14",
+        "close": 769.599976
+      },
+      {
+        "date": "2026-10-15",
+        "close": 771.789978
+      }
+    ],
+    "XLK": [
+      {
+        "date": "2026-07-17",
+        "close": 175.589996
+      },
+      {
+        "date": "2026-07-20",
+        "close": 175.710007
+      },
+      {
+        "date": "2026-07-21",
+        "close": 180.779999
+      },
+      {
+        "date": "2026-07-22",
+        "close": 180.270004
+      },
+      {
+        "date": "2026-07-23",
+        "close": 178.449997
+      },
+      {
+        "date": "2026-07-24",
+        "close": 175.880005
+      },
+      {
+        "date": "2026-07-27",
+        "close": 174.300003
+      },
+      {
+        "date": "2026-07-28",
+        "close": 171.089996
+      },
+      {
+        "date": "2026-07-29",
+        "close": 166.570007
+      },
+      {
+        "date": "2026-07-30",
+        "close": 175.729996
+      },
+      {
+        "date": "2026-07-31",
+        "close": 175.350006
+      },
+      {
+        "date": "2026-08-03",
+        "close": 178.039993
+      },
+      {
+        "date": "2026-08-04",
+        "close": 186.899994
+      },
+      {
+        "date": "2026-08-05",
+        "close": 185.910004
+      },
+      {
+        "date": "2026-08-06",
+        "close": 185.330002
+      },
+      {
+        "date": "2026-08-07",
+        "close": 187.970001
+      },
+      {
+        "date": "2026-08-10",
+        "close": 186.320007
+      },
+      {
+        "date": "2026-08-11",
+        "close": 186.089996
+      },
+      {
+        "date": "2026-08-12",
+        "close": 188.860001
+      },
+      {
+        "date": "2026-08-13",
+        "close": 190.770004
+      },
+      {
+        "date": "2026-08-14",
+        "close": 190.009995
+      },
+      {
+        "date": "2026-08-17",
+        "close": 190.320007
+      },
+      {
+        "date": "2026-08-18",
+        "close": 185.619995
+      },
+      {
+        "date": "2026-08-19",
+        "close": 183.639999
+      },
+      {
+        "date": "2026-08-20",
+        "close": 183.100006
+      },
+      {
+        "date": "2026-08-21",
+        "close": 183.309998
+      },
+      {
+        "date": "2026-08-24",
+        "close": 180.050003
+      },
+      {
+        "date": "2026-08-25",
+        "close": 181.740005
+      },
+      {
+        "date": "2026-08-26",
+        "close": 182.839996
+      },
+      {
+        "date": "2026-08-27",
+        "close": 188.610001
+      },
+      {
+        "date": "2026-08-28",
+        "close": 185.690002
+      },
+      {
+        "date": "2026-08-31",
+        "close": 186.5
+      },
+      {
+        "date": "2026-09-01",
+        "close": 183.639999
+      },
+      {
+        "date": "2026-09-02",
+        "close": 183.600006
+      },
+      {
+        "date": "2026-09-03",
+        "close": 185.970001
+      },
+      {
+        "date": "2026-09-04",
+        "close": 187.279999
+      },
+      {
+        "date": "2026-09-08",
+        "close": 187.869995
+      },
+      {
+        "date": "2026-09-09",
+        "close": 187.869995
+      },
+      {
+        "date": "2026-09-10",
+        "close": 185.220001
+      },
+      {
+        "date": "2026-09-11",
+        "close": 187.669998
+      },
+      {
+        "date": "2026-09-14",
+        "close": 184.279999
+      },
+      {
+        "date": "2026-09-15",
+        "close": 183.740005
+      },
+      {
+        "date": "2026-09-16",
+        "close": 183.929993
+      },
+      {
+        "date": "2026-09-17",
+        "close": 188.059998
+      },
+      {
+        "date": "2026-09-18",
+        "close": 189.600006
+      },
+      {
+        "date": "2026-09-21",
+        "close": 194.850006
+      },
+      {
+        "date": "2026-09-22",
+        "close": 196.270004
+      },
+      {
+        "date": "2026-09-23",
+        "close": 195.339996
+      },
+      {
+        "date": "2026-09-24",
+        "close": 194.710007
+      },
+      {
+        "date": "2026-09-25",
+        "close": 196.270004
+      },
+      {
+        "date": "2026-09-28",
+        "close": 194.529999
+      },
+      {
+        "date": "2026-09-29",
+        "close": 194.5
+      },
+      {
+        "date": "2026-09-30",
+        "close": 195.75
+      },
+      {
+        "date": "2026-10-01",
+        "close": 197.809998
+      },
+      {
+        "date": "2026-10-02",
+        "close": 199.809998
+      },
+      {
+        "date": "2026-10-05",
+        "close": 200.929993
+      },
+      {
+        "date": "2026-10-06",
+        "close": 202.0
+      },
+      {
+        "date": "2026-10-07",
+        "close": 201.389999
+      },
+      {
+        "date": "2026-10-08",
+        "close": 197.779999
+      },
+      {
+        "date": "2026-10-09",
+        "close": 198.779999
+      },
+      {
+        "date": "2026-10-12",
+        "close": 196.360001
+      },
+      {
+        "date": "2026-10-13",
+        "close": 196.279999
+      },
+      {
+        "date": "2026-10-14",
+        "close": 190.429993
+      },
+      {
+        "date": "2026-10-15",
+        "close": 189.190002
+      }
+    ],
+    "XLC": [
+      {
+        "date": "2026-07-17",
+        "close": 110.650002
+      },
+      {
+        "date": "2026-07-20",
+        "close": 110.800003
+      },
+      {
+        "date": "2026-07-21",
+        "close": 110.029999
+      },
+      {
+        "date": "2026-07-22",
+        "close": 109.199997
+      },
+      {
+        "date": "2026-07-23",
+        "close": 105.379997
+      },
+      {
+        "date": "2026-07-24",
+        "close": 106.300003
+      },
+      {
+        "date": "2026-07-27",
+        "close": 107.660004
+      },
+      {
+        "date": "2026-07-28",
+        "close": 109.669998
+      },
+      {
+        "date": "2026-07-29",
+        "close": 109.510002
+      },
+      {
+        "date": "2026-07-30",
+        "close": 106.580002
+      },
+      {
+        "date": "2026-07-31",
+        "close": 108.239998
+      },
+      {
+        "date": "2026-08-03",
+        "close": 111.339996
+      },
+      {
+        "date": "2026-08-04",
+        "close": 112.040001
+      },
+      {
+        "date": "2026-08-05",
+        "close": 110.870003
+      },
+      {
+        "date": "2026-08-06",
+        "close": 111.18
+      },
+      {
+        "date": "2026-08-07",
+        "close": 111.25
+      },
+      {
+        "date": "2026-08-10",
+        "close": 111.830002
+      },
+      {
+        "date": "2026-08-11",
+        "close": 111.269997
+      },
+      {
+        "date": "2026-08-12",
+        "close": 110.269997
+      },
+      {
+        "date": "2026-08-13",
+        "close": 112.550003
+      },
+      {
+        "date": "2026-08-14",
+        "close": 112.949997
+      },
+      {
+        "date": "2026-08-17",
+        "close": 110.82
+      },
+      {
+        "date": "2026-08-18",
+        "close": 110.480003
+      },
+      {
+        "date": "2026-08-19",
+        "close": 111.32
+      },
+      {
+        "date": "2026-08-20",
+        "close": 110.68
+      },
+      {
+        "date": "2026-08-21",
+        "close": 111.400002
+      },
+      {
+        "date": "2026-08-24",
+        "close": 112.32
+      },
+      {
+        "date": "2026-08-25",
+        "close": 113.18
+      },
+      {
+        "date": "2026-08-26",
+        "close": 112.610001
+      },
+      {
+        "date": "2026-08-27",
+        "close": 111.410004
+      },
+      {
+        "date": "2026-08-28",
+        "close": 112.989998
+      },
+      {
+        "date": "2026-08-31",
+        "close": 111.459999
+      },
+      {
+        "date": "2026-09-01",
+        "close": 110.879997
+      },
+      {
+        "date": "2026-09-02",
+        "close": 112.419998
+      },
+      {
+        "date": "2026-09-03",
+        "close": 113.379997
+      },
+      {
+        "date": "2026-09-04",
+        "close": 112.029999
+      },
+      {
+        "date": "2026-09-08",
+        "close": 111.519997
+      },
+      {
+        "date": "2026-09-09",
+        "close": 110.830002
+      },
+      {
+        "date": "2026-09-10",
+        "close": 111.5
+      },
+      {
+        "date": "2026-09-11",
+        "close": 112.599998
+      },
+      {
+        "date": "2026-09-14",
+        "close": 115.07
+      },
+      {
+        "date": "2026-09-15",
+        "close": 114.029999
+      },
+      {
+        "date": "2026-09-16",
+        "close": 113.0
+      },
+      {
+        "date": "2026-09-17",
+        "close": 112.349998
+      },
+      {
+        "date": "2026-09-18",
+        "close": 110.809998
+      },
+      {
+        "date": "2026-09-21",
+        "close": 114.75
+      },
+      {
+        "date": "2026-09-22",
+        "close": 113.529999
+      },
+      {
+        "date": "2026-09-23",
+        "close": 112.559998
+      },
+      {
+        "date": "2026-09-24",
+        "close": 113.989998
+      },
+      {
+        "date": "2026-09-25",
+        "close": 112.959999
+      },
+      {
+        "date": "2026-09-28",
+        "close": 111.18
+      },
+      {
+        "date": "2026-09-29",
+        "close": 111.470001
+      },
+      {
+        "date": "2026-09-30",
+        "close": 110.970001
+      },
+      {
+        "date": "2026-10-01",
+        "close": 109.940002
+      },
+      {
+        "date": "2026-10-02",
+        "close": 110.32
+      },
+      {
+        "date": "2026-10-05",
+        "close": 111.610001
+      },
+      {
+        "date": "2026-10-06",
+        "close": 111.650002
+      },
+      {
+        "date": "2026-10-07",
+        "close": 111.260002
+      },
+      {
+        "date": "2026-10-08",
+        "close": 112.07
+      },
+      {
+        "date": "2026-10-09",
+        "close": 110.379997
+      },
+      {
+        "date": "2026-10-12",
+        "close": 111.449997
+      },
+      {
+        "date": "2026-10-13",
+        "close": 112.279999
+      },
+      {
+        "date": "2026-10-14",
+        "close": 110.82
+      },
+      {
+        "date": "2026-10-15",
+        "close": 112.440002
+      }
+    ],
+    "XLY": [
+      {
+        "date": "2026-07-17",
+        "close": 115.440002
+      },
+      {
+        "date": "2026-07-20",
+        "close": 114.610001
+      },
+      {
+        "date": "2026-07-21",
+        "close": 114.870003
+      },
+      {
+        "date": "2026-07-22",
+        "close": 114.019997
+      },
+      {
+        "date": "2026-07-23",
+        "close": 108.760002
+      },
+      {
+        "date": "2026-07-24",
+        "close": 109.410004
+      },
+      {
+        "date": "2026-07-27",
+        "close": 110.839996
+      },
+      {
+        "date": "2026-07-28",
+        "close": 112.480003
+      },
+      {
+        "date": "2026-07-29",
+        "close": 111.610001
+      },
+      {
+        "date": "2026-07-30",
+        "close": 112.389999
+      },
+      {
+        "date": "2026-07-31",
+        "close": 116.089996
+      },
+      {
+        "date": "2026-08-03",
+        "close": 118.209999
+      },
+      {
+        "date": "2026-08-04",
+        "close": 118.290001
+      },
+      {
+        "date": "2026-08-05",
+        "close": 118.639999
+      },
+      {
+        "date": "2026-08-06",
+        "close": 118.099998
+      },
+      {
+        "date": "2026-08-07",
+        "close": 119.860001
+      },
+      {
+        "date": "2026-08-10",
+        "close": 119.669998
+      },
+      {
+        "date": "2026-08-11",
+        "close": 119.239998
+      },
+      {
+        "date": "2026-08-12",
+        "close": 117.889999
+      },
+      {
+        "date": "2026-08-13",
+        "close": 118.449997
+      },
+      {
+        "date": "2026-08-14",
+        "close": 118.199997
+      },
+      {
+        "date": "2026-08-17",
+        "close": 116.75
+      },
+      {
+        "date": "2026-08-18",
+        "close": 116.360001
+      },
+      {
+        "date": "2026-08-19",
+        "close": 118.589996
+      },
+      {
+        "date": "2026-08-20",
+        "close": 116.68
+      },
+      {
+        "date": "2026-08-21",
+        "close": 118.019997
+      },
+      {
+        "date": "2026-08-24",
+        "close": 118.300003
+      },
+      {
+        "date": "2026-08-25",
+        "close": 117.949997
+      },
+      {
+        "date": "2026-08-26",
+        "close": 117.160004
+      },
+      {
+        "date": "2026-08-27",
+        "close": 115.879997
+      },
+      {
+        "date": "2026-08-28",
+        "close": 117.209999
+      },
+      {
+        "date": "2026-08-31",
+        "close": 116.589996
+      },
+      {
+        "date": "2026-09-01",
+        "close": 114.589996
+      },
+      {
+        "date": "2026-09-02",
+        "close": 114.860001
+      },
+      {
+        "date": "2026-09-03",
+        "close": 116.459999
+      },
+      {
+        "date": "2026-09-04",
+        "close": 114.910004
+      },
+      {
+        "date": "2026-09-08",
+        "close": 113.989998
+      },
+      {
+        "date": "2026-09-09",
+        "close": 112.459999
+      },
+      {
+        "date": "2026-09-10",
+        "close": 111.959999
+      },
+      {
+        "date": "2026-09-11",
+        "close": 112.959999
+      },
+      {
+        "date": "2026-09-14",
+        "close": 112.849998
+      },
+      {
+        "date": "2026-09-15",
+        "close": 110.879997
+      },
+      {
+        "date": "2026-09-16",
+        "close": 110.18
+      },
+      {
+        "date": "2026-09-17",
+        "close": 111.389999
+      },
+      {
+        "date": "2026-09-18",
+        "close": 111.029999
+      },
+      {
+        "date": "2026-09-21",
+        "close": 112.230003
+      },
+      {
+        "date": "2026-09-22",
+        "close": 112.330002
+      },
+      {
+        "date": "2026-09-23",
+        "close": 110.650002
+      },
+      {
+        "date": "2026-09-24",
+        "close": 110.32
+      },
+      {
+        "date": "2026-09-25",
+        "close": 110.559998
+      },
+      {
+        "date": "2026-09-28",
+        "close": 109.0
+      },
+      {
+        "date": "2026-09-29",
+        "close": 109.150002
+      },
+      {
+        "date": "2026-09-30",
+        "close": 108.839996
+      },
+      {
+        "date": "2026-10-01",
+        "close": 108.809998
+      },
+      {
+        "date": "2026-10-02",
+        "close": 110.040001
+      },
+      {
+        "date": "2026-10-05",
+        "close": 110.419998
+      },
+      {
+        "date": "2026-10-06",
+        "close": 111.720001
+      },
+      {
+        "date": "2026-10-07",
+        "close": 111.360001
+      },
+      {
+        "date": "2026-10-08",
+        "close": 111.709999
+      },
+      {
+        "date": "2026-10-09",
+        "close": 112.849998
+      },
+      {
+        "date": "2026-10-12",
+        "close": 112.269997
+      },
+      {
+        "date": "2026-10-13",
+        "close": 112.360001
+      },
+      {
+        "date": "2026-10-14",
+        "close": 111.5
+      },
+      {
+        "date": "2026-10-15",
+        "close": 113.410004
+      }
+    ],
+    "XLP": [
+      {
+        "date": "2026-07-17",
+        "close": 85.190002
+      },
+      {
+        "date": "2026-07-20",
+        "close": 84.860001
+      },
+      {
+        "date": "2026-07-21",
+        "close": 84.059998
+      },
+      {
+        "date": "2026-07-22",
+        "close": 84.379997
+      },
+      {
+        "date": "2026-07-23",
+        "close": 83.209999
+      },
+      {
+        "date": "2026-07-24",
+        "close": 84.129997
+      },
+      {
+        "date": "2026-07-27",
+        "close": 85.360001
+      },
+      {
+        "date": "2026-07-28",
+        "close": 87.059998
+      },
+      {
+        "date": "2026-07-29",
+        "close": 87.360001
+      },
+      {
+        "date": "2026-07-30",
+        "close": 85.470001
+      },
+      {
+        "date": "2026-07-31",
+        "close": 85.050003
+      },
+      {
+        "date": "2026-08-03",
+        "close": 84.860001
+      },
+      {
+        "date": "2026-08-04",
+        "close": 85.370003
+      },
+      {
+        "date": "2026-08-05",
+        "close": 85.330002
+      },
+      {
+        "date": "2026-08-06",
+        "close": 85.110001
+      },
+      {
+        "date": "2026-08-07",
+        "close": 85.120003
+      },
+      {
+        "date": "2026-08-10",
+        "close": 84.949997
+      },
+      {
+        "date": "2026-08-11",
+        "close": 84.690002
+      },
+      {
+        "date": "2026-08-12",
+        "close": 85.080002
+      },
+      {
+        "date": "2026-08-13",
+        "close": 86.0
+      },
+      {
+        "date": "2026-08-14",
+        "close": 86.089996
+      },
+      {
+        "date": "2026-08-17",
+        "close": 84.68
+      },
+      {
+        "date": "2026-08-18",
+        "close": 85.580002
+      },
+      {
+        "date": "2026-08-19",
+        "close": 86.540001
+      },
+      {
+        "date": "2026-08-20",
+        "close": 85.32
+      },
+      {
+        "date": "2026-08-21",
+        "close": 85.989998
+      },
+      {
+        "date": "2026-08-24",
+        "close": 87.449997
+      },
+      {
+        "date": "2026-08-25",
+        "close": 86.519997
+      },
+      {
+        "date": "2026-08-26",
+        "close": 86.269997
+      },
+      {
+        "date": "2026-08-27",
+        "close": 85.080002
+      },
+      {
+        "date": "2026-08-28",
+        "close": 85.449997
+      },
+      {
+        "date": "2026-08-31",
+        "close": 84.980003
+      },
+      {
+        "date": "2026-09-01",
+        "close": 85.25
+      },
+      {
+        "date": "2026-09-02",
+        "close": 85.529999
+      },
+      {
+        "date": "2026-09-03",
+        "close": 85.260002
+      },
+      {
+        "date": "2026-09-04",
+        "close": 84.580002
+      },
+      {
+        "date": "2026-09-08",
+        "close": 84.019997
+      },
+      {
+        "date": "2026-09-09",
+        "close": 83.050003
+      },
+      {
+        "date": "2026-09-10",
+        "close": 83.089996
+      },
+      {
+        "date": "2026-09-11",
+        "close": 83.379997
+      },
+      {
+        "date": "2026-09-14",
+        "close": 84.419998
+      },
+      {
+        "date": "2026-09-15",
+        "close": 83.730003
+      },
+      {
+        "date": "2026-09-16",
+        "close": 83.330002
+      },
+      {
+        "date": "2026-09-17",
+        "close": 83.489998
+      },
+      {
+        "date": "2026-09-18",
+        "close": 82.800003
+      },
+      {
+        "date": "2026-09-21",
+        "close": 81.919998
+      },
+      {
+        "date": "2026-09-22",
+        "close": 82.730003
+      },
+      {
+        "date": "2026-09-23",
+        "close": 82.43
+      },
+      {
+        "date": "2026-09-24",
+        "close": 81.699997
+      },
+      {
+        "date": "2026-09-25",
+        "close": 82.059998
+      },
+      {
+        "date": "2026-09-28",
+        "close": 82.279999
+      },
+      {
+        "date": "2026-09-29",
+        "close": 81.849998
+      },
+      {
+        "date": "2026-09-30",
+        "close": 80.599998
+      },
+      {
+        "date": "2026-10-01",
+        "close": 80.330002
+      },
+      {
+        "date": "2026-10-02",
+        "close": 80.529999
+      },
+      {
+        "date": "2026-10-05",
+        "close": 81.040001
+      },
+      {
+        "date": "2026-10-06",
+        "close": 81.800003
+      },
+      {
+        "date": "2026-10-07",
+        "close": 81.699997
+      },
+      {
+        "date": "2026-10-08",
+        "close": 83.419998
+      },
+      {
+        "date": "2026-10-09",
+        "close": 83.43
+      },
+      {
+        "date": "2026-10-12",
+        "close": 84.410004
+      },
+      {
+        "date": "2026-10-13",
+        "close": 84.190002
+      },
+      {
+        "date": "2026-10-14",
+        "close": 86.059998
+      },
+      {
+        "date": "2026-10-15",
+        "close": 86.68
+      }
+    ],
+    "XLF": [
+      {
+        "date": "2026-07-17",
+        "close": 56.259998
+      },
+      {
+        "date": "2026-07-20",
+        "close": 56.040001
+      },
+      {
+        "date": "2026-07-21",
+        "close": 56.110001
+      },
+      {
+        "date": "2026-07-22",
+        "close": 56.049999
+      },
+      {
+        "date": "2026-07-23",
+        "close": 55.830002
+      },
+      {
+        "date": "2026-07-24",
+        "close": 56.310001
+      },
+      {
+        "date": "2026-07-27",
+        "close": 56.880001
+      },
+      {
+        "date": "2026-07-28",
+        "close": 57.599998
+      },
+      {
+        "date": "2026-07-29",
+        "close": 56.68
+      },
+      {
+        "date": "2026-07-30",
+        "close": 57.0
+      },
+      {
+        "date": "2026-07-31",
+        "close": 56.939999
+      },
+      {
+        "date": "2026-08-03",
+        "close": 57.380001
+      },
+      {
+        "date": "2026-08-04",
+        "close": 57.880001
+      },
+      {
+        "date": "2026-08-05",
+        "close": 58.0
+      },
+      {
+        "date": "2026-08-06",
+        "close": 57.810001
+      },
+      {
+        "date": "2026-08-07",
+        "close": 57.599998
+      },
+      {
+        "date": "2026-08-10",
+        "close": 57.810001
+      },
+      {
+        "date": "2026-08-11",
+        "close": 57.799999
+      },
+      {
+        "date": "2026-08-12",
+        "close": 57.919998
+      },
+      {
+        "date": "2026-08-13",
+        "close": 58.259998
+      },
+      {
+        "date": "2026-08-14",
+        "close": 58.16
+      },
+      {
+        "date": "2026-08-17",
+        "close": 57.580002
+      },
+      {
+        "date": "2026-08-18",
+        "close": 57.84
+      },
+      {
+        "date": "2026-08-19",
+        "close": 57.48
+      },
+      {
+        "date": "2026-08-20",
+        "close": 56.950001
+      },
+      {
+        "date": "2026-08-21",
+        "close": 57.48
+      },
+      {
+        "date": "2026-08-24",
+        "close": 58.220001
+      },
+      {
+        "date": "2026-08-25",
+        "close": 58.310001
+      },
+      {
+        "date": "2026-08-26",
+        "close": 58.259998
+      },
+      {
+        "date": "2026-08-27",
+        "close": 57.880001
+      },
+      {
+        "date": "2026-08-28",
+        "close": 58.099998
+      },
+      {
+        "date": "2026-08-31",
+        "close": 57.709999
+      },
+      {
+        "date": "2026-09-01",
+        "close": 57.200001
+      },
+      {
+        "date": "2026-09-02",
+        "close": 57.66
+      },
+      {
+        "date": "2026-09-03",
+        "close": 58.560001
+      },
+      {
+        "date": "2026-09-04",
+        "close": 58.099998
+      },
+      {
+        "date": "2026-09-08",
+        "close": 57.299999
+      },
+      {
+        "date": "2026-09-09",
+        "close": 57.060001
+      },
+      {
+        "date": "2026-09-10",
+        "close": 56.869999
+      },
+      {
+        "date": "2026-09-11",
+        "close": 57.25
+      },
+      {
+        "date": "2026-09-14",
+        "close": 57.029999
+      },
+      {
+        "date": "2026-09-15",
+        "close": 56.849998
+      },
+      {
+        "date": "2026-09-16",
+        "close": 55.93
+      },
+      {
+        "date": "2026-09-17",
+        "close": 55.880001
+      },
+      {
+        "date": "2026-09-18",
+        "close": 55.860001
+      },
+      {
+        "date": "2026-09-21",
+        "close": 55.900002
+      },
+      {
+        "date": "2026-09-22",
+        "close": 54.799999
+      },
+      {
+        "date": "2026-09-23",
+        "close": 54.540001
+      },
+      {
+        "date": "2026-09-24",
+        "close": 54.529999
+      },
+      {
+        "date": "2026-09-25",
+        "close": 54.84
+      },
+      {
+        "date": "2026-09-28",
+        "close": 54.189999
+      },
+      {
+        "date": "2026-09-29",
+        "close": 54.009998
+      },
+      {
+        "date": "2026-09-30",
+        "close": 53.400002
+      },
+      {
+        "date": "2026-10-01",
+        "close": 53.459999
+      },
+      {
+        "date": "2026-10-02",
+        "close": 53.490002
+      },
+      {
+        "date": "2026-10-05",
+        "close": 53.880001
+      },
+      {
+        "date": "2026-10-06",
+        "close": 54.009998
+      },
+      {
+        "date": "2026-10-07",
+        "close": 53.75
+      },
+      {
+        "date": "2026-10-08",
+        "close": 54.23
+      },
+      {
+        "date": "2026-10-09",
+        "close": 54.73
+      },
+      {
+        "date": "2026-10-12",
+        "close": 55.049999
+      },
+      {
+        "date": "2026-10-13",
+        "close": 54.82
+      },
+      {
+        "date": "2026-10-14",
+        "close": 54.52
+      },
+      {
+        "date": "2026-10-15",
+        "close": 55.27
+      }
+    ],
+    "XLI": [
+      {
+        "date": "2026-07-17",
+        "close": 179.410004
+      },
+      {
+        "date": "2026-07-20",
+        "close": 178.119995
+      },
+      {
+        "date": "2026-07-21",
+        "close": 178.660004
+      },
+      {
+        "date": "2026-07-22",
+        "close": 178.850006
+      },
+      {
+        "date": "2026-07-23",
+        "close": 181.940002
+      },
+      {
+        "date": "2026-07-24",
+        "close": 182.660004
+      },
+      {
+        "date": "2026-07-27",
+        "close": 183.199997
+      },
+      {
+        "date": "2026-07-28",
+        "close": 182.490005
+      },
+      {
+        "date": "2026-07-29",
+        "close": 176.660004
+      },
+      {
+        "date": "2026-07-30",
+        "close": 178.389999
+      },
+      {
+        "date": "2026-07-31",
+        "close": 179.839996
+      },
+      {
+        "date": "2026-08-03",
+        "close": 183.160004
+      },
+      {
+        "date": "2026-08-04",
+        "close": 186.399994
+      },
+      {
+        "date": "2026-08-05",
+        "close": 186.350006
+      },
+      {
+        "date": "2026-08-06",
+        "close": 184.759995
+      },
+      {
+        "date": "2026-08-07",
+        "close": 185.179993
+      },
+      {
+        "date": "2026-08-10",
+        "close": 184.600006
+      },
+      {
+        "date": "2026-08-11",
+        "close": 185.699997
+      },
+      {
+        "date": "2026-08-12",
+        "close": 185.880005
+      },
+      {
+        "date": "2026-08-13",
+        "close": 185.789993
+      },
+      {
+        "date": "2026-08-14",
+        "close": 186.509995
+      },
+      {
+        "date": "2026-08-17",
+        "close": 186.320007
+      },
+      {
+        "date": "2026-08-18",
+        "close": 183.570007
+      },
+      {
+        "date": "2026-08-19",
+        "close": 181.949997
+      },
+      {
+        "date": "2026-08-20",
+        "close": 179.770004
+      },
+      {
+        "date": "2026-08-21",
+        "close": 180.25
+      },
+      {
+        "date": "2026-08-24",
+        "close": 179.0
+      },
+      {
+        "date": "2026-08-25",
+        "close": 178.399994
+      },
+      {
+        "date": "2026-08-26",
+        "close": 180.339996
+      },
+      {
+        "date": "2026-08-27",
+        "close": 178.800003
+      },
+      {
+        "date": "2026-08-28",
+        "close": 177.139999
+      },
+      {
+        "date": "2026-08-31",
+        "close": 175.130005
+      },
+      {
+        "date": "2026-09-01",
+        "close": 172.729996
+      },
+      {
+        "date": "2026-09-02",
+        "close": 172.779999
+      },
+      {
+        "date": "2026-09-03",
+        "close": 174.559998
+      },
+      {
+        "date": "2026-09-04",
+        "close": 175.270004
+      },
+      {
+        "date": "2026-09-08",
+        "close": 174.419998
+      },
+      {
+        "date": "2026-09-09",
+        "close": 171.789993
+      },
+      {
+        "date": "2026-09-10",
+        "close": 170.550003
+      },
+      {
+        "date": "2026-09-11",
+        "close": 172.369995
+      },
+      {
+        "date": "2026-09-14",
+        "close": 169.929993
+      },
+      {
+        "date": "2026-09-15",
+        "close": 168.850006
+      },
+      {
+        "date": "2026-09-16",
+        "close": 168.710007
+      },
+      {
+        "date": "2026-09-17",
+        "close": 169.009995
+      },
+      {
+        "date": "2026-09-18",
+        "close": 169.75
+      },
+      {
+        "date": "2026-09-21",
+        "close": 169.979996
+      },
+      {
+        "date": "2026-09-22",
+        "close": 170.270004
+      },
+      {
+        "date": "2026-09-23",
+        "close": 170.100006
+      },
+      {
+        "date": "2026-09-24",
+        "close": 168.830002
+      },
+      {
+        "date": "2026-09-25",
+        "close": 170.429993
+      },
+      {
+        "date": "2026-09-28",
+        "close": 168.779999
+      },
+      {
+        "date": "2026-09-29",
+        "close": 169.130005
+      },
+      {
+        "date": "2026-09-30",
+        "close": 166.979996
+      },
+      {
+        "date": "2026-10-01",
+        "close": 168.639999
+      },
+      {
+        "date": "2026-10-02",
+        "close": 169.949997
+      },
+      {
+        "date": "2026-10-05",
+        "close": 170.100006
+      },
+      {
+        "date": "2026-10-06",
+        "close": 171.580002
+      },
+      {
+        "date": "2026-10-07",
+        "close": 167.839996
+      },
+      {
+        "date": "2026-10-08",
+        "close": 168.399994
+      },
+      {
+        "date": "2026-10-09",
+        "close": 169.25
+      },
+      {
+        "date": "2026-10-12",
+        "close": 169.149994
+      },
+      {
+        "date": "2026-10-13",
+        "close": 168.669998
+      },
+      {
+        "date": "2026-10-14",
+        "close": 167.039993
+      },
+      {
+        "date": "2026-10-15",
+        "close": 167.889999
+      }
+    ],
+    "XLV": [
+      {
+        "date": "2026-07-17",
+        "close": 161.089996
+      },
+      {
+        "date": "2026-07-20",
+        "close": 159.25
+      },
+      {
+        "date": "2026-07-21",
+        "close": 160.25
+      },
+      {
+        "date": "2026-07-22",
+        "close": 159.429993
+      },
+      {
+        "date": "2026-07-23",
+        "close": 161.440002
+      },
+      {
+        "date": "2026-07-24",
+        "close": 162.570007
+      },
+      {
+        "date": "2026-07-27",
+        "close": 163.399994
+      },
+      {
+        "date": "2026-07-28",
+        "close": 167.259995
+      },
+      {
+        "date": "2026-07-29",
+        "close": 166.240005
+      },
+      {
+        "date": "2026-07-30",
+        "close": 163.520004
+      },
+      {
+        "date": "2026-07-31",
+        "close": 162.550003
+      },
+      {
+        "date": "2026-08-03",
+        "close": 162.240005
+      },
+      {
+        "date": "2026-08-04",
+        "close": 162.100006
+      },
+      {
+        "date": "2026-08-05",
+        "close": 164.160004
+      },
+      {
+        "date": "2026-08-06",
+        "close": 164.449997
+      },
+      {
+        "date": "2026-08-07",
+        "close": 165.679993
+      },
+      {
+        "date": "2026-08-10",
+        "close": 168.440002
+      },
+      {
+        "date": "2026-08-11",
+        "close": 168.009995
+      },
+      {
+        "date": "2026-08-12",
+        "close": 168.440002
+      },
+      {
+        "date": "2026-08-13",
+        "close": 168.380005
+      },
+      {
+        "date": "2026-08-14",
+        "close": 167.369995
+      },
+      {
+        "date": "2026-08-17",
+        "close": 167.050003
+      },
+      {
+        "date": "2026-08-18",
+        "close": 169.729996
+      },
+      {
+        "date": "2026-08-19",
+        "close": 175.679993
+      },
+      {
+        "date": "2026-08-20",
+        "close": 172.389999
+      },
+      {
+        "date": "2026-08-21",
+        "close": 174.619995
+      },
+      {
+        "date": "2026-08-24",
+        "close": 174.699997
+      },
+      {
+        "date": "2026-08-25",
+        "close": 175.289993
+      },
+      {
+        "date": "2026-08-26",
+        "close": 173.539993
+      },
+      {
+        "date": "2026-08-27",
+        "close": 171.580002
+      },
+      {
+        "date": "2026-08-28",
+        "close": 171.160004
+      },
+      {
+        "date": "2026-08-31",
+        "close": 170.539993
+      },
+      {
+        "date": "2026-09-01",
+        "close": 171.669998
+      },
+      {
+        "date": "2026-09-02",
+        "close": 172.949997
+      },
+      {
+        "date": "2026-09-03",
+        "close": 173.259995
+      },
+      {
+        "date": "2026-09-04",
+        "close": 171.449997
+      },
+      {
+        "date": "2026-09-08",
+        "close": 167.130005
+      },
+      {
+        "date": "2026-09-09",
+        "close": 166.580002
+      },
+      {
+        "date": "2026-09-10",
+        "close": 165.660004
+      },
+      {
+        "date": "2026-09-11",
+        "close": 165.360001
+      },
+      {
+        "date": "2026-09-14",
+        "close": 167.75
+      },
+      {
+        "date": "2026-09-15",
+        "close": 167.660004
+      },
+      {
+        "date": "2026-09-16",
+        "close": 167.770004
+      },
+      {
+        "date": "2026-09-17",
+        "close": 168.809998
+      },
+      {
+        "date": "2026-09-18",
+        "close": 168.389999
+      },
+      {
+        "date": "2026-09-21",
+        "close": 169.009995
+      },
+      {
+        "date": "2026-09-22",
+        "close": 169.889999
+      },
+      {
+        "date": "2026-09-23",
+        "close": 168.800003
+      },
+      {
+        "date": "2026-09-24",
+        "close": 169.869995
+      },
+      {
+        "date": "2026-09-25",
+        "close": 170.699997
+      },
+      {
+        "date": "2026-09-28",
+        "close": 171.259995
+      },
+      {
+        "date": "2026-09-29",
+        "close": 170.729996
+      },
+      {
+        "date": "2026-09-30",
+        "close": 168.419998
+      },
+      {
+        "date": "2026-10-01",
+        "close": 166.199997
+      },
+      {
+        "date": "2026-10-02",
+        "close": 166.179993
+      },
+      {
+        "date": "2026-10-05",
+        "close": 167.369995
+      },
+      {
+        "date": "2026-10-06",
+        "close": 167.089996
+      },
+      {
+        "date": "2026-10-07",
+        "close": 168.809998
+      },
+      {
+        "date": "2026-10-08",
+        "close": 168.160004
+      },
+      {
+        "date": "2026-10-09",
+        "close": 170.809998
+      },
+      {
+        "date": "2026-10-12",
+        "close": 171.990005
+      },
+      {
+        "date": "2026-10-13",
+        "close": 169.660004
+      },
+      {
+        "date": "2026-10-14",
+        "close": 173.960007
+      },
+      {
+        "date": "2026-10-15",
+        "close": 177.190002
+      }
+    ],
+    "XLE": [
+      {
+        "date": "2026-07-17",
+        "close": 57.68
+      },
+      {
+        "date": "2026-07-20",
+        "close": 57.939999
+      },
+      {
+        "date": "2026-07-21",
+        "close": 58.5
+      },
+      {
+        "date": "2026-07-22",
+        "close": 59.200001
+      },
+      {
+        "date": "2026-07-23",
+        "close": 59.380001
+      },
+      {
+        "date": "2026-07-24",
+        "close": 59.619999
+      },
+      {
+        "date": "2026-07-27",
+        "close": 58.360001
+      },
+      {
+        "date": "2026-07-28",
+        "close": 57.57
+      },
+      {
+        "date": "2026-07-29",
+        "close": 58.650002
+      },
+      {
+        "date": "2026-07-30",
+        "close": 58.959999
+      },
+      {
+        "date": "2026-07-31",
+        "close": 59.549999
+      },
+      {
+        "date": "2026-08-03",
+        "close": 58.790001
+      },
+      {
+        "date": "2026-08-04",
+        "close": 58.52
+      },
+      {
+        "date": "2026-08-05",
+        "close": 57.310001
+      },
+      {
+        "date": "2026-08-06",
+        "close": 58.16
+      },
+      {
+        "date": "2026-08-07",
+        "close": 57.5
+      },
+      {
+        "date": "2026-08-10",
+        "close": 60.18
+      },
+      {
+        "date": "2026-08-11",
+        "close": 60.93
+      },
+      {
+        "date": "2026-08-12",
+        "close": 61.029999
+      },
+      {
+        "date": "2026-08-13",
+        "close": 61.060001
+      },
+      {
+        "date": "2026-08-14",
+        "close": 61.91
+      },
+      {
+        "date": "2026-08-17",
+        "close": 62.580002
+      },
+      {
+        "date": "2026-08-18",
+        "close": 63.68
+      },
+      {
+        "date": "2026-08-19",
+        "close": 63.580002
+      },
+      {
+        "date": "2026-08-20",
+        "close": 63.75
+      },
+      {
+        "date": "2026-08-21",
+        "close": 63.639999
+      },
+      {
+        "date": "2026-08-24",
+        "close": 63.110001
+      },
+      {
+        "date": "2026-08-25",
+        "close": 62.060001
+      },
+      {
+        "date": "2026-08-26",
+        "close": 62.43
+      },
+      {
+        "date": "2026-08-27",
+        "close": 62.290001
+      },
+      {
+        "date": "2026-08-28",
+        "close": 62.68
+      },
+      {
+        "date": "2026-08-31",
+        "close": 63.959999
+      },
+      {
+        "date": "2026-09-01",
+        "close": 64.769997
+      },
+      {
+        "date": "2026-09-02",
+        "close": 65.099998
+      },
+      {
+        "date": "2026-09-03",
+        "close": 64.620003
+      },
+      {
+        "date": "2026-09-04",
+        "close": 64.059998
+      },
+      {
+        "date": "2026-09-08",
+        "close": 64.769997
+      },
+      {
+        "date": "2026-09-09",
+        "close": 65.309998
+      },
+      {
+        "date": "2026-09-10",
+        "close": 64.93
+      },
+      {
+        "date": "2026-09-11",
+        "close": 65.139999
+      },
+      {
+        "date": "2026-09-14",
+        "close": 64.529999
+      },
+      {
+        "date": "2026-09-15",
+        "close": 65.93
+      },
+      {
+        "date": "2026-09-16",
+        "close": 64.029999
+      },
+      {
+        "date": "2026-09-17",
+        "close": 64.480003
+      },
+      {
+        "date": "2026-09-18",
+        "close": 64.309998
+      },
+      {
+        "date": "2026-09-21",
+        "close": 62.459999
+      },
+      {
+        "date": "2026-09-22",
+        "close": 61.779999
+      },
+      {
+        "date": "2026-09-23",
+        "close": 62.369999
+      },
+      {
+        "date": "2026-09-24",
+        "close": 62.599998
+      },
+      {
+        "date": "2026-09-25",
+        "close": 62.040001
+      },
+      {
+        "date": "2026-09-28",
+        "close": 62.099998
+      },
+      {
+        "date": "2026-09-29",
+        "close": 61.540001
+      },
+      {
+        "date": "2026-09-30",
+        "close": 61.5
+      },
+      {
+        "date": "2026-10-01",
+        "close": 62.700001
+      },
+      {
+        "date": "2026-10-02",
+        "close": 62.82
+      },
+      {
+        "date": "2026-10-05",
+        "close": 63.450001
+      },
+      {
+        "date": "2026-10-06",
+        "close": 63.75
+      },
+      {
+        "date": "2026-10-07",
+        "close": 63.360001
+      },
+      {
+        "date": "2026-10-08",
+        "close": 65.239998
+      },
+      {
+        "date": "2026-10-09",
+        "close": 65.080002
+      },
+      {
+        "date": "2026-10-12",
+        "close": 66.010002
+      },
+      {
+        "date": "2026-10-13",
+        "close": 67.199997
+      },
+      {
+        "date": "2026-10-14",
+        "close": 67.629997
+      },
+      {
+        "date": "2026-10-15",
+        "close": 66.559998
+      }
+    ],
+    "XLB": [
+      {
+        "date": "2026-07-17",
+        "close": 50.529999
+      },
+      {
+        "date": "2026-07-20",
+        "close": 50.029999
+      },
+      {
+        "date": "2026-07-21",
+        "close": 50.099998
+      },
+      {
+        "date": "2026-07-22",
+        "close": 50.82
+      },
+      {
+        "date": "2026-07-23",
+        "close": 50.290001
+      },
+      {
+        "date": "2026-07-24",
+        "close": 51.259998
+      },
+      {
+        "date": "2026-07-27",
+        "close": 51.389999
+      },
+      {
+        "date": "2026-07-28",
+        "close": 52.34
+      },
+      {
+        "date": "2026-07-29",
+        "close": 51.740002
+      },
+      {
+        "date": "2026-07-30",
+        "close": 51.639999
+      },
+      {
+        "date": "2026-07-31",
+        "close": 50.43
+      },
+      {
+        "date": "2026-08-03",
+        "close": 51.009998
+      },
+      {
+        "date": "2026-08-04",
+        "close": 52.0
+      },
+      {
+        "date": "2026-08-05",
+        "close": 52.639999
+      },
+      {
+        "date": "2026-08-06",
+        "close": 52.169998
+      },
+      {
+        "date": "2026-08-07",
+        "close": 52.860001
+      },
+      {
+        "date": "2026-08-10",
+        "close": 53.18
+      },
+      {
+        "date": "2026-08-11",
+        "close": 53.240002
+      },
+      {
+        "date": "2026-08-12",
+        "close": 52.580002
+      },
+      {
+        "date": "2026-08-13",
+        "close": 52.310001
+      },
+      {
+        "date": "2026-08-14",
+        "close": 52.540001
+      },
+      {
+        "date": "2026-08-17",
+        "close": 52.240002
+      },
+      {
+        "date": "2026-08-18",
+        "close": 51.779999
+      },
+      {
+        "date": "2026-08-19",
+        "close": 52.52
+      },
+      {
+        "date": "2026-08-20",
+        "close": 52.419998
+      },
+      {
+        "date": "2026-08-21",
+        "close": 53.540001
+      },
+      {
+        "date": "2026-08-24",
+        "close": 53.580002
+      },
+      {
+        "date": "2026-08-25",
+        "close": 53.580002
+      },
+      {
+        "date": "2026-08-26",
+        "close": 53.669998
+      },
+      {
+        "date": "2026-08-27",
+        "close": 53.23
+      },
+      {
+        "date": "2026-08-28",
+        "close": 53.18
+      },
+      {
+        "date": "2026-08-31",
+        "close": 52.689999
+      },
+      {
+        "date": "2026-09-01",
+        "close": 52.07
+      },
+      {
+        "date": "2026-09-02",
+        "close": 52.950001
+      },
+      {
+        "date": "2026-09-03",
+        "close": 52.619999
+      },
+      {
+        "date": "2026-09-04",
+        "close": 52.439999
+      },
+      {
+        "date": "2026-09-08",
+        "close": 51.939999
+      },
+      {
+        "date": "2026-09-09",
+        "close": 51.389999
+      },
+      {
+        "date": "2026-09-10",
+        "close": 50.759998
+      },
+      {
+        "date": "2026-09-11",
+        "close": 50.950001
+      },
+      {
+        "date": "2026-09-14",
+        "close": 50.490002
+      },
+      {
+        "date": "2026-09-15",
+        "close": 50.73
+      },
+      {
+        "date": "2026-09-16",
+        "close": 50.360001
+      },
+      {
+        "date": "2026-09-17",
+        "close": 50.709999
+      },
+      {
+        "date": "2026-09-18",
+        "close": 49.990002
+      },
+      {
+        "date": "2026-09-21",
+        "close": 49.709999
+      },
+      {
+        "date": "2026-09-22",
+        "close": 50.529999
+      },
+      {
+        "date": "2026-09-23",
+        "close": 50.279999
+      },
+      {
+        "date": "2026-09-24",
+        "close": 49.68
+      },
+      {
+        "date": "2026-09-25",
+        "close": 49.799999
+      },
+      {
+        "date": "2026-09-28",
+        "close": 49.470001
+      },
+      {
+        "date": "2026-09-29",
+        "close": 49.099998
+      },
+      {
+        "date": "2026-09-30",
+        "close": 48.700001
+      },
+      {
+        "date": "2026-10-01",
+        "close": 48.540001
+      },
+      {
+        "date": "2026-10-02",
+        "close": 48.860001
+      },
+      {
+        "date": "2026-10-05",
+        "close": 49.5
+      },
+      {
+        "date": "2026-10-06",
+        "close": 49.73
+      },
+      {
+        "date": "2026-10-07",
+        "close": 48.98
+      },
+      {
+        "date": "2026-10-08",
+        "close": 49.27
+      },
+      {
+        "date": "2026-10-09",
+        "close": 49.43
+      },
+      {
+        "date": "2026-10-12",
+        "close": 49.439999
+      },
+      {
+        "date": "2026-10-13",
+        "close": 49.720001
+      },
+      {
+        "date": "2026-10-14",
+        "close": 49.669998
+      },
+      {
+        "date": "2026-10-15",
+        "close": 50.560001
+      }
+    ],
+    "XLU": [
+      {
+        "date": "2026-07-17",
+        "close": 45.169998
+      },
+      {
+        "date": "2026-07-20",
+        "close": 44.939999
+      },
+      {
+        "date": "2026-07-21",
+        "close": 44.919998
+      },
+      {
+        "date": "2026-07-22",
+        "close": 45.93
+      },
+      {
+        "date": "2026-07-23",
+        "close": 46.189999
+      },
+      {
+        "date": "2026-07-24",
+        "close": 46.290001
+      },
+      {
+        "date": "2026-07-27",
+        "close": 45.68
+      },
+      {
+        "date": "2026-07-28",
+        "close": 45.52
+      },
+      {
+        "date": "2026-07-29",
+        "close": 44.91
+      },
+      {
+        "date": "2026-07-30",
+        "close": 44.66
+      },
+      {
+        "date": "2026-07-31",
+        "close": 44.349998
+      },
+      {
+        "date": "2026-08-03",
+        "close": 44.360001
+      },
+      {
+        "date": "2026-08-04",
+        "close": 44.110001
+      },
+      {
+        "date": "2026-08-05",
+        "close": 43.66
+      },
+      {
+        "date": "2026-08-06",
+        "close": 43.380001
+      },
+      {
+        "date": "2026-08-07",
+        "close": 43.610001
+      },
+      {
+        "date": "2026-08-10",
+        "close": 43.130001
+      },
+      {
+        "date": "2026-08-11",
+        "close": 43.630001
+      },
+      {
+        "date": "2026-08-12",
+        "close": 43.84
+      },
+      {
+        "date": "2026-08-13",
+        "close": 44.040001
+      },
+      {
+        "date": "2026-08-14",
+        "close": 44.310001
+      },
+      {
+        "date": "2026-08-17",
+        "close": 44.18
+      },
+      {
+        "date": "2026-08-18",
+        "close": 44.02
+      },
+      {
+        "date": "2026-08-19",
+        "close": 44.02
+      },
+      {
+        "date": "2026-08-20",
+        "close": 43.77
+      },
+      {
+        "date": "2026-08-21",
+        "close": 42.77
+      },
+      {
+        "date": "2026-08-24",
+        "close": 43.220001
+      },
+      {
+        "date": "2026-08-25",
+        "close": 43.310001
+      },
+      {
+        "date": "2026-08-26",
+        "close": 43.509998
+      },
+      {
+        "date": "2026-08-27",
+        "close": 43.18
+      },
+      {
+        "date": "2026-08-28",
+        "close": 42.73
+      },
+      {
+        "date": "2026-08-31",
+        "close": 42.23
+      },
+      {
+        "date": "2026-09-01",
+        "close": 42.560001
+      },
+      {
+        "date": "2026-09-02",
+        "close": 42.669998
+      },
+      {
+        "date": "2026-09-03",
+        "close": 43.029999
+      },
+      {
+        "date": "2026-09-04",
+        "close": 43.080002
+      },
+      {
+        "date": "2026-09-08",
+        "close": 43.450001
+      },
+      {
+        "date": "2026-09-09",
+        "close": 42.939999
+      },
+      {
+        "date": "2026-09-10",
+        "close": 42.52
+      },
+      {
+        "date": "2026-09-11",
+        "close": 42.389999
+      },
+      {
+        "date": "2026-09-14",
+        "close": 41.82
+      },
+      {
+        "date": "2026-09-15",
+        "close": 41.32
+      },
+      {
+        "date": "2026-09-16",
+        "close": 41.32
+      },
+      {
+        "date": "2026-09-17",
+        "close": 41.689999
+      },
+      {
+        "date": "2026-09-18",
+        "close": 41.099998
+      },
+      {
+        "date": "2026-09-21",
+        "close": 40.66
+      },
+      {
+        "date": "2026-09-22",
+        "close": 40.529999
+      },
+      {
+        "date": "2026-09-23",
+        "close": 39.75
+      },
+      {
+        "date": "2026-09-24",
+        "close": 39.360001
+      },
+      {
+        "date": "2026-09-25",
+        "close": 39.509998
+      },
+      {
+        "date": "2026-09-28",
+        "close": 39.25
+      },
+      {
+        "date": "2026-09-29",
+        "close": 39.709999
+      },
+      {
+        "date": "2026-09-30",
+        "close": 39.439999
+      },
+      {
+        "date": "2026-10-01",
+        "close": 39.68
+      },
+      {
+        "date": "2026-10-02",
+        "close": 39.830002
+      },
+      {
+        "date": "2026-10-05",
+        "close": 39.970001
+      },
+      {
+        "date": "2026-10-06",
+        "close": 41.16
+      },
+      {
+        "date": "2026-10-07",
+        "close": 41.150002
+      },
+      {
+        "date": "2026-10-08",
+        "close": 41.07
+      },
+      {
+        "date": "2026-10-09",
+        "close": 41.41
+      },
+      {
+        "date": "2026-10-12",
+        "close": 41.630001
+      },
+      {
+        "date": "2026-10-13",
+        "close": 41.869999
+      },
+      {
+        "date": "2026-10-14",
+        "close": 41.720001
+      },
+      {
+        "date": "2026-10-15",
+        "close": 41.650002
+      }
+    ],
+    "XLRE": [
+      {
+        "date": "2026-07-17",
+        "close": 45.419998
+      },
+      {
+        "date": "2026-07-20",
+        "close": 45.23
+      },
+      {
+        "date": "2026-07-21",
+        "close": 45.200001
+      },
+      {
+        "date": "2026-07-22",
+        "close": 45.009998
+      },
+      {
+        "date": "2026-07-23",
+        "close": 44.950001
+      },
+      {
+        "date": "2026-07-24",
+        "close": 45.950001
+      },
+      {
+        "date": "2026-07-27",
+        "close": 45.759998
+      },
+      {
+        "date": "2026-07-28",
+        "close": 46.009998
+      },
+      {
+        "date": "2026-07-29",
+        "close": 45.959999
+      },
+      {
+        "date": "2026-07-30",
+        "close": 45.299999
+      },
+      {
+        "date": "2026-07-31",
+        "close": 45.07
+      },
+      {
+        "date": "2026-08-03",
+        "close": 45.18
+      },
+      {
+        "date": "2026-08-04",
+        "close": 45.169998
+      },
+      {
+        "date": "2026-08-05",
+        "close": 45.200001
+      },
+      {
+        "date": "2026-08-06",
+        "close": 44.810001
+      },
+      {
+        "date": "2026-08-07",
+        "close": 44.98
+      },
+      {
+        "date": "2026-08-10",
+        "close": 44.400002
+      },
+      {
+        "date": "2026-08-11",
+        "close": 44.080002
+      },
+      {
+        "date": "2026-08-12",
+        "close": 44.490002
+      },
+      {
+        "date": "2026-08-13",
+        "close": 45.119999
+      },
+      {
+        "date": "2026-08-14",
+        "close": 45.27
+      },
+      {
+        "date": "2026-08-17",
+        "close": 44.830002
+      },
+      {
+        "date": "2026-08-18",
+        "close": 44.630001
+      },
+      {
+        "date": "2026-08-19",
+        "close": 44.990002
+      },
+      {
+        "date": "2026-08-20",
+        "close": 45.080002
+      },
+      {
+        "date": "2026-08-21",
+        "close": 45.080002
+      },
+      {
+        "date": "2026-08-24",
+        "close": 45.330002
+      },
+      {
+        "date": "2026-08-25",
+        "close": 45.360001
+      },
+      {
+        "date": "2026-08-26",
+        "close": 45.09
+      },
+      {
+        "date": "2026-08-27",
+        "close": 44.66
+      },
+      {
+        "date": "2026-08-28",
+        "close": 44.48
+      },
+      {
+        "date": "2026-08-31",
+        "close": 44.110001
+      },
+      {
+        "date": "2026-09-01",
+        "close": 44.040001
+      },
+      {
+        "date": "2026-09-02",
+        "close": 43.73
+      },
+      {
+        "date": "2026-09-03",
+        "close": 44.25
+      },
+      {
+        "date": "2026-09-04",
+        "close": 43.93
+      },
+      {
+        "date": "2026-09-08",
+        "close": 43.900002
+      },
+      {
+        "date": "2026-09-09",
+        "close": 43.41
+      },
+      {
+        "date": "2026-09-10",
+        "close": 43.049999
+      },
+      {
+        "date": "2026-09-11",
+        "close": 43.419998
+      },
+      {
+        "date": "2026-09-14",
+        "close": 43.119999
+      },
+      {
+        "date": "2026-09-15",
+        "close": 43.07
+      },
+      {
+        "date": "2026-09-16",
+        "close": 42.810001
+      },
+      {
+        "date": "2026-09-17",
+        "close": 42.939999
+      },
+      {
+        "date": "2026-09-18",
+        "close": 42.529999
+      },
+      {
+        "date": "2026-09-21",
+        "close": 42.59
+      },
+      {
+        "date": "2026-09-22",
+        "close": 42.5
+      },
+      {
+        "date": "2026-09-23",
+        "close": 41.84
+      },
+      {
+        "date": "2026-09-24",
+        "close": 41.650002
+      },
+      {
+        "date": "2026-09-25",
+        "close": 41.560001
+      },
+      {
+        "date": "2026-09-28",
+        "close": 41.349998
+      },
+      {
+        "date": "2026-09-29",
+        "close": 41.34
+      },
+      {
+        "date": "2026-09-30",
+        "close": 40.91
+      },
+      {
+        "date": "2026-10-01",
+        "close": 40.68
+      },
+      {
+        "date": "2026-10-02",
+        "close": 40.810001
+      },
+      {
+        "date": "2026-10-05",
+        "close": 40.669998
+      },
+      {
+        "date": "2026-10-06",
+        "close": 41.099998
+      },
+      {
+        "date": "2026-10-07",
+        "close": 40.57
+      },
+      {
+        "date": "2026-10-08",
+        "close": 40.849998
+      },
+      {
+        "date": "2026-10-09",
+        "close": 41.610001
+      },
+      {
+        "date": "2026-10-12",
+        "close": 41.919998
+      },
+      {
+        "date": "2026-10-13",
+        "close": 41.830002
+      },
+      {
+        "date": "2026-10-14",
+        "close": 41.490002
+      },
+      {
+        "date": "2026-10-15",
+        "close": 41.990002
+      }
+    ]
+  },
+  "status": {
+    "SPY": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLK": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLC": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLY": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLP": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLF": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLI": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLV": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLE": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLB": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLU": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    },
+    "XLRE": {
+      "status": "ok",
+      "observed_at": "2026-10-15",
+      "count": 64
+    }
+  }
+}
diff --git a/tests/observation-freshness.test.mjs b/tests/observation-freshness.test.mjs
index df92f9b..8f991de 100644
--- a/tests/observation-freshness.test.mjs
+++ b/tests/observation-freshness.test.mjs
@@ -71,6 +71,43 @@ try{
   const previous={checkedAt:now,rows:[spot,...stats],coverage:{usable:9,total:9,missingCore:[]}};
   const refreshing=api.refreshingMacroSnapshot(previous);
   assert.equal(refreshing.rows.find(r=>r.id===spot.id).status,'ok');
+  const contradictory={...spot,reason:'資料較舊，暫不納入判讀'};
+  assert.equal(api.mergeVerifiedMacroRows([contradictory],[])[0].reason,null,'the fetched/official-import merge clears a contradictory age-only reason too');
+  const reconciled=api.refreshingMacroSnapshot({checkedAt:now,rows:[contradictory]},false).rows[0];
+  assert.equal(reconciled.status,'ok','a release-verified current observation retains its valid status');
+  assert.equal(reconciled.is_stale,false);
+  assert.equal(reconciled.reason,null,'an expired-data reason cannot contradict the final current status');
+  assert.equal(api.refreshingMacroSnapshot({checkedAt:now,rows:[{...spot,reason:'保留前次成功觀測；資料較舊'}]},false).rows[0].reason,null,'the exact relay age-only reason is reconciled too');
+  assert.equal(api.refreshingMacroSnapshot({checkedAt:now,rows:[{...spot,reason:'來源核對失敗，需人工覆核'}]},false).rows[0].reason,'來源核對失敗，需人工覆核','unrelated source warnings are retained');
+  const importedInput={fetchedAt:now,source:'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DHHNGSP',history:[{date:'2026-10-01',value:3},{date:'2026-10-02',value:3.1},{date:'2026-10-03',value:3.2}],releaseVerification:{source:'https://fred.stlouisfed.org/series/DHHNGSP',date:'2026-10-03',value:3.2,nextReleaseDate:'2026-10-15',fetchedAt:now}};
+  const importedCache={payload:JSON.stringify(importedInput),updated_at:now,expires_at:new Date(Date.now()+3600000).toISOString()};
+  const importedDb={prepare(){return {run:async()=>({success:true}),bind(){return {all:async()=>({results:[importedCache]})}}}}};
+  const imported=await api.importedOfficialSeries('DHHNGSP',{DB:importedDb});
+  assert.equal(imported.status,'ok');assert.equal(imported.reason,null,'an imported release-verified observation clears summarize stale text at the source');
+  const staleButReleaseVerified={...contradictory,status:'stale',is_stale:true};
+  const promoted=api.refreshingMacroSnapshot({checkedAt:now,rows:[staleButReleaseVerified]},false).rows[0];
+  assert.equal(promoted.status,'ok','a valid release window can resolve an age-only stale label');
+  assert.equal(promoted.reason,null);
+  const trulyExpired=api.refreshingMacroSnapshot({checkedAt:now,rows:[{...contradictory,releaseVerification:{...spot.releaseVerification,nextReleaseDate:'2026-10-09'}}]},false).rows[0];
+  assert.equal(trulyExpired.status,'stale','an expired release window remains stale');
+  assert.match(trulyExpired.reason,/過有效期/);
+  const yen={...spot,id:'DEXJPUS',date:'2026-10-08',value:158.34,releaseVerification:{...spot.releaseVerification,source:'https://fred.stlouisfed.org/series/DEXJPUS',date:'2026-10-08',value:158.34,nextReleaseDate:'2026-10-19'}};
+  const yenVol={id:'JPY_HV20',date:yen.date,value:5.804832905239327,status:'stale',is_stale:true,validationState:'validated',derivedFrom:'DEXJPUS',historyObservations:68,requiredObservations:21};
+  const yenVol60={...yenVol,id:'JPY_HV60',value:9.756886685658461,requiredObservations:61};
+  const inherited=api.refreshingMacroSnapshot({checkedAt:now,rows:[yen,yenVol,yenVol60]},false);
+  assert.equal(inherited.rows.find(r=>r.id==='JPY_HV20').status,'ok','validated volatility follows a current, release-verified parent despite the generic seven-day cutoff');
+  assert.equal(inherited.rows.find(r=>r.id==='JPY_HV60').status,'ok');
+  assert.equal(inherited.rows.find(r=>r.id==='JPY_HV60').value,yenVol60.value,'derived value is unchanged when only freshness inheritance changes');
+  assert.deepEqual(api.refreshingMacroSnapshot({checkedAt:now,rows:[yenVol,yen,yenVol60]},false).rows.map(r=>r.id),['JPY_HV20','DEXJPUS','JPY_HV60'],'derived rows retain their original position');
+  const orphan=api.refreshingMacroSnapshot({checkedAt:now,rows:[yenVol]},false).rows[0];
+  assert.equal(orphan.validationState,'source_missing');assert.equal(orphan.value,null,'an orphan derived row cannot supply a value');
+  const expiredParent={...yen,date:'2026-10-01',releaseVerification:{...yen.releaseVerification,date:'2026-10-01',nextReleaseDate:'2026-10-09'}};
+  const invalidated=api.refreshingMacroSnapshot({checkedAt:now,rows:[expiredParent,{...yenVol,date:'2026-10-01'}]},false).rows.find(r=>r.id==='JPY_HV20');
+  assert.equal(invalidated.status,'missing','a derived value is removed from current judgment when its parent expires');
+  assert.equal(invalidated.value,null);
+  const dateMismatch=api.refreshingMacroSnapshot({checkedAt:now,rows:[yen,{...yenVol,parentDate:'2026-10-07'}]},false).rows.find(r=>r.id==='JPY_HV20');
+  assert.equal(dateMismatch.status,'missing','a derived value must match both its observation date and recorded parent date');
+  assert.equal(dateMismatch.value,null);
   assert.equal(refreshing.rows.find(r=>r.id==='TWSE_CREDIT_TRADE_VALUE').status,'ok','five-minute refresh expiry is not source expiry');
   const failure={id:'TWSE_CREDIT_TRADE_VALUE',value:null,status:'missing',reason:'HTTP 307'};
   const carried=api.mergeVerifiedMacroRows([failure],[previous])[0];
diff --git a/tests/phison-panel.test.mjs b/tests/phison-panel.test.mjs
new file mode 100644
index 0000000..b93dddd
--- /dev/null
+++ b/tests/phison-panel.test.mjs
@@ -0,0 +1,50 @@
+import assert from 'node:assert/strict';
+import {readFileSync} from 'node:fs';
+import {execFileSync} from 'node:child_process';
+const RealDate=globalThis.Date,now=RealDate.parse('2026-10-19T15:51:49Z');
+globalThis.Date=class extends RealDate{constructor(...args){super(...(args.length?args:[now]));}static now(){return now;}};
+const source=readFileSync(new URL('../dist/server/index.js',import.meta.url),'utf8');
+const api=await import('data:text/javascript;base64,'+Buffer.from(source+'\nexport {evaluateMasterModel,summarizeTaiwanMarket,retainTaiwanComparisonHistory,issuerEvidenceContext,TAIWAN_MARKET_AUDIT_IDS};').toString('base64'));
+const original=execFileSync('git',['show','HEAD:dist/server/index.js'],{encoding:'utf8',maxBuffer:8000000});
+const before=await import('data:text/javascript;base64,'+Buffer.from(original+'\nexport {evaluateMasterModel};').toString('base64'));
+try{
+ const {stock}=JSON.parse(readFileSync(new URL('./fixtures/master-remediation.json',import.meta.url),'utf8'));
+ const fresh={stockFresh:true,marketFresh:true,macroFresh:true};
+ const old=before.evaluateMasterModel(stock,null,null,fresh,{}),updated=api.evaluateMasterModel(stock,null,null,fresh,{});
+ assert.equal(updated.gates.find(g=>g.id===5).guidanceApplicability,'structural_unavailable');
+ assert.match(updated.gates.find(g=>g.id===5).detail,/公司不提供季度財測（結構性）/);
+ assert.equal(updated.gates.find(g=>g.id===5).checks[0].state,'not_applicable');
+ assert.equal(updated.gates.find(g=>g.id===5).checks[0].applicability,'structural_unavailable');
+ assert.equal(updated.gates.find(g=>g.id===5).checks[1].available,0,'structural guidance cannot create surprise samples');
+ assert.equal(updated.gates.find(g=>g.id===5).blocksOverall,true);
+ const coverage=updated.gates.find(g=>g.id===8).coverageObservations;
+ assert.equal(coverage.find(row=>row.year===2027).analysts,12);
+ assert.equal(coverage.find(row=>row.year===2027).epsAverage,281.54);
+ assert.ok(coverage.every(row=>row.productionEligible===false&&row.accountingBasis===null));
+ assert.deepEqual(updated.gates.find(g=>g.id===8).checks,old.gates.find(g=>g.id===8).checks,'Yahoo coverage cannot be borrowed by a different provider or approve a Gate');
+ const facts=updated.gates.find(g=>g.id===4).annualEvidence.facts;
+ assert.equal(facts.find(row=>row.metric==='market_share').value,null);
+ assert.equal(facts.find(row=>row.metric==='supplier_purchase_share').value,28.33);
+ assert.equal(facts.find(row=>row.metric==='customer_concentration').operator,'<');
+ assert.deepEqual(updated.veto,old.veto);assert.deepEqual(updated.scoring,old.scoring);
+ assert.deepEqual(updated.gates.find(g=>g.id===6),old.gates.find(g=>g.id===6),'financial warnings are preserved');
+ assert.equal(api.issuerEvidenceContext('5289','2026-10-19'),null,'issuer evidence is isolated');
+ assert.equal(api.issuerEvidenceContext('8299','2026-10-18'),null,'future capture cannot enter an earlier evaluation');
+ const captured=new Date(now).toISOString();
+ const rows=api.TAIWAN_MARKET_AUDIT_IDS.map((id,index)=>({id,name:id,status:'ok',date:index?'2026-10-19':'2026-10-16',value:100+index,unit:'test',source:'https://www.twse.com.tw/report',fetchedAt:captured,history:[{date:'2026-10-16',value:90+index}]}));
+ const market={checkedAt:captured,rows},summary=api.summarizeTaiwanMarket(rows);
+ assert.equal(summary.date,'2026-10-16');assert.equal(summary.dateAudit.referenceDate,'2026-10-19');assert.equal(summary.complete,true);
+ assert.equal(summary.available[1].value,91);assert.equal(rows[1].date,'2026-10-19');assert.equal(rows[1].value,101,'the common-date view never replaces the latest original row');
+ const model=api.evaluateMasterModel(stock,null,market,fresh,{}),gate2=model.gates.find(g=>g.id===2);
+ assert.equal(gate2.status,'evaluated');assert.equal(gate2.checks.filter(row=>row.state==='verified').length,9);
+ assert.match(gate2.checks[1].detail,/共同交易日 2026-10-16/);
+ const incomplete=structuredClone(rows);incomplete[1].history=[];
+ assert.equal(api.summarizeTaiwanMarket(incomplete).complete,false,'missing history cannot be forward-filled to create a common session');
+ const futureHistory=structuredClone(rows);futureHistory[1].history[0].fetchedAt='2026-10-20T00:00:00Z';
+ assert.equal(api.summarizeTaiwanMarket(futureHistory).complete,false,'a historical point captured after the evaluation cutoff cannot supply the common session');
+ const remembered=api.retainTaiwanComparisonHistory(rows.map(row=>({...row,history:[]})),[{checkedAt:captured,rows:rows.map(row=>({...row,date:'2026-10-16',value:90+api.TAIWAN_MARKET_AUDIT_IDS.indexOf(row.id)}))}],now);
+ assert.equal(remembered[1].history.find(p=>p.date==='2026-10-16').value,91);
+ const conflicting=api.retainTaiwanComparisonHistory([{...rows[1],history:[{date:'2026-10-16',value:999}]}],[{checkedAt:captured,rows:[{...rows[1],history:[{date:'2026-10-16',value:91}]}]}],now);
+ assert.ok(!conflicting[0].history.some(p=>p.date==='2026-10-16'),'conflicting historical values remain a gap');
+ console.log('Phison panel: common-session intersection, real-history retention and gaps, structural guidance, source-isolated Yahoo coverage, annual facts and unchanged financial/VETO/scoring passed');
+}finally{globalThis.Date=RealDate;}
diff --git a/tests/us-sector-session.test.mjs b/tests/us-sector-session.test.mjs
new file mode 100644
index 0000000..9b6a47a
--- /dev/null
+++ b/tests/us-sector-session.test.mjs
@@ -0,0 +1,74 @@
+// node --test handoff/v228/us_sector_session.test.mjs [上游 us_sector_history.json 路徑]
+// 沒給路徑時用同資料夾的 fixture（macro-relay-service 提交 bdb0edd 的 data/us_sector_history.json 原檔）
+import test from 'node:test';
+import assert from 'node:assert/strict';
+import { readFileSync } from 'node:fs';
+import { fileURLToPath } from 'node:url';
+import { dirname, join } from 'node:path';
+import { expectedLatestSession, sessionSettledAt, usSectorFreshness, isSession } from '../worker/us-sector-session.mjs';
+
+const here = dirname(fileURLToPath(import.meta.url));
+const path = process.argv.find((a) => a.endsWith('.json')) || join(here, 'fixtures/us-sector-bdb0edd.json');
+const real = JSON.parse(readFileSync(path, 'utf8'));
+const T = (s) => Date.parse(s);
+const withSession = (data, day, generatedAt) => {
+  const out = structuredClone(data);
+  for (const id of Object.keys(out.histories)) {
+    const rows = out.histories[id];
+    rows.push({ date: day, close: rows[rows.length - 1].close });
+    out.status[id] = { status: 'ok', observed_at: day, count: rows.length };
+  }
+  if (generatedAt) out.generated_at = generatedAt;
+  return out;
+};
+
+test('實檔：2026-10-17 01:28Z 產生、最後一天 10-15；10-19 10:26Z 應有 10-16 → LATEST_SESSION_MISSING（不是格式錯誤）', () => {
+  assert.equal(real.generated_at.slice(0, 19), '2026-10-17T01:28:36');
+  assert.equal(real.histories.SPY.at(-1).date, '2026-10-15');
+  const r = usSectorFreshness(real, T('2026-10-19T10:26:11.491Z'));
+  assert.deepEqual([r.ok, r.code, r.observed, r.expected], [false, 'LATEST_SESSION_MISSING', '2026-10-15', '2026-10-16']);
+});
+
+test('資料補上 10-16、擷取時間不變：週一早上仍可用（舊規則 57 小時會判 UNKNOWN）', () => {
+  const r = usSectorFreshness(withSession(real, '2026-10-16'), T('2026-10-19T10:26:11Z'));
+  assert.deepEqual([r.ok, r.observed, r.expected], [true, '2026-10-16', '2026-10-16']);
+});
+
+test('只刷新 generated_at、資料沒變：仍是 LATEST_SESSION_MISSING', () => {
+  const r = usSectorFreshness({ ...real, generated_at: '2026-10-19T09:00:00+00:00' }, T('2026-10-19T10:26:11Z'));
+  assert.equal(r.code, 'LATEST_SESSION_MISSING');
+});
+
+test('收盤後 8 小時內上游還沒發布：前一個交易日仍可用；超過才算缺', () => {
+  assert.equal(usSectorFreshness(real, T('2026-10-17T03:59:00Z')).ok, true);          // 10-16 收盤 20:15Z＋8h＝04:15Z
+  assert.equal(usSectorFreshness(real, T('2026-10-17T04:16:00Z')).code, 'LATEST_SESSION_MISSING');
+});
+
+test('擷取時間早於最後一列的收盤：CAPTURE_BEFORE_CLOSE', () => {
+  const r = usSectorFreshness(withSession(real, '2026-10-16', '2026-10-16T19:00:00+00:00'), T('2026-10-19T10:00:00Z'));
+  assert.equal(r.code, 'CAPTURE_BEFORE_CLOSE');
+});
+
+test('格式、來源、擷取時間各自的錯誤碼', () => {
+  const now = T('2026-10-19T10:26:11Z');
+  assert.equal(usSectorFreshness({ ...real, schema_version: 2 }, now).code, 'SCHEMA_MISMATCH');
+  assert.equal(usSectorFreshness({ ...real, source: 'x' }, now).code, 'SOURCE_MISMATCH');
+  assert.equal(usSectorFreshness({ ...real, generated_at: 'bad' }, now).code, 'CAPTURE_INVALID');
+  assert.equal(usSectorFreshness({ ...real, generated_at: '2026-10-20T00:00:00Z' }, now).code, 'CAPTURE_IN_FUTURE');
+});
+
+test('NYSE 休市日、提前收盤、夏令時間結束', () => {
+  assert.equal(isSession('2026-10-16'), true);
+  assert.equal(isSession('2026-11-26'), false);                                         // 感恩節
+  assert.equal(expectedLatestSession(T('2026-11-27T15:00:00Z')), '2026-11-25');          // 感恩節隔天上午
+  assert.equal(new Date(sessionSettledAt('2026-11-27')).toISOString(), '2026-11-27T18:15:00.000Z');   // 13:00 收盤
+  assert.equal(expectedLatestSession(T('2026-11-28T02:16:00Z')), '2026-11-27');
+  assert.equal(new Date(sessionSettledAt('2026-10-30')).toISOString(), '2026-10-30T20:15:00.000Z');   // 夏令
+  assert.equal(new Date(sessionSettledAt('2026-11-02')).toISOString(), '2026-11-02T21:15:00.000Z');   // 冬令
+  assert.equal(expectedLatestSession(T('2026-07-06T12:00:00Z')), '2026-07-02');          // 7/3 休市（獨立紀念日補假）
+});
+
+test('超出休市日表的年份：失敗而不是放行', () => {
+  const data = withSession(real, '2026-10-16');
+  assert.equal(usSectorFreshness(data, T('2028-01-05T12:00:00Z')).code, 'CALENDAR_NOT_COVERED');
+});
diff --git a/tests/us-sector-site.test.mjs b/tests/us-sector-site.test.mjs
index 492aded..2cebe7d 100644
--- a/tests/us-sector-site.test.mjs
+++ b/tests/us-sector-site.test.mjs
@@ -47,7 +47,7 @@ try {
  seed('stock:v5:8299',{...base,checkedAt:new Date().toISOString()});seed('macro:v1',{checkedAt:new Date().toISOString(),rows:[],light:'灰色',coverage:{missingCore:[]}});seed('macro-market:v7',{checkedAt:new Date().toISOString(),rows:[]});
  const model=await(await api.default.fetch(new Request('https://site.test/api/master-model?id=8299'),{DB:db})).json();assert.equal(model.report.usSectorContext.status,'OK');assert.equal(model.report.usSectorContext.observedAt,'2026-10-12');assert.equal(model.stockPriceDate,'2026-10-13');assert.ok(model.report.market.includes('美股板塊'));
  const older=structuredClone(data);for(const [id,history] of Object.entries(older.histories)){history.pop();older.status[id].observed_at=history.at(-1).date;older.status[id].count=history.length;}
- globalThis.fetch=async()=>Response.json(older);const retained=await api.refreshUSSectorSnapshot({DB:db});assert.equal(retained.sourceObservedAt,'2026-10-13');assert.equal(retained.publishStatus,'RETAINED_NEWER');
+ globalThis.fetch=async()=>Response.json(older);const retained=await api.refreshUSSectorSnapshot({DB:db});assert.equal(retained.sourceObservedAt,'2026-10-13');assert.equal(retained.generated_at,data.generated_at);assert.equal(retained.fetchError,'LATEST_SESSION_MISSING','a fetch missing the required session is rejected while the current stored snapshot is retained');
  globalThis.fetch=async()=>new Response('blocked',{status:503});const failed=await api.refreshUSSectorSnapshot({DB:db});assert.match(failed.fetchError,/503/);assert.equal(api.evaluateUSSectorContext(failed).status,'OK','a failed refresh retains a still-current original capture without moving its date');
  assert.equal((await api.default.fetch(new Request('https://site.test/api/us-sector-report',{method:'POST'}),{DB:db})).status,405);
 }finally{globalThis.fetch=originalFetch;}
diff --git a/worker/data-import.js b/worker/data-import.js
index 2d1ae5c..d11a33f 100644
--- a/worker/data-import.js
+++ b/worker/data-import.js
@@ -26,7 +26,7 @@ async function importedOfficialSeries(id, env) {
   if(['US3M','US10Y','US30Y'].includes(id))row.name={US3M:'13 週期美國國庫券折現殖利率（DTB3）',US10Y:'10 年期美債官方殖利率（DGS10）',US30Y:'30 年期美債官方殖利率（DGS30）'}[id];
   const releaseVerification=input.releaseVerification;
   if (row.status!=='ok'&&!releaseObservationCurrent(id,{...row,releaseVerification})) return null;
-  return {...row,status:'ok',provider:'FRED／原始官方提供者｜經外部抓取並保存',source:input.source,fetchedAt:input.fetchedAt,releaseVerification,snapshot:true,is_stale:false,historyObservations:history.length,historyFetchState:'fetched',sourceValidation:{state:'passed',method:'官方 CSV 原始觀測；日期、正值、排序及筆數已校驗'},detail:`官方來源觀測 ${row.date}；擷取 ${input.fetchedAt}。${releaseVerification?`官方頁面同值核對；下一次發布 ${releaseVerification.nextReleaseDate}。`:''}${id==='DEXJPUS'?'FRED H.10 日參考匯率，非盤中價格；保留完整歷史供 20／60 日波動率。':id==='IORB'?'聯準會準備金餘額利率；保留同日配對所需歷史。':['US3M','US10Y','US30Y'].includes(id)?'官方利率序列；DTB3 為折現殖利率，DGS10／DGS30 為固定到期投資收益率。':'官方現貨系列，與近月期貨分開。'}`};
+  return {...row,status:'ok',reason:null,provider:'FRED／原始官方提供者｜經外部抓取並保存',source:input.source,fetchedAt:input.fetchedAt,releaseVerification,snapshot:true,is_stale:false,historyObservations:history.length,historyFetchState:'fetched',sourceValidation:{state:'passed',method:'官方 CSV 原始觀測；日期、正值、排序及筆數已校驗'},detail:`官方來源觀測 ${row.date}；擷取 ${input.fetchedAt}。${releaseVerification?`官方頁面同值核對；下一次發布 ${releaseVerification.nextReleaseDate}。`:''}${id==='DEXJPUS'?'FRED H.10 日參考匯率，非盤中價格；保留完整歷史供 20／60 日波動率。':id==='IORB'?'聯準會準備金餘額利率；保留同日配對所需歷史。':['US3M','US10Y','US30Y'].includes(id)?'官方利率序列；DTB3 為折現殖利率，DGS10／DGS30 為固定到期投資收益率。':'官方現貨系列，與近月期貨分開。'}`};
 }
 async function officialDataImport(request, env) {
   if (request.method!=='POST') return Response.json({error:'method_not_allowed'},{status:405,headers:jsonHeaders});
diff --git a/worker/issuer-context.js b/worker/issuer-context.js
new file mode 100644
index 0000000..ef0f3fc
--- /dev/null
+++ b/worker/issuer-context.js
@@ -0,0 +1,6 @@
+// Reviewed source facts are displayed independently of scoring inputs.
+function issuerEvidenceContext(symbol,today) {
+  const data=ISSUER_CONTEXT_SEED;
+  if(symbol!==data.symbol||!masterEvidenceDate(today)||today<data.asOf||Date.parse(today)-Date.parse(data.asOf)>395*86400000)return null;
+  return {...data,coverageObservations:data.coverageObservations.filter(row=>Date.parse(`${today}T23:59:59+08:00`)>=Date.parse(row.capturedAt)&&Date.parse(today)-Date.parse(row.capturedAt)<=90*86400000)};
+}
diff --git a/worker/macro.js b/worker/macro.js
index b53d489..f3973c0 100644
--- a/worker/macro.js
+++ b/worker/macro.js
@@ -638,6 +638,8 @@ function evaluateMasterModel(stock, macro, market, freshness = {}, gateEvidence
   const today=new Date(Date.now()+8*3600000).toISOString().slice(0,10),years=[Number(today.slice(0,4)),Number(today.slice(0,4))+1];
   const officialPairs=pairMasterOfficialEvidence(gateEvidence.officialCompany?.records,stock.id,today,gateEvidence.gate5bBoundaries);
   const guidance=summarizeMasterGuidance([...officialPairs.guidance,...(gateEvidence.guidance||[])],stock.id,today),surprises=summarizeMasterSurprises([...officialPairs.surprises,...(gateEvidence.surprises||[])],stock.id,today,gateEvidence.gate5bBoundaries);
+  const issuerContext=issuerEvidenceContext(stock.id,today);
+  if(issuerContext?.guidanceDisclosure&&guidance.samples===0){guidance.applicability='structural_unavailable';guidance.disclosure=issuerContext.guidanceDisclosure;}
   const companyEstimates=verifiedCompanyConsensus(gateEvidence.officialCompany?.records,stock.id);
   const estimates=[...companyEstimates,...(gateEvidence.estimates||[])];
   const consensus=summarizeMasterConsensus(estimates,stock.id,today,years),peers=summarizeMasterPeers(gateEvidence.peerInputs,stock.id,today,years,price?.date);
@@ -719,6 +721,12 @@ function evaluateMasterModel(stock, macro, market, freshness = {}, gateEvidence
   gates.find(gate=>gate.id===4).detail+=`十維度必要資料已接入 ${tenDimensionReady}/10 項；請展開逐項缺口。`;
 
   gates.find(gate=>gate.id===5).checks=[check('5A 同指標指引回測',guidance.samples,8,guidance.metric||'原始指引與同口徑實績配對'),check('5B 財報前共識與實際 EPS',surprises.samples,8,'同股票、不同季度；共識日期早於財報公告')];
+  if(guidance.applicability==='structural_unavailable'){
+    const gate=gates.find(row=>row.id===5),disclosure=guidance.disclosure;
+    gate.guidanceApplicability=guidance.applicability;
+    gate.detail=`已自動讀取資料池：${gateEvidence.pool?.guidance||0} 筆公司指引候選、${gateEvidence.pool?.consensus||0} 筆 EPS 共識候選；${gateEvidence.pool?.status==='read_error'?'資料池讀取失敗，候選筆數待重查。':''}${disclosure.label}；核對範圍截至 ${disclosure.reviewedThrough}。${disclosure.scope}。已保存的年度指引及定性展望保留原類型；季度指引樣本不以年度數字補齊。有效市場 EPS surprise ${surprises.samples}/8 個不同季度；仍需界線前已存的季度共識與同口徑實績。`;
+    gate.checks[0]={...check('5A 季度數字財測',0,8,`${disclosure.label}；${disclosure.scope}`,'not_applicable'),applicability:'structural_unavailable'};
+  }
   const pairingProblems=[...officialPairs.rejected,...guidance.rejected.map(row=>({...row,gate:'5A'})),...surprises.rejected.map(row=>({...row,gate:'5B'}))];
   gates.find(gate=>gate.id===5).pairingAudit={engineStatus:'ready',officialGuidancePairs:officialPairs.guidance.length,officialSurprisePairs:officialPairs.surprises.length,rejected:pairingProblems};
   if(pairingProblems.length)gates.find(gate=>gate.id===5).detail+=`自動配對已執行；${[...new Set(pairingProblems.map(row=>row.reason))].join('；')}。`;
@@ -730,6 +738,7 @@ function evaluateMasterModel(stock, macro, market, freshness = {}, gateEvidence
     gate.dataState ||= gate.status==='evaluated'?'verified':gate.status==='warning'?'verified':'partial';
     if(!freshness.stockFresh&&[4,6,7,8,9,10].includes(gate.id))gate.dataState='stale';
     gate.nextAction=({3:'成熟股票依 95% 覆蓋核驗；新股獨立累積 21 個官方交易日，實際缺日仍須補齊。',4:'引擎已接軌；補核原始分級尺度、組內權重與各維度來源，逐條排除未知 Veto；真實警訊保留。',5:'自動來源持續保存；只有原始指引與實績配對、財報前共識日期均核對者才增加有效樣本。',6:qualityRisk?'核對負現金流、應收與庫存變動原因；真實警訊保留。':fq.roicApplicability?.status==='not_applicable'?'採現金流與其他適用財務比率判讀，ROIC 不沿用舊值。':'補齊最新季度必要財報欄位。',8:'自動依股票代號收集共識來源；補齊兩年共識及直接同業一致口徑，不以產業預測代替。',9:dcfFallback?'使用明列的跨週期替代情境，仍受其他 Gate 與財報警訊限制。':'核對 Rf、Beta、Kd 日期及實測資料後再確認 DCF。'})[gate.id]||null;
+    if(gate.id===5&&guidance.applicability==='structural_unavailable')gate.nextAction='季度財測屬結構性不可得；持續保存財報前季度共識，日後若有新數字財測再核對適用性。';
     const relevant=companyRecords.filter(row=>gate.id===4?['governance','veto_inputs'].includes(row.kind):gate.id===5?['quarterly_result','annual_result','management_guidance','quarterly_consensus','qualitative_outlook'].includes(row.kind):gate.id===6?row.kind==='financial_reconciliation'||row.review_type:null);
     gate.sources=relevant.map(row=>({label:`${row.period || ''} ${row.kind==='quarterly_result'?'財報實績':row.kind==='management_guidance'?'年度指引':row.kind==='qualitative_outlook'?'公司展望':row.kind==='governance'?'治理／訴訟':'財報核對'}`,url:row.source_url,sourceDate:row.source_date,detail:row.summary||row.body||'',validationStatus:row.validation_status}));
     if(gate.id===1)gate.sources=rows.filter(row=>OFFICIAL_IMPORT_SERIES.has(row.id)&&row.sourceValidation?.state==='passed').map(row=>({label:row.name,url:row.source,sourceDate:row.date,detail:`${row.value} ${row.unit}；${row.historyObservations} 筆官方觀測`,validationStatus:'VERIFIED_SOURCE'}));
@@ -750,10 +759,19 @@ function evaluateMasterModel(stock, macro, market, freshness = {}, gateEvidence
       gate.detail+=`依股票代號另已保存 ${announcements.length} 筆公司重大訊息；尚未抽取核對的指引不計入回測。`;
     }
   }
+  if(issuerContext){
+    const gate4=gates.find(row=>row.id===4),gate8=gates.find(row=>row.id===8),annual=issuerContext.annual;
+    gate4.annualEvidence=annual;
+    gate4.detail+=`FY${annual.fiscalYear} 年報已核對市占率揭露、客戶／供應商集中度與委外生產原文；生產據點與替代產能仍未知。`;
+    gate4.sources.push(...annual.facts.map(row=>({label:`FY${annual.fiscalYear} 年報第 ${row.reportPage} 頁｜${row.metric}`,url:annual.originalUrl,sourceDate:null,detail:`${row.summary}；PDF 第 ${row.pdfPage} 頁；擷取 ${annual.capturedAt}；SHA-256 ${annual.sha256}`,validationStatus:'VERIFIED_ARCHIVED_DOCUMENT'})));
+    gate8.coverageObservations=issuerContext.coverageObservations;
+    gate8.detail+=issuerContext.coverageObservations.map(row=>`${row.year}E Yahoo ${row.quote} 留存頁有 ${row.analysts} 位分析師，平均 EPS ${row.epsAverage} TWD（${row.epsLow}–${row.epsHigh}）；會計口徑未明示，獨立列參考，不借給 FactSet。`).join('');
+    gate8.sources.push(...issuerContext.coverageObservations.map(row=>({label:`${row.year}E Yahoo 分析師覆蓋（獨立留存）`,url:row.archiveUrl,sourceDate:null,detail:`擷取 ${row.capturedAt}；${row.analysts} 位；平均 EPS ${row.epsAverage} TWD；原始發布日及會計口徑未明示；SHA-256 ${row.sha256}`,validationStatus:'COVERAGE_VERIFIED_BASIS_PENDING'})));
+  }
   // Context uses the existing Gate 1/2/3 mechanisms without adding points or a
   // new readiness blocker. Missing cross-market data cannot freeze the report.
   gates[0].detail+=` ${crossMarket.summary}`;
-  gates[1].checks=(taiwan?.dateAudit?.fields||[]).map(row=>({label:row.name,available:row.state==='aligned'?1:0,required:1,state:row.state==='aligned'?'verified':'missing',detail:`資料所屬期 ${row.dataPeriod||'UNKNOWN'}；發布 ${row.publishedAt||'來源未提供'}；擷取 ${row.fetchedAt||'UNKNOWN'}；${row.reason}`}));
+  gates[1].checks=(taiwan?.dateAudit?.fields||[]).map(row=>{const point=taiwan.dateAudit.comparisonRows.find(item=>item.id===row.id),aligned=!!point||row.state==='aligned';return {label:row.name,available:aligned?1:0,required:1,state:aligned?'verified':'missing',detail:`最新資料所屬期 ${row.dataPeriod||'UNKNOWN'}；發布 ${row.publishedAt||'來源未提供'}；擷取 ${row.fetchedAt||'UNKNOWN'}；${point?`共同交易日 ${point.date}，實際觀測 ${point.value} ${point.unit||''}；最新市場基準 ${taiwan.dateAudit.referenceDate}，不補值或變更原日期。`:row.reason}`};});
   for(const rule of veto.rules)if(rule.evidence)(gates[3].sources||=[]).push({label:`Veto ${rule.label}｜官方證據`,url:rule.evidence.sourceUrl,sourceDate:rule.evidence.publishedAt,detail:rule.detail,validationStatus:rule.state==='pending'?'PARTIAL_OFFICIAL_EVIDENCE':'VERIFIED_SOURCE'});
   for(const source of veto.rules.find(row=>row.id==='cb')?.registryReview?.sources||[])if(masterEvidenceHttps(source.source_url))(gates[3].sources||=[]).push({label:'CB 登錄／原始契約來源',url:source.source_url,sourceDate:source.document_date||null,detail:source.scope||'資料登錄與條款核對；不代表完整 VETO 已排除。',validationStatus:'PARTIAL_OFFICIAL_EVIDENCE'});
   gates[0].contextAssessments=[crossMarket,rateContext,usSectorContext];
diff --git a/worker/market-timeline.js b/worker/market-timeline.js
index 3fc1c51..80c8586 100644
--- a/worker/market-timeline.js
+++ b/worker/market-timeline.js
@@ -11,6 +11,25 @@ function preferMarketObservation(primary,fallback,now=Date.now()){
  if(a&&b)return fallback.date>primary.date?fallback:primary;
  return a?primary:b?fallback:primary||fallback;
 }
+function retainTaiwanComparisonHistory(rows,previous=[],now=Date.now()){
+ const today=new Date(now+8*3600000).toISOString().slice(0,10);
+ return rows.map(row=>{
+  if(!TAIWAN_MARKET_AUDIT_IDS.includes(row.id))return row;
+  const points=new Map(),conflicts=new Set();
+  for(const payload of [...previous,{rows}])for(const saved of (payload?.rows||[]).filter(item=>item.id===row.id)){
+   for(const point of [...(saved.history||[]),{date:saved.date,value:saved.value,source:saved.source,fetchedAt:saved.fetchedAt||saved.verifiedAt||payload.checkedAt,publishedAt:saved.publishedAt||null}]){
+    if(!marketAuditDate(point.date)||point.date>today||!Number.isFinite(point.value))continue;
+    const source=point.source||saved.source,captured=marketAuditInstant(point.fetchedAt||saved.fetchedAt||saved.verifiedAt||payload.checkedAt);
+    try{if(new URL(source).protocol!=='https:'||!captured||Date.parse(captured)>now)continue;}catch{continue;}
+    if(points.has(point.date)&&points.get(point.date).value!==point.value){points.delete(point.date);conflicts.add(point.date);continue;}
+    if(!conflicts.has(point.date))points.set(point.date,{date:point.date,value:point.value,source,fetchedAt:captured,publishedAt:point.publishedAt||null});
+   }
+  }
+  // Preserve only observed history. A disagreement removes that comparison
+  // point; it never supplies a filled value or replaces the latest row.
+  return {...row,history:[...points.values()].sort((a,b)=>a.date.localeCompare(b.date)).slice(-100),...(conflicts.size?{historyConflicts:[...conflicts]}:{})};
+ });
+}
 function parseLatestTaiwanIndices(payload,now=Date.now()){
  const key=String(payload?.date||''),date=/^\d{8}$/.test(key)?`${key.slice(0,4)}-${key.slice(4,6)}-${key.slice(6)}`:null;
  if(String(payload?.stat).toUpperCase()!=='OK'||!marketAuditDate(date)||date>new Date(now+8*3600000).toISOString().slice(0,10))throw Error('TWSE_AFTER_TRADING_DATE');
@@ -43,9 +62,10 @@ function buildMarketDateAudit(rows,{checkedAt=null,evaluationAt=Date.now()}={}){
   const reason=state==='aligned'?'與本次市場資料基準同日':state==='fetch_failed_retained'?`此欄位資料為 ${row.date}，非最新；更新失敗：${row.refreshError}`:state==='source_lag'?`此欄位資料為 ${row.date}，落後市場基準 ${referenceDate}；未取得來源更新證據，不推定尚未發布`:state==='not_available_at_cutoff'?'來源或首次擷取晚於評估時間，不可用於該截點':state==='future_observation'?'觀測日期在評估日之後':row.reason||'無有效資料或日期';
   return {id,name:row.name||id,dataPeriod:validDate?row.date:null,publishedAt,fetchedAt,availabilityBasis:publishedAt?'publisher_timestamp':fetchedAt?'first_observed_by_system':'unknown',availableByCutoff,state,reason,source:row.source||null};
  });
- const eligible=fields.filter(f=>['aligned','source_lag','fetch_failed_retained'].includes(f.state)&&f.availableByCutoff),sets=eligible.map(f=>{const row=by.get(f.id);return new Set([row.date,...(row.history||[]).filter(p=>marketAuditDate(p.date)&&p.date<=referenceDate&&Number.isFinite(p.value)).map(p=>p.date)]);});
- const common=eligible.length===TAIWAN_MARKET_AUDIT_IDS.length?[...(sets[0]||[])].filter(date=>sets.every(s=>s.has(date))).sort().at(-1)||null:null;
- const comparisonRows=common?eligible.map(f=>{const row=by.get(f.id),point=row.date===common?row:row.history.find(p=>p.date===common);return {id:row.id,name:row.name,date:common,value:point.value,unit:row.unit,source:row.source,publishedAt:f.publishedAt,fetchedAt:f.fetchedAt};}):[];
+ const eligible=fields.filter(f=>['aligned','source_lag','fetch_failed_retained'].includes(f.state)&&f.availableByCutoff),sets=eligible.map(f=>{const row=by.get(f.id);return new Set([row.date,...(row.history||[]).filter(p=>marketAuditDate(p.date)&&p.date<=row.date&&p.date<=referenceDate&&Number.isFinite(p.value)&&(!p.fetchedAt||marketAuditInstant(p.fetchedAt)&&Date.parse(p.fetchedAt)<=now)&&(!p.publishedAt||marketAuditInstant(p.publishedAt)&&Date.parse(p.publishedAt)<=now)).map(p=>p.date)]);});
+ const candidate=eligible.length===TAIWAN_MARKET_AUDIT_IDS.length?[...(sets[0]||[])].filter(date=>sets.every(s=>s.has(date))).sort().at(-1)||null:null;
+ const common=candidate&&(now-Date.parse(candidate))/86400000<=5?candidate:null;
+ const comparisonRows=common?eligible.map(f=>{const row=by.get(f.id),point=row.date===common?row:row.history.find(p=>p.date===common);return {id:row.id,name:row.name,date:common,value:point.value,unit:row.unit,source:point.source||row.source,publishedAt:row.date===common?f.publishedAt:marketAuditInstant(point.publishedAt),fetchedAt:marketAuditInstant(point.fetchedAt)||f.fetchedAt};}):[];
  return {version:1,evaluationAt:new Date(now).toISOString(),referenceDate,referenceDateBasis:'latest_valid_observed_trade_date',commonTradeDate:common,status:common?'COMMON_DATE_AVAILABLE':'DATE_ALIGNMENT_INCOMPLETE',usable:valid.length,total:TAIWAN_MARKET_AUDIT_IDS.length,fields,comparisonRows,pointInTimeReconstruction:false,limitations:['發布時間未知時保留 null；擷取時間只證明網站當時已見資料。','本次共同觀測日不是歷史資訊可得性的回測證明；不前填缺失交易日。']};
 }
 async function marketAuditResponse(response){
diff --git a/worker/master-evidence.js b/worker/master-evidence.js
index dbb1c48..0448162 100644
--- a/worker/master-evidence.js
+++ b/worker/master-evidence.js
@@ -139,7 +139,7 @@ function masterQualifiedOutput({gates,stock,primaryValuation,veto,scoring,guidan
   const limits=[
     veto.status==='pending'?`否決條件仍有 ${veto.rules.filter(row=>row.state==='pending').length} 條待核；未判定安全。`:null,
     !scoring.ready?`10D 資料 ${10-missingDimensions}/10；原始分級、權重與三層評分須完整核驗，未評估項目不給中性分數。`:null,
-    !guidance.ready?`指引回測 ${guidance.samples}/8 期，樣本不足，不估管理層命中率。`:null,
+    !guidance.ready?guidance.applicability==='structural_unavailable'?`${guidance.disclosure.label}；依已核對範圍不估季度指引命中率。`:`指引回測 ${guidance.samples}/8 期，樣本不足，不估管理層命中率。`:null,
     !surprises.ready?`季度 EPS surprise ${surprises.samples}/8 期，樣本不足，不推定超預期表現。`:null,
     !current.ready?`${current.year} 共識尚未核驗，Forward P/E 不計算。`:null,
     !next.ready?`${next.year} 共識僅列輔助候選；分析師覆蓋未核驗，不計入評級。`:null,
diff --git a/worker/observation-freshness.js b/worker/observation-freshness.js
index 460bfe2..c05dd72 100644
--- a/worker/observation-freshness.js
+++ b/worker/observation-freshness.js
@@ -89,6 +89,22 @@ function coreCpiVerificationCurrent(row,now=Date.now()) {
   return new Set(valid.map(reading=>reading.sourceFamily)).size===2;
 }
 function macroObservationCurrent(row,payload,now=Date.now()) {
+  const parentId=macroDerivedParentId(row);
+  if(parentId){
+    if(!['ok','snapshot','stale'].includes(row?.status)||row.validationState!=='validated'||!Number.isFinite(row.value)||!officialImportDate(row.date))return false;
+    const parent=payload?.rows?.find(item=>item.id===parentId);
+    if(!parent||parent.date!==row.date||row.parentDate!=null&&row.parentDate!==parent.date||!Number.isFinite(parent.value))return false;
+    const candidate=parent.status==='stale'&&parent.releaseVerification?{...parent,status:parent.snapshot?'snapshot':'ok',is_stale:false}:parent;
+    if(macroObservationCurrent(candidate,payload,now))return true;
+    // ECB/Frankfurter can provide a separately labeled reference-rate series
+    // with its own complete history. It may feed volatility, but never borrows
+    // the FRED release window; validate its capture, endpoint family and age.
+    if(parent.status==='proxy'&&parent.historyFetchState==='fetched'&&parent.historyObservations>=65&&
+      recentOfficialCapture(parent.verifiedAt||parent.fetchedAt||payload.checkedAt,now)&&age(parent.date)>=-1&&age(parent.date)<=(SERIES.DEXJPUS?.[3]??7)){
+      try{const source=new URL(parent.source);return source.protocol==='https:'&&['data.ecb.europa.eu','api.frankfurter.dev'].includes(source.hostname);}catch{return false;}
+    }
+    return false;
+  }
   if(!['ok','snapshot'].includes(row?.status)||row.is_stale||!Number.isFinite(row.value)||!officialImportDate(row.date))return false;
   // A monthly BLS capture and a recent BLS/FRED comparison use distinct clocks.
   if(row.id==='CPILFESL')return coreCpiVerificationCurrent(row,now);
@@ -110,15 +126,46 @@ function macroSnapshotRecent(payload) {
 }
 function mergeVerifiedMacroRows(rows,previous) {
   return rows.map(row=>{
-    if(['ok','snapshot'].includes(row?.status)&&!row.is_stale&&Number.isFinite(row.value))return {...row,verifiedAt:row.id==='CPILFESL'&&coreCpiVerificationCurrent(row)?row.sourceVerification.checkedAt:row.verifiedAt||row.fetchedAt||new Date().toISOString()};
+    if(['ok','snapshot'].includes(row?.status)&&!row.is_stale&&Number.isFinite(row.value))return {...row,verifiedAt:row.id==='CPILFESL'&&coreCpiVerificationCurrent(row)?row.sourceVerification.checkedAt:row.verifiedAt||row.fetchedAt||new Date().toISOString(),reason:obsoleteObservationReason(row.reason)?null:row.reason};
     const candidates=previous.flatMap(p=>(p?.rows||[]).filter(old=>old.id===row.id&&macroObservationCurrent(old,p)).map(old=>({old,p}))).sort((a,b)=>b.old.date.localeCompare(a.old.date)||Date.parse(b.old.verifiedAt||b.old.fetchedAt||b.p.checkedAt)-Date.parse(a.old.verifiedAt||a.old.fetchedAt||a.p.checkedAt));
     const best=candidates[0];
     if(!best)return row;
     return {...best.old,history:best.old.history||best.p.sourceHistories?.[row.id],status:'snapshot',snapshot:true,is_stale:false,sourceValidation:best.old.sourceValidation||{state:'passed',method:'保留有效期內上次已核對的來源觀測'},verifiedAt:best.old.verifiedAt||best.old.fetchedAt||best.p.checkedAt,refreshError:row.reason||'本次來源未完成核驗',reason:'本次來源暫不可用；保留有效期內已核實的官方觀測，日期不變。'};
   });
 }
+function obsoleteObservationReason(reason) {
+  return ['資料較舊，暫不納入判讀','觀測資料較舊，暫不納入判讀','EIA 觀測較舊，暫不納入判讀','保留前次成功觀測；資料較舊'].includes(reason);
+}
+function macroDerivedParentId(row) {
+  if(row?.derivedFrom==='DEXJPUS'||row?.id==='JPY_HV20'||row?.id==='JPY_HV60')return 'DEXJPUS';
+  return null;
+}
 function refreshingMacroSnapshot(payload,refreshing=true) {
-  const rows=(payload.rows||[]).map(row=>['ok','snapshot'].includes(row.status)&&!macroObservationCurrent(row,payload)?{...row,status:'stale',is_stale:true,reason:'官方觀測或最近來源核對已過有效期；等待更新。'}:row);
+  const sourceRows=payload.rows||[];
+  const refreshSource=row=>{
+    if(!['ok','snapshot','stale'].includes(row?.status))return row;
+    // A release-verified observation may remain current beyond its ordinary
+    // SERIES age. Re-evaluate stale rows with that evidence and keep status,
+    // is_stale and expiry reason aligned to the same final decision.
+    const candidate=row.status==='stale'&&row.releaseVerification?{...row,status:row.snapshot?'snapshot':'ok',is_stale:false}:row;
+    const current=macroObservationCurrent(candidate,payload);
+    if(current)return {...candidate,is_stale:false,reason:obsoleteObservationReason(candidate.reason)?null:candidate.reason};
+    if(['ok','snapshot'].includes(row.status))return {...row,status:'stale',is_stale:true,reason:'官方觀測或最近來源核對已過有效期；等待更新。'};
+    return {...row,is_stale:true,reason:obsoleteObservationReason(row.reason)?'官方觀測或最近來源核對已過有效期；等待更新。':row.reason};
+  };
+  // Refresh source observations first; derived rows inherit the parent's
+  // release/session validity instead of applying a generic seven-day clock.
+  const refreshed=sourceRows.map(row=>macroDerivedParentId(row)?row:refreshSource(row));
+  const parentPayload={...payload,rows:refreshed.filter(row=>!macroDerivedParentId(row))};
+  const rows=refreshed.map(row=>{
+    const parentId=macroDerivedParentId(row);
+    if(!parentId)return row;
+    const parent=parentPayload.rows.find(item=>item.id===parentId);
+    if(row.validationState!=='validated'||row.value==null)return row;
+    const dateMismatch=parent&&(parent.date!==row.date||row.parentDate!=null&&row.parentDate!==parent.date);
+    if(!parent||dateMismatch||!macroObservationCurrent(row,parentPayload))return {...row,value:null,status:'missing',is_stale:false,validationState:!parent?'source_missing':dateMismatch?'source_date_mismatch':'source_stale',reason:`母序列 ${parentId} 過期、未核或日期不一致；衍生波動率不納入判讀。`};
+    return {...row,derivedFrom:parentId,parentDate:parent.date,status:row.snapshot?'snapshot':'ok',is_stale:false,reason:null};
+  });
   const monthly=new Map(rows.filter(row=>['CPILFESL','PCEPILFE'].includes(row.id)).map(row=>[row.id,row]));
   const derived=(payload.derived||[]).map(row=>{
     const id=row.name?.startsWith('核心 CPI ')?'CPILFESL':row.name?.startsWith('核心 PCE ')?'PCEPILFE':null,parent=monthly.get(id);
diff --git a/worker/observations.js b/worker/observations.js
index adc01a6..a0c91cb 100644
--- a/worker/observations.js
+++ b/worker/observations.js
@@ -1951,10 +1951,11 @@ function summarizeTaiwanMarket(rows = []) {
   const ids = ['TWSE_TAIEX','TWSE_TOTAL_TRADE_VALUE','TWSE_BREADTH','TPEX_BREADTH','TWSE_MARGIN_BALANCE_NTD','TWSE_SHORT_BALANCE','TWSE_MARGIN_MARKET_CAP_RATIO','TWSE_CREDIT_TRADE_VALUE','TWSE_DAYTRADE'];
   const by = Object.fromEntries(rows.map(row => [row.id, row]));
   const valid = id => ['ok','snapshot'].includes(by[id]?.status) && by[id]?.is_stale !== true && finiteNumber(by[id]?.value) && /^\d{4}-\d{2}-\d{2}$/.test(by[id]?.date || '');
-  const available = ids.filter(valid).map(id => ({ id, name: by[id].name, date: by[id].date, value: by[id].value, unit: by[id].unit, source: by[id].source }));
-  const dates = [...new Set(available.map(row => row.date))];
+  const latestAvailable = ids.filter(valid).map(id => ({ id, name: by[id].name, date: by[id].date, value: by[id].value, unit: by[id].unit, source: by[id].source }));
+  const dates = [...new Set(latestAvailable.map(row => row.date))];
   const dateAudit=buildMarketDateAudit(rows);
-  return { usable: available.length, total: ids.length, date: dates.length === 1 ? dates[0] : null, dates, aligned: dates.length === 1, complete: available.length === ids.length && dates.length === 1 && !dateAudit.fields.some(f=>['future_observation','not_available_at_cutoff'].includes(f.state)), available, dateAudit, missing: ids.filter(id => !valid(id)).map(id => ({ id, name: by[id]?.name || SERIES[id]?.[0] || id, reason: by[id]?.reason || '本次來源未回傳有效數值' })) };
+  const common=dateAudit.commonTradeDate,available=common?dateAudit.comparisonRows:latestAvailable,aligned=!!common||dates.length===1;
+  return { usable: available.length, total: ids.length, date: common||(dates.length === 1 ? dates[0] : null), dates, aligned, comparisonBasis:common?'latest_common_observed_session':'latest_observations',latestAvailable,complete: available.length === ids.length && aligned && !dateAudit.fields.some(f=>['future_observation','not_available_at_cutoff'].includes(f.state)), available, dateAudit, missing: ids.filter(id => !valid(id)).map(id => ({ id, name: by[id]?.name || SERIES[id]?.[0] || id, reason: by[id]?.reason || '本次來源未回傳有效數值' })) };
 }
 function evaluate(rows, internalRows=[]) {
   const by = Object.fromEntries([...rows,...internalRows].map(x => [x.id,x])), valid = id => ['ok','snapshot'].includes(by[id]?.status)&&by[id]?.is_stale!==true;
@@ -2171,10 +2172,10 @@ async function macroMarketResponse(env={},ctx={}) {
     rows.push(live10Y3MSpread(t10y3m?[...rows,t10y3m]:rows));
     const yen=macroMarketRows.find(row=>row.id==='DEXJPUS'),yenHistory=yen?.history||[];
     const rollingVol=(n)=>{const required=n+1,points=yenHistory.slice(-required);if(yen?.historyFetchState==='fetch_failed'||!yenHistory.length)return {value:null,state:'fetch_failed',reason:yen?.reason||'匯率歷史來源沒有回應'};if(yen?.historyFetchState==='source_stale'||yen?.status==='stale')return {value:null,state:'source_stale',reason:yen.reason||'匯率來源觀測已過期'};if(points.length<required)return {value:null,state:'sample_insufficient',reason:`已取回 ${yenHistory.length} 筆；${n} 日波動率需 ${required} 筆交易日資料`};const gap=points.slice(1).find((x,i)=>Date.parse(x.date)-Date.parse(points[i].date)>5*86400000);if(gap)return {value:null,state:'sample_insufficient',reason:`已取回 ${yenHistory.length} 筆，但計算窗口含超過 5 日的觀測缺口，無法視為連續交易日樣本`};const returns=points.slice(1).map((x,i)=>Math.log(x.value/points[i].value)).filter(Number.isFinite);if(returns.length!==n)return {value:null,state:'sample_insufficient',reason:`有效日報酬 ${returns.length}/${n}；樣本不足`};const mean=returns.reduce((a,b)=>a+b,0)/n,variance=returns.reduce((s,x)=>s+(x-mean)**2,0)/(n-1);return {value:Math.sqrt(variance*252)*100,state:'validated',reason:null};};
-    for(const n of [20,60]){const result=rollingVol(n);rows.push({id:`JPY_HV${n}`,name:`日圓匯率歷史波動率（${n} 日）`,group:'曲線／放大器',unit:'% 年化',value:result.value,date:yenHistory.at(-1)?.date||null,status:result.value==null?'missing':'ok',validationState:result.state,historyObservations:yenHistory.length,requiredObservations:n+1,reason:result.reason,provider:`${yen?.provider||'FRED／ECB 匯率來源'}；按日對數報酬年化標準差計算`,source:yen?.source||link('DEXJPUS')});}
+    for(const n of [20,60]){const result=rollingVol(n);rows.push({id:`JPY_HV${n}`,name:`日圓匯率歷史波動率（${n} 日）`,group:'曲線／放大器',unit:'% 年化',value:result.value,date:yenHistory.at(-1)?.date||null,derivedFrom:'DEXJPUS',parentDate:yenHistory.at(-1)?.date||null,status:result.value==null?'missing':'ok',validationState:result.state,historyObservations:yenHistory.length,requiredObservations:n+1,reason:result.reason,provider:`${yen?.provider||'FRED／ECB 匯率來源'}；按日對數報酬年化標準差計算`,source:yen?.source||link('DEXJPUS')});}
     const previous=await readRuntimeCache(env,'macro:v1');
-    const verified=mergeVerifiedMacroRows(rows,[lastGood,previous?.payload]);
-    return {checkedAt:new Date().toISOString(),rows:verified.map(({history,...row})=>row),taiwanMarket:summarizeTaiwanMarket(verified)};
+    const verified=retainTaiwanComparisonHistory(mergeVerifiedMacroRows(rows,[lastGood,previous?.payload]),[lastGood,previous?.payload]);
+    return {checkedAt:new Date().toISOString(),rows:verified.map(({history,...row})=>TAIWAN_MARKET_AUDIT_IDS.includes(row.id)?{...row,history}:row),taiwanMarket:summarizeTaiwanMarket(verified)};
   })().then(async payload=>{
     macroMarketCache={at:Date.now(),payload};
     await writeRuntimeCache(env,'macro-market:v7',payload,ttl);
diff --git a/worker/us-sector-session.mjs b/worker/us-sector-session.mjs
new file mode 100644
index 0000000..f593841
--- /dev/null
+++ b/worker/us-sector-session.mjs
@@ -0,0 +1,90 @@
+// us_sector_session.mjs — 美股板塊快照「應有交易日」檢查（給 v228 的修補建議，gate-probe 不部署）
+//
+// 取代 normalizeUSSectorSnapshot 裡的「generated_at 距今 > 36 小時就丟 SCHEMA_SOURCE_OR_CAPTURE」：
+//   1. 格式、來源、擷取時間各自回報錯誤碼，不再混在一起。
+//   2. 時效改看「資料有沒有包含最後一個應有的交易日」，不看 generated_at 有多舊：
+//      週末、假日不會誤判過期；只刷新 generated_at、資料沒變，也不會被當成更新。
+//   3. 交易日依 NYSE 官方休市日與提前收盤日；超出表列年份就失敗（逼著更新表，不靜默放行）。
+//
+// NYSE 休市日與提前收盤：https://www.nyse.com/markets/hours-calendars（2026-10-19 讀取）
+
+export const NYSE_HOLIDAYS = new Set([
+  '2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03', '2026-05-25', '2026-06-19', '2026-07-03',
+  '2026-09-07', '2026-11-26', '2026-12-25',
+  '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18', '2027-07-05',
+  '2027-09-06', '2027-11-25', '2027-12-24',
+]);
+export const NYSE_EARLY_CLOSE = new Set(['2026-11-27', '2026-12-24', '2027-11-26']);   // 13:00 收盤
+export const CALENDAR_FIRST_DAY = '2026-01-01';
+export const CALENDAR_LAST_DAY = '2027-12-31';
+// 上游排程 23:35 UTC（週一至週五），GitHub 實際延遲約 1.9–2.5 小時（2026-10-14～10-17 的提交時間）；
+// 收盤後 8 小時內還沒發布，才算缺少該交易日。
+export const PUBLISH_GRACE_HOURS = 8;
+const SETTLE_MINUTES = 15;   // 收盤後 15 分鐘才算完成（沿用 v228 的 16:15）
+
+const DAY = 86400000;
+const isDay = (s) => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && new Date(s + 'T00:00:00Z').toISOString().slice(0, 10) === s;
+const addDays = (s, n) => new Date(Date.parse(s + 'T00:00:00Z') + n * DAY).toISOString().slice(0, 10);
+
+function nyParts(ms) {
+  const p = Object.fromEntries(new Intl.DateTimeFormat('en-CA', {
+    timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit',
+    hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
+  }).formatToParts(new Date(ms)).map((x) => [x.type, x.value]));
+  return { day: `${p.year}-${p.month}-${p.day}`, minutes: Number(p.hour) * 60 + Number(p.minute) };
+}
+
+export function calendarCovers(day) {
+  return isDay(day) && day >= CALENDAR_FIRST_DAY && day <= CALENDAR_LAST_DAY;
+}
+
+export function isSession(day) {
+  if (!calendarCovers(day)) throw Error('CALENDAR_NOT_COVERED');
+  const wd = new Date(day + 'T00:00:00Z').getUTCDay();
+  return wd !== 0 && wd !== 6 && !NYSE_HOLIDAYS.has(day);
+}
+
+// 該交易日收盤後 15 分鐘的 UTC 時刻（夏令／冬令由 America/New_York 決定）
+export function sessionSettledAt(day) {
+  const close = (NYSE_EARLY_CLOSE.has(day) ? 13 * 60 : 16 * 60) + SETTLE_MINUTES;
+  const noon = Date.parse(day + 'T12:00:00Z');
+  const ny = nyParts(noon);
+  const offsetMin = (ny.minutes - 12 * 60) + (ny.day < day ? -1440 : ny.day > day ? 1440 : 0);   // 紐約比 UTC 慢幾分鐘（負值）
+  return Date.parse(day + 'T00:00:00Z') + (close - offsetMin) * 60000;
+}
+
+// 現在這個時刻「應該已經有」的最後一個交易日
+export function expectedLatestSession(now, graceHours = PUBLISH_GRACE_HOURS) {
+  let d = nyParts(now).day;
+  for (let i = 0; i < 15; i++, d = addDays(d, -1)) {
+    if (isSession(d) && now >= sessionSettledAt(d) + graceHours * 3600000) return d;
+  }
+  throw Error('NO_SESSION_FOUND');
+}
+
+// 回傳 {ok:true, observed, expected} 或 {ok:false, code, ...}；不丟例外，呼叫端照 code 顯示
+export function usSectorFreshness(data, now = Date.now(), opts = {}) {
+  const grace = opts.graceHours ?? PUBLISH_GRACE_HOURS;
+  if (!data || typeof data !== 'object') return { ok: false, code: 'SCHEMA_MISMATCH', detail: 'root' };
+  if (data.schema_version !== 1) return { ok: false, code: 'SCHEMA_MISMATCH', detail: `schema_version=${data.schema_version}` };
+  if (data.source !== 'Yahoo Finance chart API (unofficial)') return { ok: false, code: 'SOURCE_MISMATCH', detail: String(data.source) };
+  if (!data.histories || typeof data.histories !== 'object' || Array.isArray(data.histories) || !data.status) {
+    return { ok: false, code: 'SCHEMA_MISMATCH', detail: 'histories/status' };
+  }
+  const captured = Date.parse(data.generated_at || '');
+  if (!Number.isFinite(captured)) return { ok: false, code: 'CAPTURE_INVALID', detail: String(data.generated_at) };
+  if (captured > now + 60000) return { ok: false, code: 'CAPTURE_IN_FUTURE', detail: data.generated_at };
+  const spy = Array.isArray(data.histories.SPY) ? data.histories.SPY : [];
+  const observed = spy.length ? spy[spy.length - 1].date : null;
+  if (!isDay(observed)) return { ok: false, code: 'BENCHMARK_UNAVAILABLE' };
+  let expected;
+  try {
+    if (!isSession(observed)) return { ok: false, code: 'NOT_A_SESSION', observed };
+    expected = expectedLatestSession(now, grace);
+  } catch (e) {
+    return { ok: false, code: e.message, observed };   // CALENDAR_NOT_COVERED：休市日表要更新
+  }
+  if (captured < sessionSettledAt(observed)) return { ok: false, code: 'CAPTURE_BEFORE_CLOSE', observed, captured_at: data.generated_at };
+  if (observed < expected) return { ok: false, code: 'LATEST_SESSION_MISSING', observed, expected, captured_at: data.generated_at };
+  return { ok: true, observed, expected, captured_at: data.generated_at };
+}
diff --git a/worker/us-sectors.js b/worker/us-sectors.js
index 26d3fd3..38372a9 100644
--- a/worker/us-sectors.js
+++ b/worker/us-sectors.js
@@ -9,11 +9,12 @@ function usSectorClock(now) {
   return {day:`${parts.year}-${parts.month}-${parts.day}`,minutes:Number(parts.hour)*60+Number(parts.minute)};
 }
 function usSectorCloseCompleted(date,clock) {
-  return cmDate(date)&&![0,6].includes(new Date(date).getUTCDay())&&(date<clock.day||date===clock.day&&clock.minutes>=975);
+  return cmDate(date)&&US_SECTOR_SESSION.calendarCovers(date)&&US_SECTOR_SESSION.isSession(date)&&(date<clock.day||date===clock.day&&clock.minutes>=(US_SECTOR_SESSION.NYSE_EARLY_CLOSE.has(date)?795:975));
 }
 function normalizeUSSectorSnapshot(data,now=Date.now()) {
-  const captured=Date.parse(data?.generated_at||'');
-  if(data?.schema_version!==1||data.source!=='Yahoo Finance chart API (unofficial)'||!data.histories||typeof data.histories!=='object'||Array.isArray(data.histories)||!data.status||!Number.isFinite(captured)||captured>now+60000||now-captured>36*3600000)throw Error('SCHEMA_SOURCE_OR_CAPTURE');
+  const freshness=US_SECTOR_SESSION.usSectorFreshness(data,now);
+  if(!freshness.ok)throw Object.assign(Error(freshness.code),{freshness});
+  const captured=Date.parse(data.generated_at);
   const histories={},status={},currentClock=usSectorClock(now),captureClock=usSectorClock(captured);
   for(const id of ['SPY',...US_SECTOR_CORE.SECTORS]) {
     const rows=data.histories[id],state=data.status[id],valid=Array.isArray(rows)&&rows.length<=300&&rows.every(row=>usSectorCloseCompleted(row?.date,currentClock)&&usSectorCloseCompleted(row?.date,captureClock)&&typeof row.close==='number'&&Number.isFinite(row.close)&&row.close>0);
@@ -23,11 +24,11 @@ function normalizeUSSectorSnapshot(data,now=Date.now()) {
     histories[id]=ok?sorted:[];status[id]=ok?{status:'ok',observed_at:latest,count:sorted.length}:{status:'unknown',observed_at:state?.observed_at||null,count:0};
   }
   if(!histories.SPY.length)throw Error('BENCHMARK_UNAVAILABLE');
-  return {schema_version:1,generated_at:data.generated_at,source:data.source,histories,status,sourceObservedAt:histories.SPY.at(-1).date};
+  return {schema_version:1,generated_at:data.generated_at,source:data.source,histories,status,sourceObservedAt:histories.SPY.at(-1).date,sessionFreshness:freshness};
 }
 function evaluateUSSectorContext(snapshot,{referenceDate=null,now=Date.now()}={}) {
   const limits={scoreContribution:0,macroGateOverride:null,vetoOverride:null},unknown=reason=>({...US_SECTOR_CORE.buildSectorReport(),...limits,errorCode:reason,sourceUrl:US_SECTOR_URL,pending:!!snapshot?.pending,refreshing:!!snapshot?.refreshing,referenceDate,summary:`美股板塊 UNKNOWN：${reason}；其他報告繼續輸出，新增評分0。`});
-  let data;try{data=normalizeUSSectorSnapshot(snapshot,now);}catch(error){return unknown(snapshot?.error||error.message);}
+  let data;try{data=normalizeUSSectorSnapshot(snapshot,now);}catch(error){return {...unknown(snapshot?.error||error.message),sessionFreshness:error.freshness||null};}
   if(referenceDate!=null&&(!cmDate(referenceDate)||referenceDate>new Date(now+8*3600000).toISOString().slice(0,10)))return unknown('REFERENCE_DATE_INVALID');
   const sourceCoverage=['SPY',...US_SECTOR_CORE.SECTORS].filter(id=>data.status[id].status==='ok').length;
   const analysis={...data,histories:{},status:{}};

```

## 完整中繼 git diff（PR #6 六檔，未省略）

基準 `46b58640c7b3f839c0c4d55e77ddddacfaacbb64`。此diff已在獨立分支提交，尚未合併。

```diff
diff --git a/.github/workflows/us-sector-history.yml b/.github/workflows/us-sector-history.yml
index f537fef..5fcd000 100644
--- a/.github/workflows/us-sector-history.yml
+++ b/.github/workflows/us-sector-history.yml
@@ -10,6 +10,8 @@ on:
   workflow_dispatch:
   schedule:
     - cron: '35 23 * * 1-5'
+    # Retry after a late-finalized Yahoo bar; publishes only when rows actually change.
+    - cron: '45 3 * * 2-6'
 permissions:
   contents: write
 concurrency:
@@ -59,6 +61,11 @@ jobs:
               echo "Sector snapshot guard failed" >&2
               exit "$guard_status"
             fi
+            if [ -f data/us_sector_history.json ] && python3 -c 'import json,sys; k=lambda p:{x:json.load(open(p)).get(x) for x in ("histories","status")}; sys.exit(0 if k(sys.argv[1])==k(sys.argv[2]) else 1)' /tmp/us-sector-publish-candidate.json data/us_sector_history.json; then
+              echo "Sector rows unchanged (generated_at ignored); no publication required"
+              echo "publication_outcome=UNCHANGED" >> "$GITHUB_OUTPUT"
+              exit 0
+            fi
             cp /tmp/us-sector-publish-candidate.json data/us_sector_history.json
             python scripts/check_us_sector_snapshot.py data/us_sector_history.json
             git add -- data/us_sector_history.json
diff --git a/scripts/check_us_sector_snapshot.py b/scripts/check_us_sector_snapshot.py
index 96f9cca..a7973f7 100644
--- a/scripts/check_us_sector_snapshot.py
+++ b/scripts/check_us_sector_snapshot.py
@@ -3,6 +3,7 @@ import json
 import math
 import pathlib
 import sys
+from us_market_calendar import expected_latest_session
 TICKERS={'SPY','XLK','XLC','XLY','XLP','XLF','XLI','XLV','XLE','XLB','XLU','XLRE'}
 def validate(data, now=None):
     now=now or dt.datetime.now(dt.timezone.utc)
@@ -44,6 +45,12 @@ def validate(data, now=None):
             age=(now.date()-dt.date.fromisoformat(observed)).days
             if age<0 or age>5:issues.append('STALE_OR_FUTURE_DATA')
         except (TypeError,ValueError):issues.append('INVALID_DATE')
+        try:
+            # A five-day window cannot see one missing session (2026-10-16 was absent from the 10-16 21:28 ET run).
+            # The site reader allows PUBLISH_GRACE_HOURS; the publisher itself does not.
+            expected=expected_latest_session(now,grace_hours=0)   # the publisher runs after the close: no grace
+            if dt.date.fromisoformat(observed)<expected:issues.append('LATEST_SESSION_MISSING:expected '+expected.isoformat())
+        except ValueError as exc:issues.append(str(exc) if str(exc) in ('CALENDAR_NOT_COVERED','NO_SESSION_FOUND') else 'INVALID_DATE')
     return {'status':'OK' if not issues else 'UNKNOWN','coverage':sum(isinstance(status.get(t),dict) and status[t].get('status')=='ok' for t in TICKERS),'observed_at':observed,'issues':issues}
 if __name__=='__main__':
     payload=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
diff --git a/scripts/test_us_sector_feed.py b/scripts/test_us_sector_feed.py
index c1e95c7..a2badab 100644
--- a/scripts/test_us_sector_feed.py
+++ b/scripts/test_us_sector_feed.py
@@ -27,4 +27,13 @@ class FeedTests(unittest.TestCase):
         data=build(failing)
         self.assertTrue(all(x['status']=='UNKNOWN' for x in data['status'].values()))
         self.assertTrue(all(x==[] for x in data['histories'].values()))
+    def test_dropped_bars_are_recorded(self):
+        body={'chart':{'result':[{'meta':{'gmtoffset':0},'indicators':{'quote':[{'close':[100.0,None]}]},'timestamp':[1790000000,1790086400]}]}}
+        with patch('us_sector_feed.urllib.request.urlopen',return_value=io.BytesIO(json.dumps(body).encode())):
+            got=fetch('SPY',detail=True)
+        self.assertEqual(len(got['rows']),1)
+        self.assertEqual(len(got['dropped']),1)
+        rows=[{'date':'2026-09-'+str(i).zfill(2),'close':100+i} for i in range(1,22)]
+        data=build(lambda _:{'rows':rows,'dropped':['2026-09-22']})
+        self.assertEqual(data['status']['SPY']['dropped_bars'],['2026-09-22'])
 if __name__=='__main__':unittest.main()
diff --git a/scripts/test_us_sector_snapshot.py b/scripts/test_us_sector_snapshot.py
index efa0b84..368c3e0 100644
--- a/scripts/test_us_sector_snapshot.py
+++ b/scripts/test_us_sector_snapshot.py
@@ -57,4 +57,20 @@ class SnapshotTests(unittest.TestCase):
         data=self.make_data()
         data['histories']['SPY']='corrupt'
         self.assertIn('SPY:MISSING_HISTORY',validate(data,now)['issues'])
+    def test_latest_session_missing_real_case(self):
+        # Published 2026-10-17 01:28Z (Fri 21:28 ET, after the close) with the last row 10-15: one session missing.
+        data=self.make_data(dt.date(2026,10,15))
+        result=validate(data,dt.datetime(2026,10,17,1,28,36,tzinfo=dt.timezone.utc))
+        self.assertIn('LATEST_SESSION_MISSING:expected 2026-10-16',result['issues'])
+        self.assertEqual(result['status'],'UNKNOWN')
+        # Before the 10-16 close the 10-15 session is the latest one that must be present.
+        self.assertEqual(validate(data,dt.datetime(2026,10,16,19,0,tzinfo=dt.timezone.utc))['status'],'OK')
+    def test_weekend_and_holiday(self):
+        data=self.make_data(dt.date(2026,10,16))
+        self.assertEqual(validate(data,dt.datetime(2026,10,19,10,26,tzinfo=dt.timezone.utc))['status'],'OK')
+        data=self.make_data(dt.date(2026,11,25))   # Thanksgiving 11-26 closed
+        self.assertEqual(validate(data,dt.datetime(2026,11,27,15,0,tzinfo=dt.timezone.utc))['status'],'OK')
+    def test_calendar_not_covered_fails_closed(self):
+        data=self.make_data(dt.date(2028,1,4))
+        self.assertIn('CALENDAR_NOT_COVERED',validate(data,dt.datetime(2028,1,5,12,0,tzinfo=dt.timezone.utc))['issues'])
 if __name__=='__main__':unittest.main()
diff --git a/scripts/us_market_calendar.py b/scripts/us_market_calendar.py
new file mode 100644
index 0000000..b812074
--- /dev/null
+++ b/scripts/us_market_calendar.py
@@ -0,0 +1,41 @@
+#!/usr/bin/env python3
+"""NYSE trading calendar used to decide which completed US session a snapshot must contain.
+
+Holidays and early closes: https://www.nyse.com/markets/hours-calendars (read 2026-10-19).
+Outside the listed years the calendar refuses to answer (CALENDAR_NOT_COVERED) instead of guessing.
+"""
+import datetime as dt
+from zoneinfo import ZoneInfo
+
+NY = ZoneInfo('America/New_York')
+NYSE_HOLIDAYS = {
+    '2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03', '2026-05-25', '2026-06-19', '2026-07-03',
+    '2026-09-07', '2026-11-26', '2026-12-25',
+    '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18', '2027-07-05',
+    '2027-09-06', '2027-11-25', '2027-12-24',
+}
+NYSE_EARLY_CLOSE = {'2026-11-27', '2026-12-24', '2027-11-26'}   # 13:00 close
+FIRST_DAY, LAST_DAY = dt.date(2026, 1, 1), dt.date(2027, 12, 31)
+SETTLE_MINUTES = 15            # a close counts as completed 15 minutes after the bell (same as the site reader)
+PUBLISH_GRACE_HOURS = 8        # cron 23:35 UTC + observed GitHub delay of 1.9-2.5 h ~= close + 6.1 h in summer
+
+
+def is_session(day):
+    if not FIRST_DAY <= day <= LAST_DAY:
+        raise ValueError('CALENDAR_NOT_COVERED')
+    return day.weekday() < 5 and day.isoformat() not in NYSE_HOLIDAYS
+
+
+def session_settled_utc(day):
+    close = dt.time(13, SETTLE_MINUTES) if day.isoformat() in NYSE_EARLY_CLOSE else dt.time(16, SETTLE_MINUTES)
+    return dt.datetime.combine(day, close, tzinfo=NY).astimezone(dt.timezone.utc)
+
+
+def expected_latest_session(now, grace_hours=PUBLISH_GRACE_HOURS):
+    """Latest NYSE session whose close (plus publication grace) is already in the past at `now`."""
+    day = now.astimezone(NY).date()
+    for _ in range(15):
+        if is_session(day) and now >= session_settled_utc(day) + dt.timedelta(hours=grace_hours):
+            return day
+        day -= dt.timedelta(days=1)
+    raise ValueError('NO_SESSION_FOUND')
diff --git a/scripts/us_sector_feed.py b/scripts/us_sector_feed.py
index d12b47c..b25d77a 100644
--- a/scripts/us_sector_feed.py
+++ b/scripts/us_sector_feed.py
@@ -6,7 +6,7 @@ import sys
 import urllib.parse
 import urllib.request
 TICKERS=('SPY','XLK','XLC','XLY','XLP','XLF','XLI','XLV','XLE','XLB','XLU','XLRE')
-def fetch(ticker):
+def fetch(ticker,detail=False):
     url='https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(ticker)+'?range=3mo&interval=1d'
     req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
     with urllib.request.urlopen(req,timeout=15) as response:
@@ -16,21 +16,26 @@ def fetch(ticker):
     dates=chart['timestamp']
     if not isinstance(dates,list) or not isinstance(closes,list) or len(dates)!=len(closes):
         raise ValueError('CHART_LENGTH_MISMATCH')
-    rows={}
+    rows,dropped={},[]
     for ts,price in zip(dates,closes):
+        day=(dt.datetime.fromtimestamp(ts,dt.timezone.utc)+dt.timedelta(seconds=offset)).date().isoformat()
         if not isinstance(price,bool) and isinstance(price,(int,float)) and 0<price<float('inf'):
-            day=(dt.datetime.fromtimestamp(ts,dt.timezone.utc)+dt.timedelta(seconds=offset)).date().isoformat()
             if day in rows: raise ValueError('DUPLICATE_TRADING_DATE')
             rows[day]={'date':day,'close':round(price,6)}
-    return [rows[k] for k in sorted(rows)]
-def build(fetcher=fetch):
+        else:
+            dropped.append(day)   # recorded instead of silently skipped (e.g. a null close for the latest bar)
+    out=[rows[k] for k in sorted(rows)]
+    return {'rows':out,'dropped':dropped} if detail else out
+def build(fetcher=lambda ticker:fetch(ticker,detail=True)):
     result={'schema_version':1,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'source':'Yahoo Finance chart API (unofficial)','histories':{},'status':{}}
     for ticker in TICKERS:
         try:
-            rows=fetcher(ticker)
+            got=fetcher(ticker)
+            rows,dropped=(got['rows'],got['dropped']) if isinstance(got,dict) else (got,[])
             if len(rows)<21: raise ValueError('INSUFFICIENT_HISTORY')
             result['histories'][ticker]=rows
             result['status'][ticker]={'status':'ok','observed_at':rows[-1]['date'],'count':len(rows)}
+            if dropped: result['status'][ticker]['dropped_bars']=dropped
         except Exception as exc:
             result['histories'][ticker]=[]
             result['status'][ticker]={'status':'UNKNOWN','reason':type(exc).__name__}

```

## 交接完整性

下方檔案hash可獨立核對；此記錄末尾為 `END_OF_GPT_V228_CHECKPOINT`，讀不到末尾表示回應被截斷，請分段讀或直接下載raw。

| 檔案 | SHA-256 |
| --- | --- |
| macro-market-raw.json | 3905328861fb4b648d0b0c8dd4bb930b8a1bb1198e4e51a30c39c2bda1e65a96 |
| a1-full-row-comparison.json | e9cb031ccb6fcd153fa3440f662b03195c3e9826dabb8d27a93e1d3caf7ddd38 |
| full-site.diff | 2f074818aa04c396493403cf0122fc586d52f13f19b9804bcc9d1351bd3d8417 |
| full-relay.diff | 7523357543809bb24ee4df9327611d93aaaa6b5ec755690a49ebe5dc07b3e3d1 |
| site-npm-test.log | 27bf51a280035eb9bf6c4ecf0ca9a5bafd6fd62a73eb10561adee32f64b62e3d |

END_OF_GPT_V228_CHECKPOINT
