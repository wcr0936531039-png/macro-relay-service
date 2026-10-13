import {returnsFromCloses} from './us-sector-history.js';
import {SECTORS,evaluateSectorRotation} from './us-sector-rotation.js';
export function evaluateSectorSnapshot(snapshot = {}) {
  const histories=snapshot.histories || {};
  const feedStatus=snapshot.status || {};
  const benchmark=feedStatus.SPY?.status==='ok' ? returnsFromCloses(histories.SPY) : {status:'UNKNOWN'};
  const benchmarkValid=benchmark.status==='OK' && (!feedStatus.SPY?.observed_at || feedStatus.SPY.observed_at===benchmark.observedAt);
  const sectors={};
  for (const symbol of SECTORS) {
    const history=feedStatus[symbol]?.status==='ok' ? returnsFromCloses(histories[symbol]) : {status:'UNKNOWN'};
    sectors[symbol]=history.status==='OK' && benchmarkValid && history.observedAt===benchmark.observedAt && (!feedStatus[symbol]?.observed_at || feedStatus[symbol].observed_at===history.observedAt) ? history : {};
  }
  const result=evaluateSectorRotation({benchmark:benchmarkValid?benchmark:{},sectors});
  return {...result,source:snapshot.source || null,generatedAt:snapshot.generated_at || null,benchmarkObservedAt:benchmark.observedAt || null};
}
