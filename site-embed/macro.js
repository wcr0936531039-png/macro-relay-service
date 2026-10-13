/**
 * Optional macro panel: official-source observations from public snapshot.
 * Add <div id="master-model-macro"></div> and load this file as a module.
 */
const URL='https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/data/keyless_snapshot.json';
const root=document.getElementById('master-model-macro');
const el=(tag,text)=>{const n=document.createElement(tag);n.textContent=text;return n};
async function render(){
 if(!root)return;
 root.replaceChildren(el('p','正在取得總經觀測資料…'));
 try{
  const r=await fetch(URL,{cache:'no-store',signal:AbortSignal.timeout(12000)});
  if(!r.ok)throw Error('HTTP '+r.status);
  const data=await r.json();
  if(data.schema_version!==1||!data.series)throw Error('SCHEMA_MISMATCH');
  const fragment=document.createDocumentFragment();
  fragment.append(el('h3','總經官方觀測資料'));
  fragment.append(el('p','資料池更新：'+(data.generated_at||'未知')+'（非即時報價）'));
  for(const [key,series] of Object.entries(data.series)){
   const card=el('section','');card.style.cssText='border:1px solid #aaa5;border-radius:10px;padding:10px;margin:8px 0';
   const history=Array.isArray(series.history)?series.history:[];
   const last=history.filter(x=>Number.isFinite(x.value)&&/^\\d{4}-\\d{2}-\\d{2}$/.test(x.date||'')).sort((a,b)=>b.date.localeCompare(a.date))[0];
   const stale=last&&Number.isFinite(series.max_age_days)&&(Date.now()-Date.parse(last.date+'T00:00:00Z'))/86400000>series.max_age_days;
   card.append(el('strong',key),el('p',last?last.value+'｜觀測 '+last.date+(stale?'｜資料逾期':''):'缺資料'));
   card.append(el('small','狀態：'+(series.status||'unknown')+'｜來源：'+(series.provider||series.source||'未提供')));
   fragment.append(card);
  }
  root.replaceChildren(fragment);
 }catch(err){root.replaceChildren(el('p','總經資料無法讀取：'+err.message));}
}
render();
