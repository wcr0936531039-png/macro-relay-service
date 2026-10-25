# 2026-10-26 部署紀錄
狀態：BLOCKED；重新嘗試後仍未部署。
交接：gate-probe/handoff/GPT_NEXT.md，blob 7ecf334c68164fd67a31e93eb8efa55ab6a8ebbd。
授權：乾淨 v234 → owner-bundle → owner-bundle2 → build → UTC 全套測試 → 單次部署。
最新 Sites 讀回：active，latest_version_number=234。
阻塞：本輪 exec_command 仍回覆 No usable execution environment is available。
兩份 patch 尚未套用；node build.mjs 與 TZ=UTC npm test 均未執行。
以下 SHA 為交接提供的預期值，本輪未下載或自行核算：
owner-bundle-20261025.patch：25ad83272642ef3038f79ba0025e264317086b3511d9adb3d5980b528b216afb
owner-bundle2-20261025.patch：f5068830265e6b0ace2ee881656d1a9ddbf33460b26d3f774644e0485168c334
兩包後 dist/index.html 預期：2b707b79fc43e8a9f2c29da15cb42ed7cbe906b3ea66aa5b428d4305f4a27544
① 四檔三問：未部署、未驗收。
② 四檔可轉債卡：未部署、未驗收。
③ 下一次官方匯入後美元零軸與草案分數：未驗收。
④ TW_EXPORT_ORDERS 日期／值／狀態／不計分及總經前後：未驗收。
⑤ 四檔評級、Gate、風險許可不變：未取得部署前後比較。
⑥ 新卡片、集保、融資維持率、金價與調整後轉換價：未驗收。
10/25 印出的憑證名稱：Sites siwc_bypass_bearer_token（OAI-Sites-Authorization 服務存取權杖）。
有效期：Sites get_site／generate_siwc_bypass_token 契約沒有到期欄位，文件未承諾自動過期；不能假定已失效。
輪替方法：Sites generate_siwc_bypass_token；已有權杖時重新產生會輪替，舊權杖可能短暫繼續有效。
撤銷限制：目前工具未提供獨立 revoke；輪替是已確認的替換途徑，沒有確認即刻失效的保證。
本輪僅查方法，未呼叫輪替工具，未宣稱舊權杖撤銷，未輸出其值。
依據：Sites 原生工具契約與 identity-and-secrets.md；Git push 憑證的到期規則不能套用到此權杖。
未變更部署、排程或排隊功能；恢復執行環境後依授權完整重做，不跳過測試。
