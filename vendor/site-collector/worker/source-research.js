// Deterministic source collection. No model API, keys, or inferred consensus.
const SOURCE_RESEARCH_VERSION = 'stock-sources-v1';
const SOURCE_FEED_REGISTRY = {
  twse: {url:'https://openapi.twse.com.tw/v1/opendata/t187ap04_L',name:'TWSE 每日重大訊息',kind:'company_announcement'},
  tpex: {url:'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O',name:'TPEx 每日重大訊息',kind:'company_announcement'},
  semiconductors: {url:'https://www.trendforce.com/feed/Semiconductors.html',name:'TrendForce 半導體研究',kind:'industry_report'},
  display: {url:'https://www.trendforce.com/feed/Display.html',name:'TrendForce 顯示器研究',kind:'industry_report'},
  energy: {url:'https://www.trendforce.com/feed/Energy.html',name:'TrendForce 能源研究',kind:'industry_report'},
  consumer: {url:'https://www.trendforce.com/feed/Consumer_electronics.html',fallbackUrls:['https://www.trendforce.com/presscenter/news/Consumer%20Electronics'],name:'TrendForce 消費電子研究',kind:'industry_report'},
  steel: {url:'https://worldsteel.org/feed/',name:'世界鋼鐵協會產業資料',kind:'industry_report'},
  aviation: {url:'https://www.iata.org/api/rss/pressrelease',name:'IATA 航空市場資料',kind:'industry_report'},
};
const sourceResearchTasks = new Map(), sourceFeedTasks = new Map();
function sourceText(value,limit=400) {
  return String(value||'').replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g,'$1').replace(/<[^>]+>/g,' ').replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;|&apos;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/\s+/g,' ').trim().slice(0,limit);
}
function sourceDate(value) {
  let s=String(value||'').trim();
  if(/^\d{7}$/.test(s))s=`${Number(s.slice(0,3))+1911}-${s.slice(3,5)}-${s.slice(5,7)}`;
  if(/^\d{3}[/.]\d{1,2}[/.]\d{1,2}$/.test(s)){const [y,m,d]=s.split(/[/.]/);s=`${Number(y)+1911}-${m.padStart(2,'0')}-${d.padStart(2,'0')}`;}
  if(/^\d{8}$/.test(s))s=`${s.slice(0,4)}-${s.slice(4,6)}-${s.slice(6,8)}`;
  s=s.replaceAll('/','-');
  if(!officialImportDate(s)||s>new Date().toISOString().slice(0,10))return null;
  return s;
}
function validSourceRecord(row,key) {
  const spec=SOURCE_FEED_REGISTRY[key];if(!spec||row.kind!==spec.kind||!sourceDate(row.source_date)||!row.id||!row.title)return false;
  try {const u=new URL(row.source_url);return u.protocol==='https:'&&(spec.kind==='company_announcement'?u.href===spec.url&&/^\d{4}$/.test(row.symbol):key==='steel'?u.hostname==='worldsteel.org'&&/^\/media\/press-releases\/\d{4}\/[a-z0-9-]+\/$/.test(u.pathname):key==='aviation'?u.hostname==='www.iata.org'&&/^\/en\/pressroom\/\d{4}-releases\/[a-z0-9-]+\/?$/.test(u.pathname):u.hostname==='www.trendforce.com'&&/^\/presscenter\/news\/\d{8}-\d+\.html$/.test(u.pathname));}catch{return false;}
}
function parseSourceFeed(text,key) {
  const spec=SOURCE_FEED_REGISTRY[key],records=[];
  if(!spec)throw Error('unknown_source');
  if(spec.kind==='company_announcement') {
    const rows=JSON.parse(text);if(!Array.isArray(rows))throw Error('invalid_announcement_format');
    for(const raw of rows.slice(0,5000)) {
      const row=Object.fromEntries(Object.entries(raw).map(([key,value])=>[key.trim(),value]));
      const symbol=String(row['公司代號']||row.SecuritiesCompanyCode||row.CompanyCode||'').trim();
      const date=sourceDate(row['發言日期']||row['公告日期']||row.DateOfAnnouncement||row.Date||row.AnnouncementDate);
      const title=sourceText(row['主旨']||row.Subject||row.SubjectOfAnnouncement,200);
      if(!/^\d{4}$/.test(symbol)||!date||!title)continue;
      // 官方開放資料沒有「序號」欄；公開資訊觀測站以 公司代號＋發言日期＋發言時間 辨識同一則重大訊息，用這三欄當原始識別，不用標題自編。
      const time=String(row['發言時間']||row.TimeOfAnnouncement||'').trim().padStart(6,'0'),officialTime=/^\d{6}$/.test(time)&&time!=='000000'?time:null;
      const serial=String(row['序號']||row.SerialNumber||'').trim()||null;
      const record={id:`${key}:${symbol}:${date}:${serial||officialTime||title}`,symbol,kind:spec.kind,title,source_url:spec.url,source_date:date,provider:spec.name,validation_status:'VERIFIED_SOURCE',summary:sourceText(row['說明']||row.Description||row.Explanation,300),
        announcement_time:officialTime,official_key:officialTime?{symbol,spoke_date:date,spoke_time:officialTime,serial}:null,id_basis:serial?'官方序號':officialTime?'公司代號＋發言日期＋發言時間（官方欄位）':'標題（官方未提供發言時間）',
        fact_date:sourceDate(row['事實發生日']||row.FactDate)||null,clause:sourceText(row['符合條款']||row.Clause,40)||null};
      if(validSourceRecord(record,key))records.push(record);
    }
  } else {
    if(!/<rss[\s>]/i.test(text))throw Error('invalid_report_feed');
    const blocks=[...text.matchAll(/<item>([\s\S]*?)<\/item>/gi)];
    for(const [,block] of blocks.slice(0,60)) {
      const field=name=>sourceText(block.match(new RegExp(`<${name}[^>]*>([\\s\\S]*?)<\\/${name}>`,'i'))?.[1],500);
      const url=field('link'),published=Date.parse(field('pubDate'));
      if(!Number.isFinite(published)||published>Date.now()+60000)continue;
      const record={id:url,kind:spec.kind,title:field('title').split(/\s+/).slice(0,22).join(' '),source_url:url,source_date:new Date(published).toISOString().slice(0,10),published_at:new Date(published).toISOString(),provider:spec.name,validation_status:'VERIFIED_SOURCE',summary:key==='steel'?'世界鋼鐵協會原始產業資料；日期由原始 RSS 核對。全球粗鋼資料不等同特殊鋼需求或個別公司訂單。':'研究機構發布的產業研究；標題與發布日期已由原始 RSS 核對。報告預測不視為公司指引或市場 EPS 共識。'};
      if(key==='aviation')record.summary='IATA 原始航空市場資料；發布日期由 RSS 核對。旅運／貨運需求不等同航太零件訂單或個別公司獲利。';
      record.source_excerpt=sourceText(field('description'),360);
      record.read_state=record.source_excerpt?'rss_excerpt':'metadata_only';
      if(record.source_excerpt)record.summary=`RSS 原文摘要：${record.source_excerpt}；僅作產業研究參考，未核對全文，不替代公司指引或 EPS 共識。`;
      if(validSourceRecord(record,key))records.push(record);
    }
    if(!blocks.length)throw Error('empty_report_feed');
    if(!records.length)throw Error('no_valid_report_dates');
  }
  return [...new Map(records.map(row=>[row.id,row])).values()].sort((a,b)=>b.source_date.localeCompare(a.source_date));
}
function validSourceFeedUrl(key,url){const spec=SOURCE_FEED_REGISTRY[key];return !!spec&&[spec.url,...(spec.fallbackUrls||[])].includes(url);}
function parseSourceReportPage(text,key){
  const spec=SOURCE_FEED_REGISTRY[key];if(!spec?.fallbackUrls?.length)throw Error('unsupported_report_page');
  const records=[];
  const pattern=/<h3\b[^>]*>[\s\S]*?<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>[\s\S]*?<\/h3>\s*<h4\b[^>]*>([\s\S]*?)<\/h4>(?:\s*<p\b[^>]*>([\s\S]*?)<\/p>)?/gi;
  for(const match of text.matchAll(pattern)){
    // 「8 October 2026」按 UTC 解析；Date.parse 會用執行環境時區（台北時區會變成前一天，網址日期對不上而整頁 0 筆）。
    const dateText=sourceText(match[3]),dm=dateText.match(/^(\d{1,2}) ([A-Za-z]+) (20\d{2})$/),month=dm?['january','february','march','april','may','june','july','august','september','october','november','december'].indexOf(dm[2].toLowerCase()):-1;
    const timestamp=month>=0?Date.UTC(Number(dm[3]),month,Number(dm[1])):NaN;
    if(!Number.isFinite(timestamp)||timestamp>Date.now()+8*3600000)continue; // 台北當天凌晨 UTC 仍是前一天，容許 8 小時
    const date=new Date(timestamp).toISOString().slice(0,10),url=new URL(match[1],spec.url).href;
    if(!url.includes('/'+date.replaceAll('-','')+'-'))continue;
    const excerpt=sourceText(match[4],360),row={id:url,kind:'industry_report',title:sourceText(match[2],200),source_url:url,source_date:date,published_at:null,date_precision:'day',provider:spec.name,validation_status:'VERIFIED_SOURCE',source_excerpt:excerpt,read_state:excerpt?'category_excerpt':'metadata_only',summary:excerpt?`官方分類頁原文摘要：${excerpt}；僅作產業研究參考，未核對全文，不替代公司指引或EPS共識。`:'官方分類頁標題與發布日；未核對全文，不替代公司指引或EPS共識。'};
    if(validSourceRecord(row,key))records.push(row);
  }
  if(!records.length)throw Error('no_valid_report_page_records');
  return [...new Map(records.map(r=>[r.id,r])).values()].sort((a,b)=>b.source_date.localeCompare(a.source_date));
}
async function collectSourceFeed(key,{fetchImpl=fetch,timeoutMs=9000}={}){
  const spec=SOURCE_FEED_REGISTRY[key];if(!spec)throw Error('unknown_source');
  const attempts=[];
  for(const source of [spec.url,...(spec.fallbackUrls||[])]){
    let httpStatus=null;
    try{
      // TrendForce 對不帶 User-Agent（或 Node 預設 "node"）的請求回 403；GitHub 實測帶瀏覽器式字串 200。
      const response=await fetchImpl(source,{headers:{'User-Agent':'Mozilla/5.0 (compatible; TaiwanStockMaster/1.0; +official public data)',Accept:spec.kind==='industry_report'?'application/rss+xml,application/xml,text/html':'application/json'},signal:AbortSignal.timeout(timeoutMs)});httpStatus=response.status;
      if(!response.ok)throw Error(`HTTP ${httpStatus}`);
      const text=await response.text();if(text.length>2500000)throw Error('source_too_large');
      const records=source===spec.url?parseSourceFeed(text,key):parseSourceReportPage(text,key);
      attempts.push({source,httpStatus,status:'ok',records:records.length});
      return {key,source,primarySource:spec.url,fetchedAt:new Date().toISOString(),records,status:'ok',error:null,attempts,content_version:2};
    }catch(error){attempts.push({source,httpStatus,status:'error',error:String(error.message||error).slice(0,160)});}
  }
  throw Object.assign(Error(attempts.map(a=>a.error).join('; ')),{sourceAttempts:attempts});
}
function freshSourceFeed(saved,key,now=Date.now()){
  const row=saved?.payload,captured=Date.parse(row?.fetchedAt||'');
  return saved?.fresh===true&&row?.status==='ok'&&row?.content_version===2&&validSourceFeedUrl(key,row.source||SOURCE_FEED_REGISTRY[key]?.url)&&Number.isFinite(captured)&&captured<=now+60000&&now-captured<=6*3600000&&Array.isArray(row.records)&&(SOURCE_FEED_REGISTRY[key]?.kind==='company_announcement'||row.records.length>0)&&row.records.every(r=>validSourceRecord(r,key));
}
function sourceIndustryProfile(issuer) {
  const code=String(issuer.industry_code||'').padStart(2,'0');
  const memory=new Set(['8299','5289','2408','2344','3260','4967','2451']);
  if(memory.has(issuer.id))return {category:'semiconductors',label:'記憶體／儲存',test:/memory|DRAM|NAND|SSD|storage|HBM/i,basis:'記憶體／儲存產品分類'};
  if(issuer.id==='2404')return {category:'semiconductors',label:'半導體廠務工程',test:/semiconductor|foundry|fab|capacity|capital expenditure|chip/i,basis:'廠務工程與半導體資本支出關聯，屬間接產業證據'};
  if(code==='10'||/鋼鐵/.test(issuer.industry)||['5009','2027'].includes(issuer.id))return {category:'steel',label:'鋼鐵業',test:/crude steel production|short range outlook|steel demand/i,basis:'鋼鐵產業統計；特殊鋼、航太訂單與公司轉嫁能力須另行核對'};
  if(['2618','2610','2634','4572','4541','3004'].includes(issuer.id))return {category:'aviation',label:'航空／航太',test:/passenger|cargo|demand|profit|outlook|fuel/i,basis:'航空市場需求；航太供應鏈僅作下游客戶背景，不能替代訂單驗證'};
  if(code==='24'||/半導體/.test(issuer.industry))return {category:'semiconductors',label:'半導體業',test:/\b(?:semiconductor|foundry|chips?|IC|packaging|wafers?|HBM)\b/i,basis:'官方名冊產業代碼優先；尚未核對個別產品曝險'};
  if(code==='26'||/光電/.test(issuer.industry))return {category:'display',label:'光電業',test:/display|panel|OLED|LCD|monitor/i,basis:'官方名冊產業代碼優先；尚未核對個別產品曝險'};
  if(['25','27','28'].includes(code)||/電腦|電子零組件|通信|通訊/.test(issuer.industry))return {category:'consumer',label:issuer.industry,test:/\b(?:PC|computer|notebook|smartphone|server|consumer|component)s?\b/i,basis:'官方名冊產業代碼優先；尚未核對個別產品曝險'};
  if(code==='35'||/綠能|能源/.test(issuer.industry))return {category:'energy',label:issuer.industry,test:/energy|solar|battery|storage|power/i,basis:'官方名冊產業代碼優先；尚未核對個別產品曝險'};
  return {category:null,label:issuer.industry,basis:'此產業尚無已驗證的自動報告來源；公司公告與財報仍獨立抓取'};
}
async function fetchSourceFeed(key,env,force=false) {
  const cacheKey=`source-feed:v1:${key}`,saved=await readRuntimeCache(env,cacheKey);
  if(freshSourceFeed(saved,key)&&(!force||saved.payload.captureMode==='external_collector'))return {...saved.payload,cache:'fresh'};
  if(sourceFeedTasks.has(key))return sourceFeedTasks.get(key);
  const task=(async()=>{
    const spec=SOURCE_FEED_REGISTRY[key],fetchedAt=new Date().toISOString();
    try {
      const payload=await collectSourceFeed(key);
      if(!await writeRuntimeCache(env,cacheKey,payload,6*3600000))throw Error('source_storage_failed');
      return payload;
    }catch(error){
      const latest=await readRuntimeCache(env,cacheKey);
      if(freshSourceFeed(latest,key)&&(!saved||Date.parse(latest.updatedAt)>Date.parse(saved.updatedAt)))return {...latest.payload,cache:'external_saved',primaryError:String(error.message||error).slice(0,160)};
      return {key,source:spec.url,fetchedAt:saved?.payload?.fetchedAt||null,records:saved?.payload?.records||[],status:saved?.payload?'stale':'source_error',error:String(error.message||error).slice(0,160),attempts:error.sourceAttempts||[]};
    }
  })().finally(()=>sourceFeedTasks.delete(key));sourceFeedTasks.set(key,task);return task;
}
async function resolveResearchIssuer(id,env) {
  const roster=await readRuntimeCache(env,'market-official-universe:v1');
  let issuer=roster?.payload?.rows?.find(row=>row.id===id);
  if(issuer)return {...issuer,identitySource:'TWSE／TPEx 官方公司名冊',identityStale:!roster.fresh};
  const response=await searchTaiwanStocks(new Request(`https://site.internal/api/taiwan-stock-search?q=${id}`),env),result=await response.json();
  issuer=result.results?.find(row=>row.id===id);
  if(!issuer||!['TWSE','TPEX'].includes(issuer.market))throw Error('issuer_not_verified');
  return {...issuer,market:issuer.market.toLowerCase(),identitySource:result.source,identityStale:false};
}
async function collectStockSources(id,env,force=false) {
  const issuer=await resolveResearchIssuer(id,env),profile=sourceIndustryProfile(issuer);
  const keys=[issuer.market,...(profile.category?[profile.category]:[])];
  const feeds=await Promise.all(keys.map(key=>fetchSourceFeed(key,env,force)));
  const old=await readRuntimeCache(env,`${SOURCE_RESEARCH_VERSION}:${id}`),cutoff=new Date(Date.now()-180*86400000).toISOString().slice(0,10);
  const announcements=feeds[0].records.filter(row=>row.symbol===id);
  const industry=feeds.slice(1).flatMap(feed=>feed.records.map(row=>({...row,source_feed_key:feed.key,source_fetched_at:feed.fetchedAt,source_stale:feed.status!=='ok'}))).filter(row=>profile.test?.test(row.title));
  const records=[...new Map([...(old?.payload?.records||[]).filter(row=>row.kind==='company_announcement'&&row.source_date>=cutoff),...announcements,...industry].map(row=>[row.id,row])).values()].sort((a,b)=>b.source_date.localeCompare(a.source_date)).slice(0,50);
  const roster=await readRuntimeCache(env,'market-official-universe:v1');
  const peers=(roster?.payload?.rows||[]).filter(row=>row.id!==id&&(issuer.industry_code?row.industry_code===issuer.industry_code:row.industry===issuer.industry)).slice(0,8).map(row=>({symbol:row.id,name:row.name,industry:row.industry,relation:'同名冊產業候選；尚未核對直接競爭關係',production_eligible:false}));
  const errors=feeds.filter(feed=>feed.error).map(feed=>({source:feed.source,error:feed.error,stale:feed.status==='stale'}));
  const payload={version:SOURCE_RESEARCH_VERSION,content_version:2,symbol:id,name:issuer.name,industry:issuer.industry,identitySource:issuer.identitySource,identityStale:issuer.identityStale,profile:{label:profile.label,basis:profile.basis},checkedAt:new Date().toISOString(),status:errors.length?'partial':industry.length?'sources_ready':'partial',records,errors,feeds:feeds.map(({key,source,fetchedAt,status,error,attempts})=>({key,source,fetchedAt,status,error,attempts})),peerCandidates:peers,gaps:[...(!profile.category?['此產業的研究報告來源尚未接入']:industry.length?[]:['目前原始來源未找到符合產品分類的產業報告']),...(!announcements.length?['每日重大訊息來源本次無此公司公告；不代表沒有歷史法說或風險']:[]),'2026／2027 可追溯 EPS 共識及至少三家直接同業估值仍待核對','八期事前公司指引與財報前 EPS 共識尚未由此來源建立'],gatesPromoted:false};
  const remaining=feeds.map(feed=>6*3600000-(Date.now()-Date.parse(feed.fetchedAt))).filter(Number.isFinite);
  const ttl=errors.length?5*60000:Math.max(60000,Math.min(6*3600000,...remaining));
  if(!await writeRuntimeCache(env,`${SOURCE_RESEARCH_VERSION}:${id}`,payload,ttl))throw Error('research_storage_failed');
  return payload;
}
async function stockSourceResearchResponse(request,env={},ctx={}) {
  if(!['GET','POST'].includes(request.method))return Response.json({error:'method_not_allowed'},{status:405,headers:jsonHeaders});
  const url=new URL(request.url),id=url.searchParams.get('id');
  if(!/^[1-9]\d{3}$/.test(id||''))return Response.json({error:'invalid_symbol'},{status:400,headers:jsonHeaders});
  const cached=await readRuntimeCache(env,`${SOURCE_RESEARCH_VERSION}:${id}`);
  if(cached?.fresh&&cached.payload.content_version===2&&url.searchParams.get('refresh')!=='1')return Response.json({...cached.payload,cache:'fresh'},{headers:jsonHeaders});
  if(!sourceResearchTasks.has(id)) {
    const task=collectStockSources(id,env,url.searchParams.get('refresh')==='1').catch(async error=>{const payload={symbol:id,status:'source_error',checkedAt:new Date().toISOString(),records:cached?.payload?.records||[],is_stale:!!cached?.payload,gaps:[String(error.message||error)],gatesPromoted:false};await writeRuntimeCache(env,`${SOURCE_RESEARCH_VERSION}:${id}`,payload,5*60000);return payload;}).finally(()=>sourceResearchTasks.delete(id));
    sourceResearchTasks.set(id,task);try{ctx.waitUntil?.(task);}catch{}
  }
  if(typeof ctx.waitUntil!=='function')return Response.json(await sourceResearchTasks.get(id),{headers:jsonHeaders});
  return Response.json({...cached?.payload,symbol:id,status:cached?.payload?.status||'pending',pending:true,refreshing:!!cached?.payload,is_stale:!!cached?.payload,records:cached?.payload?.records||[],gatesPromoted:false},{headers:jsonHeaders});
}
