"""Run the saved macro collector with the authorized morning credit skip.

The downloaded collector is left byte-for-byte unchanged. Its definitions are
loaded before its CLI dispatch. Only the credit collection function is replaced
for this morning invocation; no source observations or dates are changed.
"""
import json
import pathlib
import sys

collector = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path(__file__).with_name('collector.py')
payload = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else collector.parent / 'payload'
sys.argv = [str(collector), '--output', str(payload), '--macro-only']
source = collector.read_text()
boundary = '\nif args.statistics_only:'
if source.count(boundary) != 1:
    raise RuntimeError('Saved collector dispatch changed; review before execution')
scope = {'__name__': 'official_morning_definitions', '__file__': str(collector)}
exec(compile(source.split(boundary)[0], str(collector), 'exec'), scope)
scope['collect_statistics'] = lambda: None
status = scope['collect_macro']()
status['statisticsSkipped'] = 'Morning run: retain last night\'s verified observations and capture timestamps.'
scope['save']('macro-collection-status.json', status)
print(json.dumps({'morningCreditSkipped': True, 'series': len(status['series']),
                  'coreCpiPassed': status['coreCpi']['passed'], 'errors': status['errors']}), flush=True)
