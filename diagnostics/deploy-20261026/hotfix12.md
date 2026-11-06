# hotfix12｜2026-11-06（兩包已發布；讀回追蹤中）
- 擁有者已明確授權第1、2項；只改中繼，網站程式未改、未部署。
- Patch3 SHA41536a3d717ad7e418f9560a552ff48fe65b820cf02e316842cb3a06e3b5dea3；patch4 SHA9a72b4595bd05015a98cd9bf4f019988420271579a9d4bcfbe4b82c07e797b48，兩者核對相同。
- 最新main 02c559a依序git am成功，完整python -m unittest discover -s tests：61/61過、exit0；GitHub連接器以相同樹／權限依序發布53047292fe42b53b7dc981a1a4daf51f90597cc8→c0c1efe805555c315796e5889af4f26249e05d4e，main非強推一次前進。
- 第1項發布前keyless coverage17/61；下一次真實發布的coverage及Cboe VIX日期／provider待讀回，不拿Claude試跑或fixture當本輪結果。
- 第2項auto已限22:30～23:59；publisher一律拒絕早於22:30的statistics；沿用只接受30小時內合法夜間原檔，原SHA／capturedAt不改，無合格檔則記carryNote；夜間增加23:35屬本包授權內容。
- 真實夜間→翌晨carry／網站v254合規新匯入七列驗收仍待後續實際資料，不以既有上午擷取信用充作驗收。
