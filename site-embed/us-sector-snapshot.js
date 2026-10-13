import {returnsFromCloses} from './us-sector-history.js';
import {SECTORS,evaluateSectorRotation} from './us-sector-rotation.js';
export function evaluateSectorSnapshot(snapshot = {}) {
  const histories=snapshot.histories || {};
  const feedStatus=snapshot.status || {};
  const benchmark=feedStatus.SPY?.status==='ok' ? returnsFromCloses(histories.SPY) : {status:'UNKNOWN'};
  const sectors={};
  for (const symbol of SECTORS) {
    const history=feedStatus[symbol]?.status==='ok' ? returnsFromCloses(histories[symbol]) : {status:'UNKNOWN'};
    sectors[symbol]=history.status==='OK' && benchmark.status==='OK' && history.observedAt===benchmark.observedAt ? history : {};
  }
  const result=evaluateSectorRotation({benchmark:benchmark.status==='OK'?benchmark:{},sectors});
  return {...result,source:snapshot.source || null,generatedAt:snapshot.generated_at || null,benchmarkObservedAt:benchmark.observedAt || null};
}
