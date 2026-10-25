# 2026-10-26 部署／恢復巡檢報告
結論：v235 部署成功；讀回未全通過，手動巡檢 partial，每日巡檢保持停用。
環境已恢復；基線 v234 faf5eb7953e12d7e6cb7480687ee7ae603368746，保留回滾。
owner-bundle-20261025.patch SHA256：25ad83272642ef3038f79ba0025e264317086b3511d9adb3d5980b528b216afb
owner-bundle2-20261025.patch SHA256：f5068830265e6b0ace2ee881656d1a9ddbf33460b26d3f774644e0485168c334
兩包依序套用；node build.mjs 成功；TZ=UTC npm test exit 0。
新增 owner-20261025 17/17、owner-bundle2 9/9；無跳過全套測試。
dist/index.html SHA256：2b707b79fc43e8a9f2c29da15cb42ed7cbe906b3ea66aa5b428d4305f4a27544
來源 commit：4ac4af9f0817c40a135c8e1b1df3603569726b1b；單次部署 v235，10/26 05:34 台北成功。
① PASS：2404／8299／5289／5009 三問均由正式 API 讀回並以同版 DOM 函式驗證；缺值未當通過。
② FAIL：四檔 CB 卡存在，但自動登錄／月報收集 failed；8299 未讀出所要求三券與目前轉換價。
診斷：urllib 官方檔可解析群聯國內1＋海外2；本機 Node 同端點 HTTP200 後讀 JSON 逾時；不據此外推 Worker 精確根因。
③ PASS：DTWEXAFEGS 官方匯入 ok:true，最新來源10/16；面板按 d+8 採10/14，草案−1、正式貢獻0。
④ FAIL：TW_EXPORT_ORDERS 仍讀舊經濟部62.36／2026-09-01／stale／403；不是國發會新口徑，未計分。
同一組已保存輸入離線比較：台股分數56→56、覆蓋93%→96%；expected 8→7 未改組別權重。
⑤ 部署後、手動更新前，四檔評級／正式分數／風險許可未變；8299／5289／5009 Gate1 partial→evaluated，故不宣稱 Gate 全同。
⑥ PARTIAL：四檔新增卡片均由 API＋DOM 核對；不冒稱手機／桌面實機驗收。
8299 集保26.79%、2026-10-22、1週；上市融資維持率176.9929646%、2026-10-22。
金價新標題與1／5日顯示程式已上線；正式讀回1日0%、5日−3.1544327%；19/21樣本，20日留缺。
CB目前2468.8及海外「未含後續調整」內容未取得；沒有手填驗收數字。
手動更新：最新發布工具重新下載，市場已有72日，用 --sessions 1；官方最新交易日10/22。
官方行情與名冊匯入 ok:true＋scanner讀回10/22、72日、1947/1985檔，98.0856%；未補造缺值。
晨間 wrapper 僅收總經／CPI，未產生 statistics.json；系列9/9、來源錯誤0，DTWEXAFEGS已納入。
九序列分批匯入均 ok:true；CPI BLS／FRED 2026-09 同值338.896，passed:true，來源歷史讀回成功。
八組來源94筆、公告3組均匯入 ok:true；消費電子RSS空回應及HTML備援紀錄保留。
新權杖完成上述實際匯入與讀回認證，非僅管理工具成功。
巡檢runId：21560dd5-7e2d-4d14-a7b8-a8ef70b94fb3；中途輪詢程序中斷後接續原run，未重建。
completedAt：2026-10-25T22:59:32.912Z（10/26 06:59台北）；history同runId／完成時間相符，status=partial。
最終模組：總經ok55/55、擴展partial10/12、跨市場ok4/4、板塊ok11/11、公告ok3/3。
最終讀回摘要：市場／貴金屬pending36/36、美股指數pending3/3；覆蓋齊全不當作最新更新完成。
Gate審計：8299／5289／2404／5009 全為step_timeout、recorded:false；history成功保存Gate數0/4。
手動更新後四檔Gate1／3均由partial→evaluated；5009另有Gate4／6 blocked→warning、7／10→evaluated、9→conditional。
5009 blocked→degraded／C；其他三檔評級未變；四檔riskPermission均仍not_cleared，Gate5／8未自動通過。
晨間信用保留10/22及原verifiedAt／fetchedAt 2026-10-24T14:34:37.808561+00:00，未重置成當輪時間。
事故憑證名稱：siwc_bypass_bearer_token；已依授權輪替，get_site與正式HTTP讀回驗證成功；未輸出或保存其值。
呼叫端 importerNode／site_private_fetch.mjs／deploy-readback.mjs／poll_existing_run.mjs 均查為執行時stdin輸入，無寫死權杖。
有效期未有官方保證；輪替後舊權杖短暫有效的限制仍保留，未聲稱已驗證立即撤銷。
恢復條件未達：先修CB收集／Gate審計逾時、外銷口徑與M1B−M2核驗，再重跑完整巡檢及讀回；本輪未啟用排程或開始排隊功能。
