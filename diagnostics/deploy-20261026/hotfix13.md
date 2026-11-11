# hotfix13（2026-11-12）
- 授權已確認；中繼U-6前輪完成183aa79／49ba865、兩blob吻合，本輪未重做。
- v255 SHA=20fc9d2ee2914be3c9d8db31cf9e968665de99247bda053d5ca37924d4d2fbde；v256 SHA=979bdf669db8453a3b51835a9e738578f5e3b95bab29c63832e8273a758fc576；依序套用build，完整TZ=UTC npm test一次exit0（末組94/94）；匿名後台e5d736dc7c026c2768147d4f5256dbd52917ac92b634b97c18a0ccafaf11cd42吻合。
- 一次部署succeeded，source=4c8f2b91b23a442495a295fb3014aa7e026f1e41，原3785fe0留回滾；部署後compact HTTP200／true／1073字元（首輪輪詢最大1072）；精簡指令已換，存取段保留、06:30／22:30與enabled不變。
- workflow確認patch5未套（無wait-night／night輸入）；v254按交接11/08結案：11/06匯入欄位已驗證，時段另屬中繼patch4，不再要求額外合規匯入驗收。
# 最新：11/12 00:35 夜巡檢 完成｜Gate 5/5
runId a14175b1-b8e3-442d-bbd6-51e8e83a5de5｜completedAt 2026-11-11T16:35:25.806Z｜查詢 58 次｜relayImport ok（market=imported、series=imported、statistics=not_in_bundle、cpi=imported、sources=imported、news=imported）
異常：sourceResearch:source_error、fullMarketScanner:source_error
