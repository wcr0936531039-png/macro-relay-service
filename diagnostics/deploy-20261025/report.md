# 2026-10-25 三項修補部署報告
- 範圍：僅 GPT_NEXT.md 指定 final.patch；排隊功能未開始。
- 基線：488b8bc9ab0402472496a80abb1cee17aea35fae（v233）。
- Patch SHA-256：d4940c2da9bc70452a36d75481c70143b69ccc82a6fdcc2ee5a5cbb3e4503899。
- 乾淨基線重套 → build → 全套測試 → 推送 → 私人部署，結果 succeeded。
- 正式版本：v234；來源 commit faf5eb7953e12d7e6cb7480687ee7ae603368746；v233 保留回滾。
- 部署前 `TZ=UTC npm test`：exit 0；信用／接續35/35、來源恢復14/14。
- 首次 Asia/Tokyo 測試有2項既有文字日期解析失敗；UTC重跑通過，未擴改來源解析程式。
## 三項正式讀回
1. PASS：原保存10/22信用包 POST HTTP200、ok=true、8列接受；原始capturedAt未改。
2. PASS：7項信用觀測日均10/22，calendarDiscrepancy=true，status=ok。
3. PASS：7項 verifiedAt／fetchedAt 均為2026-10-24T14:34:37.808561+00:00，並非本輪時間。
4. PASS：run總經與直接 /api/macro 同為55/55；55列id／日期／數值／status／reason逐列完全一致。
5. PASS：兩者checkedAt相同（2026-10-25T11:53:15.133Z）；summaryScope=final_readback。
- 接續原run完成於台北19:58:48；匹配history已保存，四檔Gate快照4/4 recorded。
- 整輪仍partial：其他來源／Gate缺口保留；不以這三項修補宣稱整站全數通過。
- 10/27 22:30新信用接受、10/28上午原verifiedAt保留與10/22升final：尚待實際跨日驗收。
## 私人下載ZIP
- 檔名：taiwan-master-v233-488b8bc-source.zip；已私下交付，未放入任何公開repo。
- ZIP SHA-256：0a49b604c370bfea60f47f488fd9b7e550053d9297e4f7692cf6b62b6fcd7673。
- 來源為488b8bc，未套final.patch；148個檔，含FILE_MANIFEST.tsv逐檔SHA-256。
- 排除dist/server/index.js、node_modules、.env／憑證；3個設定／操作檔已去識別化。
- 原始來源未有遷移檔；既有worker、tests、build、package及lock、dist/index.html均包含。
- 原版無pretest build hook：須先npm ci及npm run build，再以TZ=UTC npm test。
- 原版collector的週末today測試缺陷照原樣保留；ZIP不能宣稱目前週日直接npm ci && npm test全通過。
## 工具事故
- 首次長stdin遭終端截斷，尚未送出HTTP；錯誤輸出含服務憑證，未寫進公開repo或ZIP。
- 已改成隱藏stdin僅傳小型設定、body由原保存檔讀入，避免再印出輸入；未宣稱原憑證已撤銷。
