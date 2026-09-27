import assert from 'node:assert/strict';
import { adaptSnapshotRows, readMacroSnapshot } from '../worker/read_macro_snapshot.js';

const snapshot = { schema_version: 1, status: 'partial', generated_at: '2026-09-27T00:00:00Z', indicators: {
  ON_RRP: { value: 0, date: '2026-09-25', status: 'ok', provider: 'FRED' },
  REPO_TEMPORARY_OPERATIONS: { value: 2.5, date: '2026-09-25', status: 'stale', is_stale: true },
  NFP_CHANGE: { value: 150, date: '2026-08-01', status: 'ok' },
  T5YIE: { value: null, date: null, status: 'missing' },
  TW_NDC_SIGNAL: { value: 41, date: '2026-08-01', status: 'ok', light: '紅燈' },
} };
const rows = adaptSnapshotRows(snapshot);
assert.equal(rows.find(x => x.id === 'RRPONTSYD').value, 0);
assert.equal(rows.find(x => x.id === 'RPONTSYD').status, 'stale');
assert.equal(rows.find(x => x.id === 'PAYEMS').value, 150);
assert.equal(rows.find(x => x.id === 'TW_NDC_SIGNAL').light, '紅燈');
assert.equal(rows.some(x => x.id === 'T5YIE'), false);
const uninitialized = await readMacroSnapshot({ MACRO_KV: { get: async () => null } });
assert.equal(uninitialized.status, 'uninitialized');
assert.match(uninitialized.reason, /未對外部資料源發出/);
await assert.rejects(readMacroSnapshot({}), /MACRO_KV binding/);
console.log('worker snapshot reader checks passed');
