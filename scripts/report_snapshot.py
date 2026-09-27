"""Summarize observations without confusing a successful job with full coverage."""
import json
import os
from pathlib import Path
path = Path('snapshot.json')
lines = ['## Macro relay data audit', '']
if not path.exists():
    lines += ['No snapshot produced. Check the fetch step logs.']
else:
    data = json.loads(path.read_text())
    c = data['coverage']
    lines += [f"Usable: **{c['usable']}/{c['total']}**; retained: {c['retained']}. Mode: {os.environ.get('DRY_RUN', 'see fetch step')}", '', '| Indicator | Value | Observation | Status | Reason |', '|---|---:|---|---|---|']
    for key, row in data['indicators'].items():
        cells = [key, str(row.get('value')), str(row.get('date')), row.get('status','missing'), row.get('error') or row.get('upstream_warning') or '']
        lines.append('| ' + ' | '.join(str(x).replace('|','/').replace('\n',' ') for x in cells) + ' |')
    if c['usable'] < c['total']:
        print(f"::warning::Partial data coverage: {c['usable']}/{c['total']}. This run is not a full data acceptance pass.")
summary = '\n'.join(lines)+'\n'
print(summary)
if os.environ.get('GITHUB_STEP_SUMMARY'):
    with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f: f.write(summary)
