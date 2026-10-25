# 本機測試結果（摘要，非逐字完整 stdout）

最終命令：`npm test`（含 pipefail 保存執行結果），完成 exit 0。

已依序完成 test:legacy → test:advisory-integration → test:fixpack → test:c2 → test:credit-window → test:source-recovery。

- test:credit-window：35 tests、35 pass、0 fail。
- test:source-recovery：14 tests、14 pass、0 fail；含本輪新增8項回歸。
- 新增 finalize 跨夜續跑測試涵蓋最後讀回及 history 相同狀態。
- 原 observation-freshness 單獨測試通過。
- site-module-contract 單獨測試通過，完整套件亦通過。
- `git diff --check` 通過。
- 乾淨 worktree：基線488b8bc → `git apply --check final.patch` → `git apply final.patch` → `node build.mjs` 通過；產物與工作副本逐位元一致。

過程失敗（均已處理）：
1. 原板塊30次上限的partial被finalize改回pending；修正後回歸通過。
2. 來源HTTP503被finalize舊快取成功蓋掉；現在保留來源失敗並另列latestReadback，回歸通過。
3. 原official-collector測試使用週日today當交易日，導致抓取歷史失敗；測試fixture改最近平日，生產collector未改。

非失敗提示：npm既有http-proxy設定警告、Node MODULE_TYPELESS_PACKAGE_JSON提示；未為消除提示而改無關設定。

沒有執行部署、沒有修改正式資料；測試輸入與前後比較為本機受控重播，不能當作部署後正式站驗收。
