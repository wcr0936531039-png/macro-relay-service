/**
 * Drop-in public quote panel for the existing ChatGPT Site.
 * Mount with: <div id="master-model-quotes"></div>
 * <script type="module" src="https://cdn.jsdelivr.net/gh/wcr0936531039-png/macro-relay-service@main/site-embed/quotes.js"></script>
 * Public quotes only; fundamentals remain unavailable until independently sourced.
 */
const FEED='https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/data/stock_snapshots_v2.json';
const LABELS={'8299':'群聯','5289':'宜鼎','2404':'漢唐','5009':'榮鋼'};
const METRICS={close:'收盤價',volume_shares:'成交股數',turnover_twd:'成交金額'};
const mount=document.getElementById('master-model-quotes');
function node(tag,text){const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);return n;}
function latest(rows,metric){return rows.filter(x=>x.metric===metric&&x.status==='ok'&&Number.isFinite(x.value)).sort((a,b)=>b.observed_at.localeCompare(a.observed_at))[0];}
function renderError(msg){mount.replaceChildren(node('p',msg));}
async function run(){
 if(!mount)return;
 mount.replaceChildren(node('p','正在取得官方行情…'));
 try{
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),12000);
  let response;try{response=await fetch(FEED,{cache:'no-store',signal:controller.signal});}finally{clearTimeout(timer);}
  if(!response.ok)throw Error('HTTP '+response.status);
  const data=await response.json();
  if(data.schema_version!==2||!data.stocks||typeof data.stocks!=='object')throw Error('SCHEMA_MISMATCH');
  const fragment=document.createDocumentFragment();
  const title=node('h3','台股官方行情｜資料更新 '+(data.generated_at||'未知'));fragment.append(title);
  for(const [ticker,name] of Object.entries(LABELS)){
   const stock=data.stocks[ticker],card=node('section');card.style.cssText='border:1px solid #aaa5;border-radius:10px;padding:12px;margin:10px 0';
   card.append(node('h4',name+' '+ticker));
   if(!Array.isArray(stock?.observations)){card.append(node('p','缺資料'));fragment.append(card);continue;}
   const rows=stock.observations.filter(x=>x.ticker===ticker);
   const close=latest(rows,'close');
   const age=close?Math.floor((Date.now()-Date.parse(close.observed_at+'T00:00:00Z'))/86400000):Infinity;
   card.append(node('p',close?'觀測日期：'+close.observed_at+(age>5?'｜歷史資料，請核對最新交易日':''):'行情缺資料'));
   for(const [metric,label] of Object.entries(METRICS)){
    const item=latest(rows,metric);
    card.append(node('p',label+'：'+(item?item.value.toLocaleString('zh-TW'):'缺資料')));
   }
   card.append(node('small','來源：'+(close?.source||'未提供')+'｜EPS、ROIC、估值尚未接入'));
   fragment.append(card);
  }
  mount.replaceChildren(fragment);
 }catch(e){renderError('行情暫時無法讀取（'+e.message+'），不顯示推測數值。');}
}
run();
