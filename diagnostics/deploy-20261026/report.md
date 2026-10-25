# 2026-10-26 部署紀錄
狀態：BLOCKED；本輪未部署。
交接：gate-probe/handoff/GPT_NEXT.md，blob 88db4792a19fa2346faa422465ce043bd8528cf3。
授權範圍：owner-bundle-20261025.patch → owner-bundle2-20261025.patch → build → UTC 全套測試 → 單次部署。
Sites 讀回：active、owner，最新版本仍為 v234。
阻塞：本機執行環境離線，兩次 exec_command 均回覆 No usable execution environment is available。
兩份 patch 均尚未套用；未執行 node build.mjs。
TZ=UTC npm test：未執行，不能宣稱 exit 0。
Patch SHA-256：本輪尚未下載核算；交接只列縮寫，不當作完整核驗。
dist/index.html SHA-256：本輪未產生。
① 四檔三問：新版本未部署，未驗收。
② 四檔可轉債卡：新版本未部署，未驗收。
③ 美元零軸：新版本及下一次官方匯入尚未驗收。
④ TW_EXPORT_ORDERS 與台股總經分數前後：尚未取得部署前後比較。
⑤ 四檔評級、Gate、風險許可不變：尚未取得部署前後比較。
⑥ 第二包新卡片、集保、融資維持率、金價與目前轉換價：未驗收。
10/25 工具事故憑證名稱：Sites siwc_bypass_bearer_token（OAI-Sites-Authorization 服務存取 bearer token）。
未重新輸出憑證值；本輪未要求或宣稱撤銷／輪替。
未更動排隊功能、來源程式、部署版本或排程。
續作：恢復本機執行環境後，從乾淨 v234 依序套兩包、核 SHA、build、TZ=UTC npm test，再部署一次及完成①～⑥。
