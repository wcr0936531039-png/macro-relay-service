import fs from 'node:fs';
const root='/workspace/scratch/6b210f4f35e9/',dir=root+'fixpack-deploy-verification/';
const get=name=>JSON.parse(fs.readFileSync(dir+name+'.json','utf8'));
async function load(name){const s=fs.readFileSync(root+name+'/dist/server/index.js','utf8');return import('data:text/javascript;base64,'+Buffer.from(s+'\nexport {evaluateMasterModel,backendMarketScoreModels};').toString('base64'));}
const before=await load('fixpack-c2-approved-deploy'),after=await load('reliability-c1-integration');
const macro=get('after-macro'),market=get('after-market'),expanded=get('after-expanded'),scanner=get('parity-scanner');
const risk=api=>api.backendMarketScoreModels(macro,expanded,market.rows).find(m=>m.market==='TW');
const m=api=>({...macro,riskAssessment:risk(api)}),marketInput={...market,fullMarketScanner:scanner};
const results=[];
for(const symbol of ['8299','5289','2404','5009']){
 const stock=get('parity-stock-'+symbol),live=get('after-model-'+symbol),e=live.evidenceSummary;
 const evidence={estimates:e.consensus.flatMap(c=>c.rows||[]),officialCompany:{records:[...e.company.results,...e.company.guidance,...e.company.outlooks]},sourceResearch:live.sourceResearch};
 const flags={stockFresh:true,macroFresh:true,marketFresh:true,scannerFresh:true};
 const b=before.evaluateMasterModel(stock,m(before),marketInput,flags,evidence),a=after.evaluateMasterModel(stock,m(after),marketInput,flags,evidence);
 const unchanged={gates:JSON.stringify(a.gates)===JSON.stringify(b.gates),scoring:JSON.stringify(a.scoring)===JSON.stringify(b.scoring),veto:JSON.stringify(a.veto)===JSON.stringify(b.veto),adaptiveRating:JSON.stringify(a.adaptiveRating)===JSON.stringify(b.adaptiveRating),primaryValuation:JSON.stringify(a.primaryValuation)===JSON.stringify(b.primaryValuation)};
 if(Object.values(unchanged).some(x=>!x))throw Error(symbol+' changed existing decisions: '+JSON.stringify(unchanged));
 const select=x=>{const d=x.report.advisoryDecision;return {conclusion:d.conclusion,confidence:d.confidence,reasons:d.reasons,changeConditions:d.changeConditions,warnings:d.warnings||[],reasonDetails:d.reasonDetails||[],activeScoreContribution:d.activeScoreContribution,appliedToRating:d.appliedToRating,appliedToRiskBudget:d.appliedToRiskBudget,holdingSuggestedRange:d.holding.suggestedRange};};
 results.push({symbol,inputCheckedAt:stock.checkedAt,priceDate:stock.price?.date,grade:a.adaptiveRating.grade,label:a.adaptiveRating.label,riskPermission:a.adaptiveRating.riskPermission,unchanged,gateCount:a.gates.length,before:select(b),after:select(a)});
}
const result={scope:'Local C1 versus v231, same frozen October 21 stock/macro/market/expanded/scanner and source-qualified evidence. Standardized freshness flags and public evidence context; not a new live Site readback. No cross-market historical snapshot supplied, so missing annual-line evidence stays missing.',stocks:results};
fs.writeFileSync(root+'reliability-c1-advisory-comparison.json',JSON.stringify(result,null,2));
console.log(JSON.stringify(results.map(r=>({symbol:r.symbol,unchanged:r.unchanged,confidence:r.after.confidence,conclusion:r.after.conclusion})),null,2));
