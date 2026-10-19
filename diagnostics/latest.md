# GPT → Claude：v228 第 5 節程式與查核（2026-10-19）

依第 0 節交接管道，本檔寫在 GPT 連線有寫入權的公開 repo：`wcr0936531039-png/macro-relay-service/diagnostics/latest.md`。這是公開內容，只包含必要程式片段與查核；無網站憑證、Cookie 或完整請求標頭。

## 第 5 節所要求的程式

來源：正式網站 v228 checkout，`worker/observations.js`，`summarize()`（約第 125 行）：

```js
function summarize(id, history) {
  if (!history.length) return missing(id, '期間內沒有可用數值');
  const newest = history.at(-1), monthly = id==='CPILFESL'||SERIES[id][3] >= 80, weekly = ['ICSA','CCSA','WALCL','WCESTUS1'].includes(id);
  const steps = monthly ? 1 : weekly ? 1 : 5;
  const older = history.length > steps ? history.at(-steps-1) : null;
  const stale = age(newest.date) > SERIES[id][3];
  return { id, name: SERIES[id][0], group: SERIES[id][1], unit: SERIES[id][2], ...newest,
    status: stale ? 'stale' : 'ok', reason: stale ? '資料較舊，暫不納入判讀' : null,
    delta: older ? newest.value - older.value : null, previousDate: older?.date ?? null,
    percent: older && older.value !== 0 ? (newest.value / older.value - 1) * 100 : null,
    changeLabel: monthly ? '較上期' : weekly ? '較前一週' : '較 5 筆前',
    source: link(id), provider: 'FRED／原始提供者', history };
}
```

相關的官方發布驗證在 `worker/observation-freshness.js`：

```js
function releaseObservationCurrent(id,row,now=Date.now()) {
  const v=row.releaseVerification;
  return validReleaseVerification(id,v,row)&&recentOfficialCapture(v.fetchedAt,now)&&now<=Date.parse(`${v.nextReleaseDate}T23:59:59Z`);
}
```

它只回傳布林值，不會修改 row.status 或 row.reason。新資料的 `mergeVerifiedMacroRows()` 對有效的 `status:'ok'` row 只補 `verifiedAt`；快取則由 `refreshingMacroSnapshot()` 判斷是否改成 stale。這幾段未顯示「發布週期驗證把 stale 改回 ok、卻留下舊 reason」的狀態升級路徑。

## 查核結論與下一步

畫面／API 曾觀察到 `status=ok` 但 `reason='資料較舊，暫不納入判讀'`。目前可定位的字串生產者是 `summarize()`；它本身會同步產生 stale 狀態與 reason。請先確認正式回應的完整 row 是從目前 v228 的哪個來源或快取路徑產生，再判定這是舊快取遺留、其他建構器，或前端組合文字；不要直接假設發布週期函式升級了狀態。

建議補的回歸測試：以帶有有效 `releaseVerification`、資料觀測日超過一般 SERIES 天數且 `reason` 為過期文字的 row，檢查最後 API payload 的 `status`、`is_stale`、`reason` 三者一致；另測試來源驗證失效時仍回到 stale 並保留明確過期原因。狀態和理由應由同一個最終判定結果輸出，不能用單獨清除文字掩蓋真正過期。

網站程式修補目前只待本地準備與測試；尚未提交網站 repo，尚未部署。若 Claude 判定需要改動，請先提供最小 diff 與測試結果供網站擁有者審閱。
