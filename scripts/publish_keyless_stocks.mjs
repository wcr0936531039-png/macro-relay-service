import {mkdir,writeFile} from 'node:fs/promises';
const codes=['8299','5289','2404','5009'];
const month=new Date().toISOString().slice(0,7);
const generated_at=new Date().toISOString();
const sourceTpex='https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes';
const out={schema_version:2,generated_at,stocks:{}};
function num(x){const n=Number(String(x??'').replaceAll(',',''));return Number.isFinite(n)&&String(x??'').trim()!==''?n:null;}
function rocDate(x){const s=String(x??'');if(!/^\d{7}$/.test(s))throw Error('INVALID_TPEX_DATE');return [Number(s.slice(0,3))+1911,s.slice(3,5),s.slice(5,7)].join('-');}
const tpexRes=await fetch(sourceTpex,{headers:{Accept:'application/json'}});
if(!tpexRes.ok)throw Error('TPEX_HTTP_'+tpexRes.status);
const tpex=await tpexRes.json();
if(!Array.isArray(tpex))throw Error('TPEX_SCHEMA_CHANGED');
for(const ticker of codes){
 let rows=[];
 if(ticker!=='2404'){
  const row=tpex.find(x=>String(x.SecuritiesCompanyCode).trim()===ticker);
  if(!row)throw Error('TPEX_MISSING_'+ticker);
  const date=rocDate(row.Date);
  for(const [metric,field] of [['close','Close'],['volume_shares','TradingShares'],['turnover_twd','TransactionAmount']]){
   if(!(field in row))throw Error('TPEX_FIELD_MISSING_'+field);
   const value=num(row[field]);
   if(value!==null)rows.push({ticker,metric,value,observed_at:date,period:'daily',source:'TPEx official',source_url:sourceTpex,status:'ok'});
  }
 }else{
  const url=new URL('https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY');
  url.searchParams.set('date',month.replace('-','')+'01');url.searchParams.set('stockNo',ticker);url.searchParams.set('response','json');
  const res=await fetch(url,{headers:{Accept:'application/json','User-Agent':'Mozilla/5.0'}});
  if(!res.ok)throw Error('TWSE_HTTP_'+res.status);
  const payload=await res.json();
  if(payload.stat!=='OK'||!Array.isArray(payload.fields)||!Array.isArray(payload.data))throw Error('TWSE_SCHEMA');
  const cols=['日期','收盤價','成交股數','成交金額'].map(x=>payload.fields.findIndex(f=>String(f).includes(x)));
  if(cols.some(x=>x<0))throw Error('TWSE_FIELDS');
  for(const row of payload.data){
   const d=String(row[cols[0]]).split('/');if(d.length!==3)continue;
   const date=[Number(d[0])+1911,d[1].padStart(2,'0'),d[2].padStart(2,'0')].join('-');
   for(const [metric,col] of [['close',cols[1]],['volume_shares',cols[2]],['turnover_twd',cols[3]]]){
    const value=num(row[col]);if(value!==null)rows.push({ticker,metric,value,observed_at:date,period:'daily',source:'TWSE official',source_url:url.toString(),status:'ok'});
   }
  }
 }
 if(!rows.length)throw Error('NO_VALID_ROWS_'+ticker);
 out.stocks[ticker]={schema_version:2,ticker,updated_at:generated_at,observations:rows};
}
await mkdir('data',{recursive:true});
await writeFile('data/stock_snapshots_v2.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({generated_at,stocks:Object.fromEntries(Object.entries(out.stocks).map(([k,v])=>[k,v.observations.length]))}));
