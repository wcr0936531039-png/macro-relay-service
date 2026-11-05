#!/usr/bin/env bash
# 在 GitHub 上跑網站的官方資料收集程式（vendor/site-collector，與網站 v253 相同），整理成匯入套件。
# 用法：scripts/run_official_collector.sh <工作資料夾> [交易日數，預設 5] [信用統計 auto|on|off，預設 auto]
# auto：台北 12:00～20:59 略過信用統計（當晚才公布），其他時間照收。
# 不需要任何金鑰、不連網站；推送由工作流程另外做。結束碼＝套件是否有內容（publish_official_import.py）。
set -uo pipefail
work="$1"; sessions="${2:-5}"; stats="${3:-auto}"
src="$work/collected"; out="$work/bundle"; mkdir -p "$src"
hour=$((10#$(TZ=Asia/Taipei date +%H)))
skip=""
if [ "$stats" = off ] || { [ "$stats" = auto ] && [ "$hour" -ge 12 ] && [ "$hour" -lt 21 ]; }; then skip="--skip-statistics"; fi
if [ "$hour" -lt 12 ]; then window=morning; elif [ "$hour" -lt 21 ]; then window=afternoon; else window=night; fi
echo "台北 ${hour} 時｜${window}｜交易日 ${sessions}｜${skip:-含信用統計}"
python vendor/site-collector/scripts/collect-official-data.py --output "$src" --sessions "$sessions" $skip > "$work/official.log" 2>&1; official=$?
echo "官方收集結束碼 ${official}"; tail -n 15 "$work/official.log"
node vendor/site-collector/scripts/collect-source-research.mjs "$src" > "$work/sources.log" 2>&1; sources=$?
echo "產業來源／新聞結束碼 ${sources}"; tail -c 1500 "$work/sources.log"; echo
python scripts/publish_official_import.py "$src" "$out" --window "${window}${skip:+-no-statistics}" --keep-sessions "$sessions" --exit "official=${official}" --exit "sources=${sources}"
