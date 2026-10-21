# 2026-10-21 部署前完整驗證通過

- 乾淨基線與兩份補丁依序重建，兩次 build 通過。
- 部署前重新執行完整 npm test：exit 0；所有 legacy、NYSE calendar 9 項、既有 advisory 38 項、修正包 4 項、C2 5 項測試通過，fail 0。
- 完整本輪輸出已取得（66,369 bytes）；將一併留存。
- npm 只有既有 http-proxy config 提示；無測試失敗。
- git diff --check 通過。
- HTML SHA-256 `93d22d219109e52161e0e85ab926ad86dab6fadfc5083c57144e5c21b1f9e638`。
- Worker SHA-256 `613ac53005c0346259bf4aff78f95e18ced8c4c29a81f1d964ff9b4a56e79675`。
- 待發布產物用相同凍結輸入重播：8299、5289、2404 改為未評（估值分歧），5009 保留 C；40 個 Gate 狀態、scoring、VETO、riskPermission 均保持原值。
- 新抓取 2026-10-20 官方信用資料成功，collectionAttempts=1；待部署後匯入核對真實修訂留存。未改交易日期或填造資料。

開始同步本次來源與打包。v230 仍為回滾點，發布結果及現行資料缺口另寫 diagnostics/latest.md。
