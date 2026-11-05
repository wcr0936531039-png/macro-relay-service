# hotfix10｜2026-11-05（部署後驗收中）
- 排程原06:30／22:30、enabled=true；11/01～11/04的內部跳過原因不提供，只可核實三秒no_update且網站無run。prompt已修強制HTTP流程；今晨POST202→status16×200→history200，06:40:37完成、Gate5/5。
- v253／中繼patch2 SHA核對89d4971f4c192746178ffb78154968e83369084569570d6d8582e0bc1b5b4e50／3767e66c69c1062e28002fa6638c9718ec7656333756c56938b0fd2edeb83011；中繼本機d85ceca、47/47過。推main遭自動核准拒絕（未認定此新增推送獲本對話授權），未繞過，兩份均未發布。
- 已明確授權的v249→v250→v251→v252四包SHA全符，以a09fea94cc327b8f66f6a8a286090aa10fdee288建置；完整TZ=UTC npm test exit0（末組87/87），v253不在部署包內。
- HTML de5a6d6bd6b55b777985fb05b50b455b0db7c6ec8b4c476a6e8905211da37deb；本機匿名化核對後台ff8dfc94f54fa4aa0673dbe6f7d0ee69fdfe0c019da3e2a3dd627258d704a0c3相符，原始操作說明未改。
- 實際部署後台39c504578c9faa9e0c7d728400719830d7c70021a715460829c82fae2ad3143c；單次原生部署succeeded，Sites版本249＝功能v249～v252，v248留回滾；環境RELAY_OFFICIAL_IMPORT_ENABLED=true（revision8）。
- 已僅補prompt的版本辨識：以實際relayImport／officialImport欄位判定，避免原生249誤當功能未250；時段／enabled不變。run_now=inline_run，已按保存指令實跑。
- 部署後POST202、reason=null，新run e8fa23c8-471c-48e4-977c-d8c655eec8b4；正在同身分10秒checkpoint，尚未completedAt／history驗收，不預填成功。
- official-import已可讀：generatedAt=2026-11-05T01:52:12Z、5類資料；收集器曾下載中斷，行情／名冊缺項保留，BLS403使用官方API備援。
- 部署前五檔8299／5289／2404／5009／2330皆data_unavailable、無grade；部署後評級、Gate5／8不採用、信用previousDate、relay各組與參考價仍待本run讀回。
