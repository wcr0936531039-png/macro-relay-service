const NEWS_FEEDS = [
  { topic: '政策／利率', name: '聯準會', candidates: [
    { name: '聯準會', url: 'https://www.federalreserve.gov/feeds/press_monetary.xml', host: 'www.federalreserve.gov' },
  ] },
  { topic: '能源供給', name: '美國能源署', candidates: [
    { name: '美國能源署｜Today in Energy', url: 'https://www.eia.gov/rss/todayinenergy.xml', host: 'www.eia.gov' },
    { name: '美國能源署｜新聞稿備援', url: 'https://www.eia.gov/rss/press_rss.xml', host: 'www.eia.gov' },
    { name: '美國能源署｜Today in Energy 官方網頁', url: 'https://www.eia.gov/todayinenergy/', host: 'www.eia.gov', format:'eia_html' },
  ] },
  { topic: '通膨／就業', name: '美國勞工統計局', candidates: [
    { name: '美國勞工統計局｜Employment Situation RSS', url: 'https://www.bls.gov/feed/empsit.rss', host: 'www.bls.gov' },
    { name: '美國勞工統計局｜最新公告 RSS 備援', url: 'https://www.bls.gov/feed/bls_latest.rss', host: 'www.bls.gov' },
    { name: '美國勞工統計局｜CPI 官方公告', url: 'https://www.bls.gov/news.release/cpi.nr0.htm', host: 'www.bls.gov', format:'bls_html' },
    { name: '美國勞工統計局｜就業官方公告', url: 'https://www.bls.gov/news.release/empsit.nr0.htm', host: 'www.bls.gov', format:'bls_html' },
  ] },
];
function validateOfficialNewsCapture(input,now=Date.now()) {
  if(!input||!recentOfficialCapture(input.capturedAt,now)||!Array.isArray(input.feeds)||input.feeds.length!==NEWS_FEEDS.length)throw Error('invalid_official_news_capture');
  const topics=new Set();
  for(const feed of input.feeds){
    const spec=NEWS_FEEDS.find(x=>x.topic===feed.topic);if(!spec||topics.has(feed.topic)||!Array.isArray(feed.items)||feed.items.length>3)throw Error('invalid_official_news_feed');topics.add(feed.topic);
    if(!feed.items.length&&typeof feed.error!=='string')throw Error('missing_official_news_failure');
    for(const item of feed.items){
      const url=new URL(item.url),date=Date.parse(item.date+'T00:00:00Z');
      if(url.protocol!=='https:'||url.username||url.password||url.hash||url.port||!spec.candidates.some(x=>x.host===url.hostname)||!spec.candidates.some(x=>x.name===item.source)||item.topic!==feed.topic||typeof item.title!=='string'||!item.title.trim()||item.title.length>240||!/^\d{4}-\d{2}-\d{2}$/.test(item.date)||!Number.isFinite(date)||new Date(date).toISOString().slice(0,10)!==item.date||date>now)throw Error('invalid_official_news_article');
    }
  }
  return input;
}
function xmlText(s) {
  return String(s || '').replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1').replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim().slice(0, 240);
}
function tag(s, name) { return s.match(new RegExp(`<${name}(?:\\s[^>]*)?>([\\s\\S]*?)<\\/${name}>`, 'i'))?.[1] || ''; }
function parseOfficialNewsHtml(html,candidate,feed,now=Date.now()) {
  let articles=[];
  if(candidate.format==='eia_html')articles=[...html.matchAll(/<span\s+class=["']date["'][^>]*>([^<]+)<\/span>\s*<h[1-3][^>]*>\s*<a\s+href=["'](detail\.php\?id=\d+)["'][^>]*>([\s\S]*?)<\/a>/gi)].map(m=>({title:xmlText(m[3]),url:new URL(m[2],candidate.url).href,stamp:Date.parse(m[1])}));
  if(candidate.format==='bls_html'){
    const plain=html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' '),date=plain.match(/Transmission of material in this (?:news )?release is embargoed until[\s\S]{0,220}?\b((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, 20\d{2})/i);
    if(date)articles=[{title:xmlText(tag(html,'title')).replace(/\s+/g,' '),url:candidate.url,stamp:Date.parse(date[1]+' 00:00:00 GMT')}];
  }
  return articles.filter(x=>x.title&&Number.isFinite(x.stamp)&&x.stamp<=now).sort((a,b)=>b.stamp-a.stamp).slice(0,3).map(({stamp,...x})=>({...x,date:new Date(stamp).toISOString().slice(0,10),topic:feed.topic,source:candidate.name}));
}
async function officialNews(feed) {
  const errors = [];
  for (const candidate of feed.candidates || [feed]) {
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), candidate.format?10000:7000);
    try {
      const r = await fetch(candidate.url, { signal: controller.signal, headers: { Accept: candidate.format?'text/html':'application/rss+xml, application/xml, text/xml','User-Agent':'TaiwanStockMaster/1.0 (official public releases)' } });
      if (!r.ok) throw Error(`HTTP ${r.status}`);
      const xml = await r.text();
      if(candidate.format){
        if(xml.length>500000)throw Error('公告網頁超出預期大小');
        const items=parseOfficialNewsHtml(xml,candidate,feed);if(!items.length)throw Error('官方網頁缺少可核對標題／原始發布日');
        return {topic:feed.topic,source:candidate.name,items,error:null,delivery:'official_html_fallback',primary_error:errors.join('；')||null,sourceUrl:candidate.url};
      }
      if (xml.length > 450000 || !/<(?:rss|feed)\b/i.test(xml)) throw Error('公告格式不符');
      const articles = [...xml.matchAll(/<item(?:\s[^>]*)?>([\s\S]*?)<\/item>/gi)].slice(0, 18).map(m => {
        const body = m[1], title = xmlText(tag(body, 'title'));
        const raw = xmlText(tag(body, 'link'));
        const date = new Date(xmlText(tag(body, 'pubDate') || tag(body, 'dc:date')));
        try {
          const link = new URL(raw);
          if (link.protocol !== 'https:' || ![candidate.host, candidate.host.replace(/^www\./, '')].includes(link.hostname) || !title || !Number.isFinite(date.getTime()) || date.getTime()>Date.now()) return null;
          return { title, url: link.href, date: date.toISOString().slice(0, 10), topic: feed.topic, source: candidate.name };
        } catch { return null; }
      }).filter(Boolean).sort((a,b) => b.date.localeCompare(a.date)).slice(0, 3);
      if (!articles.length) throw Error('未找到可核對的近期公告');
      return { topic: feed.topic, source: candidate.name, items: articles, error: null,
        delivery: candidate === feed.candidates?.[0] ? 'primary' : 'official_fallback',
        ...(errors.length ? { primary_error: errors[0] } : {}) };
    } catch (e) {
      errors.push(`${candidate.name}：${e.name === 'AbortError' ? '來源逾時' : e.message}`);
    } finally { clearTimeout(timer); }
  }
  return { topic: feed.topic, source: feed.name, items: [], error: errors.join('；') || '官方公告來源暫不可用' };
}
