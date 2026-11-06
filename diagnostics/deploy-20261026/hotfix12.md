# hotfix12｜2026-11-06：兩包已發布；合法夜間沿用待實測
- 擁有者已在本對話授權第1、2項；中繼main依序git am，網站程式未改、未部署。
- Patch3 SHA41536a3d717ad7e418f9560a552ff48fe65b820cf02e316842cb3a06e3b5dea3；patch4 SHA9a72b4595bd05015a98cd9bf4f019988420271579a9d4bcfbe4b82c07e797b48，核對相同；完整python -m unittest discover -s tests exit0、61/61通過。
- main 02c559a→53047292fe42b53b7dc981a1a4daf51f90597cc8→c0c1efe805555c315796e5889af4f26249e05d4e；GitHub連接器發布兩個有序提交，樹與本機逐一完全相同（含權限），一次非強推更新main。
- 真GitHub push工作流程42198760610成功；keyless generated_at=2026-11-06T09:56:11.336629+00:00，coverage由17/61→55/61。VIXCLS status=ok、provider=Cboe官方VIX每日收盤，11/03=20.83、11/04=16.61、11/05=28.18；本機用新函式真抓亦相同。
- FRED DGS10／SOFR／DTWEXAFEGS均ok（最新觀測11/04／11/04／10/30）；剩6項是TWSE當沖缺表、當日融資融券未取得，照實留缺，未用昨日值充今日。
- 官方套件auto已限台北22:30～23:59；publisher不論模式都拒絕早於22:30的statistics，只沿用30小時內合格夜間原檔，原SHA／capturedAt不改；加入23:35夜間排程為本包授權內容。
- 使用目前GitHub上午09:50真statistics／news（兩檔SHA均與manifest相符）離線重建：window=afternoon-no-statistics、statistics不發布且不沿用，carryNote明載早於22:30；news正常保留。此為真輸入離線驗證，未把本機包推上official-import。
- 正式official-import目前仍舊morning清單（generatedAt=2026-11-06T01:51:14Z、尚無carried）；下一份修補後正式早／下午清單及合法夜間→翌晨同SHA沿用仍待實際發布，不以fixture或舊上午擷取充作完成。
- 既有v254一次性驗收仍待首份合規夜間信用匯入：核對原capturedAt≥22:30、previousDate為前一交易日、captureDeferred=false；尚未新建網站run或改網站／巡檢時段來湊驗收。
