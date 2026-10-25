# 2026-10-26 部署紀錄
狀態：BLOCKED；重新嘗試後仍未部署。
交接：gate-probe/handoff/GPT_NEXT.md，blob 1e9527146025503d89318d2e760d51b945a67246。
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
前輪僅查方法；本輪依擁有者明確授權執行輪替，詳見下列結果。
依據：Sites 原生工具契約與 identity-and-secrets.md；Git push 憑證的到期規則不能套用到此權杖。
未變更部署、排程或排隊功能；恢復執行環境後依授權完整重做，不跳過測試。
輪替結果：generate_siwc_bypass_token 成功；僅在記憶體比較，確認新舊值不同。
輪替讀回：重新 get_site 所取權杖與新權杖一致；全程未輸出或寫入權杖值。
已確認使用者：台股整站每日巡檢；指示每輪 get_site 動態取得，無固定權杖需替換。
既有交接記載呼叫端：importerNode、site_private_fetch.mjs、deploy-readback.mjs、poll_existing_run.mjs。
上述本機程式本輪無法重新讀取；不能宣稱已完整排查或更新其所有使用端。
macro_morning.py 已讀取：僅執行來源收集，不含本站權杖或認證設定，無需替換。
GitHub 兩倉庫關鍵字搜尋無命中；索引搜尋不等於完整程式／Secrets 審計。
每日巡檢現況：Sites 與 Automations 均顯示已停用；本輪未變更排程。
資料匯入驗證：BLOCKED；無本機執行環境或認證 HTTP 替代工具，未呼叫匯入 API。
待續：環境恢復後，以新 get_site 結果經隱藏 stdin 執行匯入器、讀回保存結果並檢查全部本機呼叫端。
本輪無法宣稱每天資料匯入正常；舊權杖立即失效仍未驗證。
最新續作：依 01:05 交接重試，執行環境仍不可用；Sites 再讀仍為 v234、巡檢停用。
恢復條件：先部署並完成①～⑥，再手動完整巡檢；官方行情與含 DTWEXAFEGS 的序列匯入須 ok:true 且讀回日期通過。
尚未滿足恢復條件，故本輪保持巡檢停用；不是缺少擁有者授權。
