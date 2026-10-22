import fs from 'node:fs';
import {createHash} from 'node:crypto';
const root='/workspace/scratch/6b210f4f35e9/';
const get=name=>JSON.parse(fs.readFileSync(root+'fixpack-deploy-verification/'+name+'.json','utf8'));
async function load(name){const source=fs.readFileSync(root+name+'/dist/server/index.js','utf8');return import('data:text/javascript;base64,'+Buffer.from(source+'\nrelaySeries=async()=>null;readStockRelay=async()=>null;getOfficialIssuedShares=async()=>({data:new Map(),errors:[]});\nexport {evaluateMasterModel,backendMarketScoreModels,loadTaiwanDashboard,mergeVerifiedMacroRows,buildTaiwanStockSnapshot};').toString('base64'));}
const before=await load('fixpack-c2-approved-deploy'),after=await load('credit-window-20261022');
const hash=value=>createHash('sha256').update(JSON.stringify(value)).digest('hex');
const macro=get('after-macro'),market=get('after-market'),expanded=get('after-expanded'),scanner=get('parity-scanner');
const stocks=[];
const originalNow=Date.now;
Date.now=()=>Date.parse(macro.checkedAt);
for(const symbol of ['8299','5289','2404','5009']){
 const stock=get('parity-stock-'+symbol),live=get('after-model-'+symbol),e=live.evidenceSummary;
 const evidence={estimates:e.consensus.flatMap(row=>row.rows||[]),officialCompany:{records:[...e.company.results,...e.company.guidance,...e.company.outlooks]},sourceResearch:live.sourceResearch};
 const flags={stockFresh:true,macroFresh:true,marketFresh:true,scannerFresh:true};
 const evaluate=api=>api.evaluateMasterModel(stock,{...macro,riskAssessment:api.backendMarketScoreModels(macro,expanded,market.rows).find(row=>row.market==='TW')},{...market,fullMarketScanner:scanner},flags,evidence);
 const b=evaluate(before),a=evaluate(after),fields=['gates','scoring','veto','adaptiveRating','primaryValuation'];
 const unchanged=Object.fromEntries(fields.map(key=>[key,hash(b[key])===hash(a[key])]));
 if(Object.values(unchanged).some(value=>!value))throw Error(symbol+' decision changed');
 stocks.push({symbol,sourceInputDate:stock.checkedAt,grade:a.adaptiveRating.grade,label:a.adaptiveRating.label,riskPermission:a.adaptiveRating.riskPermission,unchanged,
  gates:b.gates.map((gate,index)=>({id:gate.id,before:gate.status,after:a.gates[index].status,beforeDataState:gate.dataState,afterDataState:a.gates[index].dataState,fullObjectUnchanged:hash(gate)===hash(a.gates[index])}))});
}
Date.now=originalNow;
// Synthetic transport fixtures demonstrate only the changed capture policy.
const ids=['TWSE_MARGIN_BALANCE_NTD','TWSE_MARGIN_CHANGE_NTD','TWSE_MARGIN_BALANCE_UNITS','TWSE_SHORT_BALANCE','TWSE_SHORT_CHANGE','TWSE_MARGIN_MARKET_CAP_RATIO','TWSE_CREDIT_TRADE_VALUE'];
const savedAt='2026-10-21T15:00:00Z',clock='2026-10-22T02:14:00Z';
const saved=ids.map((id,index)=>({id,value:index-2,date:'2026-10-21',status:'ok',verifiedAt:savedAt,fetchedAt:savedAt,source:'https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN?date=20261021'}));
function db(){return {prepare(sql){return {run:async()=>({success:true}),bind(key){const payload=key==='macro-market:v7'?{checkedAt:savedAt,rows:saved}:key==='stock-credit:v1:8299'?{symbol:'8299',dataset:'TaiwanStockMarginPurchaseShortSale',source:'https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockMarginPurchaseShortSale',capturedAt:savedAt,rows:[{stock_id:'8299',date:'2026-10-21',MarginPurchaseTodayBalance:110,MarginPurchaseYesterdayBalance:100,ShortSaleTodayBalance:210}]}:null;return {all:async()=>({results:payload?[{payload:JSON.stringify(payload),updated_at:savedAt,expires_at:'2026-10-23T00:00:00Z'}]:[]})}}}}};}
const NativeDate=Date,originalFetch=globalThis.fetch;
globalThis.Date=class extends NativeDate{constructor(...args){super(...(args.length?args:[NativeDate.parse(clock)]));}static now(){return NativeDate.parse(clock);}};
async function capture(api){const calls=[];globalThis.fetch=async input=>{
 const url=new URL(input);calls.push(url.pathname);
 if(url.hostname==='api.finmindtrade.com'){const dataset=url.searchParams.get('dataset');calls[calls.length-1]=url.pathname+'?dataset='+dataset;return Response.json({status:200,data:dataset==='TaiwanStockMarginPurchaseShortSale'?[{stock_id:'8299',date:'2026-10-21',MarginPurchaseTodayBalance:120,MarginPurchaseYesterdayBalance:100,ShortSaleTodayBalance:220}]:[]});}
 if(url.pathname.endsWith('/FMTQIK'))return Response.json([{Date:'1151021',TradeValue:'900000000000'}]);
 if(url.pathname.endsWith('/MI_MARGN'))return Response.json({stat:'OK',date:'20261021',tables:[{fields:['項目','買進','賣出','償還','前日餘額','今日餘額'],data:[['融資(交易單位)',0,0,0,100,110],['融券(交易單位)',0,0,0,200,210],['融資金額(仟元)',0,0,0,300000000,310000000]]}]});
 if(url.pathname.endsWith('/MI_MARGN_TREND'))return Response.json({stat:'OK',date:'20261021',data:[{date:'20261021',marginAmt:310000000,marketValue:1000000}]});
 if(url.pathname.endsWith('/BFIJ3U'))return Response.json({stat:'OK',date:'20261021',crdAmt:12000000000});
 throw Error('Unexpected fixture request');
 };const rows=api.mergeVerifiedMacroRows(await api.loadTaiwanDashboard({DB:db()}),[]),stock=await api.buildTaiwanStockSnapshot('8299',{DB:db()});return {calls,rows,stockCredit:{marketActivity:stock.marketActivity,datasetStatus:stock.datasetStatus.marginCredit}};}
let b,a;try{b=await capture(before);a=await capture(after);}finally{globalThis.Date=NativeDate;globalThis.fetch=originalFetch;}
const select=row=>Object.fromEntries(['id','value','date','status','is_stale','verifiedAt','fetchedAt','captureDeferred','capturePolicy'].map(key=>[key,row?.[key]??null]));
const result={scope:'Local-only replay against v231. Four stocks use identical frozen 2026-10-21 inputs and explicit freshness flags; this is not a fresh production readback.',stocks,
 capturePolicy:{synthetic:true,clock,savedCaptureAt:savedAt,beforeCreditRequests:b.calls.filter(path=>/MI_MARGN|BFIJ3U/.test(path)).length,afterCreditRequests:a.calls.filter(path=>/MI_MARGN|BFIJ3U/.test(path)).length,rows:ids.map(id=>({id,before:select(b.rows.find(row=>row.id===id)),after:select(a.rows.find(row=>row.id===id))})),stockCredit:{symbol:'8299',beforeRequests:b.calls.filter(path=>path.includes('TaiwanStockMarginPurchaseShortSale')).length,afterRequests:a.calls.filter(path=>path.includes('TaiwanStockMarginPurchaseShortSale')).length,before:b.stockCredit,after:a.stockCredit}}};
fs.writeFileSync(root+'credit-window-20261022-before-after.json',JSON.stringify(result,null,2));
console.log(JSON.stringify({stocks:stocks.map(({symbol,grade,label,riskPermission,unchanged})=>({symbol,grade,label,riskPermission,unchanged})),creditRequests:{before:result.capturePolicy.beforeCreditRequests,after:result.capturePolicy.afterCreditRequests},rows:result.capturePolicy.rows.length}));
