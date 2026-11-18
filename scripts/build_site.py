import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
dest=ROOT/'site/data';dest.mkdir(exist_ok=True)
for name in ['tasks.jsonl','sources.json','manifest.json']:
    shutil.copyfile(ROOT/'data'/name,dest/name)
(dest/'leaderboard.json').write_text('[]\n') if not (dest/'leaderboard.json').exists() else None
evidence=ROOT/'docs/evidence/reference-run/report.json'
if evidence.exists():shutil.copyfile(evidence,dest/'diagnostic-report.json')
print('Static site built')
