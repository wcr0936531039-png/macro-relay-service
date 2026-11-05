# hotfix10（11/05 22時接續，進行中）
- 新授權v253／中繼patch2已讀取；兩份SHA分別3767e66c69c1062e28002fa6638c9718ec7656333756c56938b0fd2edeb83011、89d4971f4c192746178ffb78154968e83369084569570d6d8582e0bc1b5b4e50，均核對相同。
- 中繼從origin/main 261bc2a另開乾淨分支git am成功；47/47通過，正在推main。先前本機分支分歧已隔離，未覆寫遠端歷史。
- 網站v249～v252原本機a09fea9保留，已疊v253並build；完整TZ=UTC npm test正在執行，尚未部署，正式仍v248。
- 排程prompt已修為每輪強制Sites→POST→同run輪詢→history，原時段與enabled不變；11/01～11/04平台逐輪內部跳過原因未暴露，未猜測。
- 11/05晨間已實際POST202接續凌晨run d6cfe6c4-5704-456f-92a2-f5eedb18fba4；16次status200、history200、06:40:37台北completedAt匹配、Gate5/5recorded，詳見automation-runs/20261105-morning.md。
- 晨間來源仍partial：全市場timeout、FRED逾時／BLS403；當時v248未接relayImport，沒有以直接Master讀回倒填審計。
- 待完成：v253後台匿名化SHA核對並還原、完整測試exit0、設定RELAY_OFFICIAL_IMPORT_ENABLED=true、單次部署、部署後首次巡檢與五檔評級／Gate5／8／參考價讀回。
