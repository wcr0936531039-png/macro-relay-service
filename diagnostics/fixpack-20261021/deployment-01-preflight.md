# 2026-10-21 修正包＋C2 部署前檢查

擁有者已在對話直接授權部署本次兩份已審補丁，未擴大至其他待辦。

- 現行正式版仍為 v230，保留為回滾點。
- Sites 最新原始碼乾淨基線：`f9c5f15b371de58d0a06ef5251ce5c8a895f217e`。
- 已按 `fixpack.patch → build → c2.patch → build` 重新套用，無衝突。
- fixpack SHA-256：`d69ac5bb2538c9b3115306eb8c490077797b284a69e9c07151dbcf560bae6d0c`。
- C2 SHA-256：`9ad8c47bae31fa31008f88895b8a40e3f46fbf9ec6d94f505c6215dd69ad34e4`。
- HTML SHA-256：`93d22d219109e52161e0e85ab926ad86dab6fadfc5083c57144e5c21b1f9e638`。
- Worker SHA-256：`613ac53005c0346259bf4aff78f95e18ced8c4c29a81f1d964ff9b4a56e79675`。
- 以上四項均與 07:45 審查一致。
- 新一輪完整 `npm test` 已啟動，尚未宣稱通過；完成後才能發布。
- 正在讀取部署前實際 API 快照。尚未發布。

後續結果會寫入 diagnostics/latest.md；不在公開紀錄存放憑證、私人網站入口或 Tiingo 原始價格。
