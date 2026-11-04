import {readFile,writeFile,mkdir} from 'node:fs/promises';
import path from 'node:path';
// Build replaces this marker in the downloadable bundle. No credentials needed.
let sourceModule = '__SOURCE_RESEARCH_MODULE__';
let newsModule = '__OFFICIAL_NEWS_MODULE__';
if(newsModule==='__OFFICIAL_NEWS_MODULE__')newsModule=await readFile(new URL('../worker/official-news.js',import.meta.url),'utf8');
if(sourceModule==='__SOURCE_RESEARCH_MODULE__')sourceModule=await readFile(new URL('../worker/source-research.js',import.meta.url),'utf8');
const isDate=value=>{const t=Date.parse(`${value}T00:00:00Z`);return /^\d{4}-\d{2}-\d{2}$/.test(value)&&Number.isFinite(t)&&new Date(t).toISOString().slice(0,10)===value;};
const {SOURCE_FEED_REGISTRY,collectSourceFeed}=new Function('officialImportDate',sourceModule+'\nreturn {SOURCE_FEED_REGISTRY,collectSourceFeed};')(isDate);
const folder=process.argv[2];if(!folder)throw Error('Usage: node collect-source-research.mjs <payload-folder>');
await mkdir(folder,{recursive:true});
const results=await Promise.all(Object.entries(SOURCE_FEED_REGISTRY).map(async([key,spec])=>{
  try {return await collectSourceFeed(key,{timeoutMs:15000});}
  catch(error){return {key,source:spec.url,error:String(error.message||error),attempts:error.sourceAttempts||[]};}
}));
const feeds=results.filter(x=>!x.error),errors=results.filter(x=>x.error);
if(feeds.length)await writeFile(path.join(folder,'sources.json'),JSON.stringify({schema_version:1,researchFeeds:feeds}));
await writeFile(path.join(folder,'source-collection-status.json'),JSON.stringify({checkedAt:new Date().toISOString(),feeds:feeds.map(({key,source,fetchedAt,records,attempts})=>({key,source,fetchedAt,records:records.length,attempts})),errors}));
console.log(JSON.stringify({saved:feeds.length,records:feeds.reduce((n,x)=>n+x.records.length,0),errors}));
const newsApi=new Function(newsModule+'\nreturn {NEWS_FEEDS,officialNews};')();
const newsFeeds=await Promise.all(newsApi.NEWS_FEEDS.map(newsApi.officialNews));
const officialNewsCapture={capturedAt:new Date().toISOString(),feeds:newsFeeds};
await writeFile(path.join(folder,'news.json'),JSON.stringify({schema_version:1,officialNewsCapture}));
const newsStatus={capturedAt:officialNewsCapture.capturedAt,feeds:newsFeeds.map(feed=>({topic:feed.topic,source:feed.source,items:feed.items.length,error:feed.error,delivery:feed.delivery,primary_error:feed.primary_error}))};
await writeFile(path.join(folder,'news-collection-status.json'),JSON.stringify(newsStatus));
console.log('OFFICIAL_NEWS',JSON.stringify(newsStatus));
if(!feeds.length)process.exitCode=1;
